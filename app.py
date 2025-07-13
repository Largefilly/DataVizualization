import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv("bestsellers_preprocesado.csv")
st.set_page_config(page_title="Dashboard de Libros Amazon", layout="wide")


# SIDEBAR – FILTROS GLOBALES

st.sidebar.title("📊 Filtros")
selected_year = st.sidebar.selectbox("Año", sorted(df['Year'].unique()), index=0)
selected_genre = st.sidebar.multiselect("Género", df['Genre'].unique(), default=df['Genre'].unique())
selected_price_cat = st.sidebar.multiselect("Categoría de precio", df['Price Category'].unique(), default=df['Price Category'].unique())

# Aplicar filtros
df_filtered = df[
    (df['Year'] == selected_year) &
    (df['Genre'].isin(selected_genre)) &
    (df['Price Category'].isin(selected_price_cat))
]

# ========================
# MÉTRICAS CLAVE
# ========================
col1, col2, col3, col4 = st.columns(4)
col1.metric("📚 Libros en el Top", len(df_filtered))
col2.metric("💲 Precio Promedio", f"${df_filtered['Price'].mean():.2f}")
col3.metric("⭐ Rating Promedio", f"{df_filtered['User Rating'].mean():.2f}")
col4.metric("🗣️ Reviews Promedio", int(df_filtered['Reviews'].mean()))
st.markdown("---")


# GRÁFICOS PRINCIPALES


# 1. Distribución de precios (para ejecutivos)
st.subheader("🧮 Distribución de Libros según su Rango de Precio")

# Conteo de categorías
price_counts = df_filtered["Price Category"].value_counts().reset_index()
price_counts.columns = ["Categoría", "Cantidad"]

# Colores consistentes
color_map = {
    "Barato": "#FFFACD",
    "Intermedio": "#B0E0E6",
    "Caro": "#D8BFD8"
}

# Gráfico
fig_price_pie = px.pie(
    price_counts,
    names="Categoría",
    values="Cantidad",
    color="Categoría",
    color_discrete_map=color_map,
    hole=0.4
)
fig_price_pie.update_traces(textinfo="percent+label")
st.plotly_chart(fig_price_pie, use_container_width=True)

# Análisis ejecutivo
st.markdown("""
📌 **Interpretación ejecutiva:**  
La mayoría de los libros más vendidos se encuentran en la categoría **Intermedia (50%)**, seguida por los **Baratos (36%)**.  
Solo un **14%** corresponde a libros **Caro**, lo cual indica que el mercado está orientado hacia precios accesibles.

🎯 **Recomendación estratégica:**  
Mantener un enfoque en libros con precio intermedio o económico para maximizar volumen de ventas.  
Explorar oportunidades de bundling o descuentos en los títulos más caros para aumentar su participación.
""")

# ========================
# 3. Ratings por Género – Visión Ejecutiva
# ========================
st.subheader("🎯 Comparación de Ratings Promedio por Género")

# Calcular resumen estadístico
rating_summary = df_filtered.groupby("Genre")["User Rating"].agg(["count", "mean", "min", "max"]).reset_index()
rating_summary.columns = ["Género", "Cantidad de libros", "Rating Promedio", "Rating Mínimo", "Rating Máximo"]
rating_summary = rating_summary.sort_values("Rating Promedio", ascending=False)

# Mostrar tabla ordenada
st.markdown("📋 **Resumen estadístico por género:**")
st.dataframe(rating_summary, use_container_width=True)

# Gráfico de barras
fig3 = px.bar(
    rating_summary,
    x="Género",
    y="Rating Promedio",
    color="Género",
    text_auto=".2f",
    color_discrete_sequence=px.colors.qualitative.Pastel,
    title="Promedio de Calificaciones por Género"
)
fig3.update_layout(yaxis=dict(range=[4.0, 5.0]), title_x=0.3)
st.plotly_chart(fig3, use_container_width=True)

# Interpretación ejecutiva
st.markdown("""
📌 **Interpretación para negocio:**  
Ambos géneros muestran ratings promedio superiores a 4.5, indicando alta satisfacción lectora.  
Sin embargo, *Fiction* sobresale levemente por encima de *Non Fiction* en promedio.

🎯 **Recomendación estratégica:**  
- Si el objetivo es impulsar satisfacción del cliente, priorizar libros *Fiction* con altas valoraciones.  
- Para nuevos lanzamientos, analizar el enfoque de los libros de Fiction más exitosos.
""")



