import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ===============================
# CONFIGURASI HALAMAN
# ===============================
st.set_page_config(
    page_title="Dashboard Analisis Kuesioner",
    page_icon="📈",
    layout="wide"
)

st.title("📊 Dashboard Analisis Data Kuesioner")

# ===============================
# LOAD DATA LANGSUNG (TANPA UPLOAD)
# ===============================
try:
    df = pd.read_excel("data_kuesioner.xlsx")
except:
    st.error("File data_kuesioner.xlsx tidak ditemukan di folder project.")
    st.stop()

question_cols = [col for col in df.columns if col.startswith("Q")]

if not question_cols:
    st.error("Tidak ditemukan kolom pertanyaan (diawali 'Q').")
    st.stop()

# ===============================
# MAPPING NILAI
# ===============================
mapping = {
    "SS": 5,
    "S": 4,
    "CS": 4,
    "N": 3,
    "TS": 2,
    "STS": 1
}

df_numeric = df[question_cols].replace(mapping).apply(pd.to_numeric, errors="coerce")

# ===============================
# SIDEBAR FILTER
# ===============================
st.sidebar.header("⚙️ Filter Data")

selected_questions = st.sidebar.multiselect(
    "Pilih Pertanyaan",
    question_cols,
    default=question_cols
)

chart_type = st.sidebar.radio(
    "Pilih Jenis Grafik",
    ["Bar", "Pie", "Line", "Radar"]
)

if not selected_questions:
    st.warning("Pilih minimal satu pertanyaan.")
    st.stop()

# ===============================
# METRIK RINGKASAN
# ===============================
col1, col2, col3 = st.columns(3)

col1.metric("Jumlah Responden", len(df))
col2.metric("Total Jawaban", df[selected_questions].count().sum())
col3.metric("Rata-rata Keseluruhan", round(df_numeric[selected_questions].mean().mean(), 2))

st.divider()

# ===============================
# VISUALISASI
# ===============================

if chart_type == "Bar":
    st.subheader("📊 Rata-rata Skor per Pertanyaan")

    mean_scores = df_numeric[selected_questions].mean().reset_index()
    mean_scores.columns = ["Pertanyaan", "Skor"]

    fig = px.bar(
        mean_scores,
        x="Pertanyaan",
        y="Skor",
        text="Skor",
        color="Skor",
        color_continuous_scale="Blues"
    )

    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


elif chart_type == "Pie":
    st.subheader("🥧 Distribusi Jawaban")

    flat = df[selected_questions].stack().dropna().value_counts().reset_index()
    flat.columns = ["Jawaban", "Jumlah"]

    fig = px.pie(
        flat,
        names="Jawaban",
        values="Jumlah",
        hole=0.4
    )

    st.plotly_chart(fig, use_container_width=True)


elif chart_type == "Line":
    st.subheader("📈 Tren Rata-rata Skor")

    mean_scores = df_numeric[selected_questions].mean()

    fig = px.line(
        x=mean_scores.index,
        y=mean_scores.values,
        markers=True
    )

    fig.update_layout(
        xaxis_title="Pertanyaan",
        yaxis_title="Rata-rata Skor"
    )

    st.plotly_chart(fig, use_container_width=True)


elif chart_type == "Radar":
    st.subheader("🛡️ Radar Chart")

    mean_scores = df_numeric[selected_questions].mean()

    if len(mean_scores) < 3:
        st.warning("Radar membutuhkan minimal 3 pertanyaan.")
    else:
        labels = list(mean_scores.index)
        values = list(mean_scores.values)

        labels += [labels[0]]
        values += [values[0]]

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=labels,
            fill='toself'
        ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0,5]))
        )

        st.plotly_chart(fig, use_container_width=True)
