import json
import os
import pickle

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Konfigurasi halaman
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Skrining Diabetes", page_icon="🩸", layout="wide")

# Tema Warna
INK = "#1A2E30"
DEEP_TEAL = "#195A5F"
CARE_TEAL = "#12B8B0"
CORAL = "#D97F6C"
WARM_WHITE = "#F3EDE6"
LINE = "#E0D8D0"
MUTED = "#7A8E90"
BG_SOFT = WARM_WHITE
SIDEBAR_BG = "#FFFFFF"
SIDEBAR_ACTIVE_BG = DEEP_TEAL

HERO_BG = "#E8DDD4"

FEATURES = ['Glucose', 'BMI', 'Age', 'Pregnancies', 'DiabetesPedigreeFunction', 'BloodPressure']
LABEL = {
    'Glucose': 'Glukosa 2 jam (mg/dl)', 
    'BMI': 'BMI (kg/m²)', 
    'Age': 'Usia (tahun)',
    'Pregnancies': 'Jumlah kehamilan', 
    'DiabetesPedigreeFunction': 'Riwayat keluarga (DPF)',
    'BloodPressure': 'Tekanan darah diastolik (mmHg)'
}
RANGE = {
    'Pregnancies': (0, 13, 3, 1), 
    'Glucose': (44, 198, 116, 1), 
    'BloodPressure': (44, 104, 72, 1),
    'BMI': (18.2, 50.0, 32.1, 0.1), 
    'DiabetesPedigreeFunction': (0.078, 1.191, 0.355, 0.001),
    'Age': (21, 66, 29, 1)
}

# ---------------------------------------------------------------------------
# CSS Kustom
# ---------------------------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"], .stMarkdown, .stText, input, button, textarea, select,
p, span, label, div, h1, h2, h3, h4, h5, h6 {{
    font-family: 'Inter', sans-serif !important;
}}

[data-testid="stAppViewContainer"] {{
    background-color: {BG_SOFT};
}}

h1, h2, h3 {{ color: {INK}; font-weight: 800; letter-spacing: -0.02em; }}
h1 {{ font-size: 2.4rem; }}
.lede {{ color: {MUTED}; font-size: 1.05rem; max-width: 65ch; font-weight: 400; }}

/* HERO BOX */
.hero-box {{
    background: {HERO_BG};
    border-radius: 16px;
    padding: 1.8rem 2rem;
    margin-bottom: 2rem;
    border-left: 5px solid {DEEP_TEAL};
}}
.hero-box h1 {{
    margin: 0 0 0.4rem 0;
    font-size: 2.2rem;
    color: {INK};
}}
.hero-box .lede {{
    margin: 0;
    color: #5A6E70;
    font-size: 1rem;
    font-weight: 400;
}}

/* SECTION DIVIDER */
.section-divider {{
    border: none;
    border-top: 1.5px solid {LINE};
    margin: 2rem 0 1.6rem 0;
}}

/* SIDEBAR */
[data-testid="stSidebar"] {{
    background: {SIDEBAR_BG};
    border-right: 1px solid {LINE};
    box-shadow: 2px 0 10px rgba(25, 90, 95, 0.06);
}}
[data-testid="stSidebar"] > div:first-child {{
    padding-top: 1.2rem;
}}