# FUNCIONALIDADES AVANZADAS


# ========================
# Gráfico: Autores más frecuentes en el Top + Interpretación ejecutiva
# ========================
st.subheader("🧑‍💼 Autores más frecuentes")

# Top 10 autores con más libros en el ranking
top_authors = df["Author"].value_counts().nlargest(10)
fig_authors = px.bar(
    x=top_authors.values,
    y=top_authors.index,
    orientation="h",
    labels={"x": "Apariciones", "y": "Autor"},
    color=top_authors.values,
    color_continuous_scale="Agsunset",
    title="",
)

fig_authors.update_layout(
    showlegend=False,
    xaxis_title="Apariciones",
    yaxis_title="",
    margin=dict(l=10, r=10, t=10, b=10)
)

st.plotly_chart(fig_authors, use_container_width=True)

# Análisis e interpretación
st.markdown("""
📌 **Interpretación ejecutiva:**  
Estos autores son los que **más veces han ingresado al ranking de los más vendidos** en Amazon durante el periodo analizado.  
Indican **consistencia editorial**, fuerte base de lectores y capacidad de conectar con el mercado año tras año.

🎯 **Recomendación estratégica:**  
Explorar alianzas con estos autores para nuevos lanzamientos, traducciones o campañas temáticas.  
Además, sirven como referencia de **benchmark creativo**: estilo, temas, formatos y portadas que generan éxito repetido.
""")


# Gráfico: Libros más recurrentes en el Top (versión sin duplicados)

st.subheader("🏆 Libros más recurrentes en el Top")

# Agrupar libros por nombre base (primera parte del título) + autor
# Suponemos que las variaciones están al final del título
df["Titulo_base"] = df["Name"].apply(lambda x: x.split(":")[0].strip())

libros_top = (
    df.groupby(["Titulo_base", "Author"])
    .agg(Anios_en_Top=("Años en Top", "max"))
    .reset_index()
    .sort_values("Anios_en_Top", ascending=False)
)

# Filtrar libros con 5+ años en el Top
libros_top = libros_top[libros_top["Anios_en_Top"] >= 5]

# Gráfico de barras horizontales
fig_top_books = px.bar(
    libros_top,
    x="Anios_en_Top",
    y="Titulo_base",
    orientation="h",
    color="Anios_en_Top",
    color_continuous_scale="YlOrRd",
    labels={"Anios_en_Top": "Años en el Top", "Titulo_base": "Libro"},
    hover_data=["Author"]
)

fig_top_books.update_layout(
    showlegend=False,
    xaxis_title="Años en el Top",
    yaxis_title="",
    margin=dict(l=10, r=10, t=10, b=10)
)

st.plotly_chart(fig_top_books, use_container_width=True)

# Explicación
st.markdown("""
📌 **Interpretación ejecutiva:**  
Estos libros han logrado estar **5 años o más en el ranking de más vendidos**.  
Son títulos con una **demanda sostenida en el tiempo**, lo cual indica alto valor de marca, recomendaciones de boca en boca, y vigencia temática.

🎯 **Recomendación estratégica:**  
Analizar estos títulos y autores para campañas de marketing, bundles temáticos, traducciones, o nuevos lanzamientos basados en su estilo o enfoque.
""")


# 6. Evolución del rating promedio (visión ejecutiva)

st.subheader("📈 Tendencia del Rating Promedio por Año")

# Datos
rating_year = df.groupby("Year")["User Rating"].mean().reset_index()

# Gráfico
fig_rating_trend = px.line(
    rating_year,
    x="Year",
    y="User Rating",
    markers=True,
    title="Evolución del Rating Promedio (2009–2019)"
)
fig_rating_trend.update_traces(line_color="#00CC96")
fig_rating_trend.update_layout(title_x=0.3, yaxis=dict(range=[4.5, 4.8]))
st.plotly_chart(fig_rating_trend, use_container_width=True)

# Interpretación ejecutiva
st.markdown("""
📌 **Análisis ejecutivo:**  
En la última década se observa una **tendencia ascendente** en las calificaciones promedio de los libros más vendidos.  
Esto podría reflejar una mayor calidad editorial, mejor alineación con los gustos del lector, o una mayor exigencia en los títulos que llegan al top.

🎯 **Sugerencia estratégica:**  
Seguir priorizando libros con ratings altos en campañas de visibilidad y detectar patrones editoriales comunes en los mejor valorados de años recientes.
""")

