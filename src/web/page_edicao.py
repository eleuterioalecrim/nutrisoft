import pandas as pd
import streamlit as st

from src.edicoes import (
    BASES_EDITAVEIS,
    campo_id_base,
    listar_registros,
    atualizar_registro_com_historico,
    historico_por_base_registro,
    campos_editaveis,
)
from src.exportacao import enriquecer_com_nome_paciente
from src.web.common import mostrar_dataframe, csv_multiselect
from src.web.styles import header, card_info
from src.opcoes_anamnese import (
    SEXO,
    SIM_NAO,
    SIM_NAO_EVENTUAL,
    SINTOMAS,
    HISTORIA_PATOLOGICA,
    HISTORIA_FAMILIAR_OPCOES,
    ATIVIDADE_FISICA_TIPO,
    FREQUENCIA_SEMANAL,
    PERIODO_DIA,
    CONSUMO_ALCOOL,
    TABAGISMO,
    QUALIDADE_SONO,
    COMPORTAMENTO_PESO,
    DISPOSICAO,
    FUNCIONAMENTO_INTESTINAL,
    FUNCIONAMENTO_URINARIO,
    DENTICAO,
    MASTIGACAO,
    QUEM_COZINHA,
    APETITE,
    INGESTAO_AGUA,
    GRUPOS_ALIMENTARES,
    HABITOS_FIM_SEMANA,
)
from src.catalogo_exames import EXAMES_COMUNS, UNIDADES_COMUNS


CAMPOS_LONGOS = {
    "observacoes", "historia_doenca_atual", "internacoes_cirurgias",
    "medicamentos_suplementos", "desjejum", "lanche_manha", "almoco",
    "lanche_tarde", "jantar", "ceia", "evolucao", "conduta",
    "objetivo_proximo_retorno",
}

MULTI_OPCOES = {
    "sintomas": SINTOMAS,
    "historia_patologica_pregressa": HISTORIA_PATOLOGICA,
    "historia_familiar": HISTORIA_FAMILIAR_OPCOES,
    "alimentos_preferidos": GRUPOS_ALIMENTARES,
    "habitos_fim_de_semana": HABITOS_FIM_SEMANA,
}

SELECT_OPCOES = {
    "sexo": SEXO,
    "amamentou": SIM_NAO,
    "tratamento_nutricional_anterior": SIM_NAO,
    "habito_beliscar": SIM_NAO_EVENTUAL,
    "atividade_fisica": ATIVIDADE_FISICA_TIPO,
    "horario_atividade_fisica": PERIODO_DIA,
    "consumo_alcool": CONSUMO_ALCOOL,
    "tabagismo": TABAGISMO,
    "qualidade_sono": QUALIDADE_SONO,
    "comportamento_peso": COMPORTAMENTO_PESO,
    "disposicao_fisica": DISPOSICAO,
    "funcionamento_intestinal": FUNCIONAMENTO_INTESTINAL,
    "funcionamento_urinario": FUNCIONAMENTO_URINARIO,
    "denticao": DENTICAO,
    "mastigacao": MASTIGACAO,
    "quem_cozinha": QUEM_COZINHA,
    "apetite": APETITE,
    "horario_mais_fome": PERIODO_DIA,
    "ingestao_agua_dia": INGESTAO_AGUA,
    "nome_exame": EXAMES_COMUNS,
    "nome_padronizado": EXAMES_COMUNS,
    "unidade": UNIDADES_COMUNS,
}

NUMERICOS = {
    "idade", "peso", "altura", "imc", "circunferencia_cintura",
    "idade_min", "idade_max", "valor_min", "valor_max", "resultado"
}


def _split_multivalor(valor: str) -> list[str]:
    if not valor:
        return []
    partes = []
    for pedaco in str(valor).replace(",", ";").split(";"):
        pedaco = pedaco.strip()
        if pedaco:
            partes.append(pedaco)
    return partes


def _label_registro(registro: dict, nome_base: str) -> str:
    campo_id = campo_id_base(nome_base)
    partes = [f"{campo_id}: {registro.get(campo_id, '')}"]
    if registro.get("paciente_id"):
        partes.append(f"Paciente ID: {registro.get('paciente_id')}")
    if registro.get("nome"):
        partes.append(registro.get("nome"))
    if registro.get("data_exame"):
        partes.append(registro.get("data_exame"))
    if registro.get("nome_exame"):
        partes.append(registro.get("nome_exame"))
    if registro.get("data_anamnese"):
        partes.append(registro.get("data_anamnese"))
    if registro.get("data_avaliacao"):
        partes.append(registro.get("data_avaliacao"))
    return " | ".join([str(p) for p in partes if p])


