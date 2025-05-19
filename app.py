import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Analisis Kinerja Individu", layout="wide")
st.title("📊 Aplikasi Analisis Kinerja Individu Pelindo")

uploaded_file = st.file_uploader("Unggah file Penilaian_Kinerja.csv", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Konversi kolom ke numerik
    for col in ["Skor_KPI_Final", "Skor_Assessment", "Skor_Kinerja_Individu"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Kategorisasi
    def kategori(skor):
        if pd.isna(skor): return "Tidak Dinilai"
        elif skor > 110: return "Istimewa"
        elif skor > 105: return "Sangat Baik"
        elif skor >= 90: return "Baik"
        elif skor >= 80: return "Cukup"
        else: return "Kurang"

    df["Kategori_KPI"] = df["Skor_KPI_Final"].apply(kategori)
    df["Kategori_Assessment"] = df["Skor_Assessment"].apply(kategori)
    df["Kategori_Kinerja_Individu"] = df["Skor_Kinerja_Individu"].apply(kategori)

    # Hitung GAP KPI terhadap atasan
    skor_kpi_dict = df.set_index("NIPP_Pekerja")["Skor_KPI_Final"].to_dict()
    def hitung_gap(row):
        skor_unit = row["Skor_KPI_Final"]
        skor_atasan = skor_kpi_dict.get(row["NIPP_Atasan"])
        if pd.notna(skor_unit) and pd.notna(skor_atasan) and skor_atasan != 0:
            return (skor_unit - skor_atasan) / skor_atasan * 100
        return None

    df["Gap_KPI_vs_Atasan_%"] = df.apply(hitung_gap, axis=1)

    st.subheader("📂 Tabel Data dan Kategori Penilaian")
    st.dataframe(df[[
        "NIPP_Pekerja", "Nama_Posisi", "Skor_KPI_Final", "Kategori_KPI",
        "Skor_Assessment", "Kategori_Assessment",
        "Skor_Kinerja_Individu", "Kategori_Kinerja_Individu",
        "NIPP_Atasan", "Gap_KPI_vs_Atasan_%"
    ]])

    # === Visualisasi 3 Skor ===
    st.subheader("📈 Distribusi Skor Penilaian")
    col1, col2, col3 = st.columns(3)

    with col1:
        fig, ax = plt.subplots()
        sns.histplot(df["Skor_KPI_Final"].dropna(), kde=True, ax=ax, color="steelblue")
        ax.set_title("Distribusi Skor KPI Final")
        st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots()
        sns.histplot(df["Skor_Assessment"].dropna(), kde=True, ax=ax, color="darkorange")
        ax.set_title("Distribusi Skor Assessment")
        st.pyplot(fig)

    with col3:
        fig, ax = plt.subplots()
        sns.histplot(df["Skor_Kinerja_Individu"].dropna(), kde=True, ax=ax, color="seagreen")
        ax.set_title("Distribusi Skor Kinerja Individu")
        st.pyplot(fig)

    # === GAP KPI vs ATASAN ===
    st.subheader("📉 Distribusi Gap KPI terhadap Atasan")
    fig, ax = plt.subplots()
    sns.histplot(df["Gap_KPI_vs_Atasan_%"].dropna(), bins=30, kde=True, color="mediumvioletred")
    ax.axvline(-5, color='red', linestyle='--', label='-5% Threshold')
    ax.axvline(5, color='green', linestyle='--', label='+5% Threshold')
    ax.set_title("Distribusi Gap KPI terhadap Atasan")
    ax.set_xlabel("Gap (%)")
    ax.legend()
    st.pyplot(fig)

    # === Kuota Otomatis ===
    st.subheader("🎯 Simulasi Kuota Otomatis Berdasarkan Skor Kinerja Individu")
    q80 = df["Skor_Kinerja_Individu"].quantile(0.80)
    q20 = df["Skor_Kinerja_Individu"].quantile(0.20)

    def assign_kuota(skor):
        if pd.isna(skor): return "Tidak Ditetapkan"
        elif skor >= q80: return "A (Top Performer)"
        elif skor <= q20: return "C (Low Performer)"
        else: return "B (Middle Performer)"

    df["Kategori_Kuota_Otomatis"] = df["Skor_Kinerja_Individu"].apply(assign_kuota)

    st.markdown(f"""
    **Distribusi Kuota Berdasarkan Skor Kinerja Individu:**
    - A (Top 20%) ≥ {q80:.2f}
    - B (Middle 60%) {q20:.2f} – {q80:.2f}
    - C (Bottom 20%) ≤ {q20:.2f}
    """)

    kuota_counts = df["Kategori_Kuota_Otomatis"].value_counts().reindex(["A (Top Performer)", "B (Middle Performer)", "C (Low Performer)"], fill_value=0)
    fig, ax = plt.subplots()
    ax.pie(kuota_counts, labels=kuota_counts.index, autopct='%1.1f%%', startangle=90, colors=["gold", "skyblue", "lightcoral"])
    ax.set_title("Distribusi Kuota Otomatis")
    st.pyplot(fig)

    # === Unduh Hasil Lengkap ===
    st.subheader("📥 Unduh Hasil Analisis")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Unduh CSV Hasil", csv, file_name="Analisis_Kinerja_Pelindo.csv")