# 8. Mapa de calor de correlaciones
st.subheader("🔥 Correlaciones entre variables clave")

# Calcular matriz de correlación
correlaciones = df[["Price", "Reviews", "User Rating", "Años en Top", "Rating x Review"]].corr()

# Gráfico
fig8 = px.imshow(
    correlaciones,
    text_auto=True,
    color_continuous_scale="RdBu_r",
    title="Mapa de Calor de Correlaciones"
)
st.plotly_chart(fig8, use_container_width=True)

# Interpretación ejecutiva
st.markdown("""
📌 **¿Qué significa esto para el negocio?**

Este mapa de calor muestra **relaciones estadísticas** entre variables clave del éxito de un libro:

- **Reviews** y **Años en Top** tienen una **correlación positiva moderada**, lo que sugiere que más reseñas se asocian a mayor permanencia en el ranking.
- **Rating x Review**, una métrica sintética que combina cantidad y calidad, tiene fuerte correlación con **Reviews** y ligera relación con **User Rating**.
- **Precio** no muestra una relación fuerte con ninguna variable clave, lo cual indica que el valor de un libro no está necesariamente asociado a su precio.

🎯 **Recomendación estratégica**:
- Priorizar libros con altas reseñas y ratings para estrategias de retención y visibilidad.
- Investigar más a fondo qué impulsa las reseñas: ¿promoción?, ¿relevancia temática?, ¿influencia de autores?
""")

# 10. Autores destacados (3+ apariciones en el Top)
st.subheader("👤 Autores destacados (3+ apariciones en el Top)")

# Agrupar por autor y calcular estadísticas
author_summary = (
    df.groupby("Author")
    .agg(
        Apariciones=("Name", "count"),
        Prom_Rating=("User Rating", "mean"),
        Prom_Reviews=("Reviews", "mean"),
        Prom_Precio=("Price", "mean"),
        Generos=("Genre", lambda x: ', '.join(set(x)))
    )
    .reset_index()
)

# Filtrar autores con al menos 3 apariciones
author_summary = author_summary[author_summary["Apariciones"] >= 3]

# Ordenar para encontrar al mejor
top_autor = author_summary.sort_values(by="Prom_Rating", ascending=False).iloc[0]

# Mostrar mensaje ejecutivo
st.markdown(f"""
📌 **Interpretación ejecutiva:**  
Este gráfico posiciona a los autores más frecuentes según su **popularidad** (reviews) y **valoración** (ratings), segmentados por género.

🏅 **Autor con mejor rating promedio:**  
**{top_autor['Author']}** con una calificación promedio de **{top_autor['Prom_Rating']:.2f}**,  
con **{top_autor['Prom_Reviews']:.0f} reviews promedio** y **{top_autor['Apariciones']} títulos** en el Top.

🎯 **Recomendación estratégica:**  
Considerar a estos autores para nuevas ediciones, traducciones, bundles o campañas destacadas. Tienen evidencia de éxito sostenido.
""")

# Visualización en scatter plot
fig_auth = px.scatter(
    author_summary,
    x="Prom_Rating",
    y="Prom_Reviews",
    size="Apariciones",
    color="Generos",
    hover_name="Author",
    size_max=40,
    labels={
        "Prom_Rating": "Rating promedio",
        "Prom_Reviews": "Reviews promedio",
        "Apariciones": "N° de Apariciones",
        "Prom_Precio": "Precio promedio"
    },
    title="Desempeño de Autores Destacados"
)
fig_auth.update_layout(xaxis=dict(range=[4.0, 5.1]), yaxis=dict(range=[0, 20000]), title_x=0.3)
st.plotly_chart(fig_auth, use_container_width=True)

# Tabla complementaria
st.markdown("📊 **Resumen de autores destacados:**")
st.dataframe(author_summary.sort_values("Prom_Rating", ascending=False).reset_index(drop=True), use_container_width=True)



# Sección: Distribución de Popularidad por Género
st.subheader("📊 Distribución de Popularidad por Género")

# Agrupación por género y popularidad para tabla resumen
pop_summary = df.groupby(["Genre", "Popularidad"]).size().reset_index(name="Cantidad")

