from collections import Counter

from .database import ler_csv
from .pacientes import buscar_paciente_por_id, listar_pacientes
from .antropometria import obter_antropometria_mais_recente, calcular_evolucao_antropometrica
from .anamnese import gerar_resumo_nutricional_paciente
from .exames import gerar_resumo_exames_paciente, listar_exames_alterados_por_paciente
from .analises import executar_analise_exames


def gerar_dashboard_paciente(paciente_id: str) -> dict:
    paciente = buscar_paciente_por_id(paciente_id)

    if not paciente:
        return {
            "sucesso": False,
            "erro": f"Paciente ID {paciente_id} não encontrado.",
            "dashboard": None,
        }

    executar_analise_exames()

    antropometria_atual = obter_antropometria_mais_recente(paciente_id)
    evolucao_antropometrica = calcular_evolucao_antropometrica(paciente_id)
    resumo_nutricional = gerar_resumo_nutricional_paciente(paciente_id)
    resumo_exames = gerar_resumo_exames_paciente(paciente_id)
    exames_alterados = listar_exames_alterados_por_paciente(paciente_id)

    alertas = []

    if antropometria_atual:
        if antropometria_atual.get("risco_cintura") in ["Atenção", "Risco aumentado"]:
            alertas.append(f"Circunferência da cintura: {antropometria_atual.get('risco_cintura')}.")
        if antropometria_atual.get("classificacao_imc") not in ["Eutrofia", "", "IMC inválido"]:
            alertas.append(f"IMC classificado como {antropometria_atual.get('classificacao_imc')}.")

    for item in exames_alterados[:5]:
        if item.get("status") in ["Acima", "Abaixo"]:
            alertas.append(item.get("insight", ""))

    if resumo_nutricional.get("possui_anamnese"):
        for ponto in resumo_nutricional.get("pontos_atencao", [])[:3]:
            alertas.append(ponto)

    dashboard = {
        "paciente": paciente,
        "antropometria_atual": antropometria_atual,
        "evolucao_antropometrica": evolucao_antropometrica,
        "resumo_nutricional": resumo_nutricional,
        "resumo_exames": resumo_exames,
        "exames_alterados": exames_alterados,
        "alertas": [a for a in alertas if a],
    }

    return {
        "sucesso": True,
        "erro": "",
        "dashboard": dashboard,
    }


def gerar_indicadores_gerais() -> dict:
    executar_analise_exames()

    pacientes = listar_pacientes()
    anamneses = ler_csv("anamnese")
    antropometrias = ler_csv("antropometria")
    exames = ler_csv("exames")
    analises = ler_csv("analise_exames")

    pacientes_com_exames_alterados = set()
    status_counter = Counter()

    for analise in analises:
        status = analise.get("status", "Sem status")
        status_counter[status] += 1
        if status in ["Acima", "Abaixo"]:
            pacientes_com_exames_alterados.add(analise.get("paciente_id", ""))

    exames_alterados_counter = Counter(
        analise.get("nome_exame_padronizado", "Exame")
        for analise in analises
        if analise.get("status") in ["Acima", "Abaixo"]
    )

    return {
        "total_pacientes": len(pacientes),
        "total_anamneses": len(anamneses),
        "total_avaliacoes_antropometricas": len(antropometrias),
        "total_exames": len(exames),
        "total_analises": len(analises),
        "pacientes_com_exames_alterados": len([p for p in pacientes_com_exames_alterados if p]),
        "distribuicao_status_exames": dict(status_counter),
        "exames_mais_alterados": dict(exames_alterados_counter.most_common(10)),
    }


def formatar_dashboard_paciente_texto(paciente_id: str) -> str:
    resultado = gerar_dashboard_paciente(paciente_id)

    if not resultado["sucesso"]:
        return resultado["erro"]

    d = resultado["dashboard"]
    paciente = d["paciente"]
    linhas = []

    linhas.append("=" * 80)
    linhas.append(f"Dashboard do Paciente: {paciente.get('nome', '')} | ID {paciente.get('paciente_id', '')}")
    linhas.append("=" * 80)
    linhas.append(f"Idade: {paciente.get('idade', '')} | Sexo: {paciente.get('sexo', '')} | Telefone: {paciente.get('telefone', '')}")

    linhas.append("\n[Antropometria atual]")
    antrop = d.get("antropometria_atual")
    if antrop:
        linhas.append(f"Data: {antrop.get('data_avaliacao', '')}")
        linhas.append(f"Peso: {antrop.get('peso', '')} kg")
        linhas.append(f"IMC: {antrop.get('imc', '')} | {antrop.get('classificacao_imc', '')}")
        linhas.append(f"Cintura: {antrop.get('circunferencia_cintura', '')} cm | {antrop.get('risco_cintura', '')}")
    else:
        linhas.append("Sem avaliação antropométrica cadastrada.")

    linhas.append("\n[Evolução antropométrica]")
    evo = d.get("evolucao_antropometrica", {})
    if evo.get("possui_dados"):
        linhas.append(f"Período: {evo.get('primeira_data', '')} a {evo.get('ultima_data', '')}")
        linhas.append(f"Variação de peso: {evo.get('delta_peso', '')} kg")
        linhas.append(f"Variação de IMC: {evo.get('delta_imc', '')}")
        linhas.append(f"Variação de cintura: {evo.get('delta_cintura', '')} cm")
    else:
        linhas.append(evo.get("resumo", "Sem dados."))

    linhas.append("\n[Resumo de exames]")
    resumo_exames = d.get("resumo_exames", {})
    linhas.append(resumo_exames.get("resumo", "Sem exames cadastrados."))

    linhas.append("\n[Alertas]")
    alertas = d.get("alertas", [])
    if alertas:
        for alerta in alertas:
            linhas.append(f"- {alerta}")
    else:
        linhas.append("- Nenhum alerta automático no momento.")

    return "\n".join(linhas)


def formatar_indicadores_gerais_texto() -> str:
    indicadores = gerar_indicadores_gerais()
    linhas = []

    linhas.append("=" * 80)
    linhas.append("Dashboard Geral - NutriSoft")
    linhas.append("=" * 80)
    linhas.append(f"Pacientes cadastrados: {indicadores['total_pacientes']}")
    linhas.append(f"Anamneses cadastradas: {indicadores['total_anamneses']}")
    linhas.append(f"Avaliações antropométricas: {indicadores['total_avaliacoes_antropometricas']}")
    linhas.append(f"Exames cadastrados: {indicadores['total_exames']}")
    linhas.append(f"Análises geradas: {indicadores['total_analises']}")
    linhas.append(f"Pacientes com exames alterados: {indicadores['pacientes_com_exames_alterados']}")

    linhas.append("\n[Distribuição dos exames por status]")
    distribuicao = indicadores.get("distribuicao_status_exames", {})
    if distribuicao:
        for status, qtd in distribuicao.items():
            linhas.append(f"- {status}: {qtd}")
    else:
        linhas.append("- Sem análises disponíveis.")

    linhas.append("\n[Exames mais alterados]")
    alterados = indicadores.get("exames_mais_alterados", {})
    if alterados:
        for exame, qtd in alterados.items():
            linhas.append(f"- {exame}: {qtd}")
    else:
        linhas.append("- Nenhum exame alterado identificado.")

    return "\n".join(linhas)
