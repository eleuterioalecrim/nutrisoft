import pandas as pd
import streamlit as st

from src.pacientes import cadastrar_paciente, buscar_pacientes_por_nome
from src.web.common import df_csv, mostrar_dataframe, selecionar_paciente
from src.web.styles import header, completion_box, card_alerta, card_info
from src.completude import calcular_completude_paciente, listar_completude_pacientes
from src.web.navigation import avancar_fluxo, mostrar_proxima_etapa
from src.exclusao_paciente import contar_dados_paciente, excluir_dados_paciente


def _abrir_modal_exclusao(paciente_id: str):
    st.session_state["paciente_excluir_id"] = paciente_id
    st.session_state["modal_exclusao_aberto"] = True


def _fechar_modal_exclusao():
    st.session_state["paciente_excluir_id"] = None
    st.session_state["modal_exclusao_aberto"] = False


def _render_conteudo_confirmacao_exclusao(paciente_id: str):
    info = contar_dados_paciente(paciente_id)
    paciente = info.get("paciente") or {}

    card_alerta(
        "<b>Atenção:</b> esta ação irá excluir TUDO relacionado a este paciente: "
        "cadastro, anamnese, recordatório, antropometria, exames, análises, evolução e arquivos gerados. "
        "Um backup será criado antes da exclusão."
    )

    st.write(f"**Paciente:** {paciente.get('nome', '')}")
    st.write(f"**ID:** {paciente.get('paciente_id', '')}")

    st.subheader("Dados que serão removidos")
    contagens = info.get("contagens", {})
    df_contagens = pd.DataFrame([
        {"Base": base, "Registros": qtd}
        for base, qtd in contagens.items()
    ])
    mostrar_dataframe(df_contagens, "Nenhum registro vinculado encontrado.")

    c1, c2 = st.columns(2)
    c1.metric("Total de registros", info.get("total_registros", 0))
    c2.metric("Arquivos gerados", info.get("total_arquivos", 0))

    if info.get("arquivos_gerados"):
        with st.expander("Arquivos gerados que serão removidos"):
            for arquivo in info["arquivos_gerados"]:
                st.write(f"- `{arquivo}`")

    st.divider()

    texto_esperado = f"EXCLUIR {paciente_id}"
    st.write("Para confirmar, digite exatamente:")
    st.code(texto_esperado)

    confirmacao = st.text_input(
        "Confirmação",
        key=f"confirmacao_excluir_{paciente_id}",
        placeholder=texto_esperado,
    )

    col1, col2 = st.columns(2)
    with col1:
        cancelar = st.button("Cancelar", use_container_width=True, key=f"cancelar_excluir_{paciente_id}")
    with col2:
        confirmar = st.button(
            "Confirmar exclusão definitiva",
            type="primary",
            use_container_width=True,
            key=f"confirmar_excluir_{paciente_id}",
        )

    if cancelar:
        _fechar_modal_exclusao()
        st.rerun()

    if confirmar:
        resultado = excluir_dados_paciente(
            paciente_id=paciente_id,
            confirmar_texto=confirmacao,
            excluir_arquivos_gerados=True,
            criar_backup=True,
        )

        if resultado["sucesso"]:
            st.session_state["mensagem_exclusao_sucesso"] = {
                "paciente_id": paciente_id,
                "backup": resultado.get("backup", {}).get("backup_zip") if resultado.get("backup") else "",
                "removidos": resultado.get("removidos", {}),
            }
            _fechar_modal_exclusao()
            st.rerun()
        else:
            st.error(resultado["erro"])


if hasattr(st, "dialog"):
    @st.dialog("Confirmar exclusão do paciente")
    def _modal_confirmacao_exclusao(paciente_id: str):
        _render_conteudo_confirmacao_exclusao(paciente_id)
else:
    _modal_confirmacao_exclusao = None


def _render_modal_ou_fallback():
    if not st.session_state.get("modal_exclusao_aberto"):
        return

    paciente_id = st.session_state.get("paciente_excluir_id")
    if not paciente_id:
        return

    if _modal_confirmacao_exclusao:
        _modal_confirmacao_exclusao(paciente_id)
    else:
        st.warning("Confirmação de exclusão")
        _render_conteudo_confirmacao_exclusao(paciente_id)