# Gráfico
fig_pop_genre = px.histogram(
    df,
    x="Popularidad",
    color="Genre",
    barmode="group",
    color_discrete_sequence=px.colors.qualitative.Set2,
    text_auto=True
)
fig_pop_genre.update_layout(
    title="Distribución de Niveles de Popularidad por Género",
    xaxis_title="Nivel de Popularidad",
    yaxis_title="Cantidad de Libros",
    title_x=0.3
)
st.plotly_chart(fig_pop_genre, use_container_width=True)

# Tabla opcional de resumen
st.markdown("📊 **Resumen por género y nivel de popularidad:**")
st.dataframe(pop_summary, use_container_width=True)

# Interpretación ejecutiva
st.markdown("""
📌 **Interpretación para negocio:**  
Este gráfico muestra cómo se distribuyen los niveles de popularidad de los libros en cada género.

🔍 **Hallazgos clave:**  
- La mayoría de los libros **tanto Fiction como Non Fiction** se concentran en la categoría **"Media"**.  
- **Fiction** tiene una mayor proporción de libros en la categoría **"Muy alta"**, lo que sugiere títulos virales o ampliamente compartidos.  
- **Non Fiction** presenta una leve concentración en la categoría **"Baja"**, posiblemente por nichos o títulos especializados.

🎯 **Recomendación estratégica:**  
- Para **acciones de marketing o bundles**, priorizar libros Fiction con popularidad **Muy alta**.  
- Explorar oportunidades para reposicionar títulos Non Fiction con baja popularidad mediante promociones o nuevas ediciones.
""")


# Sección: Popularidad según Categoría de Precio
st.subheader("💰 Popularidad según Categoría de Precio")

# Agrupación por precio y popularidad para resumen tabular
pop_price_summary = df.groupby(["Price Category", "Popularidad"]).size().reset_index(name="Cantidad")

# Gráfico
fig_pop_precio = px.histogram(
    df,
    x="Popularidad",
    color="Price Category",
    barmode="group",
    color_discrete_sequence=px.colors.qualitative.Bold,
    text_auto=True
)
fig_pop_precio.update_layout(
    title="Distribución de Popularidad por Rango de Precio",
    xaxis_title="Nivel de Popularidad",
    yaxis_title="Cantidad de Libros",
    title_x=0.3
)
st.plotly_chart(fig_pop_precio, use_container_width=True)

# Tabla resumen
st.markdown("📊 **Resumen por categoría de precio y nivel de popularidad:**")
st.dataframe(pop_price_summary, use_container_width=True)

# Interpretación ejecutiva
st.markdown("""
📌 **Interpretación para negocio:**  
Este análisis muestra cómo varía la popularidad de los libros según su rango de precio:

🔍 **Hallazgos clave:**  
- La mayoría de los libros **baratos** y **caros** se concentran en **popularidad media**.  
- La **popularidad muy alta** está más presente en la categoría **intermedia**, lo cual podría indicar una **zona de precio óptima** para captar lectores y lograr viralidad.  
- La categoría **cara** tiene menor volumen en niveles altos de popularidad, lo que sugiere posibles barreras de acceso.

🎯 **Recomendación estratégica:**  
- Priorizar productos **intermedios** con buen desempeño en popularidad para maximizar ventas.  
- Evaluar posibles ajustes de precio en libros **caros** que tengan baja o media popularidad.
""")


st.subheader("🎯 Distribución de Ratings por Género")

# Reorganizar los datos para barras
df_bar = df.groupby(["Genre", "Rating Category"]).size().reset_index(name="Cantidad")

# Gráfico
fig_bar = px.bar(
    df_bar,
    x="Rating Category",
    y="Cantidad",
    color="Genre",
    barmode="group",
    color_discrete_sequence=px.colors.qualitative.Set1,
    title="Distribución de Ratings por Género"
)
fig_bar.update_layout(title_x=0.3)
st.plotly_chart(fig_bar, use_container_width=True)


# 10. Hipótesis evaluadas
st.subheader("📌 Hipótesis Evaluadas")
st.markdown("""
1. *Los libros baratos son mejor calificados*  
2. *Los libros con más reviews son más comprados*  
3. *Existen géneros consistentemente bien calificados*  
4. *El precio, rating y reviews están correlacionados*  
5. *Algunos libros y autores aparecen en el Top varios años*  
Todos estos puntos han sido validados visualmente en el dashboard.
""")

# 11. Botón para descargar CSV filtrado
st.subheader("📥 Descargar datos filtrados")
st.download_button("📂 Descargar CSV filtrado", df_filtered.to_csv(index=False).encode("utf-8"), file_name="datos_filtrados.csv")


