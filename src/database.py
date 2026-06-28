import csv
from pathlib import Path
from .config import DATA_DIR, REPORTS_DIR, CHARTS_DIR, CSV_FILES


HEADERS = {
    "pacientes": [
        "paciente_id", "data_cadastro", "nome", "data_nascimento", "idade", "sexo",
        "telefone", "email", "profissao", "horario_trabalho", "observacoes"
    ],
    "anamnese": [
        "anamnese_id", "paciente_id", "data_anamnese", "queixa_principal",
        "historia_doenca_atual", "sintomas", "historia_patologica_pregressa",
        "historia_familiar", "numero_filhos_idades", "amamentou",
        "atividade_fisica", "horario_atividade_fisica", "consumo_alcool",
        "tabagismo", "qualidade_sono", "hora_acordar", "hora_dormir",
        "comportamento_peso", "disposicao_fisica", "funcionamento_intestinal",
        "funcionamento_urinario", "internacoes_cirurgias",
        "medicamentos_suplementos", "intolerancia_alergia_alimentar",
        "denticao", "mastigacao", "quem_cozinha", "apetite",
        "horario_mais_fome", "ingestao_agua_dia",
        "tratamento_nutricional_anterior", "qual_tratamento",
        "alimentos_preferidos", "habito_beliscar", "alimentos_que_nao_gosta",
        "habitos_fim_de_semana"
    ],
    "recordatorio_habitual": [
        "recordatorio_id", "paciente_id", "data_registro", "desjejum",
        "lanche_manha", "almoco", "lanche_tarde", "jantar", "ceia", "observacoes"
    ],
    "antropometria": [
        "antropometria_id", "paciente_id", "data_avaliacao", "peso", "altura",
        "imc", "classificacao_imc", "circunferencia_cintura", "risco_cintura", "observacoes"
    ],
    "exames": [
        "exame_id", "paciente_id", "data_exame", "nome_exame", "resultado",
        "unidade", "observacoes"
    ],
    "referencias_exames": [
        "referencia_id", "nome_exame", "sexo", "idade_min", "idade_max",
        "valor_min", "valor_max", "unidade", "fonte_referencia", "observacoes"
    ],
    "alias_exames": ["alias", "nome_padronizado"],
    "analise_exames": [
        "analise_id", "paciente_id", "data_exame", "nome_exame_original",
        "nome_exame_padronizado", "resultado", "unidade", "valor_min",
        "valor_max", "status", "insight", "fonte_referencia"
    ],
    "evolucao_conduta": [
        "evolucao_id", "paciente_id", "data_registro", "evolucao", "conduta",
        "objetivo_proximo_retorno", "profissional_responsavel"
    ],
}


def criar_csv_se_nao_existir(caminho: Path, cabecalho: list[str]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    if not caminho.exists():
        with caminho.open("w", newline="", encoding="utf-8") as arquivo:
            writer = csv.writer(arquivo)
            writer.writerow(cabecalho)


def garantir_cabecalho_atualizado(nome_base: str) -> None:
    caminho = CSV_FILES[nome_base]
    cabecalho = HEADERS[nome_base]

    criar_csv_se_nao_existir(caminho, cabecalho)

    with caminho.open("r", newline="", encoding="utf-8") as arquivo:
        reader = csv.reader(arquivo)
        linhas = list(reader)

    if not linhas:
        with caminho.open("w", newline="", encoding="utf-8") as arquivo:
            csv.writer(arquivo).writerow(cabecalho)
        return

    cabecalho_atual = linhas[0]

    if cabecalho_atual != cabecalho:
        dados_antigos = []
        for linha in linhas[1:]:
            registro = {campo: "" for campo in cabecalho}
            for idx, campo in enumerate(cabecalho_atual):
                if campo in registro and idx < len(linha):
                    registro[campo] = linha[idx]
            dados_antigos.append(registro)

        with caminho.open("w", newline="", encoding="utf-8") as arquivo:
            writer = csv.DictWriter(arquivo, fieldnames=cabecalho)
            writer.writeheader()
            writer.writerows(dados_antigos)


def inicializar_banco_csv() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    for nome in CSV_FILES:
        garantir_cabecalho_atualizado(nome)


def ler_csv(nome_base: str) -> list[dict]:
    inicializar_banco_csv()
    caminho = CSV_FILES[nome_base]

    with caminho.open("r", newline="", encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


def salvar_csv(nome_base: str, linhas: list[dict]) -> None:
    inicializar_banco_csv()
    caminho = CSV_FILES[nome_base]
    cabecalho = HEADERS[nome_base]

    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=cabecalho)
        writer.writeheader()
        for linha in linhas:
            writer.writerow({campo: linha.get(campo, "") for campo in cabecalho})


def adicionar_linha(nome_base: str, linha: dict) -> None:
    inicializar_banco_csv()
    caminho = CSV_FILES[nome_base]
    cabecalho = HEADERS[nome_base]

    with caminho.open("a", newline="", encoding="utf-8") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=cabecalho)
        writer.writerow({campo: linha.get(campo, "") for campo in cabecalho})


def obter_proximo_id(nome_base: str, campo_id: str) -> str:
    linhas = ler_csv(nome_base)
    maior_id = 0

    for linha in linhas:
        valor = str(linha.get(campo_id, "")).strip()
        if valor.isdigit():
            maior_id = max(maior_id, int(valor))

    return str(maior_id + 1).zfill(4)


def atualizar_linha(nome_base: str, campo_id: str, valor_id: str, novos_dados: dict) -> bool:
    linhas = ler_csv(nome_base)
    atualizado = False

    for linha in linhas:
        if str(linha.get(campo_id, "")).strip() == str(valor_id).strip():
            linha.update(novos_dados)
            atualizado = True
            break

    if atualizado:
        salvar_csv(nome_base, linhas)

    return atualizado


def remover_linha(nome_base: str, campo_id: str, valor_id: str) -> bool:
    linhas = ler_csv(nome_base)
    total_antes = len(linhas)

    linhas = [
        linha for linha in linhas
        if str(linha.get(campo_id, "")).strip() != str(valor_id).strip()
    ]

    if len(linhas) < total_antes:
        salvar_csv(nome_base, linhas)
        return True

    return False
