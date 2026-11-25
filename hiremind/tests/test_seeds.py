"""CV de prueba del grupo (datos/seeds/) y modo prueba del correo."""
import pytest
from pydantic import ValidationError

from agente import config, correo
from agente.ingesta import leer_pdf
from agente.modelos import Criterio, Vacante
from agente.seeds import VACANTES_SEEDS, archivos


@pytest.mark.parametrize("carpeta,cantidad", [("farmareds", 25), ("cocinero", 20), ("game_designer", 25), ("tecnico_redes", 25)])
def test_cada_vacante_tiene_sus_cv(carpeta, cantidad):
    assert len(archivos(carpeta)) == cantidad
    assert abs(sum(c.peso for c in VACANTES_SEEDS[carpeta].criterios) - 100) < 0.01


def test_solo_el_cv_escaneado_requiere_revision_manual():
    ilegibles = [p.name for c in VACANTES_SEEDS for p in archivos(c) if not leer_pdf(p.read_bytes()).legible]
    assert ilegibles == ["CV_19_Wilson_Calapi.pdf"]


def test_el_requisito_de_edad_del_aviso_farmareds_se_rechaza():
    with pytest.raises(ValidationError, match="datos personales"):
        Vacante(titulo="Auxiliar de farmacia", criterios=[
            Criterio(id="edad", tipo="habilidad", nombre="Edad entre 20 y 40 años", peso=100, palabras_clave=["20 a 40"])])


def test_modo_prueba_redirige_todos_los_correos(monkeypatch):
    enviados = []

    class SMTPFalso:
        def __init__(self, *a, **k): pass
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def starttls(self): pass
        def login(self, *a): pass
        def send_message(self, m): enviados.append(m)

    monkeypatch.setattr(correo.smtplib, "SMTP", SMTPFalso)
    monkeypatch.setattr(config, "MAIL_HOST", "smtp.prueba")
    monkeypatch.setattr(config, "MAIL_PASSWORD", "x")
    monkeypatch.setattr(config, "MAIL_FROM", "rrhh@prueba.ec")
    monkeypatch.setattr(config, "MAIL_REDIRIGIR_A", "yo@prueba.ec")
    correo.enviar("c.mendoza.net@email.com", "Avanzas", "texto", "<p>x</p>")
    assert enviados[0]["To"] == "yo@prueba.ec" and "c.mendoza.net@email.com" in enviados[0]["Subject"]

    monkeypatch.setattr(config, "MAIL_REDIRIGIR_A", "")
    correo.enviar("c.mendoza.net@email.com", "Avanzas", "texto", "<p>x</p>")
    assert enviados[1]["To"] == "c.mendoza.net@email.com"


def test_correo_partido_en_dos_lineas_se_detecta():
    assert correo.buscar_correo("Correo: bruno.cedeno.dev@correo.\nexample\nHABILIDADES") == "bruno.cedeno.dev@correo.example"
    assert correo.buscar_correo("Correo: damian@correo\n.example") == "damian@correo.example"
    assert correo.buscar_correo("Instagram: @sazondemayra") == ""
