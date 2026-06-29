import streamlit as st
from urllib.parse import quote, unquote

FLUXO_ATENDIMENTO = [
    "Pacientes",
    "Anamnese",
    "Antropometria",
    "Exames",
    "Dashboard",
]

MENU_GROUPS = [
    ("Operação", [
        ("🏠", "Início", "Visão geral"),
        ("👤", "Pacientes", "Cadastro e consulta"),
        ("📝", "Anamnese", "Ficha guiada"),
        ("📏", "Antropometria", "Medidas e evolução"),
        ("🧪", "Exames", "Exames e referências"),
    ]),
    ("Análise", [
        ("📊", "Dashboard", "Painel clínico"),
        ("📈", "Completude", "Maturidade do cadastro"),
    ]),
    ("Gestão", [
        ("✏️", "Edição", "Correção com histórico"),
        ("🗑️", "Exclusão de paciente", "Exclusão segura"),
        ("🗂️", "Bases CSV", "Exportação e bases"),
    ]),
]

PAGINAS_VALIDAS = {
    pagina
    for _, itens in MENU_GROUPS
    for _, pagina, _ in itens
}


def _get_query_page() -> str | None:
    try:
        valor = st.query_params.get("page")
        if isinstance(valor, list):
            valor = valor[0] if valor else None
        if valor:
            return unquote(str(valor))
    except Exception:
        return None
    return None


def _set_query_page(pagina: str):
    try:
        st.query_params["page"] = quote(pagina)
    except Exception:
        pass


def definir_pagina(pagina: str):
    if pagina not in PAGINAS_VALIDAS:
        pagina = "Início"
    st.session_state["pagina_atual"] = pagina
    _set_query_page(pagina)


def avancar_fluxo(pagina_atual: str):
    if pagina_atual not in FLUXO_ATENDIMENTO:
        return

    indice = FLUXO_ATENDIMENTO.index(pagina_atual)
    if indice + 1 < len(FLUXO_ATENDIMENTO):
        definir_pagina(FLUXO_ATENDIMENTO[indice + 1])


def proxima_pagina(pagina_atual: str) -> str | None:
    if pagina_atual not in FLUXO_ATENDIMENTO:
        return None

    indice = FLUXO_ATENDIMENTO.index(pagina_atual)
    if indice + 1 < len(FLUXO_ATENDIMENTO):
        return FLUXO_ATENDIMENTO[indice + 1]

    return None


def _url_pagina(pagina: str) -> str:
    return f"?page={quote(pagina)}"


def _render_nav_item(icone: str, pagina: str, descricao: str, ativo: bool):
    active_class = " active" if ativo else ""
    aria_current = ' aria-current="page"' if ativo else ""
    href = _url_pagina(pagina)

    st.sidebar.markdown(
        f"""
        <a class="ns-nav-link{active_class}" href="{href}" target="_self"{aria_current}>
            <span class="ns-nav-icon">{icone}</span>
            <span class="ns-nav-content">
                <span class="ns-nav-title">{pagina}</span>
                <span class="ns-nav-desc">{descricao}</span>
            </span>
            <span class="ns-nav-indicator"></span>
        </a>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> str:
    pagina_query = _get_query_page()

    if pagina_query in PAGINAS_VALIDAS:
        st.session_state["pagina_atual"] = pagina_query
    elif "pagina_atual" not in st.session_state:
        st.session_state["pagina_atual"] = "Início"

    pagina_atual = st.session_state.get("pagina_atual", "Início")
    if pagina_atual not in PAGINAS_VALIDAS:
        pagina_atual = "Início"
        st.session_state["pagina_atual"] = "Início"

    st.sidebar.markdown(
        """
        <div class="ns-brand">
            <div class="ns-brand-mark">🥗</div>
            <div class="ns-brand-copy">
                <div class="ns-brand-title">NutriSoft</div>
                <div class="ns-brand-subtitle">Gestão nutricional local</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown('<div class="ns-sidebar-divider"></div>', unsafe_allow_html=True)

    for grupo, itens in MENU_GROUPS:
        st.sidebar.markdown(
            f'<div class="ns-nav-section">{grupo}</div>',
            unsafe_allow_html=True,
        )

        for icone, pagina, descricao in itens:
            _render_nav_item(
                icone=icone,
                pagina=pagina,
                descricao=descricao,
                ativo=(pagina == pagina_atual),
            )

    st.sidebar.markdown('<div class="ns-sidebar-divider"></div>', unsafe_allow_html=True)

    prox = proxima_pagina(pagina_atual)
    if prox:
        st.sidebar.markdown(
            f"""
            <a class="ns-next-step" href="{_url_pagina(prox)}" target="_self">
                <span class="ns-next-label">Próxima etapa</span>
                <span class="ns-next-title">{prox}</span>
            </a>
            """,
            unsafe_allow_html=True,
        )

    st.sidebar.markdown(
        """
        <div class="ns-sidebar-footer">
            <div>Banco local: <b>CSV</b></div>
            <div>Interface: <b>Streamlit</b></div>
            <div class="ns-version">v1.13</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return pagina_atual


def mostrar_proxima_etapa(pagina_atual: str):
    prox = proxima_pagina(pagina_atual)
    if prox:
        st.caption(f"Após salvar, o sistema seguirá para: {prox}.")