def _render_alerta_sucesso_exclusao():
    msg = st.session_state.get("mensagem_exclusao_sucesso")
    if not msg:
        return

    st.success(f"Paciente {msg['paciente_id']} e todos os dados vinculados foram excluídos com sucesso.")

    if msg.get("backup"):
        st.info(f"Backup gerado: {msg['backup']}")

    with st.expander("Registros removidos"):
        df = pd.DataFrame([
            {"Base": base, "Registros removidos": qtd}
            for base, qtd in msg.get("removidos", {}).items()
        ])
        mostrar_dataframe(df, "Sem detalhes.")

    if st.button("OK", key="limpar_msg_exclusao"):
        del st.session_state["mensagem_exclusao_sucesso"]
        st.rerun()


def _render_acoes_paciente():
    st.subheader("Ações do paciente")

    paciente_id = selecionar_paciente("Selecione o paciente", key="paciente_acoes_id")
    if not paciente_id:
        return

    info = contar_dados_paciente(paciente_id)
    paciente = info.get("paciente") or {}

    st.write(f"**Paciente:** {paciente.get('nome', '')}")
    st.write(f"**ID:** {paciente.get('paciente_id', '')}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Registros vinculados", info.get("total_registros", 0))
    c2.metric("Arquivos gerados", info.get("total_arquivos", 0))
    c3.metric("Status", "Ativo")

    card_info(
        "Use a exclusão apenas quando realmente quiser remover o paciente do sistema. "
        "Antes de apagar, o NutriSoft cria um backup local."
    )

    if st.button(
        "🗑️ Excluir paciente e todos os dados vinculados",
        type="primary",
        use_container_width=True,
        key=f"abrir_excluir_{paciente_id}",
    ):
        _abrir_modal_exclusao(paciente_id)
        st.rerun()


def render():
    header("👤 Pacientes", "Cadastro, consulta, completude e ações do paciente.")

    _render_modal_ou_fallback()
    _render_alerta_sucesso_exclusao()

    aba_cadastrar, aba_listar, aba_buscar, aba_completude, aba_acoes = st.tabs([
        "Cadastrar",
        "Listar",
        "Buscar",
        "Completude",
        "Ações",
    ])

    with aba_cadastrar:
        mostrar_proxima_etapa("Pacientes")

        with st.form("form_paciente", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                nome = st.text_input("Nome *")
                data_nascimento = st.text_input("Data de nascimento", placeholder="AAAA-MM-DD ou DD/MM/AAAA")
                sexo = st.selectbox("Sexo", ["Não informado", "M", "F", "Outro"])
                telefone = st.text_input("Telefone")

            with col2:
                email = st.text_input("E-mail")
                profissao = st.text_input("Profissão/Estudo")
                horario_trabalho = st.text_input("Horário de trabalho/estudo")
                observacoes = st.text_area("Observações")

            submitted = st.form_submit_button("Salvar paciente", type="primary")

            if submitted:
                resultado = cadastrar_paciente({
                    "nome": nome,
                    "data_nascimento": data_nascimento,
                    "sexo": sexo,
                    "telefone": telefone,
                    "email": email,
                    "profissao": profissao,
                    "horario_trabalho": horario_trabalho,
                    "observacoes": observacoes,
                })

                if resultado["sucesso"]:
                    st.success(f"Paciente cadastrado com sucesso. ID: {resultado['paciente']['paciente_id']}")
                    avancar_fluxo("Pacientes")
                    st.rerun()
                else:
                    for erro in resultado["erros"]:
                        st.error(erro)

    with aba_listar:
        mostrar_dataframe(df_csv("pacientes"), "Nenhum paciente cadastrado.")

    with aba_buscar:
        termo = st.text_input("Digite parte do nome")
        if termo:
            encontrados = pd.DataFrame(buscar_pacientes_por_nome(termo))
            mostrar_dataframe(encontrados, "Nenhum paciente encontrado.")

    with aba_completude:
        st.subheader("Completude por paciente")
        df = pd.DataFrame(listar_completude_pacientes())
        mostrar_dataframe(df, "Sem pacientes para avaliar.")
        if not df.empty:
            st.bar_chart(df.set_index("nome")[["percentual"]], height=340)

        st.divider()
        paciente_id = selecionar_paciente("Ver detalhe do paciente", key="pacientes_completude_detalhe")
        if paciente_id:
            c = calcular_completude_paciente(paciente_id)
            completion_box(f"{c['nivel']} — {c['percentual']:.1f}%", c["descricao"], c["percentual"])
            if c["pendencias"]:
                st.write("Pendências:")
                for p in c["pendencias"]:
                    st.warning(p)
            else:
                st.success("Informações suficientes para acompanhamento.")

    with aba_acoes:
        _render_acoes_paciente()
