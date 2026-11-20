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
