"""Correo al candidato seleccionado (SMTP con STARTTLS, p. ej. Gmail con contraseña de aplicación)."""
from __future__ import annotations

import html
import re
import smtplib
from email.message import EmailMessage
from email.utils import formataddr

from . import config
from .modelos import Vacante

RE_CORREO = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


class ErrorCorreo(Exception):
    pass


def configurado() -> bool:
    return bool(config.MAIL_HOST and config.MAIL_FROM and (not config.MAIL_SMTP_AUTH or config.MAIL_PASSWORD))


def correo_valido(correo: str) -> bool:
    return bool(RE_CORREO.fullmatch(correo.strip()))


def buscar_correo(texto: str) -> str:
    """Primer correo que aparece en el CV (solo para sugerirlo; el LLM nunca lo ve)."""
    # en PDF de dos columnas el correo a veces queda partido: "nombre@correo" + salto + ".example"
    unido = re.sub(r"(?<=[.@])[ \t]*\n\s*|[ \t]*\n\s*(?=[.@][\w-])", "", texto)
    m = RE_CORREO.search(texto) or RE_CORREO.search(unido)
    return m.group(0).rstrip(".") if m else ""


def componer(vac: Vacante, nombre: str, fortalezas: list[str], mensaje: str = "") -> tuple[str, str, str]:
    """Devuelve (asunto, texto plano, html)."""
    asunto = f"Avanzas a la siguiente etapa: {vac.titulo}"
    saludo = f"Hola {nombre}," if nombre else "Hola,"
    puntos = [
        "Revisamos tu hoja de vida y queremos invitarte a una entrevista para el puesto de "
        f"«{vac.titulo}».",
    ]
    if vac.descripcion:
        puntos.append(f"Sobre el puesto: {vac.descripcion}")
    if fortalezas:
        puntos.append("De tu perfil destacamos: " + ", ".join(fortalezas) + ".")
    if mensaje.strip():
        puntos.append(mensaje.strip())
    puntos.append("En los próximos días te contactaremos para coordinar la fecha y hora de la entrevista. "
                  "Si tienes alguna pregunta, puedes responder a este correo.")
    texto = saludo + "\n\n" + "\n\n".join(puntos) + "\n\nSaludos cordiales,\nEquipo de selección"

    e = html.escape
    parrafos = "".join(f'<p style="margin:0 0 14px">{e(p)}</p>' for p in puntos)
    cuerpo = f"""<div style="font-family:Arial,Helvetica,sans-serif;max-width:560px;margin:auto;color:#0A0147">
<div style="background:#0A0147;color:#fff;padding:18px 22px;border-bottom:6px solid #2EE5A7">
<div style="font-size:12px;letter-spacing:2px;text-transform:uppercase;color:#2EE5A7">Proceso de selección</div>
<div style="font-size:22px;font-weight:bold;margin-top:4px">{e(vac.titulo)}</div></div>
<div style="padding:22px;border:2px solid #0A0147;border-top:0;font-size:15px;line-height:1.55">
<p style="margin:0 0 14px;font-weight:bold">{e(saludo)}</p>{parrafos}
<p style="margin:18px 0 0">Saludos cordiales,<br><strong>Equipo de selección</strong></p></div></div>"""
    return asunto, texto, cuerpo


def enviar(destino: str, asunto: str, texto: str, cuerpo_html: str) -> None:
    if not configurado():
        raise ErrorCorreo("El correo no está configurado (falta hiremind/.env con MAIL_HOST, MAIL_USERNAME y MAIL_PASSWORD)")
    if config.MAIL_REDIRIGIR_A:  # modo prueba: nunca se escribe a la dirección real del CV
        asunto = f"[PRUEBA → {destino}] {asunto}"
        destino = config.MAIL_REDIRIGIR_A
    msg = EmailMessage()
    msg["Subject"] = asunto
    msg["From"] = formataddr(("HireMind · Selección", config.MAIL_FROM))
    msg["To"] = destino
    msg.set_content(texto)
    msg.add_alternative(cuerpo_html, subtype="html")
    try:
        with smtplib.SMTP(config.MAIL_HOST, config.MAIL_PORT, timeout=20) as s:
            if config.MAIL_STARTTLS:
                s.starttls()
            if config.MAIL_SMTP_AUTH:
                s.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)
            s.send_message(msg)
    except smtplib.SMTPAuthenticationError as ex:
        raise ErrorCorreo("El servidor de correo rechazó el usuario o la contraseña") from ex
    except (smtplib.SMTPException, OSError) as ex:
        raise ErrorCorreo(f"No se pudo enviar el correo ({type(ex).__name__}: {ex})") from ex
