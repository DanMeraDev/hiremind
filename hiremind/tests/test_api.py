"""Pruebas de la API (sin LM Studio: el modelo se reemplaza por uno falso)."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from agente import config, llm
from agente.modelos import ExtraccionCV
from api.main import app

CVS = Path(__file__).resolve().parent.parent / "datos" / "cvs"


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", str(tmp_path / "t.db"))
    monkeypatch.setattr(config, "ARCHIVOS_DIR", str(tmp_path / "archivos"))
    return TestClient(app)


def _extraccion_falsa(texto):
    return ExtraccionCV.model_validate({
        "nombre_candidato": "Andrea Salazar Vinueza",
        "formacion": [], "idiomas": [], "proyectos": [], "experiencia": [],
        "habilidades": [{"nombre": "Excel", "cita": "Excel avanzado (tablas dinámicas, BUSCARV)"},
                        {"nombre": "Python", "cita": "Python experto"}],  # esta cita es inventada
    }), 1


def test_vacante_discriminatoria_devuelve_errores_legibles(cliente):
    r = cliente.post("/api/vacantes", json={"titulo": "x", "criterios": [
        {"id": "a", "tipo": "habilidad", "nombre": "Mujer menor de 30 años", "peso": 100, "palabras_clave": ["x"]}]})
    assert r.status_code == 422 and "datos personales" in r.json()["errores"][0]


def test_demo_no_se_duplica(cliente):
    assert cliente.post("/api/vacantes/demo").json() == {"creadas": 2}
    assert cliente.post("/api/vacantes/demo").json() == {"creadas": 0}
    assert len(cliente.get("/api/vacantes").json()) == 2


def test_flujo_completo(cliente, monkeypatch):
    monkeypatch.setattr(llm, "extraer", _extraccion_falsa)
    monkeypatch.setattr(llm, "justificar", lambda t, r: "Cumple con Excel.")
    cliente.post("/api/vacantes/demo")
    vid = cliente.get("/api/vacantes").json()[0]["id"]

    escaneado = cliente.post(f"/api/vacantes/{vid}/cvs",
                             files={"archivo": ("cv_08_escaneado.pdf", (CVS / "cv_08_escaneado.pdf").read_bytes())})
    assert escaneado.json()["estado"] == "revision_manual"

    ok = cliente.post(f"/api/vacantes/{vid}/cvs",
                      files={"archivo": ("cv_01_contable.pdf", (CVS / "cv_01_contable.pdf").read_bytes())}).json()
    assert ok["estado"] == "evaluado" and ok["no_verificados"] == 1 and ok["puntaje"] == 20  # solo Excel

    rk = cliente.get(f"/api/vacantes/{vid}/ranking").json()
    assert [m["archivo"] for m in rk["revision_manual"]] == ["cv_08_escaneado.pdf"]
    cand = rk["candidatos"][0]
    assert cand["top"] and "fecha de nacimiento" in cand["datos_quitados"]
    assert cliente.get(f"/api/candidatos/{cand['id']}/pdf").headers["content-type"] == "application/pdf"

    nuevo = cliente.patch(f"/api/evaluaciones/{cand['eval_id']}/criterios/exp", json={"estado": "cumple"}).json()
    assert nuevo["puntaje"] == 50
    assert "Andrea Salazar" in cliente.get(f"/api/vacantes/{vid}/ranking.csv").text

    res = cliente.get("/api/resumen").json()
    assert res["evaluados"] == 1 and res["revision"] == 1 and res["corregidas"] == 1


def _con_candidato(cliente, monkeypatch):
    monkeypatch.setattr(llm, "extraer", _extraccion_falsa)
    monkeypatch.setattr(llm, "justificar", lambda t, r: "Cumple con Excel.")
    cliente.post("/api/vacantes/demo")
    vid = cliente.get("/api/vacantes").json()[0]["id"]
    cliente.post(f"/api/vacantes/{vid}/cvs",
                 files={"archivo": ("cv_01_contable.pdf", (CVS / "cv_01_contable.pdf").read_bytes())})
    return vid, cliente.get(f"/api/vacantes/{vid}/ranking").json()["candidatos"][0]["id"]


def test_seleccionar_envia_correo_y_sugiere_preguntas(cliente, monkeypatch):
    from agente import correo, entrevista
    vid, cid = _con_candidato(cliente, monkeypatch)
    enviados = []
    monkeypatch.setattr(correo, "enviar", lambda *a: enviados.append(a))
    monkeypatch.setattr(entrevista.llm, "_cliente", lambda: (_ for _ in ()).throw(ConnectionError()))  # sin LM Studio

    b = cliente.get(f"/api/candidatos/{cid}/seleccion/borrador").json()
    assert "Asistente contable" in b["asunto"] and "Andrea Salazar Vinueza" in b["texto"]

    assert cliente.post(f"/api/candidatos/{cid}/seleccionar", json={"correo": "no-es-correo"}).status_code == 422

    r = cliente.post(f"/api/candidatos/{cid}/seleccionar", json={"correo": "andrea@ejemplo.com"}).json()
    destino, asunto, texto, cuerpo = enviados[0]
    assert destino == "andrea@ejemplo.com" and "Excel" in texto and "<div" in cuerpo
    assert r["correo_enviado"] and r["origen_preguntas"] == "plantilla"
    assert any(p["tipo"] == "verificacion" and p["criterio"] == "Experiencia contable (2 años)" for p in r["preguntas"])

    sel = cliente.get(f"/api/vacantes/{vid}/ranking").json()["candidatos"][0]["seleccion"]
    assert sel["correo"] == "andrea@ejemplo.com" and len(sel["preguntas"]) == len(r["preguntas"])

    assert cliente.delete(f"/api/candidatos/{cid}/seleccion").status_code == 204
    assert cliente.get(f"/api/vacantes/{vid}/ranking").json()["candidatos"][0]["seleccion"] is None


def test_error_de_correo_no_guarda_la_seleccion(cliente, monkeypatch):
    from agente import correo
    vid, cid = _con_candidato(cliente, monkeypatch)

    def falla(*a):
        raise correo.ErrorCorreo("El servidor de correo rechazó el usuario o la contraseña")
    monkeypatch.setattr(correo, "enviar", falla)
    r = cliente.post(f"/api/candidatos/{cid}/seleccionar", json={"correo": "a@b.co"})
    assert r.status_code == 502 and "rechazó" in r.json()["detail"]
    assert cliente.get(f"/api/vacantes/{vid}/ranking").json()["candidatos"][0]["seleccion"] is None


def test_preguntas_del_llm_pasan_por_el_filtro_de_equidad(monkeypatch):
    from agente import entrevista
    from agente.demo import VACANTES_DEMO
    respuesta = {"preguntas": [
        {"pregunta": "¿Está casada o tiene hijos?", "criterio": "General", "tipo": "experiencia", "proposito": "x"},
        *[{"pregunta": f"¿Cómo concilia cuentas bancarias? {i}", "criterio": "Excel", "tipo": "tecnica", "proposito": "y"}
          for i in range(4)]]}

    class Falso:
        class chat:
            class completions:
                @staticmethod
                def create(**kw):
                    import json
                    from types import SimpleNamespace as N
                    return N(choices=[N(message=N(content=json.dumps(respuesta)))])
    monkeypatch.setattr(entrevista.llm, "_cliente", lambda: Falso)
    preguntas, origen = entrevista.sugerir(VACANTES_DEMO[0], [], {})
    assert origen == "llm" and len(preguntas) == 4 and all("casada" not in p.pregunta for p in preguntas)
