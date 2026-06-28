import streamlit as st


def aplicar_estilo_global():
    st.markdown(
        """
        <style>
            .main .block-container {
                padding-top: 1.5rem;
                padding-bottom: 2rem;
            }

            .nutri-header {
                padding: 1.2rem 1.4rem;
                border-radius: 18px;
                background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 45%, #66BB6A 100%);
                color: white;
                margin-bottom: 1.2rem;
                box-shadow: 0 6px 18px rgba(0,0,0,0.08);
            }

            .nutri-header h1 {
                margin: 0;
                font-size: 2.1rem;
                font-weight: 800;
            }

            .nutri-header p {
                margin: 0.3rem 0 0 0;
                font-size: 1rem;
                opacity: 0.95;
            }

            .section-card {
                padding: 1rem 1.1rem;
                border: 1px solid #E0E0E0;
                border-radius: 16px;
                background: #FFFFFF;
                box-shadow: 0 4px 12px rgba(0,0,0,0.04);
                margin-bottom: 1rem;
            }

            .soft-alert {
                padding: 0.9rem 1rem;
                border-left: 5px solid #2E7D32;
                background: #F1F8E9;
                border-radius: 10px;
                margin: 0.6rem 0;
            }

            .danger-alert {
                padding: 0.9rem 1rem;
                border-left: 5px solid #D84315;
                background: #FFF3E0;
                border-radius: 10px;
                margin: 0.6rem 0;
            }

            .muted-small {
                color: #616161;
                font-size: 0.9rem;
            }

            div[data-testid="stMetric"] {
                background: #FFFFFF;
                border: 1px solid #E8E8E8;
                padding: 0.8rem;
                border-radius: 14px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.035);
            }

            div[data-testid="stSidebar"] {
                background: #F7FBF4;
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


def section_card_inicio():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)


def section_card_fim():
    st.markdown('</div>', unsafe_allow_html=True)