.sb-logo {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 0.4rem 1.2rem 0.4rem;
    margin-bottom: 0.4rem;
    border-bottom: 1px solid {LINE};
}}
.sb-logo .dot {{
    width: 34px; height: 34px; border-radius: 10px;
    background: linear-gradient(135deg, {DEEP_TEAL} 0%, {CARE_TEAL} 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}}
.sb-logo .txt {{
    font-weight: 700; font-size: 1.05rem; color: {INK};
}}

.sb-nav-label {{
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: {MUTED};
    padding: 1.1rem 0.9rem 0.5rem 0.9rem;
}}

[data-testid="stSidebar"] .stRadio > div {{
    gap: 2px;
}}
[data-testid="stSidebar"] .stRadio label {{
    width: 100%;
    padding: 0.6rem 0.9rem;
    border-radius: 10px;
    color: #8AACAF !important;
    font-weight: 500 !important;
    font-size: 0.93rem;
    transition: background 0.15s ease, color 0.15s ease;
    margin-bottom: 1px;
    background: transparent !important;
}}
[data-testid="stSidebar"] .stRadio label:hover {{
    background: rgba(25, 90, 95, 0.07) !important;
    color: {DEEP_TEAL} !important;
}}
[data-testid="stSidebar"] .stRadio input[type="radio"] {{
    display: none;
}}
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child {{
    display: none;
}}
[data-testid="stSidebar"] .stRadio label[data-checked="true"],
[data-testid="stSidebar"] .stRadio label:has(input:checked) {{
    background: {SIDEBAR_ACTIVE_BG} !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 14px rgba(25, 90, 95, 0.30);
    font-weight: 600 !important;
}}

.sb-foot {{
    color: {MUTED}; font-size: 0.78rem; line-height: 1.6;
}}
.sb-foot a {{ color: {CARE_TEAL}; text-decoration: none; }}

/* INPUTS */
input[type="number"] {{
    border-radius: 12px !important;
    border: 1px solid #C8DFE0 !important;
    background-color: #FFFFFF !important;
    box-shadow: 0 2px 6px rgba(25, 90, 95, 0.06) !important;
    padding: 10px !important;
}}

/* BUTTON */
.stButton > button[kind="primary"],
button[kind="primary"],
[data-testid="stFormSubmitButton"] > button {{
    background: {CORAL} !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 15px rgba(217, 127, 108, 0.4) !important;
    font-weight: 700 !important;
    transition: all 0.3s ease;
}}
.stButton > button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(217, 127, 108, 0.6) !important;
}}

/* READING PANEL */
.reading {{
    background: #FFFFFF;
    padding: 1.8rem 1.6rem 1.5rem;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(25, 90, 95, 0.10);
    border-left: 8px solid var(--tone);
}}
.reading .lbl {{ color: {MUTED}; font-size: 0.95rem; margin: 0; font-weight: 600; }}
.reading .num {{ font-size: 4.5rem; font-weight: 800; line-height: 1.1; color: var(--tone); margin: 0.35rem 0 0.2rem; }}
.reading .num small {{ font-size: 1.8rem; font-weight: 700; margin-left: 0.2rem; color: {MUTED}; }}
.reading .verdict {{ font-size: 1.25rem; font-weight: 800; color: {INK}; margin: 0.4rem 0 1rem; }}

