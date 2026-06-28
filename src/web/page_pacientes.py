import pandas as pd
import streamlit as st

from src.pacientes import cadastrar_paciente, buscar_pacientes_por_nome
from src.web.common import df_csv, mostrar_dataframe
from src.web.styles import header


def render():
    header("👤 Pacientes", "Cadastro, consulta e organização da base nominal de pacientes.")

    aba_cadastrar, aba_listar, aba_buscar = st.tabs(["Cadastrar", "Listar", "Buscar"])

    with aba_cadastrar:
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
