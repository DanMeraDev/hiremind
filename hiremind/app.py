"""HireMind · interfaz Streamlit (Registrar vacante · Cargar hojas de vida · Ver ranking).

Ejecutar:  streamlit run app.py
"""
from __future__ import annotations

import pandas as pd
import streamlit as st
from pydantic import ValidationError

from agente import config, db, llm
from agente.demo import VACANTES_DEMO
from agente.modelos import Criterio, Vacante
from agente.pipeline import evaluar_cv

st.set_page_config(page_title="HireMind", page_icon="🧭", layout="wide")

ETIQUETA_ESTADO = {"cumple": "✅ Cumple", "parcial": "🟡 Parcial", "no_identificado": "⚪ No identificado"}
TIPOS = ["habilidad", "experiencia", "formacion", "idioma"]
NIVELES = ["", "bachillerato", "tecnico", "tecnologo", "tercer_nivel", "cuarto_nivel"]
NIV_IDIOMA = ["", "basico", "intermedio", "avanzado", "nativo"]


# ---------------------------------------------------------------- utilidades
def vacantes() -> list[Vacante]:
    with db.conectar() as con:
        return db.listar_vacantes(con)


def elegir_vacante(clave: str) -> Vacante | None:
    vs = vacantes()
    if not vs:
        st.info("Primero registre una vacante en **1 · Vacante**.")
        return None
    return st.selectbox("Vacante", vs, format_func=lambda v: v.titulo, key=clave)


def mensaje_validacion(e: ValidationError) -> str:
    return " · ".join(err["msg"].removeprefix("Value error, ") for err in e.errors())


# ---------------------------------------------------------------- barra lateral
with st.sidebar:
    st.title("HireMind")
    st.caption("Preselección de hojas de vida · 100 % local")
    pagina = st.radio("Paso", ["1 · Vacante", "2 · Hojas de vida", "3 · Ranking"], label_visibility="collapsed")
    ok, info = llm.servidor_disponible()
    (st.success if ok else st.error)(("Modelo: " if ok else "") + info)
    st.caption("La IA ordena y justifica. **La decisión final es de una persona.**")


# ---------------------------------------------------------------- 1. Vacante
if pagina == "1 · Vacante":
    st.header("Registrar vacante")
    st.write("Defina los criterios y su peso. Los pesos deben sumar 100 %. "
             "No se permiten criterios sobre edad, género, estado civil, nacionalidad o religión.")

    existentes = vacantes()
    if not existentes and st.button("Cargar 2 vacantes de ejemplo"):
        with db.conectar() as con:
            for v in VACANTES_DEMO:
                db.guardar_vacante(con, v)
        st.rerun()

    opciones = [None, *existentes]
    actual = st.selectbox("Editar", opciones, format_func=lambda v: "➕ Nueva vacante" if v is None else v.titulo)

    titulo = st.text_input("Título del puesto", value=actual.titulo if actual else "")
    descripcion = st.text_area("Descripción", value=actual.descripcion if actual else "", height=80)

    filas = [{
        "tipo": c.tipo, "nombre": c.nombre, "peso": c.peso,
        "palabras_clave": ", ".join(c.palabras_clave), "anios_min": c.anios_min,
        "nivel_min": c.nivel_min or "", "idioma": c.idioma or "", "nivel_idioma": c.nivel_idioma or "",
    } for c in (actual.criterios if actual else [])] or [
        {"tipo": "habilidad", "nombre": "", "peso": 100.0, "palabras_clave": "", "anios_min": 0.0,
         "nivel_min": "", "idioma": "", "nivel_idioma": ""}]

    tabla = st.data_editor(
        pd.DataFrame(filas), num_rows="dynamic", width="stretch", key=f"crit_{actual.id if actual else 0}",
        column_config={
            "tipo": st.column_config.SelectboxColumn("Tipo", options=TIPOS, required=True),
            "nombre": st.column_config.TextColumn("Criterio", required=True),
            "peso": st.column_config.NumberColumn("Peso %", min_value=0, max_value=100, step=5),
            "palabras_clave": st.column_config.TextColumn("Palabras clave / sinónimos (separadas por coma)"),
            "anios_min": st.column_config.NumberColumn("Años mín. (experiencia)", min_value=0, step=0.5),
            "nivel_min": st.column_config.SelectboxColumn("Nivel mín. (formación)", options=NIVELES),
            "idioma": st.column_config.TextColumn("Idioma"),
            "nivel_idioma": st.column_config.SelectboxColumn("Nivel idioma", options=NIV_IDIOMA),
        })
    total = float(pd.to_numeric(tabla["peso"], errors="coerce").fillna(0).sum())
    (st.success if abs(total - 100) < 0.01 else st.warning)(f"Suma de pesos: {total:g} %")

    if st.button("Guardar vacante", type="primary"):
        try:
            criterios = []
            for i, f in enumerate(tabla.to_dict("records")):
                if not str(f.get("nombre") or "").strip():
                    continue
                criterios.append(Criterio(
                    id=f"c{i + 1}", tipo=f["tipo"], nombre=str(f["nombre"]).strip(), peso=float(f["peso"] or 0),
                    palabras_clave=[p.strip() for p in str(f.get("palabras_clave") or "").split(",") if p.strip()],
                    anios_min=float(f.get("anios_min") or 0), nivel_min=f.get("nivel_min") or None,
                    idioma=(f.get("idioma") or None), nivel_idioma=f.get("nivel_idioma") or None))
            vac = Vacante(id=actual.id if actual else None, titulo=titulo.strip(), descripcion=descripcion,
                          criterios=criterios)
            if not vac.titulo:
                raise ValueError("Escriba el título del puesto")
        except ValidationError as e:
            st.error(mensaje_validacion(e))
        except ValueError as e:
            st.error(str(e))
        else:
            with db.conectar() as con:
                db.guardar_vacante(con, vac)
            st.success("Vacante guardada.")


