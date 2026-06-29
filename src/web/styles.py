import streamlit as st


def aplicar_estilo_global():
    st.markdown(
        """
        <style>
            :root {
                --nutri-primary: #1F7A4D;
                --nutri-primary-dark: #145A38;
                --nutri-soft: #F4FAF6;
                --nutri-border: #E6ECE8;
                --nutri-text: #1F2933;
                --nutri-muted: #667085;
                --nutri-card: #FFFFFF;
                --nutri-warning: #B76E00;
                --nutri-danger: #B42318;
                --nutri-success: #027A48;
            }

            .main .block-container {
                padding-top: 1.2rem;
                padding-bottom: 2rem;
                max-width: 1380px;
            }

            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #F7FBF8 0%, #EEF7F1 100%);
                border-right: 1px solid var(--nutri-border);
            }

            section[data-testid="stSidebar"] h1,
            section[data-testid="stSidebar"] h2,
            section[data-testid="stSidebar"] h3 {
                color: var(--nutri-primary-dark);
            }

            .nutri-header {
                padding: 1.1rem 1.3rem;
                border-radius: 22px;
                background: linear-gradient(135deg, #114D31 0%, #1F7A4D 48%, #6BCB8F 100%);
                color: white;
                margin-bottom: 1.2rem;
                box-shadow: 0 14px 35px rgba(31, 122, 77, 0.18);
            }

            .nutri-header h1 {
                margin: 0;
                font-size: 2rem;
                font-weight: 800;
                letter-spacing: -0.02em;
            }

            .nutri-header p {
                margin: 0.35rem 0 0 0;
                font-size: 1rem;
                opacity: 0.92;
            }

            .nutri-card {
                padding: 1rem 1.1rem;
                border: 1px solid var(--nutri-border);
                border-radius: 18px;
                background: var(--nutri-card);
                box-shadow: 0 10px 25px rgba(16, 24, 40, 0.045);
                margin-bottom: 1rem;
            }

            .soft-alert {
                padding: 0.9rem 1rem;
                border-left: 5px solid var(--nutri-primary);
                background: var(--nutri-soft);
                border-radius: 14px;
                margin: 0.6rem 0;
                color: var(--nutri-text);
            }

            .danger-alert {
                padding: 0.9rem 1rem;
                border-left: 5px solid var(--nutri-danger);
                background: #FFF5F3;
                border-radius: 14px;
                margin: 0.6rem 0;
                color: var(--nutri-text);
            }

            .completion-box {
                padding: 1rem;
                border-radius: 18px;
                border: 1px solid var(--nutri-border);
                background: white;
                box-shadow: 0 10px 25px rgba(16, 24, 40, 0.045);
                margin: 0.8rem 0 1rem 0;
            }

            .completion-title {
                font-weight: 800;
                font-size: 1.05rem;
                color: var(--nutri-text);
                margin-bottom: 0.2rem;
            }

            .completion-subtitle {
                color: var(--nutri-muted);
                font-size: 0.9rem;
                margin-bottom: 0.8rem;
            }

            .status-pill {
                display: inline-block;
                padding: 0.22rem 0.58rem;
                border-radius: 999px;
                font-size: 0.78rem;
                font-weight: 700;
                background: #ECFDF3;
                color: #027A48;
                border: 1px solid #ABEFC6;
            }

            .status-pill-warning {
                background: #FFFAEB;
                color: #B54708;
                border: 1px solid #FEDF89;
            }

            .status-pill-danger {
                background: #FEF3F2;
                color: #B42318;
                border: 1px solid #FECDCA;
            }

            .nav-caption {
                font-size: 0.78rem;
                color: var(--nutri-muted);
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-weight: 800;
                margin-top: 0.8rem;
                margin-bottom: 0.2rem;
            }

            div[data-testid="stMetric"] {
                background: #FFFFFF;
                border: 1px solid var(--nutri-border);
                padding: 0.85rem;
                border-radius: 18px;
                box-shadow: 0 8px 22px rgba(16, 24, 40, 0.04);
            }

            div[data-testid="stMetric"] label {
                color: var(--nutri-muted);
            }

            .stTabs [data-baseweb="tab-list"] {
                gap: 0.4rem;
            }

            .stTabs [data-baseweb="tab"] {
                border-radius: 999px;
                padding: 0.45rem 0.9rem;
                background: #F8FAFC;
                border: 1px solid #EAECF0;
            }

            .stTabs [aria-selected="true"] {
                background: #ECFDF3;
                border: 1px solid #ABEFC6;
                color: var(--nutri-primary-dark);
                font-weight: 700;
            }

            .muted-small {
                color: var(--nutri-muted);
                font-size: 0.9rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def header(titulo: str, subtitulo: str = ""):
    st.markdown(
        f"""
        <div class="nutri-header">
            <h1>{titulo}</h1>
            <p>{subtitulo}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card_info(texto: str):
    st.markdown(f'<div class="soft-alert">{texto}</div>', unsafe_allow_html=True)


def card_alerta(texto: str):
    st.markdown(f'<div class="danger-alert">{texto}</div>', unsafe_allow_html=True)


def status_pill(texto: str, tipo: str = "success"):
    classe = "status-pill"
    if tipo == "warning":
        classe += " status-pill-warning"
    elif tipo == "danger":
        classe += " status-pill-danger"
    st.markdown(f'<span class="{classe}">{texto}</span>', unsafe_allow_html=True)


def completion_box(titulo: str, subtitulo: str, percentual: float):
    percentual = max(0, min(100, float(percentual or 0)))
    st.markdown(
        f"""
        <div class="completion-box">
            <div class="completion-title">{titulo}</div>
            <div class="completion-subtitle">{subtitulo}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(percentual / 100, text=f"{percentual:.1f}% completo")