def _select_com_valor(campo: str, valor: str, opcoes: list[str], key: str):
    valor = str(valor or "")
    opcoes = list(opcoes)

    if valor and valor not in opcoes:
        opcoes = opcoes[:-1] + [valor] + (["Outro"] if "Outro" in opcoes else [])

    index = opcoes.index(valor) if valor in opcoes else 0
    escolha = st.selectbox(campo, opcoes, index=index, key=key)

    if escolha == "Outro":
        return st.text_input(f"{campo} - informar outro", value="" if valor == "Outro" else valor, key=f"{key}_outro")

    return escolha


def _multiselect_com_valor(campo: str, valor: str, opcoes: list[str], key: str):
    atuais = _split_multivalor(valor)
    opcoes = list(opcoes)

    extras = [v for v in atuais if v not in opcoes]
    opcoes_final = opcoes + extras

    selecionados = st.multiselect(campo, opcoes_final, default=atuais, key=key)
    outro = st.text_input(f"{campo} - complemento opcional", value="", key=f"{key}_outro")
    if outro.strip():
        selecionados.append(outro.strip())
    return csv_multiselect(selecionados)


def _input_campo(nome_base: str, campo: str, valor: str, key_prefix: str):
    key = f"{key_prefix}_{nome_base}_{campo}"

    if campo in MULTI_OPCOES:
        return _multiselect_com_valor(campo, valor, MULTI_OPCOES[campo], key)

    if campo in SELECT_OPCOES:
        return _select_com_valor(campo, valor, SELECT_OPCOES[campo], key)

    if campo == "sexo":
        return _select_com_valor(campo, valor, SEXO, key)

    if campo in NUMERICOS:
        return st.text_input(campo, value=str(valor or ""), key=key)

    if campo.startswith("data_"):
        return st.text_input(campo, value=str(valor or ""), placeholder="AAAA-MM-DD", key=key)

    if campo in CAMPOS_LONGOS or len(str(valor or "")) > 80:
        return st.text_area(campo, value=str(valor or ""), height=90, key=key)

    return st.text_input(campo, value=str(valor or ""), key=key)


def render():
    header("✏️ Edição guiada com histórico", "Edição respeitando combos, listas e menus usados no cadastro.")

    card_info(
        "Esta tela altera o registro atual, mas grava cada mudança em `historico_edicoes.csv`. "
        "Campos que foram cadastrados por combo/lista continuam como combo/lista na edição."
    )

    nome_base = st.selectbox("Base para edição", list(BASES_EDITAVEIS.keys()), key="edicao_base")
    registros = listar_registros(nome_base)

    if not registros:
        st.info("Não há registros nesta base.")
        return

    opcoes = {_label_registro(r, nome_base): r for r in registros}
    escolha = st.selectbox("Registro", list(opcoes.keys()), key=f"edicao_registro_{nome_base}")
    registro = opcoes[escolha]
    campo_id = campo_id_base(nome_base)
    registro_id = registro.get(campo_id, "")

    st.subheader("Registro atual")
    df_atual = enriquecer_com_nome_paciente(nome_base)
    if not df_atual.empty and campo_id in df_atual.columns:
        mostrar_dataframe(df_atual[df_atual[campo_id].astype(str) == str(registro_id)], "Registro não encontrado na visualização.")
    else:
        st.json(registro)

    st.subheader("Editar informações")
    with st.form(f"form_edicao_registro_{nome_base}_{registro_id}"):
        usuario = st.text_input("Responsável pela alteração", value="NutriSoft", key=f"usuario_{nome_base}_{registro_id}")
        motivo = st.text_input("Motivo da alteração", placeholder="Ex.: correção de digitação, atualização em retorno...", key=f"motivo_{nome_base}_{registro_id}")

        novos = {}
        for campo in campos_editaveis(nome_base):
            valor = registro.get(campo, "")
            novos[campo] = _input_campo(nome_base, campo, valor, key_prefix=f"edit_{registro_id}")

        submitted = st.form_submit_button("Salvar alterações", type="primary")

        if submitted:
            resultado = atualizar_registro_com_historico(nome_base, registro_id, novos, usuario=usuario, motivo=motivo)
            if resultado["sucesso"]:
                if resultado["alteracoes"] > 0:
                    st.success(f"Registro atualizado. Alterações gravadas no histórico: {resultado['alteracoes']}.")
                else:
                    st.info("Nenhuma alteração detectada.")
            else:
                st.error(resultado["erro"])

    st.subheader("Histórico deste registro")
    historico = pd.DataFrame(historico_por_base_registro(nome_base, registro_id))
    mostrar_dataframe(historico, "Ainda não há histórico de edição para este registro.")