# ---------------------------------------------------------------- 2. Hojas de vida
elif pagina == "2 · Hojas de vida":
    st.header("Cargar hojas de vida")
    vac = elegir_vacante("vac_carga")
    if vac:
        archivos = st.file_uploader("Hojas de vida en PDF", type=["pdf"], accept_multiple_files=True)
        st.caption("Los PDF escaneados o ilegibles no se descartan: pasan a revisión manual.")
        if archivos and st.button(f"Evaluar {len(archivos)} hoja(s) de vida", type="primary",
                                  disabled=not llm.servidor_disponible()[0]):
            barra = st.progress(0.0)
            filas = []
            for i, a in enumerate(archivos, 1):
                barra.progress((i - 1) / len(archivos), text=f"Evaluando {a.name} ({i}/{len(archivos)})…")
                try:
                    with db.conectar() as con:
                        r = evaluar_cv(con, vac, a.name, a.getvalue())
                    filas.append({"Archivo": a.name, "Candidato": r.nombre or "—",
                                  "Resultado": "Evaluado" if r.estado == "evaluado" else "Revisión manual",
                                  "Puntaje": r.puntaje if r.estado == "evaluado" else None,
                                  "Segundos": round(r.segundos, 1), "Nota": r.motivo})
                except Exception as e:  # p. ej. LM Studio se cerró
                    filas.append({"Archivo": a.name, "Resultado": "Error", "Nota": f"{type(e).__name__}: {e}"})
            barra.progress(1.0, text="Listo")
            st.dataframe(pd.DataFrame(filas), width="stretch", hide_index=True)
            tiempos = [f["Segundos"] for f in filas if f.get("Segundos")]
            if tiempos:
                st.caption(f"Tiempo promedio: {sum(tiempos) / len(tiempos):.1f} s por CV")
            st.success("Vea el resultado en **3 · Ranking**.")


# ---------------------------------------------------------------- 3. Ranking
else:
    st.header("Ranking de candidatos")
    vac = elegir_vacante("vac_rank")
    if vac:
        with db.conectar() as con:
            filas = db.ranking(con, vac.id)
            manual = db.revision_manual(con, vac.id)
        if not filas and not manual:
            st.info("Todavía no hay hojas de vida evaluadas para esta vacante.")
        else:
            st.write(f"Se ordenan **todos** los CV evaluados ({len(filas)}). "
                     f"Revise con atención el **top {config.TOP_N}** y decida a quién entrevistar.")
            resumen = pd.DataFrame([{
                "#": i, "Candidato": f["nombre"], "Puntaje": f["puntaje"],
                **{c.nombre: ETIQUETA_ESTADO[c.estado] for c in f["criterios"]},
                "Revisar": "⭐ Top" if i <= config.TOP_N else "",
                "Corregido": "✏️" if f["corregida"] else "",
            } for i, f in enumerate(filas, 1)])
            st.dataframe(resumen, width="stretch", hide_index=True,
                         column_config={"Puntaje": st.column_config.ProgressColumn(
                             "Puntaje", min_value=0, max_value=100, format="%.1f")})
            st.download_button("Descargar ranking (CSV)", resumen.to_csv(index=False).encode("utf-8"),
                               f"ranking_vacante_{vac.id}.csv", "text/csv")

            st.subheader("Detalle y evidencias")
            for i, f in enumerate(filas, 1):
                top = "⭐ " if i <= config.TOP_N else ""
                with st.expander(f"{top}#{i} · {f['nombre']} · {f['puntaje']:.1f} / 100 · {f['archivo']}",
                                 expanded=i == 1):
                    st.markdown(f"**Justificación:** {f['justificacion']}")
                    if f["corregida"]:
                        st.caption("✏️ Un criterio fue corregido por una persona; la justificación es la original del agente.")
                    for c in f["criterios"]:
                        a, b = st.columns([3, 1])
                        with a:
                            st.markdown(f"**{c.nombre}** · peso {c.peso:g} % · {ETIQUETA_ESTADO[c.estado]}"
                                        + (" · ✏️ corregido" if c.corregido else ""))
                            st.caption(c.detalle)
                            for cita in c.citas[:3]:
                                st.markdown(f"> “{cita}”")
                        with b:
                            nuevo = st.selectbox("Corregir", list(ETIQUETA_ESTADO),
                                                 index=list(ETIQUETA_ESTADO).index(c.estado),
                                                 format_func=ETIQUETA_ESTADO.get,
                                                 key=f"cor_{f['eval_id']}_{c.criterio_id}", label_visibility="collapsed")
                            if nuevo != c.estado:
                                with db.conectar() as con:
                                    db.corregir_criterio(con, f["eval_id"], c.criterio_id, nuevo)
                                st.rerun()
                    st.caption(f"Tiempo: {f['segundos']:.1f} s · intentos del modelo: {f['intentos']}"
                               + (f" · datos personales excluidos antes del análisis: {', '.join(f['datos_quitados'])}"
                                  if f["datos_quitados"] else ""))

            if manual:
                st.subheader(f"Revisión manual ({len(manual)})")
                st.caption("Estos CV no se descartan: una persona debe revisarlos directamente.")
                st.dataframe(pd.DataFrame(manual).rename(columns={"archivo": "Archivo", "motivo": "Motivo",
                                                                  "creado": "Fecha"}),
                             width="stretch", hide_index=True)
