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
from src.interpretacao_exames import gerar_insights_exames_paciente
from src.catalogo_exames import EXAMES_COMUNS, UNIDADES_COMUNS, cobertura_catalogo
from src.referencias_padrao import carregar_catalogo_padrao
from src.reparo_referencias import reparar_referencias_e_analises
from src.exames_fluxo import exames_disponiveis_para_data, validar_exame_duplicado
from src.web.common import selecionar_paciente, mostrar_dataframe
from src.web.styles import header, card_alerta, card_info
from src.web.navigation import avancar_fluxo


def _card_cobertura_catalogo():
    cobertura = cobertura_catalogo()

    st.subheader("Cobertura do catálogo")
    c1, c2, c3 = st.columns(3)
    c1.metric("Tipos de exames", cobertura["total_exames"])
    c2.metric("Referências cadastráveis", cobertura["total_referencias"])
    c3.metric("Cobertura", f"{cobertura['cobertura_percentual']}%")

    if cobertura["exames_sem_referencia"]:
        st.error("Exames sem referência no catálogo: " + ", ".join(cobertura["exames_sem_referencia"]))
    else:
        st.success("Todos os tipos de exames do catálogo possuem pelo menos uma referência inicial.")


def render():
    header("🧪 Exames e análise", "Cadastro inteligente, referências rastreáveis e análise por painéis.")

    aba_exame, aba_lista, aba_referencia, aba_alias, aba_analise = st.tabs([
        "Cadastrar exame",
        "Exames do paciente",
        "Referências",
        "Aliases",
        "Análise orientada",
    ])

    with aba_exame:
        paciente_id = selecionar_paciente("Paciente", key="exames_paciente_cadastro")

        if paciente_id:
            st.info(
                "A data abaixo controla a lista suspensa. "
                "Exames já cadastrados para este paciente nesta data deixam de aparecer como opção."
            )

            data_exame = st.text_input(
                "Data do exame",
                placeholder="AAAA-MM-DD; vazio = hoje",
                key="exames_data_autoridade",
            )

            opcoes_exames = exames_disponiveis_para_data(paciente_id, data_exame)
            total_disponivel = len([x for x in opcoes_exames if x not in ["", "Outro"]])

            if total_disponivel == 0:
                st.warning(
                    "Todos os exames do catálogo já foram cadastrados para este paciente nesta data. "
                    "Use 'Outro' apenas se for um exame realmente diferente."
                )
            else:
                st.caption(f"Exames disponíveis para esta data: {total_disponivel}")

            with st.form("form_exame", clear_on_submit=True):
                col1, col2 = st.columns([2, 1])
                with col1:
                    exame_escolhido = st.selectbox("Exame", opcoes_exames)
                with col2:
                    nome_manual = st.text_input("Nome manual", placeholder="Use apenas se escolher Outro")

                col3, col4, col5 = st.columns(3)
                with col3:
                    resultado = st.text_input("Resultado numérico")
                with col4:
                    unidade_select = st.selectbox("Unidade", UNIDADES_COMUNS)
                with col5:
                    unidade_manual = st.text_input("Unidade manual", placeholder="Use se escolher Outro")

                observacoes = st.text_area("Observações", placeholder="Opcional")

                submitted = st.form_submit_button("Salvar exame", type="primary")

                if submitted:
                    nome_exame = nome_manual if exame_escolhido == "Outro" else exame_escolhido
                    unidade = unidade_manual if unidade_select == "Outro" else unidade_select

                    duplicado = validar_exame_duplicado(paciente_id, data_exame, nome_exame)

                    if duplicado["duplicado"]:
                        st.error(duplicado["mensagem"])
                    else:
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
                            st.rerun()
                        else:
                            for erro in r["erros"]:
                                st.error(erro)

            if st.button("Concluir sessão de exames e ir para Dashboard", type="primary"):
                avancar_fluxo("Exames")
                st.rerun()

    with aba_lista:
        paciente_id = selecionar_paciente("Paciente", key="exames_paciente_lista")
        if paciente_id:
            mostrar_dataframe(pd.DataFrame(listar_exames_por_paciente(paciente_id)), "Sem exames cadastrados.")

    with aba_referencia:
        card_info(
            "O NutriSoft carrega automaticamente uma base inicial de referências e aliases. "
            "As faixas são rastreáveis e editáveis, pois cada laboratório pode usar métodos e intervalos próprios."
        )

        if st.button("Recarregar/completar referências e aliases padrão", type="primary"):
            resultado = carregar_catalogo_padrao()
            st.success(
                f"Referências criadas: {resultado['referencias']['criadas']} | "
                f"Referências já existentes: {resultado['referencias']['ignoradas']} | "
                f"Aliases criados: {resultado['aliases']['criados']} | "
                f"Aliases já existentes: {resultado['aliases']['ignorados']} | "
                f"Cobertura: {resultado['cobertura']['cobertura_percentual']}%"
            )

        _card_cobertura_catalogo()

        st.subheader("Cadastrar referência manual")
        with st.form("form_referencia", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nome_exame = st.selectbox("Nome padronizado do exame", EXAMES_COMUNS)
                nome_manual = st.text_input("Nome manual", placeholder="Use se escolher Outro")
                sexo = st.selectbox("Sexo", ["Todos", "M", "F", "Outro", "Não informado"])
                idade_min = st.number_input("Idade mínima", min_value=0, max_value=120, value=18)
                idade_max = st.number_input("Idade máxima", min_value=0, max_value=120, value=120)
            with col2:
                valor_min = st.text_input("Valor mínimo")
                valor_max = st.text_input("Valor máximo")
                unidade = st.selectbox("Unidade", UNIDADES_COMUNS)
                unidade_manual = st.text_input("Unidade manual", placeholder="Use se escolher Outro")
                fonte_referencia = st.text_input("Fonte da referência")
                observacoes = st.text_area("Observações")

            submitted = st.form_submit_button("Salvar referência", type="primary")

            if submitted:
                nome_final = nome_manual if nome_exame == "Outro" else nome_exame
                unidade_final = unidade_manual if unidade == "Outro" else unidade

                r = cadastrar_referencia_exame({
                    "nome_exame": nome_final,
                    "sexo": sexo,
                    "idade_min": str(idade_min),
                    "idade_max": str(idade_max),
                    "valor_min": valor_min,
                    "valor_max": valor_max,
                    "unidade": unidade_final,
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
            nome_padronizado = st.selectbox("Nome padronizado", EXAMES_COMUNS)
            nome_manual = st.text_input("Nome manual", placeholder="Use se escolher Outro")
            submitted = st.form_submit_button("Salvar alias", type="primary")

            if submitted:
                nome_final = nome_manual if nome_padronizado == "Outro" else nome_padronizado
                r = cadastrar_alias_exame(alias, nome_final)

                if r["sucesso"]:
                    st.success("Alias salvo.")
                else:
                    for erro in r["erros"]:
                        st.error(erro)

        st.subheader("Aliases cadastrados")
        mostrar_dataframe(pd.DataFrame(listar_alias_exames()), "Sem aliases cadastrados.")

    with aba_analise:
        paciente_id = selecionar_paciente("Paciente", key="exames_paciente_analise")

        if paciente_id:
            if st.button("Executar análise comparativa", type="primary"):
                total = executar_analise_exames()
                st.success(f"Análise executada. Registros analisados: {total}")

            resumo = gerar_resumo_exames_paciente(paciente_id)
            insights = gerar_insights_exames_paciente(paciente_id)

            st.subheader("Resumo executivo")
            st.info(insights.get("resumo_executivo") or resumo.get("resumo"))

            c1, c2, c3, c4 = st.columns(4)
            status = insights.get("status", {})
            c1.metric("Total analisado", insights.get("total", 0))
            c2.metric("Acima", status.get("Acima", 0))
            c3.metric("Abaixo", status.get("Abaixo", 0))
            c4.metric("Sem referência", status.get("Sem referência", 0))

            st.subheader("Prioridades por painel")
            prioridades = insights.get("prioridades", [])
            if prioridades:
                df_prior = pd.DataFrame(prioridades)
                st.dataframe(df_prior, width="stretch", hide_index=True)
                st.bar_chart(df_prior.set_index("painel")[["score"]])
            else:
                st.success("Nenhum painel com prioridade automática no momento.")

            st.subheader("Alertas interpretativos")
            alertas = insights.get("alertas", [])
            if alertas:
                for alerta in alertas:
                    card_alerta(f"<b>{alerta['painel']}</b> — {alerta['mensagem']}")
            else:
                st.success("Sem alertas de exames com base nas referências cadastradas.")

            st.subheader("Recomendações de fluxo")
            for rec in insights.get("recomendacoes", []):
                st.write(f"- {rec}")

            with st.expander("Ver análise completa"):
                mostrar_dataframe(pd.DataFrame(listar_analises_por_paciente(paciente_id)), "Sem análises disponíveis.")

            with st.expander("Ver exames alterados ou pendentes"):
                mostrar_dataframe(pd.DataFrame(listar_exames_alterados_por_paciente(paciente_id)), "Sem exames alterados ou pendentes.")
