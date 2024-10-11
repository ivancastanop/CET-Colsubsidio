import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Alistamiento de Información - Históricos SNIES",
    page_icon="",
)

st.title("Alistamiento de Información - Registros Calificados")

uploaded_file = st.file_uploader(
    "Selecciona el archivo a cargar: ", accept_multiple_files=False
)


def cargar_datos():
    df_list = [pd.read_pickle(f"Base_{i}.pkl") for i in range(5)]
    return df_list


def procesar_archivo(archivo, df_list):
    try:
        df = pd.read_excel(archivo)
    except ValueError as e:
        st.error("El archivo no se pudo cargar. No contiene el formato correcto")
        return None, None, None, None, None

    filtros = df["CÓDIGO SNIES"]
    df_inscritos, df_matriculados, df_admitidos, df_graduados, df_primer_curso = df_list
    df_inscritos = df_inscritos[df_inscritos["CÓDIGO SNIES"].isin(filtros)]
    df_matriculados = df_matriculados[df_matriculados["CÓDIGO SNIES"].isin(filtros)]
    df_admitidos = df_admitidos[df_admitidos["CÓDIGO SNIES"].isin(filtros)]
    df_graduados = df_graduados[df_graduados["CÓDIGO SNIES"].isin(filtros)]
    df_primer_curso = df_primer_curso[df_primer_curso["CÓDIGO SNIES"].isin(filtros)]

    return df_inscritos, df_matriculados, df_admitidos, df_graduados, df_primer_curso


def agrupar_datos(df, columna):
    df_agrupado = df.groupby(["AÑO", "SEMESTRE"])[columna].sum().reset_index()
    df_agrupado["AÑO_SEMESTRE"] = (
        df_agrupado["AÑO"].astype(str) + "-" + df_agrupado["SEMESTRE"].astype(str)
    )
    return df_agrupado


def crear_grafico(df_agrupado, columna, titulo):
    base = (
        alt.Chart(df_agrupado)
        .mark_line(point=True)
        .encode(
            x=alt.X("AÑO_SEMESTRE:N", title="Año y Semestre"),
            y=alt.Y(columna, scale=alt.Scale(zero=False), title=titulo),
        )
    )
    text = base.mark_text(align="left", baseline="middle", dx=10, dy=-5).encode(
        text=columna
    )
    chart = (base + text).properties(
        title=alt.TitleParams(titulo, anchor="middle"), width=500, height=300
    )
    return chart


df_list = cargar_datos()

if st.button("Procesar archivo"):
    df_inscritos, df_matriculados, df_admitidos, df_graduados, df_primer_curso = (
        procesar_archivo(uploaded_file, df_list)
    )

    if df_inscritos is not None:
        data_frames = {
            "Inscritos": ("INSCRITOS", df_inscritos),
            "Matriculados": ("MATRICULADOS", df_matriculados),
            "Admitidos": ("ADMITIDOS", df_admitidos),
            "Graduados": ("GRADUADOS", df_graduados),
            "Primer Curso": ("PRIMER CURSO", df_primer_curso),
        }

        for titulo, (columna, df) in data_frames.items():
            df_agrupado = agrupar_datos(df, columna)
            chart = crear_grafico(df_agrupado, columna, f"Estudiantes {titulo}")
            with st.container():
                st.write(f"### {titulo}")
                st.altair_chart(chart, use_container_width=True)

        st.success("Proceso terminado con éxito")
