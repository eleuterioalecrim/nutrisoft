import pandas as pd
import streamlit as st

from src.exclusao_paciente import contar_dados_paciente, excluir_dados_paciente
from src.web.common import selecionar_paciente, mostrar_dataframe
from src.web.styles import header, card_alerta, card_info


def render():
    header("🗑️ Exclusão de paciente", "Remoção segura dos dados do paciente com backup automático.")

    card_alerta(
        "<b>Atenção:</b> esta ação remove os registros do paciente das bases locais. "
        "Antes da exclusão, o sistema gera um backup em <code>backups/pacientes_excluidos/</code>."
    )

    paciente_id = selecionar_paciente("Paciente para exclusão", key="exclusao_paciente_id")

    if not paciente_id:
        return

    info = contar_dados_paciente(paciente_id)
    paciente = info.get("paciente") or {}

    st.subheader("Paciente selecionado")
    st.write(f"**ID:** {paciente.get('paciente_id', '')}")
    st.write(f"**Nome:** {paciente.get('nome', '')}")

    st.subheader("Dados encontrados")
    contagens = info.get("contagens", {})
    df_contagens = pd.DataFrame([
        {"Base": base, "Registros": qtd}
        for base, qtd in contagens.items()
    ])
    mostrar_dataframe(df_contagens, "Nenhum registro encontrado.")

    c1, c2 = st.columns(2)
    c1.metric("Total de registros", info.get("total_registros", 0))
    c2.metric("Arquivos gerados", info.get("total_arquivos", 0))

    arquivos = info.get("arquivos_gerados", [])
    if arquivos:
        with st.expander("Arquivos gerados que serão removidos"):
            for arquivo in arquivos:
                st.write(f"- `{arquivo}`")

    st.divider()

    st.subheader("Confirmação de segurança")
    card_info(
        "Para confirmar, digite exatamente o texto solicitado abaixo. "
        "Isso evita exclusão acidental durante o atendimento."
    )

    texto_esperado = f"EXCLUIR {paciente_id}"
    st.code(texto_esperado)

    col1, col2 = st.columns(2)
    with col1:
        criar_backup = st.checkbox("Criar backup antes de excluir", value=True)
    with col2:
        excluir_arquivos = st.checkbox("Excluir PDFs/gráficos gerados do paciente", value=True)

    confirmacao = st.text_input("Digite a confirmação")

    if st.button("Excluir todos os dados deste paciente", type="primary"):
        resultado = excluir_dados_paciente(
            paciente_id=paciente_id,
            confirmar_texto=confirmacao,
            excluir_arquivos_gerados=excluir_arquivos,
            criar_backup=criar_backup,
        )

        if resultado["sucesso"]:
            st.success("Paciente e dados vinculados foram excluídos com sucesso.")

            if resultado.get("backup"):
                st.info(f"Backup gerado: {resultado['backup']['backup_zip']}")

            st.subheader("Registros removidos")
            df_removidos = pd.DataFrame([
                {"Base": base, "Registros removidos": qtd}
                for base, qtd in resultado["removidos"].items()
            ])
            mostrar_dataframe(df_removidos, "Nenhum registro removido.")

            if resultado["arquivos_removidos"]:
                with st.expander("Arquivos removidos"):
                    for arquivo in resultado["arquivos_removidos"]:
                        st.write(f"- `{arquivo}`")
        else:
            st.error(resultado["erro"])
