from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Carte des cybermenaces", page_icon="🌍", layout="wide")

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;800&family=Inter:wght@400;500;600;700&display=swap');

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(255, 0, 120, 0.18), transparent 30%),
                radial-gradient(circle at top right, rgba(0, 255, 255, 0.12), transparent 25%),
                linear-gradient(135deg, #050816 0%, #0b1220 40%, #090d17 100%);
            color: #ecf7ff;
            font-family: 'Inter', sans-serif;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            background: rgba(10, 12, 26, 0.94);
            border-right: 1px solid rgba(0, 255, 204, 0.28);
            box-shadow: inset -1px 0 0 rgba(255, 0, 128, 0.2);
        }

        h1, h2, h3, p, label, .stMarkdown {
            color: #eef9ff !important;
        }

        h1 {
            font-family: 'Orbitron', sans-serif;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #7af7ff !important;
            text-shadow: 0 0 20px rgba(122, 247, 255, 0.6);
        }

        .stCaption {
            color: #a7bfe7 !important;
            letter-spacing: 0.04em;
        }

        div[data-testid="stMetric"] > div {
            background: linear-gradient(180deg, rgba(18, 27, 48, 0.96), rgba(10, 17, 27, 0.96));
            border: 1px solid rgba(0, 255, 204, 0.38);
            border-radius: 18px;
            box-shadow: 0 0 0 1px rgba(255, 0, 153, 0.16), 0 12px 28px rgba(0, 0, 0, 0.35), 0 0 18px rgba(0, 255, 204, 0.12);
            padding: 0.8rem 1rem;
        }

        .stPlotlyChart > div {
            border-radius: 18px;
            overflow: hidden;
            box-shadow: 0 0 0 1px rgba(122, 247, 255, 0.16), 0 18px 30px rgba(0, 0, 0, 0.35), 0 0 24px rgba(255, 0, 153, 0.08);
        }

        .stSelectbox, .stMultiSelect, .stTextInput, .stNumberInput {
            background: rgba(13, 17, 30, 0.8);
            border-radius: 12px;
        }

        .stAlert {
            background: rgba(26, 17, 38, 0.7);
            border: 1px solid rgba(255, 0, 153, 0.32);
            color: #fef2ff;
            border-radius: 12px;
        }

        .top-banner {
            display: inline-flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.5rem 0.9rem;
            margin-bottom: 1rem;
            border: 1px solid rgba(122, 247, 255, 0.25);
            border-radius: 999px;
            background: rgba(10, 20, 32, 0.7);
            box-shadow: 0 0 18px rgba(0, 255, 204, 0.1);
            color: #dfeaff;
            font-size: 0.8rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .status-chip {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            background: rgba(0, 255, 204, 0.14);
            border: 1px solid rgba(0, 255, 204, 0.4);
            color: #75f9d8;
            font-weight: 700;
        }

        .summary-box {
            background: rgba(12, 20, 34, 0.8);
            border: 1px solid rgba(122, 247, 255, 0.15);
            border-radius: 16px;
            padding: 1rem 1rem 0.85rem;
            box-shadow: inset 0 0 0 1px rgba(255, 0, 153, 0.08);
        }

        .summary-box strong {
            color: #7af7ff;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="top-banner"><span class="status-chip">LOCAL</span> Données de cybermenaces</div>',
    unsafe_allow_html=True,
)

st.title("🌍 Carte des cybermenaces")
st.caption("Origine géographique d’adresses IP signalées pour activité malveillante.")

st.sidebar.header("Filtres de recherche")

# Chargement et validation des données
@st.cache_data
def load_data():
    return pd.read_csv(Path(__file__).with_name("ips_geo.csv"))


try:
    df = load_data()
except FileNotFoundError:
    st.error("Le fichier ips_geo.csv est introuvable. Placez-le dans le même dossier que app.py.")
    st.stop()
except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as error:
    st.error(f"Impossible de lire ips_geo.csv : {error}")
    st.stop()

required_columns = {"country", "city", "lat", "lon", "ip"}
missing_columns = sorted(required_columns - set(df.columns))
if missing_columns:
    st.error(
        "Le fichier ips_geo.csv ne contient pas les colonnes requises : "
        + ", ".join(missing_columns)
    )
    st.stop()

for column in ("country", "city", "ip"):
    df[column] = df[column].astype("string").str.strip().replace("", pd.NA)

df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
valid_rows = (
    df["country"].notna()
    & df["city"].notna()
    & df["ip"].notna()
    & df["lat"].between(-90, 90)
    & df["lon"].between(-180, 180)
)
invalid_row_count = int((~valid_rows).sum())
df = df.loc[valid_rows].copy()

has_attack_type = "type" in df.columns
if has_attack_type:
    df["type"] = df["type"].astype("string").str.strip().replace("", pd.NA)

if invalid_row_count:
    st.warning(
        f"{invalid_row_count} ligne(s) avec des champs manquants ou des coordonnées "
        "invalides ont été ignorées."
    )
if df.empty:
    st.error("Aucune ligne exploitable n’a été trouvée dans ips_geo.csv.")
    st.stop()

# Filtres indépendants
if st.sidebar.button("Réinitialiser les filtres", key="reset_filters"):
    st.session_state["pays"] = []
    if has_attack_type:
        st.session_state["types"] = []

pays = st.sidebar.multiselect(
    "Filtrer par pays",
    options=sorted(df["country"].dropna().unique()),
    key="pays",
)
if has_attack_type:
    types = st.sidebar.multiselect(
        "Filtrer par type d'attaque",
        options=sorted(df["type"].dropna().unique()),
        key="types",
    )
else:
    types = []
    st.sidebar.caption("Aucun type d’attaque n’est disponible dans les données actuelles.")

if pays:
    df = df[df["country"].isin(pays)]
if has_attack_type and types:
    df = df[df["type"].isin(types)]

# Chiffres clés
metric_columns = st.columns(4 if has_attack_type else 3)
metric_columns[0].metric("Lignes recensées", len(df))
metric_columns[1].metric("IP uniques", df["ip"].nunique())
metric_columns[2].metric("Pays concernés", df["country"].nunique())
if has_attack_type:
    metric_columns[3].metric("Types d’attaque", df["type"].nunique())

st.markdown(
    """
    <div class="summary-box">
        <strong>Vue d’ensemble</strong><br>
        Explorez les IP recensées sur la carte, comparez les pays et exportez les résultats filtrés.
    </div>
    """,
    unsafe_allow_html=True,
)

if df.empty:
    st.warning("Aucune donnée ne correspond à ces filtres. Essayez une autre combinaison.")
else:
    map_data = df.copy()
    hover_data = ["country", "ip"]
    if has_attack_type:
        hover_data.append("type")

    country_stats = (
        df.groupby("country", as_index=False)
        .agg(
            **{
                "IP recensées": ("ip", "size"),
                "IP uniques": ("ip", "nunique"),
                "Villes": ("city", "nunique"),
            }
        )
    )
    sort_choice = st.selectbox(
        "Trier les statistiques par",
        ["IP recensées (décroissant)", "IP uniques (décroissant)", "Pays (A → Z)"],
    )
    sort_column = {
        "IP recensées (décroissant)": "IP recensées",
        "IP uniques (décroissant)": "IP uniques",
        "Pays (A → Z)": "country",
    }[sort_choice]
    country_stats = country_stats.sort_values(
        sort_column,
        ascending=sort_choice == "Pays (A → Z)",
    )

    map_tab, stats_tab, data_tab = st.tabs(["Carte", "Statistiques détaillées", "Données filtrées"])

    with map_tab:
        fig_carte = px.scatter_geo(
            map_data,
            lat="lat",
            lon="lon",
            hover_name="city",
            hover_data=hover_data,
            projection="natural earth",
            color="type" if has_attack_type else None,
            color_discrete_sequence=["#00f5d4", "#ff006e", "#7b2ff7", "#00bbf9", "#f15bb5"],
            title="Répartition géographique des menaces",
        )
        fig_carte.update_traces(
            marker=dict(size=7, opacity=0.8, line=dict(width=1, color="rgba(255,255,255,0.7)"))
        )
        fig_carte.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            geo=dict(
                bgcolor="rgba(0,0,0,0)",
                showland=True,
                landcolor="#0f1d34",
                showcountries=True,
                countrycolor="#4de3ff",
            ),
            margin=dict(l=20, r=20, t=30, b=20),
            font=dict(color="#eaf9ff"),
        )
        if has_attack_type:
            fig_carte.update_layout(
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(color="#dfeaff"),
                )
            )
        st.plotly_chart(fig_carte, width="stretch")

    with stats_tab:
        st.subheader("Top 10 des pays")
        top = country_stats.nlargest(10, "IP recensées").sort_values("IP recensées")
        fig_top = px.bar(
            top,
            x="IP recensées",
            y="country",
            orientation="h",
            color="IP recensées",
            color_continuous_scale=[[0, "#00f5d4"], [0.5, "#00bbf9"], [1, "#ff006e"]],
            title="Pays les plus touchés",
        )
        fig_top.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="rgba(255,255,255,0.15)", color="#dfeaff"),
            yaxis=dict(categoryorder="total ascending", gridcolor="rgba(255,255,255,0.08)", color="#dfeaff"),
            margin=dict(l=20, r=20, t=30, b=20),
            coloraxis_showscale=False,
            font=dict(color="#eaf9ff"),
        )
        st.plotly_chart(fig_top, width="stretch")
        st.subheader("Résumé par pays")
        st.dataframe(country_stats, width="stretch", hide_index=True)
        if not has_attack_type:
            st.info("Le fichier actuel ne contient pas de colonne « type » ni de date ; ces analyses ne sont donc pas disponibles.")

    with data_tab:
        st.subheader("Lignes correspondant aux filtres")
        st.dataframe(df, width="stretch", hide_index=True)
        st.download_button(
            "Télécharger les résultats en CSV",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name="cybermenaces_filtrees.csv",
            mime="text/csv",
        )
