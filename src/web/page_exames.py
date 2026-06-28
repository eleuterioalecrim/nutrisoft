import pandas as pd
import streamlit as st

from src.analises import executar_analise_exames
from src.exames import (
    cadastrar_exame,
    cadastrar_referencia_exame,
    cadastrar_alias_exame,
    listar_exames_por_paciente,
    listar_referencias_exames,
    listar_alias_exames,
    listar_analises_por_paciente,
    listar_exames_alterados_por_paciente,
    gerar_resumo_exames_paciente,
)
from src.web.common import selecionar_paciente, mostrar_dataframe
from src.web.styles import header


def render():
    header("🧪 Exames", "Cadastro, referências, normalização de nomes e análise comparativa.")

    aba_exame, aba_lista, aba_referencia, aba_alias, aba_analise = st.tabs([
        "Cadastrar exame",
        "Exames do paciente",
        "Referências",
        "Aliases",
        "Análise",
    ])

    with aba_exame:
        paciente_id = selecionar_paciente("Paciente")
        if paciente_id:
            with st.form("form_exame", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    data_exame = st.text_input("Data do exame", placeholder="AAAA-MM-DD; vazio = hoje")
                    nome_exame = st.text_input("Nome do exame")
                    resultado = st.text_input("Resultado numérico")
                with col2:
                    unidade = st.text_input("Unidade", placeholder="mg/dL, ng/mL, g/dL...")
                    observacoes = st.text_area("Observações")

                submitted = st.form_submit_button("Salvar exame", type="primary")

                if submitted:
                    r = cadastrar_exame({
                        "paciente_id": paciente_id,
                        "data_exame": data_exame,
                        "nome_exame": nome_exame,
                        "resultado": resultado,
                        "unidade": unidade,
                        "observacoes": observacoes,
                    })
                    if r["sucesso"]:
                        st.success("Exame salvo e análise comparativa atualizada.")
                    else:
                        for erro in r["erros"]:
                            st.error(erro)

    with aba_lista:
        paciente_id = selecionar_paciente("Paciente")
        if paciente_id:
            mostrar_dataframe(pd.DataFrame(listar_exames_por_paciente(paciente_id)), "Sem exames cadastrados.")

    with aba_referencia:
        st.subheader("Cadastrar referência")
        with st.form("form_referencia", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nome_exame = st.text_input("Nome padronizado do exame")
                sexo = st.selectbox("Sexo", ["Todos", "M", "F", "Outro", "Não informado"])
                idade_min = st.text_input("Idade mínima", value="18")
                idade_max = st.text_input("Idade máxima", value="120")
            with col2:
                valor_min = st.text_input("Valor mínimo")
                valor_max = st.text_input("Valor máximo")
                unidade = st.text_input("Unidade")
                fonte_referencia = st.text_input("Fonte da referência")
                observacoes = st.text_area("Observações")

            submitted = st.form_submit_button("Salvar referência", type="primary")
            if submitted:
                r = cadastrar_referencia_exame({
                    "nome_exame": nome_exame,
                    "sexo": sexo,
                    "idade_min": idade_min,
                    "idade_max": idade_max,
                    "valor_min": valor_min,
                    "valor_max": valor_max,
                    "unidade": unidade,
                    "fonte_referencia": fonte_referencia,
                    "observacoes": observacoes,
                })
                if r["sucesso"]:
                    st.success("Referência salva.")
                else:
                    for erro in r["erros"]:
                        st.error(erro)

        st.subheader("Referências cadastradas")
        mostrar_dataframe(pd.DataFrame(listar_referencias_exames()), "Sem referências cadastradas.")

    with aba_alias:
        with st.form("form_alias", clear_on_submit=True):
            alias = st.text_input("Alias / forma alternativa", placeholder="Ex.: glicemia de jejum")
            nome_padronizado = st.text_input("Nome padronizado", placeholder="Ex.: Glicose")
            submitted = st.form_submit_button("Salvar alias", type="primary")
            if submitted:
                r = cadastrar_alias_exame(alias, nome_padronizado)
                if r["sucesso"]:
                    st.success("Alias salvo.")
                else:
                    for erro in r["erros"]:
                        st.error(erro)

        st.subheader("Aliases cadastrados")
        mostrar_dataframe(pd.DataFrame(listar_alias_exames()), "Sem aliases cadastrados.")

    with aba_analise:
        paciente_id = selecionar_paciente("Paciente")
        if paciente_id:
            if st.button("Executar análise comparativa", type="primary"):
                total = executar_analise_exames()
                st.success(f"Análise executada. Registros analisados: {total}")

            resumo = gerar_resumo_exames_paciente(paciente_id)
            st.info(resumo.get("resumo"))

            st.subheader("Análise completa")
            mostrar_dataframe(pd.DataFrame(listar_analises_por_paciente(paciente_id)), "Sem análises disponíveis.")

            st.subheader("Exames alterados ou pendentes")
            mostrar_dataframe(pd.DataFrame(listar_exames_alterados_por_paciente(paciente_id)), "Sem exames alterados ou pendentes.")
