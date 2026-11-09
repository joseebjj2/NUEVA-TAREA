import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuración de la página en modo ancho
st.set_page_config(
    page_title="Dashboard interactivo de notas",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# BARRA LATERAL (DATOS Y FILTROS)
# ---------------------------------------------------------
st.sidebar.title("Datos y filtros")

# Subida interactiva del archivo (obligatoria)
uploaded_file = st.sidebar.file_uploader("Carga el archivo de estudiantes", type=["csv"])

if uploaded_file is None:
    st.title("Dashboard interactivo de notas")
    st.info("👈 Por favor, carga tu archivo CSV en la barra lateral para comenzar.")
    st.stop()

# Lectura del archivo CSV subido
@st.cache_data
def cargar_datos(file):
    data = pd.read_csv(file)
    # Estandarizar nombres de columnas por seguridad si fuera necesario
    if "Promedio" not in data.columns:
        # Calcular promedio si no viene calculado
        if "nota_1" in data.columns and "nota_2" in data.columns:
            data["Promedio"] = (data["nota_1"] + data["nota_2"]) / 2
    if "Asistencia (%)" not in data.columns and "asistencia" in data.columns:
        data["Asistencia (%)"] = data["asistencia"]
    if "Sexo" not in data.columns and "sexo" in data.columns:
        data["Sexo"] = data["sexo"].str.capitalize()
    if "Sección" not in data.columns and "seccion" in data.columns:
        data["Sección"] = data["seccion"].str.upper()
    if "Estudiante" not in data.columns and "estudiante" in data.columns:
        data["Estudiante"] = data["estudiante"]
    if "ID" not in data.columns and "id" in data.columns:
        data["ID"] = data["id"]
    return data

df = cargar_datos(uploaded_file)

st.sidebar.markdown("---")

# Filtro de Sexo
sexos_disponibles = df["Sexo"].unique().tolist() if "Sexo" in df.columns else ["Mujer", "Hombre"]
sexo_seleccionado = st.sidebar.multiselect("Sexo", sexos_disponibles, default=sexos_disponibles)

# Filtro de Sección
secciones_disponibles = ["Todas"] + sorted(df["Sección"].unique().tolist()) if "Sección" in df.columns else ["Todas"]
seccion_seleccionada = st.sidebar.selectbox("Sección", secciones_disponibles)

# Rango del promedio
rango_promedio = st.sidebar.slider("Rango del promedio", 1.0, 7.0, (1.0, 7.0), 0.1)

# Asistencia mínima (%)
asistencia_minima = st.sidebar.number_input("Asistencia mínima (%)", min_value=0, max_value=100, value=0, step=1)

if not sexo_seleccionado:
    st.sidebar.warning("Los filtros se combinan. Quitar ambos sexos deja la selección vacía.")

# ---------------------------------------------------------
# FILTRADO DE DATOS
# ---------------------------------------------------------
df_filtrado = df.copy()

if sexo_seleccionado:
    df_filtrado = df_filtrado[df_filtrado["Sexo"].isin(sexo_seleccionado)]

if seccion_seleccionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Sección"] == seccion_seleccionada]

df_filtrado = df_filtrado[
    (df_filtrado["Promedio"] >= rango_promedio[0]) & 
    (df_filtrado["Promedio"] <= rango_promedio[1]) &
    (df_filtrado["Asistencia (%)"] >= asistencia_minima)
]

# ---------------------------------------------------------
# CUERPO PRINCIPAL
# ---------------------------------------------------------

# Logotipo institucional en la barra lateral
st.sidebar.markdown("---")
try:
    st.sidebar.image("logo-vector-universidad-san-sebastian.jpg", use_column_width=True)
except:
    pass

st.title("Dashboard interactivo de notas")
st.markdown("Explora los resultados de un curso combinando filtros. **Promedio**: 50 % de cada evaluación. **Aprobación del ejercicio**: promedio mayor o igual a 4,0. Datos ficticios.")

# Texto de filtros activos
sexos_str = ", ".join(sexo_seleccionado) if sexo_seleccionado else "Ninguno"
st.markdown(f"**Filtros activos:** {sexos_str} · **Sección:** {seccion_seleccionada} · **Promedio:** {rango_promedio[0]:.2f} a {rango_promedio[1]:.2f} · **Asistencia mínima:** {asistencia_minima} %")

st.markdown("")

# Métricas superiores
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("Estudiantes seleccionados", len(df_filtrado))
with col_m2:
    prom_general = df_filtrado["Promedio"].mean() if len(df_filtrado) > 0 else 0.0
    st.metric("Promedio general", f"{prom_general:.2f}")
with col_m3:
    if len(df_filtrado) > 0:
        aprobados = len(df_filtrado[df_filtrado["Promedio"] >= 4.0])
        porcentaje_aprobacion = (aprobados / len(df_filtrado)) * 100
    else:
        porcentaje_aprobacion = 0.0
    st.metric("Aprobación", f"{porcentaje_aprobacion:.2f} %".replace(".", ","))

st.markdown("---")

# Controles de visualización y tabla
col_ctrl1, col_ctrl2 = st.columns([2, 1])
with col_ctrl1:
    st.write("Gráfico")
    tipo_grafico = st.radio("Gráfico", ["Notas por estudiante", "Promedio por sección"], horizontal=True, label_visibility="collapsed")
with col_ctrl2:
    mostrar_tabla = st.checkbox("Mostrar tabla", value=True)

# Layout condicional para Gráfico y Tabla
if mostrar_tabla:
    col_izq, col_der = st.columns([1.2, 1])
else:
    col_izq, col_der = st.columns([1, 0.001])

with col_izq:
    st.subheader("Visualización de notas")
    if len(df_filtrado) > 0:
        fig, ax = plt.subplots(figsize=(8, 5))
        
        if tipo_grafico == "Notas por estudiante":
            ax.bar(df_filtrado["Estudiante"], df_filtrado["Promedio"], color="#1f77b4")
            ax.set_ylabel("Promedio de notas")
            ax.set_xlabel("Estudiante")
            ax.set_title("Promedio por estudiante")
            plt.xticks(rotation=45, ha="right")
        else:
            prom_seccion = df_filtrado.groupby("Sección")["Promedio"].mean().reset_index()
            ax.bar(prom_seccion["Sección"], prom_seccion["Promedio"], color="#1f77b4")
            ax.set_ylabel("Promedio de notas")
            ax.set_xlabel("Sección")
            ax.set_title("Promedio por sección")
            
        # Línea horizontal roja punteada de aprobación
        ax.axhline(4.0, color="red", linestyle="--", label="Aprobación: 4,0")
        ax.set_ylim(0, 7)
        ax.legend(loc="upper right")
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("No hay datos disponibles para los filtros seleccionados.")

    # Botón para descargar CSV filtrado
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar selección CSV",
        data=csv,
        file_name='estudiantes_filtrados.csv',
        mime='text/csv',
    )

if mostrar_tabla:
    with col_der:
        st.subheader("Estudiantes seleccionados")
        columnas_mostrar = [c for c in ["ID", "Estudiante", "Sexo", "Sección", "Promedio", "Asistencia (%)"] if c in df_filtrado.columns]
        st.dataframe(df_filtrado[columnas_mostrar], hide_index=True, use_container_width=True)

st.markdown("---")
st.caption(f"Mostrando {len(df_filtrado)} de {len(df)} estudiantes. La asistencia solo se usa como filtro; la aprobación depende del promedio.")
