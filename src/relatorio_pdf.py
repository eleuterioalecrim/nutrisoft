from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from src.config import PDF_DIR
from src.pacientes import buscar_paciente_por_id
from src.anamnese import obter_anamnese_mais_recente, obter_recordatorio_mais_recente
from src.antropometria import obter_antropometria_mais_recente, calcular_evolucao_antropometrica
from src.exames import listar_analises_por_paciente
from src.interpretacao_exames import gerar_insights_exames_paciente
from src.utils import data_hora_atual


def _safe_filename(texto: str) -> str:
    texto = re.sub(r"[^a-zA-Z0-9_-]+", "_", texto or "paciente")
    return texto.strip("_")[:80]


def _p(texto):
    return str(texto or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def gerar_pdf_analise_paciente(paciente_id: str) -> dict:
    paciente = buscar_paciente_por_id(paciente_id)
    if not paciente:
        return {"sucesso": False, "erro": "Paciente não encontrado.", "arquivo": ""}

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    nome_arquivo = f"analise_{paciente_id}_{_safe_filename(paciente.get('nome', 'paciente'))}.pdf"
    caminho = PDF_DIR / nome_arquivo

    doc = SimpleDocTemplate(
        str(caminho),
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TituloNutri", parent=styles["Title"], fontSize=18, leading=22, spaceAfter=14))
    styles.add(ParagraphStyle(name="SecaoNutri", parent=styles["Heading2"], fontSize=12, leading=15, spaceBefore=10, spaceAfter=6))
    styles.add(ParagraphStyle(name="TextoNutri", parent=styles["BodyText"], fontSize=9, leading=12))

    story = []

    story.append(Paragraph("NutriSoft - Relatório de Análise do Paciente", styles["TituloNutri"]))
    story.append(Paragraph(f"Gerado em: {_p(data_hora_atual())}", styles["TextoNutri"]))
    story.append(Spacer(1, 8))

    dados_paciente = [
        ["Paciente", paciente.get("nome", "")],
        ["ID", paciente.get("paciente_id", "")],
        ["Idade", paciente.get("idade", "")],
        ["Sexo", paciente.get("sexo", "")],
        ["Telefone", paciente.get("telefone", "")],
        ["E-mail", paciente.get("email", "")],
    ]
    tabela = Table(dados_paciente, colWidths=[4 * cm, 12 * cm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8F5E9")),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(tabela)

    anamnese = obter_anamnese_mais_recente(paciente_id)
    recordatorio = obter_recordatorio_mais_recente(paciente_id)
    antrop = obter_antropometria_mais_recente(paciente_id)
    evolucao = calcular_evolucao_antropometrica(paciente_id)
    insights = gerar_insights_exames_paciente(paciente_id)
    analises = listar_analises_por_paciente(paciente_id)

    story.append(Paragraph("Resumo executivo dos exames", styles["SecaoNutri"]))
    story.append(Paragraph(_p(insights.get("resumo_executivo", "")), styles["TextoNutri"]))

    story.append(Paragraph("Recomendações de fluxo", styles["SecaoNutri"]))
    for rec in insights.get("recomendacoes", []):
        story.append(Paragraph(f"• {_p(rec)}", styles["TextoNutri"]))

    story.append(Paragraph("Antropometria atual", styles["SecaoNutri"]))
    if antrop:
        dados_antrop = [
            ["Data", antrop.get("data_avaliacao", "")],
            ["Peso", f"{antrop.get('peso', '')} kg"],
            ["Altura", antrop.get("altura", "")],
            ["IMC", antrop.get("imc", "")],
            ["Classificação IMC", antrop.get("classificacao_imc", "")],
            ["Cintura", antrop.get("circunferencia_cintura", "")],
            ["Risco cintura", antrop.get("risco_cintura", "")],
        ]
        tab_antrop = Table(dados_antrop, colWidths=[4 * cm, 12 * cm])
        tab_antrop.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F1F8E9")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ]))
        story.append(tab_antrop)
    else:
        story.append(Paragraph("Sem avaliação antropométrica cadastrada.", styles["TextoNutri"]))

    story.append(Paragraph("Anamnese mais recente", styles["SecaoNutri"]))
    if anamnese:
        for campo in ["data_anamnese", "queixa_principal", "sintomas", "historia_patologica_pregressa", "historia_familiar", "atividade_fisica", "qualidade_sono", "funcionamento_intestinal", "ingestao_agua_dia", "habitos_fim_de_semana"]:
            valor = anamnese.get(campo, "")
            if valor:
                story.append(Paragraph(f"<b>{_p(campo)}:</b> {_p(valor)}", styles["TextoNutri"]))
    else:
        story.append(Paragraph("Sem anamnese cadastrada.", styles["TextoNutri"]))

    story.append(Paragraph("Recordatório mais recente", styles["SecaoNutri"]))
    if recordatorio:
        for campo in ["data_registro", "desjejum", "lanche_manha", "almoco", "lanche_tarde", "jantar", "ceia", "observacoes"]:
            valor = recordatorio.get(campo, "")
            if valor:
                story.append(Paragraph(f"<b>{_p(campo)}:</b> {_p(valor)}", styles["TextoNutri"]))
    else:
        story.append(Paragraph("Sem recordatório cadastrado.", styles["TextoNutri"]))

    story.append(Paragraph("Prioridade por painel", styles["SecaoNutri"]))
    prioridades = insights.get("prioridades", [])
    if prioridades:
        dados = [["Painel", "Score", "Alterados", "Sem ref.", "Inválidos", "Total"]]
        for p in prioridades:
            dados.append([p["painel"], p["score"], p["alterados"], p["sem_referencia"], p["invalidos"], p["total"]])
        tab = Table(dados, colWidths=[6 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm])
        tab.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E7D32")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]))
        story.append(tab)
    else:
        story.append(Paragraph("Sem prioridades automáticas.", styles["TextoNutri"]))

    story.append(Paragraph("Exames analisados", styles["SecaoNutri"]))
    if analises:
        dados = [["Data", "Exame", "Resultado", "Ref.", "Status"]]
        for a in analises[:40]:
            dados.append([
                a.get("data_exame", ""),
                a.get("nome_exame_padronizado", ""),
                f"{a.get('resultado', '')} {a.get('unidade', '')}",
                f"{a.get('valor_min', '')} - {a.get('valor_max', '')}",
                a.get("status", ""),
            ])
        tab = Table(dados, colWidths=[2.2 * cm, 5 * cm, 3 * cm, 3 * cm, 3 * cm])
        tab.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E7D32")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
        ]))
        story.append(tab)
    else:
        story.append(Paragraph("Sem exames analisados.", styles["TextoNutri"]))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Observação: este relatório é ferramenta de apoio. Não substitui diagnóstico, prescrição ou conduta clínica individualizada.",
        styles["TextoNutri"]
    ))

    doc.build(story)
    return {"sucesso": True, "erro": "", "arquivo": str(caminho)}