.scale {{ position: relative; height: 10px; border-radius: 10px; margin: 0.8rem 0 2.6rem;
          background: linear-gradient(90deg, {CARE_TEAL} 0%, #E8C9A0 45%, {CORAL} 100%); }}
.scale .pin {{ position: absolute; top: -7px; width: 6px; height: 24px; background: {INK};
               border-radius: 4px; transform: translateX(-3px); box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
.scale .tick {{ position: absolute; top: 18px; font-size: 0.75rem; color: {MUTED}; font-weight: 600; transform: translateX(-50%); }}

/* EMPTY STATE */
.empty {{ border: 2px dashed #B8D8DA; border-radius: 15px; padding: 2.5rem 1.6rem;
          color: {MUTED}; background: rgba(255,255,255,0.6); text-align: center; }}

/* FORM */
[data-testid="stForm"] {{
    border: none !important;
    background: #FFFFFF !important;
    border-radius: 20px !important;
    padding: 30px !important;
    box-shadow: 0 10px 40px rgba(25, 90, 95, 0.08) !important;
}}

/* TABS */
[data-testid="stTabs"] button {{
    border-radius: 20px;
    border: 1px solid #C8DFE0;
    padding: 5px 25px;
    margin-right: 15px;
    color: {MUTED};
}}
[data-testid="stTabs"] button[aria-selected="true"] {{
    background: linear-gradient(90deg, {DEEP_TEAL} 0%, {CARE_TEAL} 100%) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 4px 10px rgba(25, 90, 95, 0.30) !important;
}}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Pemuatan model dan data
# ---------------------------------------------------------------------------
STATUS_COLORS = {'Diabetes': CORAL, 'Non-Diabetes': CARE_TEAL}

@st.cache_resource
def load_diabetes_model():
    model_path = "generate_diabetes.pkl"
    if not os.path.exists(model_path):
        st.error(f"File model `{model_path}` tidak ditemukan.")
        return None
    with open(model_path, "rb") as file:
        return pickle.load(file)

@st.cache_data
def load_data():
    data_path = "data.csv"
    if not os.path.exists(data_path):
        st.error(f"File `{data_path}` tidak ditemukan.")
        return pd.DataFrame()
    df = pd.read_csv(data_path, index_col=0)
    df['Status'] = df['Outcome']
    df['Outcome'] = (df['Outcome'] == 'Diabetes').astype(int)
    return df

@st.cache_data
def load_report():
    report_path = "model_report.json"
    if not os.path.exists(report_path):
        return None
    with open(report_path) as f:
        return json.load(f)

def style_fig(fig, height=360):
    fig.update_layout(
        height=height, margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, sans-serif", color=INK, size=13),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None)
    )
    fig.update_xaxes(gridcolor="#E8F0F1", linecolor=LINE)
    fig.update_yaxes(gridcolor="#E8F0F1", linecolor=LINE)
    return fig

def fmt(x, d=2):
    return f"{x:.{d}f}".replace(".", ",")

def reading_panel(proba, youden):
    high = proba >= 0.5
    tone = CORAL if high else CARE_TEAL
    verdict = "Perlu pemeriksaan lanjutan" if high else "Risiko rendah"
    if not high and proba >= youden:
        verdict = "Risiko rendah, tetapi dekat ambang batas"
    pct = proba * 100
    st.markdown(f"""
    <div class="reading" style="--tone:{tone}" role="status" aria-live="polite">
      <p class="lbl">Probabilitas diabetes menurut model</p>
      <p class="num">{pct:.0f}<small>%</small></p>
      <p class="verdict">{verdict}</p>
      <div class="scale" aria-hidden="true">
        <div class="tick" style="left:50%">ambang standar 0,50</div>
        <div class="tick low" style="left:{youden*100:.1f}%">ambang sensitif {fmt(youden)}</div>
        <div class="pin" style="left:{min(max(pct, 1), 99):.1f}%"></div>
      </div>
    </div>""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Halaman 1: Skrining pasien
# ---------------------------------------------------------------------------
def page_screening():
    report = load_report()
    youden = report['youden_threshold'].get(report['best_model'], 0.4) if report else 0.4

    st.markdown('''
    <div class="hero-box">
        <h1>DASHBOARD SKRINING</h1>
        <p class="lede">Evaluasi probabilitas risiko diabetes pasien berdasarkan data klinis.</p>
    </div>
    ''', unsafe_allow_html=True)

    tab_one, tab_batch = st.tabs(["Pasien Individu", "Batch (Banyak Pasien)"])

    with tab_one:
        with st.form("form_pasien", border=False):
            col_kiri, col_kanan = st.columns([1, 2], gap="large")

            with col_kiri:
                st.markdown('### Profil Pasien')
                values = {}
                values['Age'] = st.number_input(LABEL['Age'], min_value=RANGE['Age'][0], max_value=RANGE['Age'][1], value=RANGE['Age'][2], step=RANGE['Age'][3])
                values['BMI'] = st.number_input(LABEL['BMI'], min_value=RANGE['BMI'][0], max_value=RANGE['BMI'][1], value=RANGE['BMI'][2], step=RANGE['BMI'][3], format="%.1f")
                values['Pregnancies'] = st.number_input(LABEL['Pregnancies'], min_value=RANGE['Pregnancies'][0], max_value=RANGE['Pregnancies'][1], value=RANGE['Pregnancies'][2], step=RANGE['Pregnancies'][3])
                values['DiabetesPedigreeFunction'] = st.number_input(LABEL['DiabetesPedigreeFunction'], min_value=RANGE['DiabetesPedigreeFunction'][0], max_value=RANGE['DiabetesPedigreeFunction'][1], value=RANGE['DiabetesPedigreeFunction'][2], step=RANGE['DiabetesPedigreeFunction'][3], format="%.3f")

                st.markdown('<br>', unsafe_allow_html=True)
                submitted = st.form_submit_button("Proses Prediksi", type="primary", use_container_width=True)

            with col_kanan:
                st.markdown('### Statistik Vital')
                c1, c2 = st.columns(2)
                with c1:
                    values['Glucose'] = st.number_input(LABEL['Glucose'], min_value=RANGE['Glucose'][0], max_value=RANGE['Glucose'][1], value=RANGE['Glucose'][2], step=RANGE['Glucose'][3])
                with c2:
                    values['BloodPressure'] = st.number_input(LABEL['BloodPressure'], min_value=RANGE['BloodPressure'][0], max_value=RANGE['BloodPressure'][1], value=RANGE['BloodPressure'][2], step=RANGE['BloodPressure'][3])

                st.markdown('<hr style="border:1px dashed #B8D8DA; margin: 25px 0;">', unsafe_allow_html=True)
                st.markdown('### Prognosis Hasil')

                if submitted:
                    st.session_state['last_input'] = values

                if 'last_input' not in st.session_state:
                    st.markdown('<div class="empty"><strong>Belum ada data.</strong><br>Silakan lengkapi profil dan statistik vital di sebelah kiri, lalu tekan tombol <em>Proses Prediksi</em>.</div>', unsafe_allow_html=True)
                else:
                    model = load_diabetes_model()
                    if model is not None:
                        patient = pd.DataFrame([st.session_state['last_input']])[FEATURES]
                        proba = float(model.predict_proba(patient)[0, 1])
                        reading_panel(proba, youden)

    with tab_batch:
        st.markdown('<p class="note">Unggah file CSV dengan kolom: ' + ", ".join(FEATURES) +
                    '. Setiap baris dihitung sebagai satu pasien.</p>', unsafe_allow_html=True)
        template = pd.DataFrame([{f: RANGE[f][2] for f in FEATURES}])
        st.download_button("Unduh contoh format CSV", template.to_csv(index=False), "contoh_input.csv", "text/csv")
        uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"], key="diab_csv")
        
        if uploaded_file is not None:
            input_df = pd.read_csv(uploaded_file)
            missing = [c for c in FEATURES if c not in input_df.columns]
            if missing:
                st.error(f"Kolom berikut tidak ditemukan di file: {', '.join(missing)}. Samakan nama kolom dengan contoh format CSV.")
                return
            
            X = input_df[FEATURES].apply(pd.to_numeric, errors='coerce')
            bad = X.isna().any(axis=1)
            if bad.any():
                st.warning(f"{int(bad.sum())} baris berisi nilai kosong atau bukan angka dan dilewati.")
            
            X = X[~bad]
            if X.empty:
                st.error("Tidak ada baris yang bisa dihitung.")
                return
            
            model = load_diabetes_model()
            if model is not None:
                proba = model.predict_proba(X)[:, 1]
                out = X.copy()
                out['Probabilitas diabetes'] = proba.round(3)
                out['Hasil'] = np.where(proba >= 0.5, 'Perlu pemeriksaan lanjutan', 'Risiko rendah')
                k1, k2 = st.columns(2)
                k1.metric("Pasien dihitung", len(out))
                k2.metric("Perlu pemeriksaan lanjutan", int((proba >= 0.5).sum()))
                st.dataframe(out, use_container_width=True)
                st.download_button("Unduh hasil", out.to_csv(index=False), "hasil_skrining.csv", "text/csv")

# ---------------------------------------------------------------------------
# Halaman 2: Data pasien (EDA)
# ---------------------------------------------------------------------------
def page_data():
    df = load_data()
    if df.empty:
        return

    st.markdown('''
    <div class="hero-box">
        <h1>Data Pasien</h1>
        <p class="lede">Pima Indians Diabetes Database setelah pembersihan di Capstone 1:
        perempuan keturunan Pima berusia minimal 21 tahun.</p>
    </div>
    ''', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Jumlah pasien", f"{len(df)}")
    k2.metric("Penderita diabetes", fmt(df['Outcome'].mean()*100, 1) + "%")
    k3.metric("Median glukosa, diabetes", f"{df.loc[df.Outcome==1,'Glucose'].median():.0f} mg/dl")
    k4.metric("Median glukosa, non-diabetes", f"{df.loc[df.Outcome==0,'Glucose'].median():.0f} mg/dl")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    left, right = st.columns([1.4, 1], gap="large")
    with left:
        st.subheader("Sebaran per Pemeriksaan")
        feat = st.selectbox("Pemeriksaan", FEATURES, format_func=lambda f: LABEL[f])
        fig = px.histogram(df, x=feat, color='Status', barmode='overlay', opacity=0.7, nbins=30,
                           color_discrete_map=STATUS_COLORS, labels={feat: LABEL[feat], 'count': 'Jumlah pasien'})
        fig.update_yaxes(title="Jumlah pasien")
        st.plotly_chart(style_fig(fig), use_container_width=True)
    with right:
        st.subheader("Korelasi dengan Diabetes")
        corr = df[FEATURES + ['Outcome']].corr()['Outcome'].drop('Outcome').sort_values()
        fig = go.Figure(go.Bar(x=corr.values, y=[LABEL[i] for i in corr.index], orientation='h',
                               marker_color=[CORAL if v == corr.max() else CARE_TEAL for v in corr.values],
                               text=[f"{v:.2f}" for v in corr.values], textposition='outside'))
        fig.update_xaxes(range=[0, max(0.6, corr.max() + 0.1)], title="Korelasi Pearson (r)")
        st.plotly_chart(style_fig(fig), use_container_width=True)
        st.markdown('<p class="note">Glukosa paling kuat berhubungan dengan diabetes. '
                    'Korelasi menunjukkan hubungan linear, bukan sebab-akibat.</p>', unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    with st.expander("Lihat tabel data"):
        st.dataframe(df[FEATURES + ['Status']], use_container_width=True)

# ---------------------------------------------------------------------------
# Halaman 3: Performa model
# ---------------------------------------------------------------------------
def page_model():
    report = load_report()

    if report is None:
        st.markdown('''
        <div class="hero-box">
            <h1>Performa Model</h1>
            <p class="lede">File model_report.json belum ada. Jalankan sel terakhir Capstone 2,
            lalu letakkan file tersebut di folder yang sama dengan app.py.</p>
        </div>
        ''', unsafe_allow_html=True)
        return

    best = report['best_model']

    st.markdown(f'''
    <div class="hero-box">
        <h1>Performa Model</h1>
        <p class="lede">Empat model dilatih pada {report["n_train"]} pasien dan diuji pada
        {report["n_test"]} pasien yang tidak pernah dilihat model. Model yang dipakai dashboard:
        <strong style="color:{DEEP_TEAL}">{best}</strong>, dipilih berdasarkan ROC-AUC 5-fold cross validation.</p>
    </div>
    ''', unsafe_allow_html=True)

    st.subheader("Perbandingan model")
    met = pd.DataFrame(report['metrics']).set_index('Model')
    st.dataframe(met.style.format("{:.3f}").apply(
        lambda r: ['background-color: #D6ECEC; font-weight: 600' if r.name == best else '' for _ in r], axis=1),
        use_container_width=True)
    st.markdown('<p class="note">Selisih AUC antara tiga model terbaik di bawah 0,02. Dengan data uji sebesar ini, '
                'selisih tersebut belum cukup untuk menyatakan satu model lebih unggul. Perbedaan yang nyata '
                'ada pada recall dan presisi.</p>', unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    left, right = st.columns(2, gap="large")
    with left:
        st.subheader("Kurva ROC")
        fig = go.Figure()
        palette = {
            'Logistic Regression': '#7A9EA0',
            'Random Forest': CARE_TEAL,
            'Decision Tree': '#B0CCCE',
            'MLP': DEEP_TEAL
        }
        auc = met['Test AUC'].to_dict()
        for name, pts in report['roc'].items():
            fig.add_trace(go.Scatter(x=pts['fpr'], y=pts['tpr'], mode='lines', name=f"{name} ({auc[name]:.2f})",
                                     line=dict(color=palette.get(name, MUTED), width=3.5 if name == best else 1.8)))
        fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', name='Tebakan acak (0.50)',
                                 line=dict(color=MUTED, dash='dash', width=1)))
        fig.update_xaxes(title="False positive rate", range=[0, 1])
        fig.update_yaxes(title="True positive rate", range=[0, 1.02])
        style_fig(fig, 400).update_layout(legend=dict(orientation="v", x=0.98, y=0.04, xanchor="right",
                                                      yanchor="bottom", bgcolor="rgba(255,255,255,0.9)",
                                                      bordercolor=LINE, borderwidth=1))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Confusion Matrix")
        cm = np.array(report['confusion_matrix'])
        fig = go.Figure(go.Heatmap(z=cm, x=['Prediksi Non-Diabetes', 'Prediksi Diabetes'],
                                   y=['Aktual Non-Diabetes', 'Aktual Diabetes'],
                                   colorscale=[[0, '#EAF4F4'], [1, DEEP_TEAL]], showscale=False,
                                   text=cm, texttemplate="%{text}", textfont=dict(size=22)))
        fig.update_yaxes(autorange='reversed')
        st.plotly_chart(style_fig(fig, 400), use_container_width=True)
        tn, fp, fn, tp = cm.ravel()
        st.markdown(f'<p class="note">Model {best} pada threshold 0,50. Dari {tp+fn} penderita diabetes di data uji, {tp} terdeteksi dan {fn} terlewat. '
                    f'Dari {tn+fp} pasien non-diabetes, {fp} mendapat alarm palsu.</p>', unsafe_allow_html=True)

    if report.get('feature_importance'):
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.subheader("Pemeriksaan yang Paling Berpengaruh pada Model")
        imp = pd.Series(report['feature_importance']).sort_values()
        fig = go.Figure(go.Bar(x=imp.values, y=[LABEL[i] for i in imp.index], orientation='h',
                               marker_color=CARE_TEAL, text=[f"{v:.2f}" for v in imp.values], textposition='outside'))
        fig.update_xaxes(title="Feature importance" if report['importance_type'] == 'feature_importances_' else "Koefisien")
        st.plotly_chart(style_fig(fig, 320), use_container_width=True)

# ---------------------------------------------------------------------------
# Navigasi
# ---------------------------------------------------------------------------
def main():
    with st.sidebar:
        st.markdown(f'''
        <div class="sb-logo">
            <div class="dot">🩸</div>
            <div class="txt">Skrining Diabetes</div>
        </div>
        <div class="sb-nav-label">Navigasi</div>
        ''', unsafe_allow_html=True)

        add_selectitem = st.radio(
            "Halaman",
            ["Skrining Pasien", "Data Pasien", "Performa Model"],
            label_visibility="collapsed"
        )

        st.markdown(f'''
        <div style="height:1.2rem"></div>
        <hr style="border:none;border-top:1px solid {LINE};margin:0.5rem 0 1rem;">
        <p class="sb-foot">Dibuat oleh: Kelompok 5 RB <br>
        Data: <a href="https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database" target="_blank">
        Pima Indians Diabetes Database (Kaggle)</a></p>
        <p class="sb-foot">Alat bantu skrining, bukan pengganti diagnosis tenaga kesehatan.</p>
        ''', unsafe_allow_html=True)

    if "Skrining" in add_selectitem:
        page_screening()
    elif "Data" in add_selectitem:
        page_data()
    else:
        page_model()

if __name__ == "__main__":
    main()
