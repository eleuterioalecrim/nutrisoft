import uuid

# ===== IMPORTS RELATÓRIO NUTRICIONAL =====
import math
import csv
from pathlib import Path as SysPath
from xml.sax.saxutils import escape as xml_escape
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)
from reportlab.graphics.shapes import Drawing, Rect, String
# ===== FIM IMPORTS RELATÓRIO NUTRICIONAL =====


# ===== IMPORTS PDF / REPORTLAB =====
from pathlib import Path as SysPath
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
    KeepTogether,
)
# ===== FIM IMPORTS PDF / REPORTLAB =====

import os
import sys
import subprocess
import unicodedata
import re
from pathlib import Path as SysPath
from pathlib import Path
from datetime import datetime, date
import csv
import shutil

import json
import flet as ft
from exames_grupos_prioritarios import listar_grupos_disponiveis, ordenar_exames_por_prioridade, identificar_grupo_exame, ordenar_itens_exames_por_prioridade, agrupar_itens_exames, garantir_prioritarios_no_catalogo, identificar_grupo_item, obter_nome_exame_item

# ============================================================
# BASE CSV DA NOVA APLICAÇÃO FLET
# ============================================================

APP_DIR = Path(__file__).resolve().parent
DATA_FLET_DIR = APP_DIR / "data_flet"

PACIENTE_ATUAL = {
    "id": 1,
    "nome": "Paciente exemplo",
    "idade": 42,
    "ultimo_exame": "2026-06-28",
    "status": "Atenção",
}

INDICADORES = []

SERIE_GLICOSE = [
    {"data": "Jan", "valor": 92},
    {"data": "Fev", "valor": 96},
    {"data": "Mar", "valor": 101},
    {"data": "Abr", "valor": 99},
    {"data": "Mai", "valor": 104},
    {"data": "Jun", "valor": 108},
]


# =========================
# TEMA / ESTILO
# =========================

COR_BG = "#F5F7FB"
COR_CARD = "#FFFFFF"
COR_TEXTO = "#172033"
COR_TEXTO_FRACO = "#6B7280"
COR_PRIMARIA = "#2563EB"
COR_NORMAL = "#16A34A"
COR_ALERTA = "#F59E0B"
COR_CRITICO = "#DC2626"


def cor_status(status: str) -> str:
    status = (status or "").lower()

    if status in ["normal", "ok"]:
        return COR_NORMAL

    if status in ["alto", "baixo", "atenção", "atencao", "alterado"]:
        return COR_ALERTA

    if status in ["crítico", "critico", "grave"]:
        return COR_CRITICO

    return COR_TEXTO_FRACO


# =========================
# COMPONENTES
# =========================

def app_card(content, padding=20, expand=False):
    return ft.Container(
        content=content,
        bgcolor=COR_CARD,
        border_radius=18,
        padding=padding,
        expand=expand,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=18,
            color="#1F293714",
            offset=ft.Offset(0, 6),
        ),
    )


def metric_card(nome, valor, unidade, referencia, status):
    status_color = cor_status(status)

    return app_card(
        ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            nome,
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=COR_TEXTO_FRACO,
                        ),
                        ft.Container(
                            content=ft.Text(
                                status.upper(),
                                size=10,
                                color="white",
                                weight=ft.FontWeight.BOLD,
                            ),
                            bgcolor=status_color,
                            border_radius=30,
                            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                        ),
                    ],
                ),
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    spacing=6,
                    controls=[
                        ft.Text(
                            str(valor),
                            size=30,
                            weight=ft.FontWeight.BOLD,
                            color=COR_TEXTO,
                        ),
                        ft.Text(
                            unidade,
                            size=13,
                            color=COR_TEXTO_FRACO,
                        ),
                    ],
                ),
                ft.Text(
                    f"Referência: {referencia}",
                    size=12,
                    color=COR_TEXTO_FRACO,
                ),
            ],
        ),
        padding=18,
    )


def header_paciente():
    status_color = cor_status(PACIENTE_ATUAL["status"])

    return app_card(
        ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(
                            PACIENTE_ATUAL["nome"],
                            size=26,
                            weight=ft.FontWeight.BOLD,
                            color=COR_TEXTO,
                        ),
                        ft.Text(
                            f"{PACIENTE_ATUAL['idade']} anos • Último exame: {PACIENTE_ATUAL['ultimo_exame']}",
                            size=13,
                            color=COR_TEXTO_FRACO,
                        ),
                    ],
                ),
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.Container(
                            content=ft.Text(
                                PACIENTE_ATUAL["status"],
                                color="white",
                                weight=ft.FontWeight.BOLD,
                            ),
                            bgcolor=status_color,
                            border_radius=30,
                            padding=ft.Padding.symmetric(horizontal=18, vertical=10),
                        ),
                        ft.FilledButton(
                            content="Novo exame",
                            icon=ft.Icons.ADD,
                            style=ft.ButtonStyle(
                                bgcolor=COR_PRIMARIA,
                                color="white",
                                shape=ft.RoundedRectangleBorder(radius=12),
                            ),
                        ),
                        ft.OutlinedButton(
                            content="Excluir paciente",
                            icon=ft.Icons.DELETE_OUTLINE,
                            style=ft.ButtonStyle(
                                color=COR_CRITICO,
                                shape=ft.RoundedRectangleBorder(radius=12),
                            ),
                        ),
                    ],
                ),
            ],
        ),
        padding=24,
    )


def echarts_html(titulo: str, serie: list[dict]) -> str:
    labels = [x["data"] for x in serie]
    valores = [x["valor"] for x in serie]

    option = {
        "title": {
            "text": titulo,
            "left": "left",
            "textStyle": {
                "fontSize": 18,
                "fontWeight": 700,
                "color": "#172033",
            },
        },
        "tooltip": {
            "trigger": "axis",
        },
        "grid": {
            "left": "3%",
            "right": "3%",
            "bottom": "8%",
            "top": "20%",
            "containLabel": True,
        },
        "xAxis": {
            "type": "category",
            "data": labels,
            "axisLine": {"lineStyle": {"color": "#CBD5E1"}},
            "axisLabel": {"color": "#64748B"},
        },
        "yAxis": {
            "type": "value",
            "axisLine": {"show": False},
            "splitLine": {"lineStyle": {"color": "#E5E7EB"}},
            "axisLabel": {"color": "#64748B"},
        },
        "series": [
            {
                "name": "Valor",
                "type": "line",
                "smooth": True,
                "symbolSize": 8,
                "lineStyle": {
                    "width": 4,
                },
                "areaStyle": {
                    "opacity": 0.12,
                },
                "data": valores,
                "markArea": {
                    "silent": True,
                    "itemStyle": {
                        "opacity": 0.08,
                    },
                    "data": [
                        [
                            {"yAxis": 70},
                            {"yAxis": 99},
                        ]
                    ],
                },
                "markLine": {
                    "symbol": "none",
                    "lineStyle": {
                        "type": "dashed",
                    },
                    "data": [
                        {"yAxis": 99, "name": "Limite superior"},
                    ],
                },
            }
        ],
    }

    option_json = json.dumps(option, ensure_ascii=False)

    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8" />
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            background: #FFFFFF;
            font-family: Inter, Arial, sans-serif;
            overflow: hidden;
        }}

        #chart {{
            width: 100vw;
            height: 360px;
        }}
    </style>
</head>
<body>
    <div id="chart"></div>

    <script>
        const chart = echarts.init(document.getElementById('chart'));
        const option = {option_json};
        chart.setOption(option);

        window.addEventListener('resize', function () {{
            chart.resize();
        }});
    </script>
</body>
</html>
"""



def grafico_echarts():
    """
    Versão nativa provisória para desktop Linux.
    Mantém a tela estável sem depender de WebView.
    Depois podemos reativar ECharts quando rodarmos em modo web.
    """

    valores = [item["valor"] for item in SERIE_GLICOSE]
    maior = max(valores)
    menor = min(valores)

    barras = []

    for item in SERIE_GLICOSE:
        valor = item["valor"]

        altura = 70 + int(((valor - menor) / max(1, maior - menor)) * 140)

        status_color = COR_NORMAL if valor <= 99 else COR_ALERTA

        barras.append(
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.END,
                spacing=8,
                controls=[
                    ft.Text(
                        str(valor),
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=COR_TEXTO,
                    ),
                    ft.Container(
                        width=34,
                        height=altura,
                        border_radius=10,
                        bgcolor=status_color,
                    ),
                    ft.Text(
                        item["data"],
                        size=12,
                        color=COR_TEXTO_FRACO,
                    ),
                ],
            )
        )

    return app_card(
        ft.Column(
            spacing=18,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text(
                                    "Evolução laboratorial",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=COR_TEXTO,
                                ),
                                ft.Text(
                                    "Evolução laboratorial por período, com destaque para valores fora da referência.",
                                    size=13,
                                    color=COR_TEXTO_FRACO,
                                ),
                            ],
                        ),
                        ft.Container(
                            content=ft.Text(
                                "Referência: 70 - 99 mg/dL",
                                size=12,
                                color=COR_TEXTO_FRACO,
                            ),
                            bgcolor="#F8FAFC",
                            border_radius=20,
                            padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                        ),
                    ],
                ),
                ft.Container(
                    height=280,
                    bgcolor="#F8FAFC",
                    border_radius=16,
                    padding=ft.Padding.only(left=20, right=20, top=20, bottom=16),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        controls=barras,
                    ),
                ),
            ],
        ),
        padding=20,
        expand=True,
    )

def tabela_exames():
    rows = []

    for item in INDICADORES:
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(item["nome"])),
                    ft.DataCell(ft.Text(f"{item['valor']} {item['unidade']}")),
                    ft.DataCell(ft.Text(item["referencia"])),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                item["status"].upper(),
                                size=11,
                                color="white",
                                weight=ft.FontWeight.BOLD,
                            ),
                            bgcolor=cor_status(item["status"]),
                            border_radius=20,
                            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                        )
                    ),
                ]
            )
        )

    return app_card(
        ft.Column(
            spacing=16,
            controls=[
                ft.Text(
                    "Detalhamento dos exames",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=COR_TEXTO,
                ),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Exame")),
                        ft.DataColumn(ft.Text("Resultado")),
                        ft.DataColumn(ft.Text("Referência")),
                        ft.DataColumn(ft.Text("Status")),
                    ],
                    rows=rows,
                    heading_row_color="#F8FAFC",
                    border_radius=12,
                ),
            ],
        ),
        padding=20,
    )





def status_pdf_color(status):
    status = (status or "").lower()

    if status == "normal":
        return colors.HexColor("#16A34A")

    if status in ["alto", "baixo", "atenção", "atencao"]:
        return colors.HexColor("#F59E0B")

    if status in ["crítico", "critico"]:
        return colors.HexColor("#DC2626")

    return colors.HexColor("#6B7280")



# ============================================================
# AJUSTE VISUAL - NOME DO EXAME NO HISTÓRICO
# ============================================================

def nome_exame_para_exibicao(item):
    """
    Retorna o melhor nome disponível para exibir no histórico.
    Compatível com importação de PDF, cadastro manual e versões antigas.
    """
    if not isinstance(item, dict):
        return "-"

    campos = [
        "nome_exame",
        "nome_padronizado",
        "nome",
        "exame",
        "analito",
        "tipo_exame",
        "descricao",
    ]

    for campo in campos:
        valor = str(item.get(campo) or "").strip()
        if valor:
            return valor

    return "-"


def garantir_nome_exame_item(item):
    """
    Preenche todos os aliases de nome do exame para evitar telas com coluna Exame vazia.
    """
    if not isinstance(item, dict):
        return item

    nome = nome_exame_para_exibicao(item)

    if nome and nome != "-":
        item["nome_exame"] = item.get("nome_exame") or nome
        item["nome_padronizado"] = item.get("nome_padronizado") or nome
        item["nome"] = item.get("nome") or nome
        item["exame"] = item.get("exame") or nome
        item["analito"] = item.get("analito") or nome
        item["tipo_exame"] = item.get("tipo_exame") or nome
        item["descricao"] = item.get("descricao") or nome

    return item


def buscar_resultados_paciente(paciente_id):
    return [
        r for r in globals().get("RESULTADOS_EXAMES_MOCK", [])
        if str(r.get("paciente_id")) == str(paciente_id)
    ]


def gerar_pdf_analise_paciente(paciente):
    """
    Gera PDF completo da análise do paciente.
    Nesta fase usa dados em memória do protótipo.
    Depois será conectado ao banco real.
    """
    paciente_id = str(paciente["id"])
    resultados = buscar_resultados_paciente(paciente_id)

    pasta_saida = SysPath.home() / "projetos" / "nutrisoft" / "relatorios"
    pasta_saida.mkdir(parents=True, exist_ok=True)

    nome_limpo = "".join(
        c for c in paciente["nome"]
        if c.isalnum() or c in (" ", "_", "-")
    ).strip().replace(" ", "_")

    agora = datetime.now()
    arquivo_pdf = pasta_saida / f"analise_{nome_limpo}_{agora.strftime('%Y%m%d_%H%M%S')}.pdf"

    doc = SimpleDocTemplate(
        str(arquivo_pdf),
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        "TituloNutriSoft",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#172033"),
        spaceAfter=12,
    )

    subtitulo_style = ParagraphStyle(
        "SubtituloNutriSoft",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        textColor=colors.HexColor("#6B7280"),
        spaceAfter=16,
    )

    secao_style = ParagraphStyle(
        "SecaoNutriSoft",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#172033"),
        spaceBefore=12,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "TextoNutriSoft",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#172033"),
    )

    small_style = ParagraphStyle(
        "TextoPequenoNutriSoft",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#6B7280"),
    )

    story = []

    story.append(Paragraph("NutriSoft", titulo_style))
    story.append(Paragraph("Relatório de Análise Clínica do Paciente", subtitulo_style))

    story.append(Paragraph("Dados do paciente", secao_style))

    dados_paciente = [
        ["Paciente", paciente.get("nome", "")],
        ["Idade", f'{paciente.get("idade", "-")} anos'],
        ["Data de emissão", agora.strftime("%d/%m/%Y %H:%M")],
        ["Total de resultados", str(len(resultados))],
    ]

    tabela_dados = Table(dados_paciente, colWidths=[4 * cm, 12 * cm])
    tabela_dados.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EFF6FF")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#172033")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(tabela_dados)
    story.append(Spacer(1, 10))

    if not resultados:
        story.append(Paragraph("Resumo da análise", secao_style))
        story.append(
            Paragraph(
                "Nenhum resultado de exame foi lançado para este paciente até o momento.",
                normal_style,
            )
        )
    else:
        normais = len([r for r in resultados if str(r.get("status", "")).lower() == "normal"])
        alterados = len([
            r for r in resultados
            if str(r.get("status", "")).lower() in ["alto", "baixo", "crítico", "critico"]
        ])
        sem_analise = len([
            r for r in resultados
            if str(r.get("status", "")).lower() == "sem análise"
        ])

        story.append(Paragraph("Resumo da análise", secao_style))

        resumo = [
            ["Indicador", "Quantidade"],
            ["Resultados analisados", str(len(resultados))],
            ["Dentro da referência", str(normais)],
            ["Fora da referência", str(alterados)],
            ["Sem análise automática", str(sem_analise)],
        ]

        tabela_resumo = Table(resumo, colWidths=[10 * cm, 6 * cm])
        tabela_resumo.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563EB")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        story.append(tabela_resumo)
        story.append(Spacer(1, 12))

        story.append(Paragraph("Resultados dos exames", secao_style))

        dados_exames = [
            [
                "Data",
                "Exame",
                "Resultado",
                "Referência",
                "Status",
            ]
        ]

        for item in sorted(resultados, key=lambda x: x.get("data", ""), reverse=True):
            dados_exames.append(
                [
                    data_iso_para_br(item.get("data", "")) if "data_iso_para_br" in globals() else item.get("data", ""),
                    Paragraph(_ns_nome_exame(item) if "_ns_nome_exame" in globals() else item.get("nome_exame", item.get("nome", "")), normal_style),
                    f'{item.get("resultado", "")} {item.get("unidade", "")}',
                    f'{item.get("referencia", "")} {item.get("unidade", "")}',
                    item.get("status", ""),
                ]
            )

        tabela_exames_pdf = Table(
            dados_exames,
            colWidths=[2.2 * cm, 5.0 * cm, 3.0 * cm, 3.5 * cm, 2.3 * cm],
            repeatRows=1,
        )

        tabela_exames_pdf.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563EB")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )

        story.append(tabela_exames_pdf)
        story.append(Spacer(1, 12))

        story.append(Paragraph("Fontes das referências", secao_style))

        fontes_unicas = []
        for item in resultados:
            fonte = item.get("fonte", "")
            if fonte and fonte not in fontes_unicas:
                fontes_unicas.append(fonte)

        if fontes_unicas:
            for fonte in fontes_unicas:
                story.append(Paragraph(f"- {fonte}", small_style))
        else:
            story.append(Paragraph("Nenhuma fonte de referência registrada.", small_style))

        story.append(Spacer(1, 12))

        story.append(Paragraph("Observações importantes", secao_style))
        story.append(
            Paragraph(
                "Este relatório organiza os resultados informados e compara automaticamente "
                "com as faixas de referência cadastradas no sistema. A interpretação clínica "
                "definitiva deve ser realizada por profissional habilitado, considerando o "
                "histórico, sintomas, medicamentos e demais condições do paciente.",
                normal_style,
            )
        )

    def rodape(canvas, doc_obj):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#6B7280"))
        canvas.drawString(1.5 * cm, 1.0 * cm, "NutriSoft - Relatório gerado automaticamente")
        canvas.drawRightString(19.5 * cm, 1.0 * cm, f"Página {doc_obj.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=rodape, onLaterPages=rodape)

    return str(arquivo_pdf)


def dashboard_view(page=None, on_novo_exame=None, on_excluir=None):
    paciente_inicial_id = str(globals().get("PACIENTE_SELECIONADO_ID", "1"))

    def obter_paciente(paciente_id):
        for paciente in PACIENTES_MOCK:
            if str(paciente["id"]) == str(paciente_id):
                return paciente
        if PACIENTES_MOCK:
            return PACIENTES_MOCK[0]

        return {
            "id": "",
            "nome": "Nenhum paciente cadastrado",
            "idade": "",
            "sexo": "",
            "data_nascimento": "",
            "objetivo": "",
            "observacoes": "",
        }

    paciente_dropdown = ft.Dropdown(
        label="Paciente",
        value=paciente_inicial_id,
        width=340,
        border_radius=12,
        options=[
            ft.dropdown.Option(
                key=str(paciente["id"]),
                text=f'{paciente["nome"]} - {paciente["idade"]} anos',
            )
            for paciente in PACIENTES_MOCK
        ],
    )

    painel = ft.Column(
        spacing=18,
        expand=True,
    )

    def resultados_do_paciente(paciente_id):
        return [
            r for r in globals().get("RESULTADOS_EXAMES_MOCK", [])
            if str(r.get("paciente_id")) == str(paciente_id)
        ]

    def ultimos_resultados_por_exame(resultados):
        ultimos = {}

        for item in sorted(resultados, key=lambda x: x.get("data", "")):
            ultimos[item.get("exame_id")] = item

        return list(ultimos.values())

    def card_resultado_dashboard(item):
        status = item.get("status", "Sem análise")
        status_color = cor_resultado_exame(status) if "cor_resultado_exame" in globals() else cor_status(status)

        return metric_card(
            item.get("exame_nome", "Exame"),
            item.get("resultado", "-"),
            item.get("unidade", ""),
            f'{item.get("referencia", "")} {item.get("unidade", "")}',
            status,
        )

    def cards_padrao_sem_resultados():
        return [
            app_card(
                ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text("Sem resultados", size=13, weight=ft.FontWeight.W_600, color=COR_TEXTO_FRACO),
                        ft.Text("-", size=30, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                        ft.Text("Lance um exame para iniciar a análise.", size=12, color=COR_TEXTO_FRACO),
                    ],
                ),
                padding=18,
            )
            for _ in range(4)
        ]

    def grafico_dashboard(resultados):
        if not resultados:
            return app_card(
                ft.Column(
                    spacing=14,
                    controls=[
                        ft.Text(
                            "Evolução laboratorial",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=COR_TEXTO,
                        ),
                        ft.Container(
                            height=240,
                            bgcolor="#F8FAFC",
                            border_radius=16,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=10,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.QUERY_STATS,
                                        size=42,
                                        color=COR_TEXTO_FRACO,
                                    ),
                                    ft.Text(
                                        "Nenhum resultado lançado para gerar gráfico.",
                                        size=14,
                                        color=COR_TEXTO_FRACO,
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
                padding=20,
            )

        # Para o protótipo, monta gráfico simples com os últimos resultados numéricos.
        itens_numericos = []

        for item in resultados[-8:]:
            valor = numero_br_para_float(item.get("resultado")) if "numero_br_para_float" in globals() else None
            if valor is not None:
                itens_numericos.append(
                    {
                        "nome": item.get("exame_nome", "Exame"),
                        "valor": valor,
                        "status": item.get("status", "Sem análise"),
                    }
                )

        if not itens_numericos:
            return app_card(
                ft.Column(
                    spacing=14,
                    controls=[
                        ft.Text(
                            "Evolução laboratorial",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=COR_TEXTO,
                        ),
                        ft.Container(
                            height=240,
                            bgcolor="#F8FAFC",
                            border_radius=16,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Text(
                                "Resultados lançados não possuem valor numérico para gráfico.",
                                size=14,
                                color=COR_TEXTO_FRACO,
                            ),
                        ),
                    ],
                ),
                padding=20,
            )

        maior = max([i["valor"] for i in itens_numericos])
        menor = min([i["valor"] for i in itens_numericos])

        barras = []

        for item in itens_numericos:
            altura = 70 + int(((item["valor"] - menor) / max(1, maior - menor)) * 140)
            status_color = cor_resultado_exame(item["status"]) if "cor_resultado_exame" in globals() else cor_status(item["status"])

            barras.append(
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.END,
                    spacing=8,
                    controls=[
                        ft.Text(
                            str(item["valor"]).rstrip("0").rstrip("."),
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=COR_TEXTO,
                        ),
                        ft.Container(
                            width=38,
                            height=altura,
                            border_radius=10,
                            bgcolor=status_color,
                        ),
                        ft.Text(
                            item["nome"],
                            size=11,
                            color=COR_TEXTO_FRACO,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            width=80,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                )
            )

        return app_card(
            ft.Column(
                spacing=18,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text(
                                        "Evolução laboratorial",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color=COR_TEXTO,
                                    ),
                                    ft.Text(
                                        "Últimos resultados numéricos lançados para o paciente.",
                                        size=13,
                                        color=COR_TEXTO_FRACO,
                                    ),
                                ],
                            ),
                            ft.Container(
                                content=ft.Text(
                                    "Dados carregados da base clínica",
                                    size=12,
                                    color=COR_TEXTO_FRACO,
                                ),
                                bgcolor="#F8FAFC",
                                border_radius=20,
                                padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                            ),
                        ],
                    ),
                    ft.Container(
                        height=280,
                        bgcolor="#F8FAFC",
                        border_radius=16,
                        padding=ft.Padding.only(left=20, right=20, top=20, bottom=16),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            vertical_alignment=ft.CrossAxisAlignment.END,
                            controls=barras,
                        ),
                    ),
                ],
            ),
            padding=20,
        )

    def tabela_dashboard(resultados):
        if not resultados:
            return app_card(
                ft.Column(
                    spacing=14,
                    controls=[
                        ft.Text(
                            "Histórico do paciente",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=COR_TEXTO,
                        ),
                        ft.Container(
                            padding=26,
                            bgcolor="#F8FAFC",
                            border_radius=16,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Text(
                                "Nenhum resultado lançado para este paciente.",
                                color=COR_TEXTO_FRACO,
                                size=14,
                            ),
                        ),
                    ],
                ),
                padding=20,
            )

        linhas = []

        for item in sorted(resultados, key=lambda x: x.get("data", ""), reverse=True):
            status = item.get("status", "Sem análise")
            status_color = cor_resultado_exame(status) if "cor_resultado_exame" in globals() else cor_status(status)

            linhas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(data_iso_para_br(item.get("data", "")) if "data_iso_para_br" in globals() else item.get("data", ""))),
                        ft.DataCell(ft.Text(nome_exame_para_exibicao(item))),
                        ft.DataCell(ft.Text(f'{item.get("resultado", "")} {item.get("unidade", "")}')),
                        ft.DataCell(ft.Text(f'{item.get("referencia", "")} {item.get("unidade", "")}')),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(
                                    status.upper(),
                                    size=10,
                                    color="white",
                                    weight=ft.FontWeight.BOLD,
                                ),
                                bgcolor=status_color,
                                border_radius=30,
                                padding=ft.Padding.symmetric(horizontal=10, vertical=5),
                            )
                        ),
                    ]
                )
            )

        return app_card(
            ft.Column(
                spacing=16,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                "Histórico do paciente",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=COR_TEXTO,
                            ),
                            ft.Text(
                                "Resultados lançados",
                                size=12,
                                color=COR_TEXTO_FRACO,
                            ),
                        ],
                    ),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Data")),
                            ft.DataColumn(ft.Text("Exame")),
                            ft.DataColumn(ft.Text("Resultado")),
                            ft.DataColumn(ft.Text("Referência")),
                            ft.DataColumn(ft.Text("Status")),
                        ],
                        rows=linhas,
                        heading_row_color="#F8FAFC",
                        border_radius=12,
                    ),
                ],
            ),
            padding=20,
        )

    def gerar_pdf_dashboard(paciente):
        try:
            caminho_pdf = gerar_pdf_analise_paciente(paciente)
            mostrar_snackbar(
                page,
                f"PDF gerado: {caminho_pdf}",
                COR_NORMAL,
            )
        except Exception as exc:
            mostrar_snackbar(
                page,
                f"Erro ao gerar PDF: {exc}",
                COR_CRITICO,
            )


    def atualizar_dashboard(e=None):
        paciente_id = paciente_dropdown.value or "1"
        globals()["PACIENTE_SELECIONADO_ID"] = paciente_id

        paciente = obter_paciente(paciente_id)
        resultados = resultados_do_paciente(paciente_id)
        ultimos = ultimos_resultados_por_exame(resultados)

        total_resultados = len(resultados)
        normais = len([r for r in resultados if str(r.get("status", "")).lower() == "normal"])
        alterados = len([
            r for r in resultados
            if str(r.get("status", "")).lower() in ["alto", "baixo", "crítico", "critico"]
        ])

        if alterados > 0:
            status_geral = "Atenção"
        elif total_resultados > 0:
            status_geral = "Normal"
        else:
            status_geral = paciente.get("status", "Sem dados")

        status_color = cor_status(status_geral)

        datas = sorted(
            set([r.get("data") for r in resultados if r.get("data")]),
            reverse=True,
        )

        ultimo_exame = data_iso_para_br(datas[0]) if datas and "data_iso_para_br" in globals() else paciente.get("ultimo_exame", "-")

        cards = [card_resultado_dashboard(item) for item in ultimos[:4]]

        if not cards:
            cards = cards_padrao_sem_resultados()

        while len(cards) < 4:
            cards.append(
                app_card(
                    ft.Column(
                        spacing=8,
                        controls=[
                            ft.Text("Aguardando exame", size=13, weight=ft.FontWeight.W_600, color=COR_TEXTO_FRACO),
                            ft.Text("-", size=30, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                            ft.Text("Sem resultado lançado.", size=12, color=COR_TEXTO_FRACO),
                        ],
                    ),
                    padding=18,
                )
            )

        painel.controls = [
            app_card(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text(
                                    paciente["nome"],
                                    size=26,
                                    weight=ft.FontWeight.BOLD,
                                    color=COR_TEXTO,
                                ),
                                ft.Text(
                                    f'{paciente["idade"]} anos • {total_resultados} resultado(s) • Último exame: {ultimo_exame}',
                                    size=13,
                                    color=COR_TEXTO_FRACO,
                                ),
                            ],
                        ),
                        ft.Row(
                            spacing=12,
                            controls=[
                                ft.Container(
                                    content=ft.Text(
                                        status_geral,
                                        color="white",
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    bgcolor=status_color,
                                    border_radius=30,
                                    padding=ft.Padding.symmetric(horizontal=18, vertical=10),
                                ),
                                ft.FilledButton(
                                    content="Novo exame",
                                    icon=ft.Icons.ADD,
                                    on_click=lambda ev: on_novo_exame(ev, paciente_id) if on_novo_exame else None,
                                    style=ft.ButtonStyle(
                                        bgcolor=COR_PRIMARIA,
                                        color="white",
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                    ),
                                ),
                                ft.OutlinedButton(
                                    content="Gerar PDF",
                                    icon=ft.Icons.PICTURE_AS_PDF,
                                    on_click=lambda ev: gerar_pdf_dashboard(paciente),
                                    style=ft.ButtonStyle(
                                        color=COR_PRIMARIA,
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                    ),
                                ),
                                ft.OutlinedButton(
                                    content="Excluir paciente",
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    on_click=lambda ev: on_excluir(paciente) if on_excluir else None,
                                    style=ft.ButtonStyle(
                                        color=COR_CRITICO,
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
                padding=24,
            ),

            ft.ResponsiveRow(
                columns=12,
                spacing=16,
                run_spacing=16,
                controls=[
                    ft.Container(content=cards[0], col={"xs": 12, "sm": 6, "md": 3}),
                    ft.Container(content=cards[1], col={"xs": 12, "sm": 6, "md": 3}),
                    ft.Container(content=cards[2], col={"xs": 12, "sm": 6, "md": 3}),
                    ft.Container(content=cards[3], col={"xs": 12, "sm": 6, "md": 3}),
                ],
            ),

            ft.ResponsiveRow(
                columns=12,
                spacing=16,
                run_spacing=16,
                controls=[
                    ft.Container(
                        col={"xs": 12, "sm": 4},
                        content=app_card(
                            ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text("Resultados", size=13, color=COR_TEXTO_FRACO),
                                    ft.Text(str(total_resultados), size=28, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                                ],
                            ),
                            padding=18,
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "sm": 4},
                        content=app_card(
                            ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text("Normais", size=13, color=COR_TEXTO_FRACO),
                                    ft.Text(str(normais), size=28, weight=ft.FontWeight.BOLD, color=COR_NORMAL),
                                ],
                            ),
                            padding=18,
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "sm": 4},
                        content=app_card(
                            ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text("Alterados", size=13, color=COR_TEXTO_FRACO),
                                    ft.Text(str(alterados), size=28, weight=ft.FontWeight.BOLD, color=COR_ALERTA),
                                ],
                            ),
                            padding=18,
                        ),
                    ),
                ],
            ),

            grafico_dashboard(resultados),
            tabela_dashboard(resultados),
        ]

        if page:
            page.update()

    paciente_dropdown.on_change = lambda e: atualizar_dashboard()

    atualizar_dashboard()

    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=18,
        expand=True,
        controls=[
            app_card(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text(
                                    "Dashboard clínico",
                                    size=26,
                                    weight=ft.FontWeight.BOLD,
                                    color=COR_TEXTO,
                                ),
                                ft.Text(
                                    "Selecione um paciente para acompanhar seus exames e resultados.",
                                    size=13,
                                    color=COR_TEXTO_FRACO,
                                ),
                            ],
                        ),
                        ft.Row(
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                paciente_dropdown,
                                ft.FilledButton(
                                    content="Aplicar paciente",
                                    icon=ft.Icons.CHECK,
                                    on_click=atualizar_dashboard,
                                    style=ft.ButtonStyle(
                                        bgcolor=COR_PRIMARIA,
                                        color="white",
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
                padding=24,
            ),
            painel,
        ],
    )


def placeholder_view(titulo: str, descricao: str):
    return ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        content=app_card(
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    ft.Icon(ft.Icons.CONSTRUCTION, size=48, color=COR_PRIMARIA),
                    ft.Text(
                        titulo,
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=COR_TEXTO,
                    ),
                    ft.Text(
                        descricao,
                        size=14,
                        color=COR_TEXTO_FRACO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
            padding=40,
        ),
    )



PACIENTES_MOCK = []

def paciente_item_card(paciente, on_abrir=None):
    status_color = cor_status(paciente["status"])

    return app_card(
        ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=48,
                            height=48,
                            border_radius=16,
                            bgcolor="#EFF6FF",
                            alignment=ft.Alignment.CENTER,
                            content=ft.Text(
                                paciente["nome"][:1].upper(),
                                size=20,
                                color=COR_PRIMARIA,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ),
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text(
                                    paciente["nome"],
                                    size=17,
                                    weight=ft.FontWeight.BOLD,
                                    color=COR_TEXTO,
                                ),
                                ft.Text(
                                    f'{paciente["idade"]} anos • {paciente["exames"]} exames cadastrados',
                                    size=12,
                                    color=COR_TEXTO_FRACO,
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.END,
                            spacing=4,
                            controls=[
                                ft.Text(
                                    "Último exame",
                                    size=11,
                                    color=COR_TEXTO_FRACO,
                                ),
                                ft.Text(
                                    paciente["ultimo_exame"],
                                    size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color=COR_TEXTO,
                                ),
                            ],
                        ),
                        ft.Container(
                            content=ft.Text(
                                paciente["status"],
                                size=12,
                                color="white",
                                weight=ft.FontWeight.BOLD,
                            ),
                            bgcolor=status_color,
                            border_radius=30,
                            padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                        ),
                        ft.OutlinedButton(
                            content="Abrir",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=lambda e, p=paciente: on_abrir(p) if on_abrir else None,
                            style=ft.ButtonStyle(
                                color=COR_PRIMARIA,
                                shape=ft.RoundedRectangleBorder(radius=12),
                            ),
                        ),
                    ],
                ),
            ],
        ),
        padding=18,
    )





# ============================================================






# ============================================================
# BASE PRÓPRIA DA NOVA APLICAÇÃO FLET
# ============================================================

APP_DIR_FLET = Path(__file__).resolve().parent
DATA_ANTIGO_DIR = APP_DIR_FLET / "data"
DATA_FLET_DIR = APP_DIR_FLET / "data_flet"

CSV_SCHEMA_FLET = {
    "pacientes.csv": [
        "paciente_id", "data_cadastro", "nome", "data_nascimento", "idade",
        "sexo", "telefone", "email", "profissao", "horario_trabalho", "observacoes"
    ],
    "anamnese.csv": [
        "paciente_id", "data_anamnese", "queixa_principal", "historia_doenca_atual",
        "sintomas", "historia_patologica_pregressa", "historia_familiar",
        "numero_filhos_idades", "amamentou", "atividade_fisica",
        "horario_atividade_fisica", "consumo_alcool", "tabagismo",
        "qualidade_sono", "hora_acordar", "hora_dormir", "comportamento_peso",
        "disposicao_fisica", "funcionamento_intestinal", "funcionamento_urinario",
        "internacoes_cirurgias", "medicamentos_suplementos",
        "intolerancia_alergia_alimentar", "denticao", "mastigacao",
        "quem_cozinha", "apetite", "horario_mais_fome", "ingestao_agua_dia",
        "tratamento_nutricional_anterior", "qual_tratamento",
        "objetivo_nutricional", "alimentos_preferidos", "habito_beliscar",
        "alimentos_que_nao_gosta", "habitos_fim_de_semana", "dificuldades_adesao"
    ],
    "recordatorio_habitual.csv": [
        "paciente_id", "data_registro", "desjejum", "lanche_manha",
        "almoco", "lanche_tarde", "jantar", "ceia", "observacoes"
    ],
    "antropometria.csv": [
        "paciente_id", "data_avaliacao", "tipo_avaliacao",
        "objetivo_antropometrico", "condicao_medicao", "tipo_balanca",
        "roupa_medicao", "local_cintura", "peso", "altura",
        "circunferencia_cintura", "imc", "classificacao_imc",
        "risco_cintura", "observacoes"
    ],
    "exames.csv": [
        "paciente_id", "data_exame", "nome_exame", "resultado",
        "unidade", "observacoes"
    ],
    "referencias_exames.csv": [
        "nome_exame", "sexo", "idade_min", "idade_max", "valor_min",
        "valor_max", "unidade", "fonte_referencia", "observacoes"
    ],
    "alias_exames.csv": [
        "alias", "nome_padronizado"
    ],
    "analise_exames.csv": [
        "paciente_id", "data_exame", "nome_exame", "resultado",
        "unidade", "referencia", "status", "observacoes"
    ],
    "historico_edicoes.csv": [
        "data_hora", "paciente_id", "modulo", "acao", "detalhes"
    ],
    "evolucao_conduta.csv": [
        "paciente_id", "data_registro", "conduta", "evolucao", "observacoes"
    ],
}


def inicializar_base_flet():
    DATA_FLET_DIR.mkdir(parents=True, exist_ok=True)

    for nome_arquivo, cabecalho in CSV_SCHEMA_FLET.items():
        destino = DATA_FLET_DIR / nome_arquivo
        origem = DATA_ANTIGO_DIR / nome_arquivo

        if destino.exists():
            continue

        with destino.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=cabecalho)
            writer.writeheader()
        print(f"[DATA_FLET] Criado vazio: {nome_arquivo}")


def caminho_csv_flet(nome_arquivo):
    inicializar_base_flet()
    return DATA_FLET_DIR / nome_arquivo


def csv_flet_path(nome_arquivo):
    return caminho_csv_flet(nome_arquivo)


def ler_csv_pacientes_real_definitivo():
    caminho = caminho_csv_flet("pacientes.csv")

    if not caminho.exists():
        print(f"[PACIENTES CSV] Arquivo não encontrado: {caminho}")
        return []

    try:
        with caminho.open("r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
    except UnicodeDecodeError:
        with caminho.open("r", encoding="latin-1", newline="") as f:
            rows = list(csv.DictReader(f))

    print(f"[PACIENTES CSV] Linhas lidas: {len(rows)}")
    if rows:
        print(f"[PACIENTES CSV] Primeiro paciente: {rows[0].get('nome')}")

    return rows


def ler_csv_generico_real(nome_arquivo):
    caminho = caminho_csv_flet(nome_arquivo)

    if not caminho.exists():
        return []

    try:
        with caminho.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    except UnicodeDecodeError:
        with caminho.open("r", encoding="latin-1", newline="") as f:
            return list(csv.DictReader(f))
    except Exception as exc:
        print(f"[CSV] Erro ao ler {nome_arquivo}: {exc}")
        return []


def exames_reais_paciente_definitivo(paciente_id):
    exames = ler_csv_generico_real("exames.csv")

    return [
        e for e in exames
        if str(e.get("paciente_id", "")).strip() == str(paciente_id).strip()
    ]


def analises_reais_paciente_definitivo(paciente_id):
    analises = ler_csv_generico_real("analise_exames.csv")

    return [
        a for a in analises
        if str(a.get("paciente_id", "")).strip() == str(paciente_id).strip()
    ]


def ultimo_exame_real_definitivo(paciente_id):
    exames = exames_reais_paciente_definitivo(paciente_id)

    datas = [
        str(e.get("data_exame") or e.get("data") or "").strip()
        for e in exames
        if str(e.get("data_exame") or e.get("data") or "").strip()
    ]

    if not datas:
        return "-"

    try:
        return sorted(datas)[-1]
    except Exception:
        return datas[-1]


def status_paciente_real_definitivo(paciente_id):
    exames = exames_reais_paciente_definitivo(paciente_id)
    analises = analises_reais_paciente_definitivo(paciente_id)

    if not exames:
        return "Sem exames"

    if not analises:
        return "Sem análise"

    encontrou_alerta = False

    for item in analises:
        texto = " ".join(str(v or "") for v in item.values()).lower()

        if "crítico" in texto or "critico" in texto:
            return "Crítico"

        if (
            "alto" in texto
            or "baixo" in texto
            or "alterado" in texto
            or "fora" in texto
            or "atenção" in texto
            or "atencao" in texto
        ):
            encontrou_alerta = True

    return "Atenção" if encontrou_alerta else "Normal"


def normalizar_paciente_csv_definitivo(row):
    paciente_id = str(row.get("paciente_id", "")).strip()
    nome = str(row.get("nome", "")).strip()

    idade = str(row.get("idade", "")).strip()
    if not idade:
        idade = idade_por_nascimento_csv(row.get("data_nascimento", "")) if "idade_por_nascimento_csv" in globals() else "-"

    exames = exames_reais_paciente_definitivo(paciente_id)

    return {
        "id": paciente_id,
        "nome": nome,
        "idade": idade,
        "data_nascimento": str(row.get("data_nascimento", "")).strip(),
        "sexo": str(row.get("sexo", "Não informado")).strip() or "Não informado",
        "telefone": str(row.get("telefone", "")).strip(),
        "email": str(row.get("email", "")).strip(),
        "profissao": str(row.get("profissao", "")).strip(),
        "horario_trabalho": str(row.get("horario_trabalho", "")).strip(),
        "observacoes": str(row.get("observacoes", "")).strip(),
        "ultimo_exame": ultimo_exame_real_definitivo(paciente_id),
        "status": status_paciente_real_definitivo(paciente_id),
        "exames": len(exames),
        "origem": "CSV_FLET",
    }


def pacientes_view(on_abrir=None):
    atualizar_pacientes_csv_real_definitivo()
    total = len(PACIENTES_MOCK)
    normais = len([p for p in PACIENTES_MOCK if p["status"].lower() == "normal"])
    atencao = len([p for p in PACIENTES_MOCK if p["status"].lower() in ["atenção", "atencao"]])
    criticos = len([p for p in PACIENTES_MOCK if p["status"].lower() in ["crítico", "critico"]])

    cards_resumo = ft.ResponsiveRow(
        columns=12,
        spacing=16,
        run_spacing=16,
        controls=[
            ft.Container(
                col={"xs": 12, "sm": 6, "md": 3},
                content=app_card(
                    ft.Column(
                        spacing=6,
                        controls=[
                            ft.Text("Pacientes", size=13, color=COR_TEXTO_FRACO),
                            ft.Text(str(total), size=28, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                        ],
                    ),
                    padding=18,
                ),
            ),
            ft.Container(
                col={"xs": 12, "sm": 6, "md": 3},
                content=app_card(
                    ft.Column(
                        spacing=6,
                        controls=[
                            ft.Text("Normais", size=13, color=COR_TEXTO_FRACO),
                            ft.Text(str(normais), size=28, weight=ft.FontWeight.BOLD, color=COR_NORMAL),
                        ],
                    ),
                    padding=18,
                ),
            ),
            ft.Container(
                col={"xs": 12, "sm": 6, "md": 3},
                content=app_card(
                    ft.Column(
                        spacing=6,
                        controls=[
                            ft.Text("Atenção", size=13, color=COR_TEXTO_FRACO),
                            ft.Text(str(atencao), size=28, weight=ft.FontWeight.BOLD, color=COR_ALERTA),
                        ],
                    ),
                    padding=18,
                ),
            ),
            ft.Container(
                col={"xs": 12, "sm": 6, "md": 3},
                content=app_card(
                    ft.Column(
                        spacing=6,
                        controls=[
                            ft.Text("Críticos", size=13, color=COR_TEXTO_FRACO),
                            ft.Text(str(criticos), size=28, weight=ft.FontWeight.BOLD, color=COR_CRITICO),
                        ],
                    ),
                    padding=18,
                ),
            ),
        ],
    )

    lista = ft.Column(
        spacing=12,
        controls=[paciente_item_card(p, on_abrir=on_abrir) for p in PACIENTES_MOCK],
    )

    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=18,
        expand=True,
        controls=[
            app_card(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text(
                                    "Pacientes",
                                    size=26,
                                    weight=ft.FontWeight.BOLD,
                                    color=COR_TEXTO,
                                ),
                                ft.Text(
                                    "Visão geral dos pacientes cadastrados e seus últimos exames.",
                                    size=13,
                                    color=COR_TEXTO_FRACO,
                                ),
                            ],
                        ),
                        ft.FilledButton(
                            content="Novo paciente",
                            icon=ft.Icons.PERSON_ADD,
                            style=ft.ButtonStyle(
                                bgcolor=COR_PRIMARIA,
                                color="white",
                                shape=ft.RoundedRectangleBorder(radius=12),
                            ),
                        ),
                    ],
                ),
                padding=24,
            ),
            cards_resumo,
            app_card(
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(
                                    "Lista de pacientes",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=COR_TEXTO,
                                ),
                                ft.Text(
                                    "Dados carregados da base própria Flet",
                                    size=12,
                                    color=COR_TEXTO_FRACO,
                                ),
                            ],
                        ),
                        lista,
                    ],
                ),
                padding=20,
            ),
        ],
    )





def excluir_paciente_e_vinculos(paciente):
    """
    Remove o paciente e todos os dados vinculados dentro da aplicação Flet.
    Nesta fase remove dos dados em memória do protótipo.
    Quando conectarmos ao banco real, esta função será substituída por DELETE real.
    """
    paciente_id = str(paciente["id"])

    # Remove paciente da lista
    PACIENTES_MOCK[:] = [
        p for p in PACIENTES_MOCK
        if str(p["id"]) != paciente_id
    ]

    # Remove exames cadastrados vinculados ao paciente
    for chave in list(EXAMES_CADASTRADOS_MOCK.keys()):
        if chave.startswith(f"{paciente_id}|"):
            del EXAMES_CADASTRADOS_MOCK[chave]

    # Remove resultados vinculados ao paciente
    if "RESULTADOS_EXAMES_MOCK" in globals():
        RESULTADOS_EXAMES_MOCK[:] = [
            r for r in RESULTADOS_EXAMES_MOCK
            if str(r.get("paciente_id")) != paciente_id
        ]

    # Ajusta paciente selecionado
    if PACIENTES_MOCK:
        atual = str(globals().get("PACIENTE_SELECIONADO_ID", ""))

        if atual == paciente_id or not atual:
            globals()["PACIENTE_SELECIONADO_ID"] = str(PACIENTES_MOCK[0]["id"])
    else:
        globals()["PACIENTE_SELECIONADO_ID"] = ""


def confirmar_exclusao_paciente(page, paciente, on_voltar=None):
    dialog = None

    def fechar(e):
        dialog.open = False
        page.update()

    def excluir(e):
        nome = paciente["nome"]

        excluir_paciente_e_vinculos(paciente)

        dialog.open = False

        snackbar = ft.SnackBar(
            content=ft.Text(
                f'Paciente "{nome}" excluído com todos os exames, resultados e vínculos.'
            ),
            bgcolor=COR_CRITICO,
        )

        page.overlay.append(snackbar)
        snackbar.open = True

        if on_voltar:
            on_voltar(e)

        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Excluir paciente"),
        content=ft.Text(
            f'Tem certeza que deseja excluir o paciente "{paciente["nome"]}"?\n\n'
            "Esta ação removerá o paciente da aplicação junto com todos os exames, "
            "resultados e registros vinculados.\n\n"
            "Esta operação não poderá ser desfeita."
        ),
        actions=[
            ft.TextButton(
                content="Cancelar",
                on_click=fechar,
            ),
            ft.FilledButton(
                content="Excluir definitivamente",
                icon=ft.Icons.DELETE_FOREVER,
                on_click=excluir,
                style=ft.ButtonStyle(
                    bgcolor=COR_CRITICO,
                    color="white",
                    shape=ft.RoundedRectangleBorder(radius=12),
                ),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()


def detalhe_paciente_view(paciente, on_voltar=None, on_excluir=None, on_novo_exame=None):
    status_color = cor_status(paciente["status"])

    resultados_paciente = [
        r for r in globals().get("RESULTADOS_EXAMES_MOCK", [])
        if str(r.get("paciente_id")) == str(paciente["id"])
    ]

    total_resultados = len(resultados_paciente)
    resultados_normais = len([r for r in resultados_paciente if str(r.get("status", "")).lower() == "normal"])
    resultados_alterados = len([
        r for r in resultados_paciente
        if str(r.get("status", "")).lower() in ["alto", "baixo", "crítico", "critico"]
    ])

    datas = sorted(
        set([r.get("data") for r in resultados_paciente if r.get("data")]),
        reverse=True,
    )

    ultimo_exame_real = data_iso_para_br(datas[0]) if datas else paciente["ultimo_exame"]

    linhas_exames = []

    for item in sorted(resultados_paciente, key=lambda x: x.get("data", ""), reverse=True):
        status_item = item.get("status", "Sem análise")
        status_item_color = cor_resultado_exame(status_item)

        linhas_exames.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(data_iso_para_br(item.get("data", "")))),
                    ft.DataCell(ft.Text(nome_exame_para_exibicao(item))),
                    ft.DataCell(ft.Text(f'{item.get("resultado", "")} {item.get("unidade", "")}')),
                    ft.DataCell(ft.Text(f'{item.get("referencia", "")} {item.get("unidade", "")}')),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                status_item.upper(),
                                size=10,
                                color="white",
                                weight=ft.FontWeight.BOLD,
                            ),
                            bgcolor=status_item_color,
                            border_radius=30,
                            padding=ft.Padding.symmetric(horizontal=10, vertical=5),
                        )
                    ),
                ]
            )
        )

    if not linhas_exames:
        historico_content = ft.Container(
            bgcolor="#F8FAFC",
            border_radius=16,
            padding=28,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Icon(
                        ft.Icons.BIOTECH_OUTLINED,
                        size=42,
                        color=COR_TEXTO_FRACO,
                    ),
                    ft.Text(
                        "Nenhum resultado lançado para este paciente ainda.",
                        size=14,
                        color=COR_TEXTO_FRACO,
                    ),
                    ft.Text(
                        "Use a tela Exames para lançar resultados vinculados ao paciente.",
                        size=12,
                        color=COR_TEXTO_FRACO,
                    ),
                ],
            ),
        )
    else:
        historico_content = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Data")),
                ft.DataColumn(ft.Text("Exame")),
                ft.DataColumn(ft.Text("Resultado")),
                ft.DataColumn(ft.Text("Referência")),
                ft.DataColumn(ft.Text("Status")),
            ],
            rows=linhas_exames,
            heading_row_color="#F8FAFC",
            border_radius=12,
        )

    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=18,
        expand=True,
        controls=[
            app_card(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            expand=True,
                            spacing=16,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.ARROW_BACK,
                                    tooltip="Voltar",
                                    on_click=on_voltar,
                                ),
                                ft.Container(
                                    width=56,
                                    height=56,
                                    border_radius=18,
                                    bgcolor="#EFF6FF",
                                    alignment=ft.Alignment.CENTER,
                                    content=ft.Text(
                                        paciente["nome"][:1].upper(),
                                        size=24,
                                        color=COR_PRIMARIA,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ),
                                ft.Container(
                                    expand=True,
                                    content=ft.Column(
                                        spacing=4,
                                        controls=[
                                            ft.Text(
                                                paciente["nome"],
                                                size=26,
                                                weight=ft.FontWeight.BOLD,
                                                color=COR_TEXTO,
                                                max_lines=1,
                                                overflow=ft.TextOverflow.ELLIPSIS,
                                            ),
                                            ft.Text(
                                                f'{paciente["idade"]} anos • {total_resultados} resultado(s) lançado(s) • Último exame: {ultimo_exame_real}',
                                                size=13,
                                                color=COR_TEXTO_FRACO,
                                                max_lines=1,
                                                overflow=ft.TextOverflow.ELLIPSIS,
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                        ft.Row(
                            spacing=12,
                            controls=[
                                ft.Container(
                                    content=ft.Text(
                                        paciente["status"],
                                        color="white",
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    bgcolor=status_color,
                                    border_radius=30,
                                    padding=ft.Padding.symmetric(horizontal=18, vertical=10),
                                ),
                                ft.FilledButton(
                                    content="Novo exame",
                                    icon=ft.Icons.ADD,
                                    on_click=on_novo_exame,
                                    style=ft.ButtonStyle(
                                        bgcolor=COR_PRIMARIA,
                                        color="white",
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                    ),
                                ),
                                ft.OutlinedButton(
                                    content="Excluir paciente",
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    on_click=lambda e: on_excluir(paciente) if on_excluir else None,
                                    style=ft.ButtonStyle(
                                        color=COR_CRITICO,
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
                padding=24,
            ),

            ft.ResponsiveRow(
                columns=12,
                spacing=16,
                run_spacing=16,
                controls=[
                    ft.Container(
                        col={"xs": 12, "sm": 6, "md": 3},
                        content=app_card(
                            ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text("Resultados lançados", size=13, color=COR_TEXTO_FRACO),
                                    ft.Text(str(total_resultados), size=28, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                                ],
                            ),
                            padding=18,
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "sm": 6, "md": 3},
                        content=app_card(
                            ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text("Normais", size=13, color=COR_TEXTO_FRACO),
                                    ft.Text(str(resultados_normais), size=28, weight=ft.FontWeight.BOLD, color=COR_NORMAL),
                                ],
                            ),
                            padding=18,
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "sm": 6, "md": 3},
                        content=app_card(
                            ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text("Alterados", size=13, color=COR_TEXTO_FRACO),
                                    ft.Text(str(resultados_alterados), size=28, weight=ft.FontWeight.BOLD, color=COR_ALERTA),
                                ],
                            ),
                            padding=18,
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "sm": 6, "md": 3},
                        content=app_card(
                            ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text("Arquivos vinculados", size=13, color=COR_TEXTO_FRACO),
                                    ft.Text("0", size=28, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                                ],
                            ),
                            padding=18,
                        ),
                    ),
                ],
            ),

            grafico_echarts(),

            app_card(
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(
                                    "Histórico de resultados",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=COR_TEXTO,
                                ),
                                ft.Text(
                                    "Dados lançados no protótipo",
                                    size=12,
                                    color=COR_TEXTO_FRACO,
                                ),
                            ],
                        ),
                        historico_content,
                    ],
                ),
                padding=20,
            ),
        ],
    )


# ============================================================
# RECUPERAÇÃO DAS TELAS EXAMES / REFERÊNCIAS
# ============================================================

CATALOGO_EXAMES = [
    {"id": "glicose", "nome": "Glicose", "grupo": "Metabolismo", "referencia": "70 - 99 mg/dL"},
    {"id": "colesterol_total", "nome": "Colesterol Total", "grupo": "Perfil Lipídico", "referencia": "< 190 mg/dL"},
    {"id": "hdl", "nome": "HDL", "grupo": "Perfil Lipídico", "referencia": "> 40 mg/dL"},
    {"id": "ldl", "nome": "LDL", "grupo": "Perfil Lipídico", "referencia": "< 130 mg/dL"},
    {"id": "triglicerideos", "nome": "Triglicerídeos", "grupo": "Perfil Lipídico", "referencia": "< 150 mg/dL"},
    {"id": "hemoglobina", "nome": "Hemoglobina", "grupo": "Hemograma", "referencia": "13.0 - 17.0 g/dL"},
    {"id": "hematocrito", "nome": "Hematócrito", "grupo": "Hemograma", "referencia": "40 - 52 %"},
    {"id": "leucocitos", "nome": "Leucócitos", "grupo": "Hemograma", "referencia": "4.000 - 11.000 /mm³"},
    {"id": "plaquetas", "nome": "Plaquetas", "grupo": "Hemograma", "referencia": "150.000 - 450.000 /mm³"},
    {"id": "creatinina", "nome": "Creatinina", "grupo": "Função Renal", "referencia": "0.7 - 1.3 mg/dL"},
    {"id": "ureia", "nome": "Ureia", "grupo": "Função Renal", "referencia": "10 - 50 mg/dL"},
    {"id": "tgo", "nome": "TGO / AST", "grupo": "Função Hepática", "referencia": "< 40 U/L"},
    {"id": "tgp", "nome": "TGP / ALT", "grupo": "Função Hepática", "referencia": "< 41 U/L"},
    {"id": "tsh", "nome": "TSH", "grupo": "Tireoide", "referencia": "0.4 - 4.0 µUI/mL"},
    {"id": "t4_livre", "nome": "T4 Livre", "grupo": "Tireoide", "referencia": "0.8 - 1.8 ng/dL"},
]

REFERENCIAS_MOCK = [
    {"id": "glicose", "nome": "Glicose", "grupo": "Metabolismo", "unidade": "mg/dL", "referencia": "70 - 99", "fonte": "Diretrizes da Sociedade Brasileira de Diabetes", "status": "Completa"},
    {"id": "colesterol_total", "nome": "Colesterol Total", "grupo": "Perfil Lipídico", "unidade": "mg/dL", "referencia": "< 190", "fonte": "Diretriz Brasileira de Dislipidemias e Prevenção da Aterosclerose", "status": "Completa"},
    {"id": "hdl", "nome": "HDL", "grupo": "Perfil Lipídico", "unidade": "mg/dL", "referencia": "> 40", "fonte": "Diretriz Brasileira de Dislipidemias e Prevenção da Aterosclerose", "status": "Completa"},
    {"id": "ldl", "nome": "LDL", "grupo": "Perfil Lipídico", "unidade": "mg/dL", "referencia": "< 130", "fonte": "Diretriz Brasileira de Dislipidemias e Prevenção da Aterosclerose", "status": "Completa"},
    {"id": "triglicerideos", "nome": "Triglicerídeos", "grupo": "Perfil Lipídico", "unidade": "mg/dL", "referencia": "< 150", "fonte": "Diretriz Brasileira de Dislipidemias e Prevenção da Aterosclerose", "status": "Completa"},
    {"id": "hemoglobina", "nome": "Hemoglobina", "grupo": "Hemograma", "unidade": "g/dL", "referencia": "13.0 - 17.0", "fonte": "Valores laboratoriais usuais para adultos", "status": "Completa"},
    {"id": "hematocrito", "nome": "Hematócrito", "grupo": "Hemograma", "unidade": "%", "referencia": "40 - 52", "fonte": "Valores laboratoriais usuais para adultos", "status": "Completa"},
    {"id": "leucocitos", "nome": "Leucócitos", "grupo": "Hemograma", "unidade": "/mm³", "referencia": "4.000 - 11.000", "fonte": "Valores laboratoriais usuais para adultos", "status": "Completa"},
    {"id": "plaquetas", "nome": "Plaquetas", "grupo": "Hemograma", "unidade": "/mm³", "referencia": "150.000 - 450.000", "fonte": "Valores laboratoriais usuais para adultos", "status": "Completa"},
    {"id": "creatinina", "nome": "Creatinina", "grupo": "Função Renal", "unidade": "mg/dL", "referencia": "0.7 - 1.3", "fonte": "KDIGO / valores laboratoriais usuais para adultos", "status": "Completa"},
    {"id": "ureia", "nome": "Ureia", "grupo": "Função Renal", "unidade": "mg/dL", "referencia": "10 - 50", "fonte": "Valores laboratoriais usuais para adultos", "status": "Completa"},
    {"id": "tgo", "nome": "TGO / AST", "grupo": "Função Hepática", "unidade": "U/L", "referencia": "< 40", "fonte": "Valores laboratoriais usuais para adultos", "status": "Completa"},
    {"id": "tgp", "nome": "TGP / ALT", "grupo": "Função Hepática", "unidade": "U/L", "referencia": "< 41", "fonte": "Valores laboratoriais usuais para adultos", "status": "Completa"},
    {"id": "tsh", "nome": "TSH", "grupo": "Tireoide", "unidade": "µUI/mL", "referencia": "0.4 - 4.0", "fonte": "Valores laboratoriais usuais para adultos", "status": "Completa"},
    {"id": "t4_livre", "nome": "T4 Livre", "grupo": "Tireoide", "unidade": "ng/dL", "referencia": "0.8 - 1.8", "fonte": "Valores laboratoriais usuais para adultos", "status": "Completa"},
]

EXAMES_CADASTRADOS_MOCK = {
    "1|2026-06-28": ["glicose", "colesterol_total", "triglicerideos", "hemoglobina"],
    "1|2026-06-12": ["glicose", "hdl", "ldl"],
    "2|2026-06-12": ["glicose", "colesterol_total"],
    "3|2026-05-30": ["creatinina", "ureia", "tgo", "tgp"],
}

if "RESULTADOS_EXAMES_MOCK" not in globals():
    RESULTADOS_EXAMES_MOCK = []


def data_br_para_iso(data_br):
    data_br = (data_br or "").strip()
    if "/" in data_br:
        partes = data_br.split("/")
        if len(partes) == 3:
            dia, mes, ano = partes
            return f"{ano}-{mes}-{dia}"
    return data_br


def data_iso_para_br(data_iso):
    data_iso = (data_iso or "").strip()
    if "-" in data_iso:
        partes = data_iso.split("-")
        if len(partes) == 3:
            ano, mes, dia = partes
            return f"{dia}/{mes}/{ano}"
    return data_iso


def chave_exames_paciente_data(paciente_id, data_exame):
    return f"{paciente_id}|{data_exame}"



# ===== PATCH: RESOLUÇÃO DE REFERÊNCIAS POR NOME E ALIAS =====
def _norm_ref_exame(valor):
    import unicodedata
    import re

    texto = str(valor or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    return " ".join(texto.split())


ALIASES_REFERENCIAS_EXAMES = {
    "hemoglobina glicosilada": [
        "hemoglobina glicada",
        "hemoglobina glicada a1c",
        "hemoglobina glicada a 1 c",
        "hba1c",
        "a1c",
    ],
    "hemoglobina glicada": [
        "hemoglobina glicosilada",
        "hemoglobina glicada a1c",
        "hba1c",
        "a1c",
    ],
    "ferro serico": [
        "ferro",
        "ferro soro",
        "ferro serico",
    ],
    "tgo": [
        "tgo ast",
        "transaminase glutamico oxalacetica",
        "aspartato amino transferase",
        "ast",
    ],
    "tgp": [
        "tgp alt",
        "transaminase glutamico piruvica",
        "alanina amino transferase",
        "alt",
    ],
    "t4 livre": [
        "tiroxina t4 livre",
        "tiroxina livre",
        "t4 livre",
    ],
    "tsh": [
        "hormonio tiroestimulante tsh",
        "hormonio tireoestimulante tsh",
        "tsh",
    ],
    "25oh d3": [
        "25 oh d3",
        "25oh vitamina d",
        "25 hidroxivitamina d",
        "vitamina d",
    ],
    "eas": [
        "e a s",
        "urina tipo i",
        "sumario de urina",
        "sumario urina",
        "elementos anormais e sedimento",
    ],
    "e a s": [
        "eas",
        "urina tipo i",
        "sumario de urina",
        "elementos anormais e sedimento",
    ],
    "hemacias": [
        "eritrocitos",
        "eritrocitos hemacias",
    ],
    "hemoglobina": [
        "hemoglobina",
    ],
    "hematocrito": [
        "hematocrito",
    ],
    "vcm": [
        "volume corpuscular medio",
        "vcm",
    ],
    "hcm": [
        "hemoglobina corpuscular media",
        "hcm",
    ],
    "chcm": [
        "concentracao de hemoglobina corpuscular media",
        "chcm",
    ],
    "rdw": [
        "coeficiente de variacao do volume eritrocitario rdw",
        "coeficiente de variacao do volume eritrocitario",
        "rdw",
    ],
    "leucocitos": [
        "leucocitos",
    ],
    "plaquetas": [
        "total de plaquetas",
        "plaquetas",
    ],
    "triglicerideos": [
        "triglicerides",
        "triglicerideos",
    ],
    "hdl": [
        "hdl colesterol",
        "hdl",
    ],
    "ldl": [
        "ldl colesterol",
        "ldl",
    ],
    "vldl": [
        "vldl colesterol",
        "vldl",
    ],
}


def _nomes_candidatos_referencia(nome):
    base = _norm_ref_exame(nome)
    candidatos = {base}

    for chave, aliases in ALIASES_REFERENCIAS_EXAMES.items():
        chave_norm = _norm_ref_exame(chave)

        if base == chave_norm:
            candidatos.update(_norm_ref_exame(alias) for alias in aliases)

        for alias in aliases:
            alias_norm = _norm_ref_exame(alias)
            if base == alias_norm:
                candidatos.add(chave_norm)
                candidatos.update(_norm_ref_exame(a) for a in aliases)

    return {c for c in candidatos if c}


def _nomes_ref_normalizados(ref):
    nomes = set()

    if not isinstance(ref, dict):
        return nomes

    for chave in ("nome", "nome_exame", "exame", "descricao", "id"):
        valor = ref.get(chave)
        if valor:
            nomes.add(_norm_ref_exame(valor))

    return {n for n in nomes if n}


def buscar_referencia_por_exame(exame):
    """
    Busca referência por:
    1. id exato;
    2. nome exato normalizado;
    3. aliases conhecidos;
    4. equivalência parcial segura para nomes longos.
    """
    if not isinstance(exame, dict):
        exame = {"id": str(exame), "nome": str(exame)}

    exame_id = str(exame.get("id") or "").strip()
    exame_nome = str(exame.get("nome") or exame.get("nome_exame") or exame.get("exame") or "").strip()

    # 1) ID exato
    if exame_id:
        for ref in REFERENCIAS_MOCK:
            if str(ref.get("id") or "").strip() == exame_id:
                return ref

    candidatos = _nomes_candidatos_referencia(exame_nome)

    # 2) Nome/alias exato normalizado
    for ref in REFERENCIAS_MOCK:
        nomes_ref = _nomes_ref_normalizados(ref)

        if candidatos.intersection(nomes_ref):
            return ref

    # 3) Parcial seguro apenas para nomes suficientemente longos
    for ref in REFERENCIAS_MOCK:
        nomes_ref = _nomes_ref_normalizados(ref)

        for candidato in candidatos:
            if len(candidato) < 8:
                continue

            for nome_ref in nomes_ref:
                if len(nome_ref) < 8:
                    continue

                if candidato in nome_ref or nome_ref in candidato:
                    return ref

    return None
# ===== FIM PATCH: RESOLUÇÃO DE REFERÊNCIAS POR NOME E ALIAS =====


def buscar_referencia_exame(exame_id):
    for ref in REFERENCIAS_MOCK:
        if ref["id"] == exame_id:
            return ref
    return None


def cor_status_referencia(status):
    status = (status or "").lower()
    if status == "completa":
        return COR_NORMAL
    if status in ["pendente", "incompleta"]:
        return COR_ALERTA
    return COR_CRITICO


def montar_detalhe_referencia_exame(exame):
    """
    Monta os detalhes de referência de um exame de forma segura.

    Corrige inconsistências entre:
    - catálogo de exames;
    - referências;
    - aliases;
    - exames adicionados manualmente sem unidade/fonte/status.

    Nunca acessa ref["unidade"] diretamente, para evitar KeyError.
    """
    if not isinstance(exame, dict):
        exame = {
            "id": str(exame),
            "nome": str(exame),
        }

    nome_exame = str(
        exame.get("nome")
        or exame.get("nome_exame")
        or exame.get("exame")
        or exame.get("id")
        or ""
    ).strip()

    grupo_exame = str(exame.get("grupo") or "Exames laboratoriais").strip()

    ref = None

    try:
        if "buscar_referencia_por_exame" in globals():
            ref = buscar_referencia_por_exame(exame)
    except Exception:
        ref = None

    if not ref:
        try:
            ref = buscar_referencia_exame(exame.get("id"))
        except Exception:
            ref = None

    if not ref and str(exame.get("referencia") or "").strip():
        ref = exame

    if not isinstance(ref, dict):
        return {
            "tem_referencia": False,
            "id": exame.get("id", ""),
            "nome": nome_exame,
            "grupo": grupo_exame,
            "unidade": str(exame.get("unidade") or "").strip(),
            "referencia": "",
            "fonte": "",
            "status": "Pendente",
        }

    unidade = str(
        ref.get("unidade")
        or exame.get("unidade")
        or ""
    ).strip()

    referencia = str(
        ref.get("referencia")
        or ref.get("referencia_texto")
        or exame.get("referencia")
        or exame.get("referencia_texto")
        or ""
    ).strip()

    fonte = str(
        ref.get("fonte")
        or ref.get("fonte_referencia")
        or exame.get("fonte")
        or exame.get("fonte_referencia")
        or "Valores laboratoriais usuais"
    ).strip()

    grupo = str(
        ref.get("grupo")
        or exame.get("grupo")
        or grupo_exame
        or "Exames laboratoriais"
    ).strip()

    status = str(
        ref.get("status")
        or exame.get("status")
        or ""
    ).strip()

    tem_referencia = bool(referencia)

    if not status:
        status = "Completa" if tem_referencia else "Pendente"

    return {
        "tem_referencia": tem_referencia,
        "id": ref.get("id") or exame.get("id", ""),
        "nome": ref.get("nome") or nome_exame,
        "grupo": grupo,
        "unidade": unidade,
        "referencia": referencia,
        "fonte": fonte,
        "status": status,
    }



def exames_ja_cadastrados_por_data(paciente_id, data_exame):
    chave = chave_exames_paciente_data(paciente_id, data_exame)
    ids = EXAMES_CADASTRADOS_MOCK.get(chave, [])
    return [exame for exame in CATALOGO_EXAMES if exame["id"] in ids]



# ===== PATCH: GRUPOS PRIORITÁRIOS DE EXAMES =====
def criar_opcoes_grupos_exames(lista_exames):
    """
    Cria opções de grupos para Dropdown Flet.
    """
    return [
        ft.dropdown.Option(key=grupo, text=grupo)
        for grupo in listar_grupos_disponiveis(lista_exames)
    ]


def criar_opcoes_exames_por_grupo(lista_exames, grupo=None, exames_ja_cadastrados=None):
    """
    Cria opções de exames ordenadas por prioridade e filtradas por grupo.
    """
    exames = ordenar_exames_por_prioridade(
        lista_exames,
        grupo=grupo,
        exames_ja_cadastrados=exames_ja_cadastrados,
    )

    return [
        ft.dropdown.Option(key=exame, text=exame)
        for exame in exames
    ]
# ===== FIM PATCH: GRUPOS PRIORITÁRIOS DE EXAMES =====

CATALOGO_EXAMES = garantir_prioritarios_no_catalogo(CATALOGO_EXAMES)

def exames_disponiveis_por_data(paciente_id, data_exame):
    chave = chave_exames_paciente_data(paciente_id, data_exame)
    ids = set(EXAMES_CADASTRADOS_MOCK.get(chave, []))
    return ordenar_itens_exames_por_prioridade([exame for exame in CATALOGO_EXAMES if exame["id"] not in ids])
def numero_br_para_float(valor):
    try:
        return float(str(valor).replace(",", ".").strip())
    except Exception:
        return None


def analisar_resultado_por_referencia(valor, referencia):
    valor_num = numero_br_para_float(valor)
    if valor_num is None or not referencia:
        return "Sem análise"

    ref = str(referencia).replace(",", ".").strip()

    try:
        if " - " in ref:
            minimo, maximo = ref.split(" - ")
            minimo = float(minimo.strip())
            maximo = float(maximo.strip())
            if valor_num < minimo:
                return "Baixo"
            if valor_num > maximo:
                return "Alto"
            return "Normal"

        if ref.startswith("<"):
            limite = float(ref.replace("<", "").strip())
            return "Normal" if valor_num < limite else "Alto"

        if ref.startswith(">"):
            limite = float(ref.replace(">", "").strip())
            return "Normal" if valor_num > limite else "Baixo"

    except Exception:
        return "Sem análise"

    return "Sem análise"


def cor_resultado_exame(status):
    status = (status or "").lower()
    if status == "normal":
        return COR_NORMAL
    if status in ["alto", "baixo"]:
        return COR_ALERTA
    if status in ["crítico", "critico"]:
        return COR_CRITICO
    return COR_TEXTO_FRACO


def nome_paciente_por_id(paciente_id):
    for paciente in PACIENTES_MOCK:
        if str(paciente["id"]) == str(paciente_id):
            return paciente["nome"]
    return "Paciente não identificado"


def mostrar_snackbar(page, mensagem, cor=COR_PRIMARIA):
    snackbar = ft.SnackBar(content=ft.Text(mensagem), bgcolor=cor)
    page.overlay.append(snackbar)
    snackbar.open = True
    page.update()


def resultados_por_paciente_data(paciente_id, data_iso):
    return [
        r for r in RESULTADOS_EXAMES_MOCK
        if str(r["paciente_id"]) == str(paciente_id)
        and r["data"] == data_iso
    ]


def historico_resultados_card(paciente_id, data_iso):
    resultados = resultados_por_paciente_data(paciente_id, data_iso)

    if not resultados:
        return ft.Container(
            bgcolor="#F8FAFC",
            border_radius=16,
            padding=24,
            alignment=ft.Alignment.CENTER,
            content=ft.Text(
                "Nenhum resultado lançado para este paciente nesta data.",
                size=13,
                color=COR_TEXTO_FRACO,
            ),
        )

    linhas = []
    for item in resultados:
        status_color = cor_resultado_exame(item["status"])
        linhas.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(item["exame_nome"])),
                    ft.DataCell(ft.Text(f'{item["resultado"]} {item["unidade"]}')),
                    ft.DataCell(ft.Text(f'{item["referencia"]} {item["unidade"]}')),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                item["status"].upper(),
                                size=10,
                                color="white",
                                weight=ft.FontWeight.BOLD,
                            ),
                            bgcolor=status_color,
                            border_radius=30,
                            padding=ft.Padding.symmetric(horizontal=10, vertical=5),
                        )
                    ),
                ]
            )
        )

    return ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Exame")),
            ft.DataColumn(ft.Text("Resultado")),
            ft.DataColumn(ft.Text("Referência")),
            ft.DataColumn(ft.Text("Status")),
        ],
        rows=linhas,
        heading_row_color="#F8FAFC",
        border_radius=12,
    )



UNIDADES_EXAMES = [
    "mg/dL",
    "g/dL",
    "%",
    "/mm³",
    "U/L",
    "µUI/mL",
    "ng/dL",
    "pg/mL",
    "mEq/L",
    "mmol/L",
    "UI/L",
    "µg/dL",
    "ng/mL",
    "mg/L",
]


def normalizar_unidade_padrao(unidade):
    unidade = (unidade or "").strip()

    if unidade in UNIDADES_EXAMES:
        return unidade

    if unidade:
        UNIDADES_EXAMES.append(unidade)
        return unidade

    return "mg/dL"


def exame_disponivel_card(page, exame, data_exame_control, paciente_control, atualizar_callback=None):
    detalhe_ref = montar_detalhe_referencia_exame(exame)
    status_ref_color = cor_status_referencia(detalhe_ref["status"])

    def abrir_popup_cadastro(e):
        data_br = valor_controle(data_exame_control).strip()
        data_exame = data_br_para_iso(data_br)
        paciente_id = paciente_control.value
        detalhe_ref_popup = montar_detalhe_referencia_exame(exame)

        if not paciente_id:
            mostrar_snackbar(page, "Selecione um paciente antes de cadastrar.", COR_ALERTA)
            return

        if not data_br:
            mostrar_snackbar(page, "Informe a data do exame antes de cadastrar.", COR_ALERTA)
            return

        if not detalhe_ref_popup["tem_referencia"]:
            mostrar_snackbar(page, f'O exame "{exame["nome"]}" ainda não possui referência completa.', COR_CRITICO)
            return

        chave = chave_exames_paciente_data(paciente_id, data_exame)

        if exame["id"] in EXAMES_CADASTRADOS_MOCK.get(chave, []):
            mostrar_snackbar(page, f'O exame "{exame["nome"]}" já está cadastrado nesta data.', COR_ALERTA)
            return

        resultado = ft.TextField(label="Resultado", width=180, border_radius=12)
        unidade_padrao = normalizar_unidade_padrao(detalhe_ref_popup["unidade"])

        unidade = ft.Dropdown(
            label="Unidade",
            value=unidade_padrao,
            width=180,
            border_radius=12,
            options=[
                ft.dropdown.Option(key=u, text=u)
                for u in UNIDADES_EXAMES
            ],
        )

        observacao = ft.TextField(label="Observação", multiline=True, min_lines=2, max_lines=3, border_radius=12)

        dialog = None

        def fechar(ev):
            dialog.open = False
            page.update()

        def salvar(ev):
            valor = resultado.value.strip() if resultado.value else ""

            if not valor:
                mostrar_snackbar(page, "Informe o resultado do exame.", COR_ALERTA)
                return

            item_resultado = {
                "paciente_id": paciente_id,
                "paciente_nome": nome_paciente_por_id(paciente_id),
                "data": data_exame,
                "data_exame": data_exame,
                "exame_id": exame["id"],
                "nome_exame": exame["nome"],
                "nome": exame["nome"],
                "exame": exame["nome"],
                "exame_nome": exame["nome"],
                "grupo": detalhe_ref_popup["grupo"],
                "resultado": valor,
                "unidade": unidade.value,
                "referencia": detalhe_ref_popup["referencia"],
                "referencia_texto": detalhe_ref_popup["referencia"],
                "fonte": detalhe_ref_popup["fonte"],
                "fonte_referencia": detalhe_ref_popup["fonte"],
                "observacao": observacao.value or "",
                "observacoes": observacao.value or "",
            }

            persistiu = salvar_resultado_exame_csv_definitivo(item_resultado)

            if not persistiu:
                mostrar_snackbar(
                    page,
                    f'Não foi possível salvar o exame "{exame["nome"]}" nos arquivos CSV.',
                    COR_CRITICO,
                )
                return

            status_resultado = item_resultado.get("status") or analisar_resultado_por_referencia(
                valor,
                detalhe_ref_popup["referencia"],
            )

            if chave not in EXAMES_CADASTRADOS_MOCK:
                EXAMES_CADASTRADOS_MOCK[chave] = []

            if exame["id"] not in EXAMES_CADASTRADOS_MOCK[chave]:
                EXAMES_CADASTRADOS_MOCK[chave].append(exame["id"])

            # Mantém a memória visual atualizada, mas não depende mais do append para gravar no CSV.
            try:
                ja_memoria = False
                for r in list(RESULTADOS_EXAMES_MOCK):
                    mesmo_paciente = str(r.get("paciente_id", "")).zfill(4) == str(paciente_id).zfill(4)
                    mesmo_exame = str(r.get("nome_exame") or r.get("exame_nome") or r.get("nome") or "") == exame["nome"]
                    mesmo_data = str(r.get("data_exame") or r.get("data") or "") == data_exame
                    mesmo_resultado = str(r.get("resultado") or "") == str(valor)
                    if mesmo_paciente and mesmo_exame and mesmo_data and mesmo_resultado:
                        ja_memoria = True
                        break

                if not ja_memoria:
                    list.append(RESULTADOS_EXAMES_MOCK, item_resultado)
            except Exception as exc:
                print(f"[SALVAR EXAME DEFINITIVO] Exame salvo, mas falhou atualização da memória: {exc}")

            try:
                sincronizar_resultados_exames_mock_data_flet()
                atualizar_pacientes_csv_real_definitivo()
            except Exception as exc:
                print(f"[SALVAR EXAME DEFINITIVO] Exame salvo, mas falhou atualização pós-salvamento: {exc}")

            dialog.open = False
            mostrar_snackbar(
                page,
                f'"{exame["nome"]}" salvo como {status_resultado}.',
                cor_resultado_exame(status_resultado),
            )

            if atualizar_callback:
                atualizar_callback()

            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f'Lançar resultado - {exame["nome"]}'),
            content=ft.Container(
                width=560,
                content=ft.Column(
                    tight=True,
                    spacing=14,
                    controls=[
                        ft.Container(
                            bgcolor="#F8FAFC",
                            border_radius=16,
                            padding=16,
                            content=ft.Column(
                                spacing=7,
                                controls=[
                                    ft.Text(detalhe_ref_popup["grupo"], size=12, color=COR_TEXTO_FRACO),
                                    ft.Text(exame["nome"], size=20, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                                    ft.Text(f'Referência: {detalhe_ref_popup["referencia"]} {detalhe_ref_popup["unidade"]}', size=13, color=COR_TEXTO, weight=ft.FontWeight.BOLD),
                                    ft.Text(f'Fonte: {detalhe_ref_popup["fonte"]}', size=12, color=COR_TEXTO_FRACO),
                                    ft.Text(f'Data do exame: {data_iso_para_br(data_exame)}', size=13, color=COR_TEXTO_FRACO),
                                ],
                            ),
                        ),
                        ft.Row(spacing=12, controls=[resultado, unidade]),
                        observacao,
                    ],
                ),
            ),
            actions=[
                ft.TextButton(content="Cancelar", on_click=fechar),
                ft.FilledButton(
                    content="Salvar exame",
                    icon=ft.Icons.SAVE,
                    on_click=salvar,
                    style=ft.ButtonStyle(
                        bgcolor=COR_PRIMARIA,
                        color="white",
                        shape=ft.RoundedRectangleBorder(radius=12),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    texto_referencia = (
        f'{detalhe_ref["grupo"]} • Ref.: {detalhe_ref["referencia"]} {detalhe_ref["unidade"]}'
        if detalhe_ref["tem_referencia"]
        else "Referência pendente no catálogo"
    )

    texto_fonte = (
        f'Fonte: {detalhe_ref["fonte"]}'
        if detalhe_ref["tem_referencia"]
        else "Cadastre a referência antes de lançar o resultado"
    )

    return app_card(
        ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=14,
            controls=[
                ft.Row(
                    expand=True,
                    spacing=14,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=44,
                            height=44,
                            border_radius=14,
                            bgcolor="#EFF6FF" if detalhe_ref["tem_referencia"] else "#FEF2F2",
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(ft.Icons.BIOTECH, color=COR_PRIMARIA if detalhe_ref["tem_referencia"] else COR_CRITICO, size=24),
                        ),
                        ft.Container(
                            expand=True,
                            content=ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text(exame["nome"], size=16, weight=ft.FontWeight.BOLD, color=COR_TEXTO, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                    ft.Text(texto_referencia, size=12, color=COR_TEXTO_FRACO, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                    ft.Text(texto_fonte, size=11, color=COR_TEXTO_FRACO, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                ],
                            ),
                        ),
                    ],
                ),
                ft.Container(
                    width=265,
                    content=ft.Row(
                        spacing=10,
                        alignment=ft.MainAxisAlignment.END,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                content=ft.Text(detalhe_ref["status"].upper(), size=10, color="white", weight=ft.FontWeight.BOLD),
                                bgcolor=status_ref_color,
                                border_radius=30,
                                padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                            ),
                            ft.FilledButton(
                                width=175,
                                content="Lançar",
                                icon=ft.Icons.ADD,
                                on_click=abrir_popup_cadastro,
                                style=ft.ButtonStyle(
                                    bgcolor=COR_PRIMARIA if detalhe_ref["tem_referencia"] else COR_TEXTO_FRACO,
                                    color="white",
                                    shape=ft.RoundedRectangleBorder(radius=12),
                                ),
                            ),
                        ],
                    ),
                ),
            ],
        ),
        padding=16,
    )



def grupo_exames_card(page, nome_grupo, exames, data_exame_control, paciente_control, atualizar_callback=None):
    """
    Card macro de grupo de exames.

    O grupo aparece como card principal e os exames individuais aparecem
    como cards menores internos, mantendo o botão Lançar em cada exame.
    """
    exames = list(exames or [])

    if not exames:
        return ft.Container()

    return ft.Container(
        bgcolor="#F8FAFC",
        border_radius=22,
        padding=16,
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    width=40,
                                    height=40,
                                    border_radius=14,
                                    bgcolor="#DBEAFE",
                                    alignment=ft.Alignment.CENTER,
                                    content=ft.Icon(
                                        ft.Icons.FOLDER_SPECIAL_OUTLINED,
                                        color=COR_PRIMARIA,
                                        size=23,
                                    ),
                                ),
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(
                                            nome_grupo,
                                            size=18,
                                            weight=ft.FontWeight.BOLD,
                                            color=COR_TEXTO,
                                        ),
                                        ft.Text(
                                            "Grupo de exames — lance apenas os exames individuais abaixo",
                                            size=12,
                                            color=COR_TEXTO_FRACO,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        ft.Container(
                            bgcolor="#EFF6FF",
                            border_radius=30,
                            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                            content=ft.Text(
                                f"{len(exames)} exame(s)",
                                size=11,
                                color=COR_PRIMARIA,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ),
                    ],
                ),
                ft.Column(
                    spacing=10,
                    controls=[
                        exame_disponivel_card(
                            page,
                            exame,
                            data_exame_control,
                            paciente_control,
                            atualizar_callback=atualizar_callback,
                        )
                        for exame in exames
                    ],
                ),
            ],
        ),
    )



def exame_bloqueado_card(exame):
    detalhe_ref = montar_detalhe_referencia_exame(exame)

    referencia_texto = (
        f'{detalhe_ref["grupo"]} • Ref.: {detalhe_ref["referencia"]} {detalhe_ref["unidade"]}'
        if detalhe_ref["tem_referencia"]
        else "Referência pendente"
    )

    return ft.Container(
        bgcolor="#F8FAFC",
        border_radius=16,
        padding=14,
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=42,
                            height=42,
                            border_radius=14,
                            bgcolor="#E5E7EB",
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(ft.Icons.CHECK_CIRCLE, color=COR_NORMAL, size=23),
                        ),
                        ft.Container(
                            expand=True,
                            content=ft.Column(
                                spacing=3,
                                controls=[
                                    ft.Text(exame["nome"], size=15, weight=ft.FontWeight.BOLD, color=COR_TEXTO, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                    ft.Text(referencia_texto, size=12, color=COR_TEXTO_FRACO, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                    ft.Text(f'Fonte: {detalhe_ref["fonte"]}', size=11, color=COR_TEXTO_FRACO, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                ],
                            ),
                        ),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    controls=[
                        ft.Container(
                            content=ft.Text("JÁ CADASTRADO", size=10, color="white", weight=ft.FontWeight.BOLD),
                            bgcolor=COR_TEXTO_FRACO,
                            border_radius=30,
                            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                        ),
                    ],
                ),
            ],
        ),
    )













# ============================================================
# IMPORTAÇÃO GRÁFICA DE PDF DE LABORATÓRIO COM PRÉVIA
# SEM FILEPICKER - COMPATÍVEL COM FLET DO UBUNTU
# ============================================================

def _cor_importacao_pdf(nome, padrao):
    return globals().get(nome, padrao)


def _slug_arquivo_importacao_pdf(nome):
    nome = str(nome or "arquivo.pdf")
    nome = re.sub(r"[^A-Za-z0-9_.-]+", "_", nome).strip("_")
    return nome or "arquivo.pdf"


def _pasta_carga_pdf():
    pasta = Path(__file__).resolve().parent / "importacoes" / "carga_pdf"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def _limpar_repositorio_carga_pdf(exceto=None):
    pasta = _pasta_carga_pdf()
    exceto = Path(exceto).resolve() if exceto else None

    for arquivo in pasta.glob("*.pdf"):
        try:
            if exceto and arquivo.resolve() == exceto:
                continue
            arquivo.unlink()
        except Exception:
            pass

    return pasta


def _selecionar_pdf_dialogo_nativo():
    """
    Usa seletor nativo do Linux sem depender do FilePicker do Flet.
    Primeiro tenta zenity; depois tenta tkinter.
    """
    # 1) Zenity: costuma funcionar bem no Ubuntu/GNOME.
    try:
        proc = subprocess.run(
            [
                "zenity",
                "--file-selection",
                "--title=Selecione o laudo PDF",
                "--file-filter=Arquivos PDF | *.pdf",
            ],
            capture_output=True,
            text=True,
        )

        if proc.returncode == 0:
            caminho = (proc.stdout or "").strip()
            if caminho:
                return caminho
    except FileNotFoundError:
        pass
    except Exception as exc:
        print(f"[IMPORTAÇÃO PDF] Zenity indisponível: {exc}")

    # 2) Tkinter: fallback.
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        caminho = filedialog.askopenfilename(
            title="Selecione o laudo PDF",
            filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")],
        )

        root.destroy()

        if caminho:
            return caminho
    except Exception as exc:
        print(f"[IMPORTAÇÃO PDF] Tkinter indisponível: {exc}")

    return ""


def _extrair_qtd_resultados_importador(saida):
    m = re.search(r"Resultados encontrados:\s*(\d+)", str(saida or ""))
    if not m:
        return 0

    try:
        return int(m.group(1))
    except Exception:
        return 0


def _executar_importador_pdf(caminho_pdf, paciente_id="", dry_run=True):
    script = Path(__file__).resolve().parent / "scripts" / "importar_fleury_pdf.py"

    if not script.exists():
        raise FileNotFoundError(f"Script importador não encontrado: {script}")

    cmd = [
        sys.executable,
        str(script),
        str(caminho_pdf),
    ]

    if paciente_id:
        cmd.extend(["--paciente-id", str(paciente_id)])

    if dry_run:
        cmd.append("--dry-run")

    proc = subprocess.run(
        cmd,
        cwd=str(Path(__file__).resolve().parent),
        capture_output=True,
        text=True,
    )

    saida = (proc.stdout or "").strip()
    erro = (proc.stderr or "").strip()

    return proc.returncode, saida, erro


def card_importacao_pdf_exames(page):
    estado = {
        "pdf_temp": None,
        "saida_previa": "",
        "qtd_resultados": 0,
    }

    status_text = ft.Text(
        "Carregue um laudo PDF para gerar uma prévia antes de salvar.",
        size=13,
        color=_cor_importacao_pdf("COR_TEXTO_FRACO", "#64748B"),
    )

    resultado_text = ft.Text(
        "",
        size=12,
        selectable=True,
        color=_cor_importacao_pdf("COR_TEXTO", "#111827"),
    )

    progresso = ft.ProgressRing(width=22, height=22, visible=False)

    try:
        paciente_control = paciente_dropdown_padrao()
    except Exception:
        opcoes = []
        for p in globals().get("PACIENTES_MOCK", []):
            pid = str(p.get("id") or p.get("paciente_id") or "")
            nome = str(p.get("nome") or "")
            if pid and nome:
                opcoes.append(ft.dropdown.Option(key=pid, text=nome))

        paciente_control = ft.Dropdown(
            label="Paciente",
            width=320,
            options=opcoes,
        )

    vincular_paciente = ft.Checkbox(
        label="Forçar vínculo com o paciente selecionado",
        value=False,
    )

    confirmar_btn = ft.FilledButton(
        content=ft.Text("Confirmar importação", color="white"),
        visible=False,
        style=ft.ButtonStyle(
            bgcolor=_cor_importacao_pdf("COR_NORMAL", "#16A34A"),
            color="white",
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )

    cancelar_btn = ft.OutlinedButton(
        content=ft.Text("Cancelar carga"),
        visible=False,
    )

    def mostrar_snack(mensagem, cor=None):
        if "mostrar_snackbar" in globals():
            try:
                mostrar_snackbar(page, mensagem, cor or _cor_importacao_pdf("COR_NORMAL", "#16A34A"))
                return
            except Exception:
                pass

        print(mensagem)

    def atualizar_estado_interface():
        try:
            page.update()
        except Exception:
            pass

    def limpar_estado(mensagem="Carga cancelada. O diretório temporário foi limpo."):
        pdf_temp = estado.get("pdf_temp")

        if pdf_temp:
            try:
                Path(pdf_temp).unlink()
            except Exception:
                pass

        _limpar_repositorio_carga_pdf()

        estado["pdf_temp"] = None
        estado["saida_previa"] = ""
        estado["qtd_resultados"] = 0

        confirmar_btn.visible = False
        cancelar_btn.visible = False
        progresso.visible = False
        status_text.value = mensagem
        resultado_text.value = ""

        atualizar_estado_interface()

    def gerar_previa_pdf(caminho_origem):
        if not caminho_origem:
            limpar_estado("Nenhum PDF selecionado.")
            return

        origem = Path(caminho_origem)

        if not origem.exists():
            limpar_estado(f"PDF não encontrado: {origem}")
            return

        if origem.suffix.lower() != ".pdf":
            limpar_estado("O arquivo selecionado não é PDF.")
            return

        _limpar_repositorio_carga_pdf()

        pasta = _pasta_carga_pdf()
        destino = pasta / f"carga_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{_slug_arquivo_importacao_pdf(origem.name)}"

        progresso.visible = True
        confirmar_btn.visible = False
        cancelar_btn.visible = False
        resultado_text.value = ""
        status_text.value = "Lendo PDF e gerando prévia. Nenhum dado será salvo ainda..."
        atualizar_estado_interface()

        try:
            shutil.copy2(origem, destino)

            paciente_id = ""
            if vincular_paciente.value and paciente_control.value:
                paciente_id = str(paciente_control.value)

            codigo, saida, erro = _executar_importador_pdf(destino, paciente_id=paciente_id, dry_run=True)

            estado["pdf_temp"] = str(destino)
            estado["saida_previa"] = saida
            estado["qtd_resultados"] = _extrair_qtd_resultados_importador(saida)

            progresso.visible = False
            cancelar_btn.visible = True

            if codigo != 0:
                confirmar_btn.visible = False
                resultado_text.value = (saida + "\n" + erro).strip()
                status_text.value = "Não foi possível gerar uma prévia confiável para este PDF."
                mostrar_snack("Prévia não gerada. Verifique o detalhe na tela.", _cor_importacao_pdf("COR_CRITICO", "#DC2626"))
                atualizar_estado_interface()
                return

            resultado_text.value = saida[-5000:] if saida else "Prévia gerada."

            if estado["qtd_resultados"] > 0:
                confirmar_btn.visible = True
                status_text.value = f"Prévia gerada com {estado['qtd_resultados']} exames encontrados. Revise e confirme para salvar."
                mostrar_snack("Prévia gerada. Revise antes de confirmar.", _cor_importacao_pdf("COR_NORMAL", "#16A34A"))
            else:
                confirmar_btn.visible = False
                status_text.value = "Prévia gerada, mas nenhum exame foi identificado. Não será possível confirmar esta carga."
                mostrar_snack("Nenhum exame identificado no PDF.", _cor_importacao_pdf("COR_ALERTA", "#F59E0B"))

            atualizar_estado_interface()

        except Exception as exc:
            progresso.visible = False
            confirmar_btn.visible = False
            cancelar_btn.visible = True
            resultado_text.value = str(exc)
            status_text.value = f"Erro ao gerar prévia: {exc}"
            mostrar_snack(f"Erro ao gerar prévia: {exc}", _cor_importacao_pdf("COR_CRITICO", "#DC2626"))
            atualizar_estado_interface()

    def selecionar_pdf(e):
        caminho = _selecionar_pdf_dialogo_nativo()

        if not caminho:
            mostrar_snack("Seleção cancelada ou seletor de arquivos indisponível.", _cor_importacao_pdf("COR_ALERTA", "#F59E0B"))
            return

        gerar_previa_pdf(caminho)

    def confirmar_importacao(e):
        pdf_temp = estado.get("pdf_temp")

        if not pdf_temp or not Path(pdf_temp).exists():
            mostrar_snack("Nenhum PDF carregado para confirmar.", _cor_importacao_pdf("COR_ALERTA", "#F59E0B"))
            return

        if estado.get("qtd_resultados", 0) <= 0:
            mostrar_snack("Não há exames identificados para importar.", _cor_importacao_pdf("COR_ALERTA", "#F59E0B"))
            return

        progresso.visible = True
        confirmar_btn.visible = False
        cancelar_btn.visible = False
        status_text.value = "Confirmando importação e salvando no banco..."
        atualizar_estado_interface()

        try:
            paciente_id = ""
            if vincular_paciente.value and paciente_control.value:
                paciente_id = str(paciente_control.value)

            codigo, saida, erro = _executar_importador_pdf(pdf_temp, paciente_id=paciente_id, dry_run=False)

            progresso.visible = False

            if codigo != 0:
                resultado_text.value = (saida + "\n" + erro).strip()
                status_text.value = "Falha ao confirmar importação. O PDF temporário foi removido."
                mostrar_snack("Falha ao confirmar importação.", _cor_importacao_pdf("COR_CRITICO", "#DC2626"))
                return

            resultado_text.value = saida[-5000:] if saida else "Importação concluída."
            status_text.value = "Importação confirmada. Dados salvos e diretório temporário limpo."
            mostrar_snack("Importação confirmada com sucesso.", _cor_importacao_pdf("COR_NORMAL", "#16A34A"))

            if "atualizar_pacientes_csv_real_definitivo" in globals():
                try:
                    atualizar_pacientes_csv_real_definitivo()
                except Exception as exc:
                    print(f"[IMPORTAÇÃO PDF] Falha ao atualizar pacientes: {exc}")

            if "carregar_exames_data_flet_para_memoria" in globals():
                try:
                    carregar_exames_data_flet_para_memoria()
                except Exception as exc:
                    print(f"[IMPORTAÇÃO PDF] Falha ao recarregar exames: {exc}")

        except Exception as exc:
            progresso.visible = False
            resultado_text.value = str(exc)
            status_text.value = f"Erro ao confirmar importação: {exc}"
            mostrar_snack(f"Erro ao confirmar importação: {exc}", _cor_importacao_pdf("COR_CRITICO", "#DC2626"))

        finally:
            pdf_temp_final = estado.get("pdf_temp")
            if pdf_temp_final:
                try:
                    Path(pdf_temp_final).unlink()
                except Exception:
                    pass

            _limpar_repositorio_carga_pdf()

            estado["pdf_temp"] = None
            estado["saida_previa"] = ""
            estado["qtd_resultados"] = 0

            confirmar_btn.visible = False
            cancelar_btn.visible = False
            progresso.visible = False
            status_text.value = "Importação finalizada. O diretório temporário está limpo."
            atualizar_estado_interface()

    def cancelar_importacao(e):
        limpar_estado()

    confirmar_btn.on_click = confirmar_importacao
    cancelar_btn.on_click = cancelar_importacao

    return app_card(
        ft.Column(
            spacing=14,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text(
                                    "Importar PDF de laboratório",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=_cor_importacao_pdf("COR_TEXTO", "#111827"),
                                ),
                                status_text,
                            ],
                        ),
                        ft.Row(
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                progresso,
                                ft.FilledButton(
                                    content=ft.Text("Carregar PDF", color="white"),
                                    on_click=selecionar_pdf,
                                    style=ft.ButtonStyle(
                                        bgcolor=_cor_importacao_pdf("COR_PRIMARIA", "#2563EB"),
                                        color="white",
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Container(
                    bgcolor="#F8FAFC",
                    border_radius=12,
                    padding=12,
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Text(
                                "Vínculo do paciente",
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color=_cor_importacao_pdf("COR_TEXTO", "#111827"),
                            ),
                            ft.Text(
                                "O sistema tenta identificar o paciente pelo nome no PDF. Marque a opção abaixo somente se quiser forçar o vínculo com o paciente selecionado.",
                                size=12,
                                color=_cor_importacao_pdf("COR_TEXTO_FRACO", "#64748B"),
                            ),
                            ft.Row(
                                spacing=12,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    paciente_control,
                                    vincular_paciente,
                                ],
                            ),
                        ],
                    ),
                ),
                ft.Container(
                    bgcolor="#FFFFFF",
                    border_radius=12,
                    padding=12,
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Text(
                                "Prévia da leitura",
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color=_cor_importacao_pdf("COR_TEXTO", "#111827"),
                            ),
                            resultado_text,
                            ft.Row(
                                spacing=10,
                                controls=[
                                    confirmar_btn,
                                    cancelar_btn,
                                ],
                            ),
                        ],
                    ),
                ),
            ],
        ),
        padding=20,
    )


def exames_view(page):
    data_exame = ft.TextField(
        label="Data do exame",
        value=data_hoje_br(),
        width=180,
        border_radius=12,
    )

    paciente_nome = ft.Dropdown(
        label="Paciente",
        value=str(globals().get("PACIENTE_SELECIONADO_ID", "1")),
        width=320,
        border_radius=12,
        options=[
            ft.dropdown.Option(
                key=str(paciente["id"]),
                text=f'{paciente["nome"]} - {paciente["idade"]} anos',
            )
            for paciente in PACIENTES_MOCK
        ],
    )

    lista_disponiveis = ft.Column(spacing=12)
    lista_bloqueados = ft.Column(spacing=10)
    historico_resultados_area = ft.Column(spacing=12)

    resumo_texto = ft.Text("", size=13, color=COR_TEXTO_FRACO)

    # ===== PATCH BUSCA INTELIGENTE NA TELA DE EXAMES =====

    busca_exame = ft.TextField(
        label="Busca inteligente de exame",
        hint_text="Digite: glicose, hba1c, colesterol, triglicerídeos, creatinina, vitamina D...",
        border_radius=12,
        expand=True,
    )

    busca_resultados_area = ft.Column(spacing=10)

    def _busca_norm(valor):
        try:
            return _patch_norm(valor)
        except Exception:
            import unicodedata
            texto = str(valor or "").strip().lower()
            texto = unicodedata.normalize("NFKD", texto)
            texto = "".join(c for c in texto if not unicodedata.combining(c))
            texto = re.sub(r"[^a-z0-9%/., ]+", " ", texto)
            return " ".join(texto.split())

    def _busca_nome_exame(item):
        if not isinstance(item, dict):
            return str(item or "")

        try:
            return nome_exame_para_exibicao(item)
        except Exception:
            return str(
                item.get("nome_exame")
                or item.get("nome")
                or item.get("exame")
                or item.get("descricao")
                or item.get("id")
                or ""
            ).strip()

    def _busca_termos_exame(item):
        nome = _busca_nome_exame(item)
        grupo = ""
        ref = ""
        fonte = ""
        item_id = ""

        if isinstance(item, dict):
            grupo = str(item.get("grupo") or "")
            ref = str(item.get("referencia") or item.get("referencia_texto") or "")
            fonte = str(item.get("fonte") or item.get("fonte_referencia") or "")
            item_id = str(item.get("id") or item.get("id_canonico") or "")

        termos = {
            nome,
            grupo,
            ref,
            fonte,
            item_id,
        }

        # Aliases úteis para busca rápida.
        aliases = {
            "hba1c": ["hemoglobina glicada"],
            "glicada": ["hemoglobina glicada"],
            "glico": ["glicose", "hemoglobina glicada", "glicemia media estimada"],
            "glicemia": ["glicose", "glicemia media estimada"],
            "glucose": ["glicose"],
            "colest": ["colesterol total", "hdl", "ldl", "vldl"],
            "colesterol": ["colesterol total", "hdl", "ldl", "vldl"],
            "trig": ["triglicerideos", "triglicerides"],
            "creat": ["creatinina", "tfg"],
            "renal": ["creatinina", "ureia", "tfg", "acido urico"],
            "figado": ["tgo", "tgp", "gama gt", "fosfatase alcalina", "bilirrubina"],
            "hepatico": ["tgo", "tgp", "gama gt", "fosfatase alcalina", "bilirrubina"],
            "vit d": ["vitamina d"],
            "vitamina d": ["vitamina d"],
            "b12": ["vitamina b12"],
            "ferro": ["ferro", "ferritina", "transferrina"],
            "ferr": ["ferritina", "ferro"],
            "tireoide": ["tsh", "t4 livre", "t3 livre"],
            "tsh": ["tsh"],
            "hemograma": ["hemograma", "hemoglobina", "hemacias", "leucocitos", "plaquetas"],
            "plaqueta": ["plaquetas"],
            "inflamacao": ["proteina c reativa", "pcr", "vhs"],
            "pcr": ["proteina c reativa"],
        }

        nome_n = _busca_norm(nome)

        for chave, valores in aliases.items():
            for valor in valores:
                if valor in nome_n or nome_n in valor:
                    termos.add(chave)
                    termos.add(valor)

        return " ".join(_busca_norm(t) for t in termos if t)

    def _busca_score(item, consulta):
        nome = _busca_norm(_busca_nome_exame(item))
        termos = _busca_termos_exame(item)
        q = _busca_norm(consulta)

        if not q:
            return 0

        score = 0

        if nome == q:
            score += 100
        if nome.startswith(q):
            score += 80
        if q in nome:
            score += 60
        if q in termos:
            score += 40

        partes = [p for p in q.split() if len(p) >= 2]
        for parte in partes:
            if nome.startswith(parte):
                score += 18
            elif parte in nome:
                score += 12
            elif parte in termos:
                score += 8

        return score

    def atualizar_busca_exames(e=None, refresh_page=True):
        termo = str(busca_exame.value or "").strip()

        if len(termo) < 3:
            busca_resultados_area.controls = [
                ft.Container(
                    padding=12,
                    border_radius=12,
                    bgcolor="#F8FAFC",
                    content=ft.Text(
                        "Digite pelo menos 3 letras para localizar rapidamente o exame.",
                        size=12,
                        color=COR_TEXTO_FRACO,
                    ),
                )
            ]
            if refresh_page:
                page.update()
            return

        data_br = str(data_exame.value or "").strip()
        data = data_br_para_iso(data_br)
        paciente_id = paciente_nome.value

        disponiveis = exames_disponiveis_por_data(paciente_id, data)

        encontrados = []
        for exame in disponiveis:
            score = _busca_score(exame, termo)
            if score > 0:
                encontrados.append((score, exame))

        encontrados.sort(
            key=lambda x: (
                -x[0],
                _busca_norm(_busca_nome_exame(x[1])),
            )
        )

        encontrados = [exame for _, exame in encontrados[:8]]

        if not encontrados:
            busca_resultados_area.controls = [
                ft.Container(
                    padding=12,
                    border_radius=12,
                    bgcolor="#FEF2F2",
                    content=ft.Text(
                        "Nenhum exame disponível encontrado para essa busca. Verifique se ele já foi cadastrado nesta data.",
                        size=12,
                        color="#991B1B",
                    ),
                )
            ]
        else:
            busca_resultados_area.controls = [
                ft.Text(
                    f"{len(encontrados)} resultado(s) encontrado(s)",
                    size=12,
                    color=COR_TEXTO_FRACO,
                )
            ] + [
                exame_disponivel_card(
                    page,
                    exame,
                    data_exame,
                    paciente_nome,
                    atualizar_callback=atualizar_listas,
                )
                for exame in encontrados
            ]

        if refresh_page:
            page.update()

    def limpar_busca_exames(e=None):
        busca_exame.value = ""
        atualizar_busca_exames(refresh_page=False)
        page.update()

    busca_exames_bloco = ft.Container(
        padding=14,
        border_radius=16,
        bgcolor="#F8FAFC",
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[
                        busca_exame,
                        ft.OutlinedButton(
                            content="Limpar",
                            on_click=limpar_busca_exames,
                        ),
                    ],
                ),
                busca_resultados_area,
            ],
        ),
    )

    # ===== FIM PATCH BUSCA INTELIGENTE NA TELA DE EXAMES =====

    def atualizar_listas(e=None):
        data_br = data_exame.value.strip()
        data = data_br_para_iso(data_br)
        paciente_id = paciente_nome.value

        disponiveis = exames_disponiveis_por_data(paciente_id, data)
        bloqueados = exames_ja_cadastrados_por_data(paciente_id, data)

        grupos_disponiveis = agrupar_itens_exames(disponiveis)

        lista_disponiveis.controls = [
            grupo_exames_card(
                page,
                nome_grupo,
                exames_grupo,
                data_exame,
                paciente_nome,
                atualizar_callback=atualizar_listas,
            )
            for nome_grupo, exames_grupo in grupos_disponiveis
        ]

        if not lista_disponiveis.controls:
            lista_disponiveis.controls = [
                ft.Container(
                    padding=24,
                    border_radius=16,
                    bgcolor="#F8FAFC",
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text("Todos os exames do catálogo já foram cadastrados nesta data.", size=14, color=COR_TEXTO_FRACO),
                )
            ]

        lista_bloqueados.controls = [
            exame_bloqueado_card_com_exclusao(
                page,
                exame,
                paciente_id,
                data,
                atualizar_callback=atualizar_listas,
            )
            for exame in bloqueados
        ]

        if not lista_bloqueados.controls:
            lista_bloqueados.controls = [
                ft.Container(
                    padding=18,
                    border_radius=16,
                    bgcolor="#F8FAFC",
                    content=ft.Text("Nenhum exame cadastrado nesta data.", size=13, color=COR_TEXTO_FRACO),
                )
            ]

        resumo_texto.value = f'{len(disponiveis)} exame(s) disponível(is) para cadastro • {len(bloqueados)} já cadastrado(s) nesta data'
        historico_resultados_area.controls = [historico_resultados_card(paciente_id, data)]

        try:
            atualizar_busca_exames(refresh_page=False)
        except Exception as exc:
            print(f"[BUSCA EXAMES] Falha ao atualizar busca: {exc}")

        page.update()

    data_exame.on_change = atualizar_listas
    paciente_nome.on_change = atualizar_listas
    busca_exame.on_change = atualizar_busca_exames

    atualizar_listas()

    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=18,
        expand=True,
        controls=[
            card_importacao_pdf_exames(page),

            app_card(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text("Cadastro de exames", size=26, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                                ft.Text("A lista abaixo remove automaticamente exames já cadastrados na mesma data. Use o formato DD/MM/AAAA.", size=13, color=COR_TEXTO_FRACO),
                            ],
                        ),
                        ft.Container(
                            content=ft.Text("Regra ativa: paciente + data + exame", size=12, color=COR_PRIMARIA, weight=ft.FontWeight.BOLD),
                            bgcolor="#EFF6FF",
                            border_radius=30,
                            padding=ft.Padding.symmetric(horizontal=16, vertical=10),
                        ),
                    ],
                ),
                padding=24,
            ),

            app_card(
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Row(
                            spacing=14,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                paciente_nome,
                                data_exame,
                                ft.FilledButton(
                                    content="Atualizar lista",
                                    icon=ft.Icons.REFRESH,
                                    on_click=atualizar_listas,
                                    style=ft.ButtonStyle(bgcolor=COR_PRIMARIA, color="white", shape=ft.RoundedRectangleBorder(radius=12)),
                                ),
                            ],
                        ),
                        resumo_texto,
                    ],
                ),
                padding=20,
            ),

            ft.ResponsiveRow(
                columns=12,
                spacing=16,
                run_spacing=16,
                controls=[
                    ft.Container(
                        col={"xs": 12, "md": 7},
                        content=app_card(
                            ft.Column(
                                spacing=16,
                                controls=[
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Text("Exames disponíveis por grupo", size=18, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                                            ft.Text("Cards macro com exames individuais", size=12, color=COR_TEXTO_FRACO),
                                        ],
                                    ),
                                    busca_exames_bloco,
                                    lista_disponiveis,
                                ],
                            ),
                            padding=20,
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "md": 5},
                        content=app_card(
                            ft.Column(
                                spacing=16,
                                controls=[
                                    ft.Text("Já cadastrados na data", size=18, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                                    ft.Text("Esses exames não aparecem na lista de cadastro.", size=12, color=COR_TEXTO_FRACO),
                                    lista_bloqueados,
                                ],
                            ),
                            padding=20,
                        ),
                    ),
                ],
            ),

            app_card(
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Resultados lançados", size=18, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                                ft.Text("Classificação automática por referência", size=12, color=COR_TEXTO_FRACO),
                            ],
                        ),
                        historico_resultados_area,
                    ],
                ),
                padding=20,
            ),
        ],
    )


def referencias_view(page):
    grupos = sorted(set(ref["grupo"] for ref in REFERENCIAS_MOCK))

    filtro_grupo = ft.Dropdown(
        label="Filtrar por grupo",
        value="Todos",
        width=260,
        border_radius=12,
        options=[ft.dropdown.Option(key="Todos", text="Todos os grupos")]
        + [ft.dropdown.Option(key=grupo, text=grupo) for grupo in grupos],
    )

    lista_referencias = ft.Column(spacing=12)
    resumo_texto = ft.Text("", size=13, color=COR_TEXTO_FRACO)

    def referencia_card(ref):
        status_color = cor_status_referencia(ref["status"])

        return app_card(
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        expand=True,
                        spacing=14,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=46,
                                height=46,
                                border_radius=15,
                                bgcolor="#EFF6FF",
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(ft.Icons.MENU_BOOK, color=COR_PRIMARIA, size=24),
                            ),
                            ft.Container(
                                expand=True,
                                content=ft.Column(
                                    spacing=5,
                                    controls=[
                                        ft.Text(ref["nome"], size=16, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                                        ft.Text(f'{ref["grupo"]} • Unidade: {ref["unidade"]} • Referência: {ref["referencia"]}', size=12, color=COR_TEXTO_FRACO),
                                        ft.Text(f'Fonte: {ref["fonte"]}', size=12, color=COR_TEXTO_FRACO),
                                    ],
                                ),
                            ),
                        ],
                    ),
                    ft.Container(
                        content=ft.Text(ref["status"].upper(), size=11, color="white", weight=ft.FontWeight.BOLD),
                        bgcolor=status_color,
                        border_radius=30,
                        padding=ft.Padding.symmetric(horizontal=12, vertical=7),
                    ),
                ],
            ),
            padding=16,
        )

    def atualizar_lista(e=None):
        grupo = filtro_grupo.value

        referencias = REFERENCIAS_MOCK if grupo == "Todos" else [ref for ref in REFERENCIAS_MOCK if ref["grupo"] == grupo]

        completas = len([r for r in referencias if r["status"].lower() == "completa"])
        pendentes = len(referencias) - completas

        resumo_texto.value = f"{len(referencias)} referência(s) exibida(s) • {completas} completa(s) • {pendentes} pendente(s)"
        lista_referencias.controls = [referencia_card(ref) for ref in referencias]

        page.update()

    filtro_grupo.on_change = atualizar_lista
    atualizar_lista()

    total = len(REFERENCIAS_MOCK)
    completas_total = len([r for r in REFERENCIAS_MOCK if r["status"].lower() == "completa"])
    pendentes_total = total - completas_total

    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=18,
        expand=True,
        controls=[
            app_card(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text("Referências clínicas", size=26, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                                ft.Text("Catálogo de faixas de referência usado para classificar os exames.", size=13, color=COR_TEXTO_FRACO),
                            ],
                        ),
                        ft.Container(
                            content=ft.Text("Objetivo: nenhum exame cadastrado deve ficar sem referência", size=12, color=COR_PRIMARIA, weight=ft.FontWeight.BOLD),
                            bgcolor="#EFF6FF",
                            border_radius=30,
                            padding=ft.Padding.symmetric(horizontal=16, vertical=10),
                        ),
                    ],
                ),
                padding=24,
            ),

            ft.ResponsiveRow(
                columns=12,
                spacing=16,
                run_spacing=16,
                controls=[
                    ft.Container(col={"xs": 12, "sm": 4}, content=app_card(ft.Column(spacing=6, controls=[ft.Text("Total de referências", size=13, color=COR_TEXTO_FRACO), ft.Text(str(total), size=28, weight=ft.FontWeight.BOLD, color=COR_TEXTO)]), padding=18)),
                    ft.Container(col={"xs": 12, "sm": 4}, content=app_card(ft.Column(spacing=6, controls=[ft.Text("Completas", size=13, color=COR_TEXTO_FRACO), ft.Text(str(completas_total), size=28, weight=ft.FontWeight.BOLD, color=COR_NORMAL)]), padding=18)),
                    ft.Container(col={"xs": 12, "sm": 4}, content=app_card(ft.Column(spacing=6, controls=[ft.Text("Pendentes", size=13, color=COR_TEXTO_FRACO), ft.Text(str(pendentes_total), size=28, weight=ft.FontWeight.BOLD, color=COR_ALERTA)]), padding=18)),
                ],
            ),

            app_card(
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Row(
                            spacing=14,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                filtro_grupo,
                                ft.FilledButton(
                                    content="Atualizar",
                                    icon=ft.Icons.REFRESH,
                                    on_click=atualizar_lista,
                                    style=ft.ButtonStyle(bgcolor=COR_PRIMARIA, color="white", shape=ft.RoundedRectangleBorder(radius=12)),
                                ),
                            ],
                        ),
                        resumo_texto,
                    ],
                ),
                padding=20,
            ),

            app_card(
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Catálogo de referências", size=18, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                                ft.Text("Dados carregados da base própria Flet", size=12, color=COR_TEXTO_FRACO),
                            ],
                        ),
                        lista_referencias,
                    ],
                ),
                padding=20,
            ),
        ],
    )






# ============================================================
# INTEGRAÇÃO COM BASE REAL CSV DA APLICAÇÃO ANTERIOR
# ============================================================

BASE_REAL_CSV_OK = False

try:
    from src.database import inicializar_banco_csv as real_inicializar_banco_csv
    from src.pacientes import (
        listar_pacientes as real_listar_pacientes,
        buscar_paciente_por_id as real_buscar_paciente_por_id,
        cadastrar_paciente as real_cadastrar_paciente,
    )
    from src.exames import (
        listar_exames_por_paciente as real_listar_exames_por_paciente,
        listar_analises_por_paciente as real_listar_analises_por_paciente,
    )
    from src.analises import executar_analise_exames as real_executar_analise_exames

    real_inicializar_banco_csv()
    BASE_REAL_CSV_OK = True

except Exception as exc:
    print(f"AVISO: base real CSV ainda não carregada: {exc}")
    BASE_REAL_CSV_OK = False


def idade_por_data_nascimento(data_nascimento):
    data_nascimento = str(data_nascimento or "").strip()

    if not data_nascimento:
        return "-"

    formatos = ["%Y-%m-%d", "%d/%m/%Y"]

    for fmt in formatos:
        try:
            nasc = datetime.strptime(data_nascimento, fmt)
            hoje = datetime.now()
            idade = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
            return idade
        except Exception:
            pass

    return "-"


def valor_primeiro(dados, chaves, padrao=""):
    for chave in chaves:
        if chave in dados and dados.get(chave) not in [None, ""]:
            return dados.get(chave)
    return padrao


def status_paciente_por_analises(paciente_id):
    if not BASE_REAL_CSV_OK:
        return "Sem dados"

    try:
        try:
            real_executar_analise_exames()
        except Exception:
            pass

        analises = real_listar_analises_por_paciente(str(paciente_id))

        if not analises:
            return "Sem exames"

        encontrou_alterado = False

        for item in analises:
            texto = " ".join([
                str(item.get("status", "")),
                str(item.get("classificacao", "")),
                str(item.get("situacao", "")),
                str(item.get("analise", "")),
                str(item.get("resultado_analise", "")),
                str(item.get("observacao", "")),
            ]).lower()

            if "crítico" in texto or "critico" in texto:
                return "Crítico"

            if (
                "alto" in texto
                or "baixo" in texto
                or "alterado" in texto
                or "fora" in texto
                or "atenção" in texto
                or "atencao" in texto
            ):
                encontrou_alterado = True

        return "Atenção" if encontrou_alterado else "Normal"

    except Exception:
        return "Sem análise"


def resumo_exames_reais_paciente(paciente_id):
    if not BASE_REAL_CSV_OK:
        return {
            "total": 0,
            "ultimo_exame": "-",
        }

    try:
        exames = real_listar_exames_por_paciente(str(paciente_id))
    except Exception:
        exames = []

    datas = []

    for exame in exames:
        data = valor_primeiro(exame, ["data_exame", "data", "data_cadastro"], "")
        if data:
            datas.append(str(data))

    ultimo = "-"

    if datas:
        try:
            ultimo = sorted(datas)[-1]
        except Exception:
            ultimo = datas[-1]

    return {
        "total": len(exames),
        "ultimo_exame": ultimo,
    }


def normalizar_paciente_real_para_ui(paciente):
    paciente_id = valor_primeiro(paciente, ["paciente_id", "id"], "")
    nome = valor_primeiro(paciente, ["nome", "nome_paciente"], "Paciente sem nome")
    data_nascimento = valor_primeiro(paciente, ["data_nascimento", "nascimento"], "")

    resumo_exames = resumo_exames_reais_paciente(paciente_id)

    return {
        "id": str(paciente_id),
        "nome": nome,
        "idade": idade_por_data_nascimento(data_nascimento),
        "data_nascimento": data_nascimento,
        "sexo": valor_primeiro(paciente, ["sexo"], "Não informado"),
        "telefone": valor_primeiro(paciente, ["telefone"], ""),
        "email": valor_primeiro(paciente, ["email"], ""),
        "profissao": valor_primeiro(paciente, ["profissao"], ""),
        "horario_trabalho": valor_primeiro(paciente, ["horario_trabalho"], ""),
        "observacoes": valor_primeiro(paciente, ["observacoes"], ""),
        "ultimo_exame": resumo_exames["ultimo_exame"],
        "status": status_paciente_por_analises(paciente_id),
        "exames": resumo_exames["total"],
        "origem": "CSV",
    }


def carregar_pacientes_base_real():
    if not BASE_REAL_CSV_OK:
        return []

    try:
        pacientes = real_listar_pacientes()
    except Exception as exc:
        print(f"Erro ao listar pacientes reais: {exc}")
        return []

    return [
        normalizar_paciente_real_para_ui(paciente)
        for paciente in pacientes
    ]


def atualizar_pacientes_da_base_real():
    """
    Atualiza a lista usada pela interface a partir da base real CSV.
    Não utiliza dados mockados.
    """
    global PACIENTES_MOCK

    pacientes_reais = carregar_pacientes_base_real()

    PACIENTES_MOCK[:] = pacientes_reais

    if PACIENTES_MOCK:
        atual = str(globals().get("PACIENTE_SELECIONADO_ID", ""))
        ids = [str(p["id"]) for p in PACIENTES_MOCK]

        if atual not in ids:
            globals()["PACIENTE_SELECIONADO_ID"] = str(PACIENTES_MOCK[0]["id"])
    else:
        globals()["PACIENTE_SELECIONADO_ID"] = ""

    return PACIENTES_MOCK


# ============================================================
# MÓDULOS NUTRICIONAIS RECUPERADOS DA APLICAÇÃO ANTERIOR
# Anamnese, Recordatório, Antropometria e Resumo Nutricional
# ============================================================

ANAMNESES_MOCK = []
RECORDATORIOS_MOCK = []
ANTROPOMETRIAS_MOCK = []


def obter_paciente_por_id(paciente_id):
    for paciente in PACIENTES_MOCK:
        if str(paciente["id"]) == str(paciente_id):
            return paciente
    return None


def data_hoje_br():
    try:
        return datetime.now().strftime("%d/%m/%Y")
    except Exception:
        return ""


def texto_vazio(valor, padrao="-"):
    valor = (valor or "").strip()
    return valor if valor else padrao


def anamnese_mais_recente(paciente_id):
    itens = [
        a for a in ANAMNESES_MOCK
        if str(a.get("paciente_id")) == str(paciente_id)
    ]
    return itens[-1] if itens else None


def recordatorios_paciente(paciente_id):
    return [
        r for r in RECORDATORIOS_MOCK
        if str(r.get("paciente_id")) == str(paciente_id)
    ]


def antropometrias_paciente(paciente_id):
    return [
        a for a in ANTROPOMETRIAS_MOCK
        if str(a.get("paciente_id")) == str(paciente_id)
    ]


def numero_float(valor):
    try:
        return float(str(valor).replace(",", ".").strip())
    except Exception:
        return None


def calcular_imc(peso, altura):
    peso_float = numero_float(peso)
    altura_float = numero_float(altura)

    if peso_float is None or altura_float is None or altura_float <= 0:
        return None

    if altura_float > 3:
        altura_float = altura_float / 100

    return round(peso_float / (altura_float ** 2), 2)


def classificar_imc(imc):
    if imc is None:
        return "Sem classificação"

    if imc < 18.5:
        return "Baixo peso"
    if imc < 25:
        return "Eutrofia"
    if imc < 30:
        return "Sobrepeso"
    if imc < 35:
        return "Obesidade grau I"
    if imc < 40:
        return "Obesidade grau II"

    return "Obesidade grau III"


def risco_cintura(cintura, sexo):
    cintura_float = numero_float(cintura)
    sexo = (sexo or "").upper()

    if cintura_float is None:
        return "Sem avaliação"

    if sexo == "M":
        if cintura_float >= 102:
            return "Risco aumentado"
        if cintura_float >= 94:
            return "Risco moderado"
        return "Baixo risco"

    if sexo == "F":
        if cintura_float >= 88:
            return "Risco aumentado"
        if cintura_float >= 80:
            return "Risco moderado"
        return "Baixo risco"

    return "Avaliar conforme contexto"








def multiselect_dropdown(page, titulo, opcoes, width=620):
    """
    Multisseleção 100% inline.
    Não usa AlertDialog, overlay, popup ou botão Confirmar.
    """
    selecionados = []
    opcoes_ordenadas = ordenar_opcoes_texto(opcoes)

    resumo_texto = ft.Text(
        "Nenhum item selecionado",
        size=13,
        color=COR_TEXTO_FRACO,
        max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS,
    )

    chips_area = ft.Row(
        wrap=True,
        spacing=8,
        run_spacing=8,
        controls=[],
    )

    busca = ft.TextField(
        label="Filtrar opções",
        width=width,
        border_radius=12,
        dense=True,
    )

    lista_opcoes = ft.Column(
        spacing=4,
        scroll=ft.ScrollMode.AUTO,
        controls=[],
    )

    painel = ft.Container(
        visible=False,
        bgcolor="#FFFFFF",
        border_radius=16,
        padding=14,
        height=420,
    )

    def atualizar_resumo():
        if selecionados:
            texto = f"{len(selecionados)} selecionado(s): " + "; ".join(selecionados[:4])
            if len(selecionados) > 4:
                texto += "..."
            resumo_texto.value = texto
            resumo_texto.color = COR_TEXTO
        else:
            resumo_texto.value = "Nenhum item selecionado"
            resumo_texto.color = COR_TEXTO_FRACO

    def atualizar_chips():
        chips_area.controls.clear()

        for item in selecionados:
            def remover(e, item=item):
                if item in selecionados:
                    selecionados.remove(item)

                montar_lista()
                atualizar_resumo()
                atualizar_chips()
                page.update()

            chips_area.controls.append(
                ft.Container(
                    bgcolor="#EFF6FF",
                    border_radius=22,
                    padding=ft.Padding.only(left=12, right=4, top=5, bottom=5),
                    content=ft.Row(
                        tight=True,
                        spacing=4,
                        controls=[
                            ft.Text(
                                item,
                                size=12,
                                color=COR_PRIMARIA,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                icon_size=14,
                                tooltip="Remover",
                                on_click=remover,
                            ),
                        ],
                    ),
                )
            )

    def itens_filtrados():
        termo = (busca.value or "").strip().lower()
        return [
            opcao for opcao in opcoes_ordenadas
            if termo in str(opcao).lower()
        ]

    def alternar_item(e, item):
        marcado = bool(e.control.value)

        if marcado and item not in selecionados:
            selecionados.append(item)

        if not marcado and item in selecionados:
            selecionados.remove(item)

        selecionados.sort(key=lambda x: str(x).lower())

        montar_lista()
        atualizar_resumo()
        atualizar_chips()
        page.update()

    def montar_lista():
        lista_opcoes.controls.clear()

        itens = itens_filtrados()

        if not itens:
            termo_adicionar = (busca.value or "").strip()
            pode_adicionar = bool(termo_adicionar) and str(titulo or "").strip().lower().startswith("alimentos -")

            if pode_adicionar:
                def adicionar_novo_alimento(e, item=termo_adicionar):
                    item = str(item or "").strip()

                    if not item:
                        return

                    if item not in opcoes_ordenadas:
                        opcoes_ordenadas.append(item)
                        opcoes_ordenadas.sort(key=lambda x: str(x).lower())

                    if item not in selecionados:
                        selecionados.append(item)
                        selecionados.sort(key=lambda x: str(x).lower())

                    try:
                        _recordatorio_salvar_alimento_personalizado(titulo, item)
                    except Exception:
                        pass

                    busca.value = ""
                    montar_lista()
                    atualizar_resumo()
                    atualizar_chips()
                    page.update()

                lista_opcoes.controls.append(
                    ft.Container(
                        bgcolor="#F8FAFC",
                        border_radius=12,
                        padding=12,
                        content=ft.Column(
                            spacing=8,
                            controls=[
                                ft.Text(
                                    f'Nenhuma opção encontrada para "{termo_adicionar}".',
                                    size=12,
                                    color=COR_TEXTO_FRACO,
                                ),
                                ft.Container(
                                    bgcolor=COR_PRIMARIA,
                                    border_radius=12,
                                    padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                                    on_click=adicionar_novo_alimento,
                                    content=ft.Row(
                                        tight=True,
                                        spacing=8,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Icon(ft.Icons.ADD, color="#FFFFFF", size=18),
                                            ft.Text(
                                                f'Adicionar "{termo_adicionar}"',
                                                color="#FFFFFF",
                                                size=13,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                    )
                )
            else:
                lista_opcoes.controls.append(
                    ft.Container(
                        bgcolor="#F8FAFC",
                        border_radius=12,
                        padding=12,
                        content=ft.Text(
                            "Nenhuma opção encontrada.",
                            size=12,
                            color=COR_TEXTO_FRACO,
                        ),
                    )
                )
            return

        for opcao in itens:
            lista_opcoes.controls.append(
                ft.Container(
                    bgcolor="#EFF6FF" if opcao in selecionados else "#F8FAFC",
                    border_radius=10,
                    padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                    content=ft.Checkbox(
                        label=opcao,
                        value=opcao in selecionados,
                        on_change=lambda e, item=opcao: alternar_item(e, item),
                    ),
                )
            )

    def filtrar(e):
        montar_lista()
        page.update()

    busca.on_change = filtrar

    def selecionar_todos_filtrados(e):
        for opcao in itens_filtrados():
            if opcao not in selecionados:
                selecionados.append(opcao)

        selecionados.sort(key=lambda x: str(x).lower())

        montar_lista()
        atualizar_resumo()
        atualizar_chips()
        page.update()

    def limpar_selecao(e):
        selecionados.clear()

        montar_lista()
        atualizar_resumo()
        atualizar_chips()
        page.update()

    def abrir_fechar(e):
        painel.visible = not painel.visible
        montar_lista()
        page.update()

    def recolher(e):
        painel.visible = False
        page.update()

    painel.content = ft.Column(
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            busca,
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        "Marque uma ou mais opções. Use o filtro para localizar rapidamente.",
                        size=12,
                        color=COR_TEXTO_FRACO,
                    ),
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.TextButton("Selecionar todos", on_click=selecionar_todos_filtrados),
                            ft.TextButton("Limpar", on_click=limpar_selecao),
                            ft.TextButton("Recolher", on_click=recolher),
                        ],
                    ),
                ],
            ),
            lista_opcoes,
        ],
    )

    cabecalho = ft.Container(
        bgcolor="#FFFFFF",
        border_radius=12,
        padding=ft.Padding.symmetric(horizontal=14, vertical=12),
        on_click=abrir_fechar,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=3,
                    expand=True,
                    controls=[
                        ft.Text(
                            titulo,
                            size=12,
                            color=COR_TEXTO_FRACO,
                        ),
                        resumo_texto,
                    ],
                ),
                ft.Icon(
                    ft.Icons.ARROW_DROP_DOWN,
                    color=COR_TEXTO_FRACO,
                ),
            ],
        ),
    )

    montar_lista()
    atualizar_resumo()
    atualizar_chips()

    controle = ft.Container(
        bgcolor="#F8FAFC",
        border_radius=16,
        padding=16,
        content=ft.Column(
            spacing=12,
            controls=[
                cabecalho,
                chips_area,
                painel,
            ],
        ),
    )

    return controle, selecionados


def valores_multiselect(selecionados, complemento=None):
    valores = list(selecionados)
    complemento = (complemento or "").strip()

    if complemento:
        valores.append(f"Outro/Detalhe: {complemento}")

    return "; ".join(valores) if valores else "Não informado"

def grupo_multiselecao(titulo, opcoes, col_md=4):
    """
    Cria grupo de múltipla seleção usando checkboxes.
    Retorna o controle visual e a lista de checkboxes.
    """
    checks = [
        ft.Checkbox(label=opcao, value=False)
        for opcao in opcoes
    ]

    controle = ft.Container(
        bgcolor="#F8FAFC",
        border_radius=16,
        padding=16,
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Text(
                    titulo,
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=COR_TEXTO,
                ),
                ft.ResponsiveRow(
                    columns=12,
                    spacing=4,
                    run_spacing=4,
                    controls=[
                        ft.Container(
                            col={"xs": 12, "sm": 6, "md": col_md},
                            content=check,
                        )
                        for check in checks
                    ],
                ),
            ],
        ),
    )

    return controle, checks


def valores_multiselecao(checks, complemento=None):
    valores = [
        check.label
        for check in checks
        if bool(check.value)
    ]

    complemento = (complemento or "").strip()

    if complemento:
        valores.append(f"Outro/Detalhe: {complemento}")

    return "; ".join(valores) if valores else "Não informado"


OPCOES_QUEIXA_PRINCIPAL = [
    "Perda de peso",
    "Ganho de peso",
    "Reeducação alimentar",
    "Compulsão alimentar",
    "Ansiedade relacionada à alimentação",
    "Baixa energia / fadiga",
    "Melhora de performance esportiva",
    "Controle glicêmico",
    "Controle lipídico",
    "Sintomas gastrointestinais",
    "Retenção de líquidos",
    "Acompanhamento preventivo",
]

OPCOES_DOENCAS_ATUAIS = [
    "Nenhuma informada",
    "Hipertensão arterial",
    "Pré-diabetes",
    "Diabetes tipo 1",
    "Diabetes tipo 2",
    "Diabetes gestacional",
    "Resistência à insulina",
    "Síndrome metabólica",
    "Dislipidemia",
    "Hipercolesterolemia",
    "Hipertrigliceridemia",
    "Hipotireoidismo",
    "Hipertireoidismo",
    "Nódulos tireoidianos",
    "Esteatose hepática",
    "Doença hepática",
    "Gastrite",
    "Refluxo gastroesofágico",
    "Hérnia de hiato",
    "Síndrome do intestino irritável",
    "Constipação crônica",
    "Diarreia crônica",
    "Doença celíaca",
    "Doença inflamatória intestinal",
    "Intolerância à lactose",
    "Alergia alimentar",
    "Doença renal crônica",
    "Cálculo renal",
    "Anemia",
    "Deficiência de ferro",
    "Deficiência de vitamina D",
    "Deficiência de B12",
    "Gota / ácido úrico elevado",
    "Osteopenia / osteoporose",
    "SOP - Síndrome dos ovários policísticos",
    "Endometriose",
    "Menopausa / climatério",
    "Enxaqueca",
    "Fibromialgia",
    "Ansiedade",
    "Depressão",
    "Transtorno alimentar",
    "Obesidade",
    "Sobrepeso",
    "Baixo peso",
    "Doença cardiovascular",
    "Histórico de infarto",
    "Histórico de AVC",
    "Câncer em tratamento",
    "Câncer prévio",
    "Doença autoimune",
    "Outra",
]

OPCOES_SINTOMAS = [
    "Nenhum",
    "Azia",
    "Refluxo",
    "Gases",
    "Distensão abdominal",
    "Dor abdominal",
    "Constipação",
    "Diarreia",
    "Alternância constipação/diarreia",
    "Náuseas",
    "Vômitos",
    "Saciedade precoce",
    "Fome excessiva",
    "Fome noturna",
    "Compulsão alimentar",
    "Vontade intensa de doces",
    "Fadiga",
    "Sonolência diurna",
    "Insônia",
    "Sono fragmentado",
    "Tontura",
    "Dor de cabeça",
    "Enxaqueca",
    "Queda de cabelo",
    "Unhas fracas",
    "Pele ressecada",
    "Cãibras",
    "Inchaço / retenção",
    "Dor articular",
    "Dor muscular",
    "Baixa libido",
    "Irritabilidade",
    "Ansiedade",
    "Baixa concentração",
    "Outra",
]

OPCOES_HISTORIA_PREGRESSA = [
    "Nenhuma relevante",
    "Cirurgia bariátrica",
    "Colecistectomia",
    "Apendicectomia",
    "Cirurgia intestinal",
    "Cirurgia cardíaca",
    "Cirurgia ortopédica",
    "Cirurgia ginecológica",
    "Internação recente",
    "Internação antiga",
    "Uso prolongado de antibiótico",
    "Histórico de anemia",
    "Histórico de obesidade",
    "Histórico de efeito sanfona",
    "Histórico de transtorno alimentar",
    "Histórico de diabetes gestacional",
    "Histórico cardiovascular",
    "Histórico renal",
    "Histórico hepático",
    "Histórico oncológico",
    "Outra",
]

OPCOES_HISTORIA_FAMILIAR = [
    "Não informado",
    "Obesidade",
    "Diabetes",
    "Hipertensão",
    "Dislipidemia",
    "Infarto / doença cardiovascular",
    "AVC",
    "Câncer",
    "Doença renal",
    "Doença hepática",
    "Doença tireoidiana",
    "Doença autoimune",
    "Alzheimer / demência",
    "Osteoporose",
    "Transtorno alimentar",
    "Depressão / ansiedade",
    "Outra",
]

OPCOES_MEDICAMENTOS_SUPLEMENTOS = [
    "Não faz uso",
    "Antihipertensivo",
    "Diurético",
    "Antidiabético oral",
    "Insulina",
    "Estatina",
    "Fibrato",
    "Antidepressivo",
    "Ansiolítico",
    "Estabilizador de humor",
    "Hormônio tireoidiano",
    "Corticoide",
    "Anticoncepcional",
    "Terapia hormonal",
    "Antiácido / inibidor de bomba",
    "Laxante",
    "Antibiótico recente",
    "Polivitamínico",
    "Vitamina D",
    "Vitamina B12",
    "Ferro",
    "Cálcio",
    "Magnésio",
    "Ômega 3",
    "Creatina",
    "Whey protein",
    "Cafeína / pré-treino",
    "Termogênico",
    "Fitoterápico",
    "Outro",
]

OPCOES_INTERNACOES_CIRURGIAS = [
    "Nenhuma",
    "Cirurgia bariátrica",
    "Cirurgia abdominal",
    "Cirurgia ortopédica",
    "Cirurgia cardíaca",
    "Internação nos últimos 12 meses",
    "Internação antiga",
]

OPCOES_ALIMENTOS_PREFERIDOS = [
    "Arroz",
    "Feijão",
    "Massas",
    "Pães",
    "Tapioca",
    "Batata / mandioca",
    "Aveia",
    "Frango",
    "Carne vermelha",
    "Peixe",
    "Ovos",
    "Leite e derivados",
    "Queijos",
    "Iogurte",
    "Frutas",
    "Verduras",
    "Legumes",
    "Saladas",
    "Oleaginosas",
    "Doces",
    "Chocolate",
    "Salgados",
    "Fast food",
    "Pizza",
    "Hambúrguer",
    "Refrigerante",
    "Suco",
    "Café",
    "Açaí",
    "Comida japonesa",
    "Outra",
]

OPCOES_ALIMENTOS_NAO_GOSTA = [
    "Nenhum",
    "Verduras",
    "Legumes",
    "Frutas",
    "Feijão",
    "Arroz integral",
    "Leite",
    "Iogurte",
    "Queijos",
    "Ovos",
    "Peixe",
    "Frango",
    "Carne vermelha",
    "Alimentos integrais",
    "Oleaginosas",
    "Água",
    "Saladas",
    "Comida caseira",
    "Outra",
]

OPCOES_HABITOS_FIM_SEMANA = [
    "Mantém rotina alimentar",
    "Come fora",
    "Delivery",
    "Churrasco",
    "Pizza / hambúrguer",
    "Aumenta consumo de álcool",
    "Aumenta doces",
    "Aumenta fast food",
    "Pula refeições",
    "Belisca mais",
    "Come mais tarde",
    "Reduz ingestão de água",
    "Sono desregulado",
    "Pratica atividade física",
    "Fica mais sedentário",
    "Viagens / passeios",
    "Outra",
]

OPCOES_OBJETIVO_NUTRICIONAL = [
    "Emagrecimento",
    "Ganho de massa muscular",
    "Manutenção de peso",
    "Melhora de exames laboratoriais",
    "Melhora de performance",
    "Redução de sintomas gastrointestinais",
    "Educação alimentar",
    "Controle de compulsão",
    "Melhora de energia/disposição",
]

OPCOES_DIFICULDADES_ADESAO = [
    "Falta de tempo",
    "Ansiedade",
    "Compulsão",
    "Rotina de trabalho",
    "Viagens",
    "Finais de semana",
    "Custo dos alimentos",
    "Falta de apoio familiar",
    "Não sabe cozinhar",
    "Delivery frequente",
    "Baixa organização",
]


def ordenar_opcoes_texto(opcoes):
    """
    Ordena opções alfabeticamente, preservando opções especiais no topo.
    """
    especiais = ["Não informado", "Nenhuma informada", "Nenhuma relevante", "Nenhum", "Nenhuma", "Não faz uso"]

    topo = [op for op in especiais if op in opcoes]
    restante = [op for op in opcoes if op not in topo]

    return topo + sorted(restante, key=lambda x: str(x).lower())


def gerar_opcoes_horarios(intervalo_minutos=30):
    horarios = ["Não informado"]

    for hora in range(0, 24):
        for minuto in range(0, 60, intervalo_minutos):
            horarios.append(f"{hora:02d}:{minuto:02d}")

    return horarios


OPCOES_HORARIOS = gerar_opcoes_horarios(30)


def campo_hora_dropdown(label, value="Não informado", width=170):
    return ft.Dropdown(
        label=label,
        value=value or "Não informado",
        width=width,
        border_radius=12,
        options=[
            ft.dropdown.Option(key=h, text=h)
            for h in OPCOES_HORARIOS
        ],
    )




def valor_controle(controle, padrao=""):
    """
    Obtém valor de TextField/Dropdown ou de componentes compostos,
    como Row contendo TextField + botão de calendário.
    """
    if controle is None:
        return padrao

    if hasattr(controle, "value"):
        valor = getattr(controle, "value", None)
        return valor if valor is not None else padrao

    if hasattr(controle, "controls"):
        for filho in controle.controls:
            valor = valor_controle(filho, None)
            if valor is not None:
                return valor

    if hasattr(controle, "content"):
        return valor_controle(controle.content, padrao)

    return padrao


def campo_data_calendario(page, label, value=None, width=190):
    """
    Campo de data padronizado com botão de calendário.
    Evita abrir calendário apenas ao focar no campo.
    """
    campo = ft.TextField(
        label=label,
        value=value or data_hoje_br(),
        width=width,
        border_radius=12,
        read_only=True,
    )

    def abrir_calendario(e):
        seletor = ft.DatePicker(
            first_date=datetime(1920, 1, 1),
            last_date=datetime(2100, 12, 31),
        )

        def selecionar_data(ev):
            if seletor.value:
                campo.value = seletor.value.strftime("%d/%m/%Y")
                seletor.open = False

                try:
                    if seletor in page.overlay:
                        page.overlay.remove(seletor)
                except Exception:
                    pass

                page.update()

        seletor.on_change = selecionar_data
        page.overlay.append(seletor)
        seletor.open = True
        page.update()

    return ft.Row(
        spacing=6,
        tight=True,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            campo,
            ft.IconButton(
                icon=ft.Icons.CALENDAR_MONTH,
                tooltip="Selecionar data",
                on_click=abrir_calendario,
            ),
        ],
    )



def valores_multiselect(selecionados, complemento=None):
    valores = list(selecionados)
    complemento = (complemento or "").strip()

    if complemento:
        valores.append(f"Outro/Detalhe: {complemento}")

    return "; ".join(valores) if valores else "Não informado"

def dropdown_opcoes(label, opcoes, value=None, width=260):
    """
    Cria uma lista suspensa padronizada.
    """
    valor_inicial = value if value is not None else (opcoes[0] if opcoes else None)

    opcoes_ordenadas = ordenar_opcoes_texto(opcoes)

    if value is None:
        valor_inicial = opcoes_ordenadas[0] if opcoes_ordenadas else None
    else:
        valor_inicial = value

    return ft.Dropdown(
        label=label,
        value=valor_inicial,
        width=width,
        border_radius=12,
        options=[
            ft.dropdown.Option(key=str(opcao), text=str(opcao))
            for opcao in opcoes_ordenadas
        ],
    )


def campo_texto_curto(label, width=260):
    return ft.TextField(
        label=label,
        width=width,
        border_radius=12,
    )


def campo_texto_longo(label, min_lines=2, max_lines=4):
    return ft.TextField(
        label=label,
        multiline=True,
        min_lines=min_lines,
        max_lines=max_lines,
        border_radius=12,
    )


OPCOES_SIM_NAO = [
    "Não informado",
    "Sim",
    "Não",
]

OPCOES_SEXO = [
    "Não informado",
    "M",
    "F",
    "Outro",
]

OPCOES_FREQUENCIA = [
    "Não informado",
    "Nunca",
    "Raramente",
    "1x por semana",
    "2x por semana",
    "3x por semana",
    "4x por semana",
    "5x ou mais por semana",
    "Diariamente",
]

OPCOES_ATIVIDADE_FISICA = [
    "Não informado",
    "Sedentário",
    "Caminhada",
    "Musculação",
    "Corrida",
    "Ciclismo",
    "Natação",
    "Luta / Artes marciais",
    "Funcional",
    "Pilates",
    "Outro",
]

OPCOES_CONSUMO_ALCOOL = [
    "Não informado",
    "Não consome",
    "Socialmente",
    "Finais de semana",
    "1 a 2x por semana",
    "3x ou mais por semana",
    "Diariamente",
]

OPCOES_TABAGISMO = [
    "Não informado",
    "Não fumante",
    "Ex-fumante",
    "Fumante eventual",
    "Fumante diário",
]

OPCOES_QUALIDADE_SONO = [
    "Não informado",
    "Boa",
    "Regular",
    "Ruim",
    "Insônia",
    "Sono fragmentado",
    "Sonolência diurna",
]

OPCOES_FUNCIONAMENTO_INTESTINAL = [
    "Não informado",
    "Diário",
    "A cada 2 dias",
    "A cada 3 dias ou mais",
    "Constipação",
    "Diarreia",
    "Alternância constipação/diarreia",
]

OPCOES_FUNCIONAMENTO_URINARIO = [
    "Não informado",
    "Normal",
    "Aumentado",
    "Reduzido",
    "Ardência",
    "Urgência urinária",
    "Noctúria",
]

OPCOES_APETITE = [
    "Não informado",
    "Normal",
    "Aumentado",
    "Reduzido",
    "Compulsão",
    "Oscilante",
]

OPCOES_HORARIO_FOME = [
    "Não informado",
    "Manhã",
    "Antes do almoço",
    "Tarde",
    "Noite",
    "Madrugada",
    "O dia todo",
]

OPCOES_COMPORTAMENTO_PESO = [
    "Não informado",
    "Peso estável",
    "Ganho de peso",
    "Perda de peso",
    "Efeito sanfona",
    "Dificuldade para ganhar peso",
    "Dificuldade para perder peso",
]

OPCOES_DISPOSICAO = [
    "Não informado",
    "Boa",
    "Regular",
    "Baixa",
    "Cansaço frequente",
    "Oscilante",
]

OPCOES_DENTICAO = [
    "Não informado",
    "Completa",
    "Incompleta",
    "Uso de prótese",
    "Uso de aparelho",
    "Dor ou dificuldade",
]

OPCOES_MASTIGACAO = [
    "Não informado",
    "Normal",
    "Rápida",
    "Lenta",
    "Dificuldade para mastigar",
    "Dor ao mastigar",
]

OPCOES_QUEM_COZINHA = [
    "Não informado",
    "O próprio paciente",
    "Cônjuge/familiar",
    "Funcionário(a)",
    "Restaurante",
    "Delivery frequente",
    "Variável",
]

OPCOES_HABITO_BELISCAR = [
    "Não informado",
    "Não",
    "Sim, doces",
    "Sim, salgados",
    "Sim, beliscos variados",
    "Sim, principalmente à noite",
]

OPCOES_INGESTAO_AGUA = [
    "Não informado",
    "Menos de 500 ml/dia",
    "500 ml a 1 litro/dia",
    "1 a 1,5 litro/dia",
    "1,5 a 2 litros/dia",
    "2 a 3 litros/dia",
    "Mais de 3 litros/dia",
]

OPCOES_INTOLERANCIA = [
    "Não informado",
    "Nenhuma",
    "Lactose",
    "Glúten",
    "Frutos do mar",
    "Oleaginosas",
    "Ovo",
    "Outro",
]

OPCOES_TRATAMENTO_NUTRICIONAL = [
    "Não informado",
    "Nunca fez",
    "Já fez e teve boa adesão",
    "Já fez e teve baixa adesão",
    "Em acompanhamento atualmente",
]

def paciente_dropdown_padrao(label="Paciente"):
    atualizar_pacientes_csv_real_definitivo()
    return ft.Dropdown(
        label=label,
        value=str(globals().get("PACIENTE_SELECIONADO_ID", "1")),
        width=340,
        border_radius=12,
        options=[
            ft.dropdown.Option(
                key=str(paciente["id"]),
                text=f'{paciente["nome"]} - {paciente["idade"]} anos',
            )
            for paciente in PACIENTES_MOCK
        ],
    )





def anamnese_view(page):
    paciente_control = paciente_dropdown_padrao()

    data_anamnese = campo_data_calendario(page, "Data da anamnese", data_hoje_br(), width=190)

    # História clínica com lista suspensa e múltipla seleção
    queixa_box, queixa_sel = multiselect_dropdown(page, "Queixa principal", OPCOES_QUEIXA_PRINCIPAL)
    queixa_detalhe = campo_texto_longo("Detalhe da queixa principal / observações")

    doencas_box, doencas_sel = multiselect_dropdown(page, "História de doença atual", OPCOES_DOENCAS_ATUAIS)
    doencas_detalhe = campo_texto_longo("Detalhes da doença atual")

    sintomas_box, sintomas_sel = multiselect_dropdown(page, "Sintomas observados/relatados", OPCOES_SINTOMAS)
    sintomas_detalhe = campo_texto_longo("Detalhes dos sintomas")

    pregressa_box, pregressa_sel = multiselect_dropdown(page, "História patológica pregressa", OPCOES_HISTORIA_PREGRESSA)
    pregressa_detalhe = campo_texto_longo("Detalhes da história patológica pregressa")

    familiar_box, familiar_sel = multiselect_dropdown(page, "História familiar", OPCOES_HISTORIA_FAMILIAR)
    familiar_detalhe = campo_texto_longo("Detalhes da história familiar")

    numero_filhos_idades = campo_texto_curto("Nº de filhos e idades", width=320)
    amamentou = dropdown_opcoes("Amamentou?", OPCOES_SIM_NAO, width=220)

    atividade_fisica = dropdown_opcoes("Atividade física", OPCOES_ATIVIDADE_FISICA, width=260)
    frequencia_atividade = dropdown_opcoes("Frequência", OPCOES_FREQUENCIA, width=240)
    horario_atividade_fisica = dropdown_opcoes(
        "Horário da atividade física",
        ["Não informado", "Manhã", "Tarde", "Noite", "Variável"],
        width=240,
    )

    consumo_alcool = dropdown_opcoes("Consumo de álcool", OPCOES_CONSUMO_ALCOOL, width=260)
    tabagismo = dropdown_opcoes("Tabagismo", OPCOES_TABAGISMO, width=240)
    qualidade_sono = dropdown_opcoes("Qualidade do sono", OPCOES_QUALIDADE_SONO, width=260)
    hora_acordar = campo_hora_dropdown("Hora de acordar", width=170)
    hora_dormir = campo_hora_dropdown("Hora de dormir", width=170)

    comportamento_peso = dropdown_opcoes("Comportamento do peso", OPCOES_COMPORTAMENTO_PESO, width=300)
    disposicao_fisica = dropdown_opcoes("Disposição física/energia", OPCOES_DISPOSICAO, width=280)

    funcionamento_intestinal = dropdown_opcoes("Funcionamento intestinal", OPCOES_FUNCIONAMENTO_INTESTINAL, width=300)
    funcionamento_urinario = dropdown_opcoes("Funcionamento urinário", OPCOES_FUNCIONAMENTO_URINARIO, width=280)

    internacoes_box, internacoes_sel = multiselect_dropdown(page, "Internações/Cirurgias", OPCOES_INTERNACOES_CIRURGIAS)
    internacoes_detalhe = campo_texto_longo("Detalhes de internações/cirurgias")

    medicamentos_box, medicamentos_sel = multiselect_dropdown(page, "Medicamentos/Suplementos em uso", OPCOES_MEDICAMENTOS_SUPLEMENTOS)
    medicamentos_detalhe = campo_texto_longo("Detalhes de medicamentos/suplementos")

    intolerancias = dropdown_opcoes("Intolerância/Alergia alimentar", OPCOES_INTOLERANCIA, width=300)
    detalhe_intolerancia = campo_texto_curto("Detalhe da intolerância/alergia", width=360)

    denticao = dropdown_opcoes("Dentição", OPCOES_DENTICAO, width=260)
    mastigacao = dropdown_opcoes("Mastigação", OPCOES_MASTIGACAO, width=260)

    quem_cozinha = dropdown_opcoes("Quem cozinha", OPCOES_QUEM_COZINHA, width=280)
    apetite = dropdown_opcoes("Apetite", OPCOES_APETITE, width=240)
    horario_mais_fome = dropdown_opcoes("Horário de mais fome", OPCOES_HORARIO_FOME, width=260)
    ingestao_agua = dropdown_opcoes("Ingestão de água/dia", OPCOES_INGESTAO_AGUA, width=280)

    tratamento_nutricional_anterior = dropdown_opcoes(
        "Tratamento nutricional anterior?",
        OPCOES_TRATAMENTO_NUTRICIONAL,
        width=330,
    )
    qual_tratamento = campo_texto_curto("Qual tratamento?", width=360)

    objetivo_box, objetivo_sel = multiselect_dropdown(page, "Objetivo nutricional", OPCOES_OBJETIVO_NUTRICIONAL)
    objetivo_detalhe = campo_texto_longo("Detalhes do objetivo nutricional")

    preferidos_box, preferidos_sel = multiselect_dropdown(page, "Alimentos preferidos", OPCOES_ALIMENTOS_PREFERIDOS)
    alimentos_preferidos_detalhe = campo_texto_longo("Outros alimentos preferidos / detalhes")

    nao_gosta_box, nao_gosta_sel = multiselect_dropdown(page, "Alimentos que não gosta", OPCOES_ALIMENTOS_NAO_GOSTA)
    alimentos_nao_gosta_detalhe = campo_texto_longo("Outros alimentos que não gosta / detalhes")

    habito_beliscar = dropdown_opcoes("Hábito de beliscar?", OPCOES_HABITO_BELISCAR, width=300)

    fim_semana_box, fim_semana_sel = multiselect_dropdown(page, "Hábitos de fim de semana", OPCOES_HABITOS_FIM_SEMANA)
    habitos_fim_semana_detalhe = campo_texto_longo("Detalhes dos hábitos de fim de semana")

    dificuldades_box, dificuldades_sel = multiselect_dropdown(page, "Dificuldades de adesão", OPCOES_DIFICULDADES_ADESAO)
    dificuldades_detalhe = campo_texto_longo("Detalhes das dificuldades de adesão")

    def salvar_anamnese(e):
        paciente_id = paciente_control.value

        if not paciente_id:
            mostrar_snackbar(page, "Selecione um paciente.", COR_ALERTA)
            return

        registro = {
            "paciente_id": paciente_id,
            "data_anamnese": valor_controle(data_anamnese),

            "queixa_principal": valores_multiselect(queixa_sel, queixa_detalhe.value),
            "historia_doenca_atual": valores_multiselect(doencas_sel, doencas_detalhe.value),
            "sintomas": valores_multiselect(sintomas_sel, sintomas_detalhe.value),
            "historia_patologica_pregressa": valores_multiselect(pregressa_sel, pregressa_detalhe.value),
            "historia_familiar": valores_multiselect(familiar_sel, familiar_detalhe.value),
            "numero_filhos_idades": numero_filhos_idades.value,
            "amamentou": amamentou.value,

            "atividade_fisica": f"{atividade_fisica.value} - {frequencia_atividade.value}",
            "horario_atividade_fisica": horario_atividade_fisica.value,
            "consumo_alcool": consumo_alcool.value,
            "tabagismo": tabagismo.value,
            "qualidade_sono": qualidade_sono.value,
            "hora_acordar": hora_acordar.value,
            "hora_dormir": hora_dormir.value,
            "comportamento_peso": comportamento_peso.value,
            "disposicao_fisica": disposicao_fisica.value,
            "funcionamento_intestinal": funcionamento_intestinal.value,
            "funcionamento_urinario": funcionamento_urinario.value,

            "internacoes_cirurgias": valores_multiselect(internacoes_sel, internacoes_detalhe.value),
            "medicamentos_suplementos": valores_multiselect(medicamentos_sel, medicamentos_detalhe.value),
            "intolerancia_alergia_alimentar": (
                intolerancias.value
                if intolerancias.value != "Outro"
                else detalhe_intolerancia.value
            ),

            "denticao": denticao.value,
            "mastigacao": mastigacao.value,
            "quem_cozinha": quem_cozinha.value,
            "apetite": apetite.value,
            "horario_mais_fome": horario_mais_fome.value,
            "ingestao_agua_dia": ingestao_agua.value,

            "tratamento_nutricional_anterior": tratamento_nutricional_anterior.value,
            "qual_tratamento": qual_tratamento.value,
            "objetivo_nutricional": valores_multiselect(objetivo_sel, objetivo_detalhe.value),
            "alimentos_preferidos": valores_multiselect(preferidos_sel, alimentos_preferidos_detalhe.value),
            "habito_beliscar": habito_beliscar.value,
            "alimentos_que_nao_gosta": valores_multiselect(nao_gosta_sel, alimentos_nao_gosta_detalhe.value),
            "habitos_fim_de_semana": valores_multiselect(fim_semana_sel, habitos_fim_semana_detalhe.value),
            "dificuldades_adesao": valores_multiselect(dificuldades_sel, dificuldades_detalhe.value),
        }

        ANAMNESES_MOCK.append(registro)
        mostrar_snackbar(page, "Anamnese salva com listas suspensas de múltipla seleção.", COR_NORMAL)

    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=18,
        expand=True,
        controls=[
            app_card(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text("Anamnese nutricional", size=26, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                                ft.Text("Formulário padronizado com listas suspensas de múltipla seleção e detalhes complementares.", size=13, color=COR_TEXTO_FRACO),
                            ],
                        ),
                        ft.FilledButton(
                            content="Salvar anamnese",
                            icon=ft.Icons.SAVE,
                            on_click=salvar_anamnese,
                            style=ft.ButtonStyle(bgcolor=COR_PRIMARIA, color="white", shape=ft.RoundedRectangleBorder(radius=12)),
                        ),
                    ],
                ),
                padding=24,
            ),

            app_card(
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Text("Identificação", size=18, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                        ft.ResponsiveRow(
                            columns=12,
                            spacing=14,
                            run_spacing=14,
                            controls=[
                                ft.Container(col={"xs": 12, "md": 6}, content=paciente_control),
                                ft.Container(col={"xs": 12, "md": 3}, content=data_anamnese),
                                ft.Container(col={"xs": 12, "md": 3}, content=numero_filhos_idades),
                            ],
                        ),
                        amamentou,
                    ],
                ),
                padding=20,
            ),

            app_card(
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Text("História clínica", size=18, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                        queixa_box,
                        queixa_detalhe,
                        doencas_box,
                        doencas_detalhe,
                        sintomas_box,
                        sintomas_detalhe,
                        pregressa_box,
                        pregressa_detalhe,
                        familiar_box,
                        familiar_detalhe,
                    ],
                ),
                padding=20,
            ),

            app_card(
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Text("Rotina, atividade física e sono", size=18, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                        ft.ResponsiveRow(
                            columns=12,
                            spacing=14,
                            run_spacing=14,
                            controls=[
                                ft.Container(col={"xs": 12, "md": 4}, content=atividade_fisica),
                                ft.Container(col={"xs": 12, "md": 4}, content=frequencia_atividade),
                                ft.Container(col={"xs": 12, "md": 4}, content=horario_atividade_fisica),
                                ft.Container(col={"xs": 12, "md": 4}, content=qualidade_sono),
                                ft.Container(col={"xs": 12, "md": 2}, content=hora_acordar),
                                ft.Container(col={"xs": 12, "md": 2}, content=hora_dormir),
                                ft.Container(col={"xs": 12, "md": 4}, content=disposicao_fisica),
                            ],
                        ),
                    ],
                ),
                padding=20,
            ),

            app_card(
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Text("Hábitos e histórico de saúde", size=18, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                        ft.ResponsiveRow(
                            columns=12,
                            spacing=14,
                            run_spacing=14,
                            controls=[
                                ft.Container(col={"xs": 12, "md": 4}, content=consumo_alcool),
                                ft.Container(col={"xs": 12, "md": 4}, content=tabagismo),
                                ft.Container(col={"xs": 12, "md": 4}, content=comportamento_peso),
                                ft.Container(col={"xs": 12, "md": 6}, content=funcionamento_intestinal),
                                ft.Container(col={"xs": 12, "md": 6}, content=funcionamento_urinario),
                                ft.Container(col={"xs": 12, "md": 6}, content=intolerancias),
                                ft.Container(col={"xs": 12, "md": 6}, content=detalhe_intolerancia),
                            ],
                        ),
                        internacoes_box,
                        internacoes_detalhe,
                        medicamentos_box,
                        medicamentos_detalhe,
                    ],
                ),
                padding=20,
            ),

            app_card(
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Text("Mastigação, apetite e ambiente alimentar", size=18, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                        ft.ResponsiveRow(
                            columns=12,
                            spacing=14,
                            run_spacing=14,
                            controls=[
                                ft.Container(col={"xs": 12, "md": 3}, content=denticao),
                                ft.Container(col={"xs": 12, "md": 3}, content=mastigacao),
                                ft.Container(col={"xs": 12, "md": 3}, content=quem_cozinha),
                                ft.Container(col={"xs": 12, "md": 3}, content=apetite),
                                ft.Container(col={"xs": 12, "md": 4}, content=horario_mais_fome),
                                ft.Container(col={"xs": 12, "md": 4}, content=ingestao_agua),
                                ft.Container(col={"xs": 12, "md": 4}, content=habito_beliscar),
                            ],
                        ),
                    ],
                ),
                padding=20,
            ),

            app_card(
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Text("Histórico nutricional e preferências", size=18, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                        ft.ResponsiveRow(
                            columns=12,
                            spacing=14,
                            run_spacing=14,
                            controls=[
                                ft.Container(col={"xs": 12, "md": 6}, content=tratamento_nutricional_anterior),
                                ft.Container(col={"xs": 12, "md": 6}, content=qual_tratamento),
                            ],
                        ),
                        objetivo_box,
                        objetivo_detalhe,
                        preferidos_box,
                        alimentos_preferidos_detalhe,
                        nao_gosta_box,
                        alimentos_nao_gosta_detalhe,
                        fim_semana_box,
                        habitos_fim_semana_detalhe,
                        dificuldades_box,
                        dificuldades_detalhe,
                    ],
                ),
                padding=20,
            ),
        ],
    )




# ============================================================
# LISTAS PADRONIZADAS - RECORDATÓRIO ALIMENTAR
# ============================================================

OPCOES_ALIMENTOS_RECORDATORIO_POR_REFEICAO = {
    "Desjejum": [
        "Água", "Café sem açúcar", "Café com açúcar", "Café com adoçante", "Café com leite",
        "Leite integral", "Leite desnatado", "Leite sem lactose", "Bebida vegetal",
        "Achocolatado", "Iogurte natural", "Iogurte grego", "Coalhada",
        "Queijo branco", "Queijo minas", "Ricota", "Requeijão", "Manteiga",
        "Pão francês", "Pão integral", "Pão de forma", "Tapioca", "Cuscuz", "Crepioca",
        "Ovo cozido", "Ovo mexido", "Omelete", "Aveia", "Granola", "Cereal matinal",
        "Banana", "Maçã", "Mamão", "Melão", "Melancia", "Morango", "Abacate", "Açaí",
        "Pasta de amendoim", "Mel", "Geleia", "Suco natural", "Vitamina de frutas",
        "Whey protein", "Outro",
    ],
    "Lanche da manhã": [
        "Água", "Café", "Chá", "Iogurte", "Coalhada", "Fruta", "Banana", "Maçã",
        "Pera", "Mamão", "Melão", "Morango", "Uva", "Tangerina", "Castanhas",
        "Amendoim", "Pasta de amendoim", "Barra de proteína", "Barra de cereal",
        "Biscoito integral", "Torrada integral", "Sanduíche natural",
        "Pão integral com queijo", "Ovo cozido", "Whey protein", "Suco natural",
        "Vitamina de frutas", "Outro",
    ],
    "Almoço": [
        "Água", "Arroz branco", "Arroz integral", "Feijão preto", "Feijão carioca",
        "Lentilha", "Grão-de-bico", "Macarrão", "Batata inglesa", "Batata doce",
        "Mandioca", "Inhame", "Farofa", "Frango grelhado", "Frango cozido",
        "Carne bovina", "Carne moída", "Peixe", "Atum", "Sardinha", "Ovo",
        "Omelete", "Porco", "Salada verde", "Alface", "Rúcula", "Agrião",
        "Tomate", "Cenoura", "Beterraba", "Pepino", "Brócolis", "Couve-flor",
        "Abobrinha", "Berinjela", "Chuchu", "Abóbora", "Azeite", "Abacate",
        "Suco natural", "Refrigerante", "Sobremesa", "Fruta", "Outro",
    ],
    "Lanche da tarde": [
        "Água", "Café", "Chá", "Leite", "Iogurte", "Coalhada", "Fruta", "Banana",
        "Maçã", "Mamão", "Morango", "Açaí", "Aveia", "Granola", "Castanhas",
        "Amendoim", "Pasta de amendoim", "Pão francês", "Pão integral", "Tapioca",
        "Crepioca", "Cuscuz", "Queijo branco", "Requeijão", "Ovo cozido",
        "Ovo mexido", "Sanduíche natural", "Barra de proteína", "Barra de cereal",
        "Whey protein", "Vitamina de frutas", "Suco natural", "Outro",
    ],
    "Jantar": [
        "Água", "Arroz branco", "Arroz integral", "Feijão", "Lentilha", "Grão-de-bico",
        "Macarrão", "Batata", "Batata doce", "Mandioca", "Sopa de legumes", "Caldo",
        "Frango grelhado", "Frango cozido", "Carne bovina", "Carne moída", "Peixe",
        "Atum", "Sardinha", "Ovo", "Omelete", "Salada verde", "Tomate", "Cenoura",
        "Beterraba", "Pepino", "Brócolis", "Couve-flor", "Abobrinha", "Berinjela",
        "Chuchu", "Abóbora", "Azeite", "Sanduíche natural", "Tapioca", "Crepioca",
        "Fruta", "Outro",
    ],
    "Ceia": [
        "Água", "Chá", "Leite", "Leite sem lactose", "Bebida vegetal", "Iogurte",
        "Coalhada", "Banana", "Maçã", "Mamão", "Morango", "Abacate", "Aveia",
        "Granola", "Castanhas", "Amêndoas", "Nozes", "Amendoim", "Pasta de amendoim",
        "Queijo branco", "Ovo cozido", "Whey protein", "Outro",
    ],
}

# Mantém compatibilidade com partes antigas do código que ainda esperem uma lista geral.
OPCOES_ALIMENTOS_RECORDATORIO = sorted({
    alimento
    for lista in OPCOES_ALIMENTOS_RECORDATORIO_POR_REFEICAO.values()
    for alimento in lista
})



# ===== PATCH: ALIMENTOS PERSONALIZADOS NO RECORDATÓRIO =====
def _recordatorio_arquivo_alimentos_personalizados():
    from pathlib import Path

    pasta = Path("data_flet")
    pasta.mkdir(parents=True, exist_ok=True)

    return pasta / "alimentos_recordatorio_personalizados.csv"


def _recordatorio_refeicao_por_titulo_dropdown(titulo):
    texto = str(titulo or "").strip()

    if texto.lower().startswith("alimentos -"):
        return texto.split("-", 1)[1].strip()

    return texto


def _recordatorio_norm_texto(valor):
    import unicodedata
    import re

    texto = str(valor or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    return " ".join(texto.split())


def _recordatorio_ler_alimentos_personalizados(refeicao=None):
    import csv

    arquivo = _recordatorio_arquivo_alimentos_personalizados()

    if not arquivo.exists():
        return []

    refeicao_norm = _recordatorio_norm_texto(refeicao) if refeicao else ""

    alimentos = []

    try:
        with arquivo.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                r_refeicao = str(row.get("refeicao") or "").strip()
                alimento = str(row.get("alimento") or "").strip()

                if not alimento:
                    continue

                if refeicao_norm and _recordatorio_norm_texto(r_refeicao) != refeicao_norm:
                    continue

                alimentos.append(alimento)
    except Exception:
        return []

    # remove duplicados preservando ordem
    vistos = set()
    saida = []

    for alimento in alimentos:
        chave = _recordatorio_norm_texto(alimento)

        if chave in vistos:
            continue

        vistos.add(chave)
        saida.append(alimento)

    return saida


def _recordatorio_salvar_alimento_personalizado(titulo_dropdown, alimento):
    import csv

    refeicao = _recordatorio_refeicao_por_titulo_dropdown(titulo_dropdown)
    alimento = str(alimento or "").strip()

    if not refeicao or not alimento:
        return False

    if _recordatorio_norm_texto(alimento) in {
        "outro",
        "nao informado",
        "não informado",
        "nenhum item selecionado",
    }:
        return False

    arquivo = _recordatorio_arquivo_alimentos_personalizados()
    existentes = []

    if arquivo.exists():
        try:
            with arquivo.open("r", encoding="utf-8", newline="") as f:
                existentes = list(csv.DictReader(f))
        except Exception:
            existentes = []

    chave_nova = (
        _recordatorio_norm_texto(refeicao),
        _recordatorio_norm_texto(alimento),
    )

    for row in existentes:
        chave = (
            _recordatorio_norm_texto(row.get("refeicao")),
            _recordatorio_norm_texto(row.get("alimento")),
        )

        if chave == chave_nova:
            return True

    existentes.append({
        "refeicao": refeicao,
        "alimento": alimento,
    })

    with arquivo.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["refeicao", "alimento"])
        writer.writeheader()
        writer.writerows(existentes)

    # Atualiza também a lista em memória para uso imediato.
    try:
        if refeicao in OPCOES_ALIMENTOS_RECORDATORIO_POR_REFEICAO:
            if alimento not in OPCOES_ALIMENTOS_RECORDATORIO_POR_REFEICAO[refeicao]:
                OPCOES_ALIMENTOS_RECORDATORIO_POR_REFEICAO[refeicao].insert(-1, alimento)
    except Exception:
        pass

    return True
# ===== FIM PATCH: ALIMENTOS PERSONALIZADOS NO RECORDATÓRIO =====


def opcoes_recordatorio_por_refeicao(titulo):
    refeicao = str(titulo or "").strip()
    opcoes = list(OPCOES_ALIMENTOS_RECORDATORIO_POR_REFEICAO.get(refeicao, []))

    if not opcoes:
        opcoes = list(OPCOES_ALIMENTOS_RECORDATORIO)

    personalizados = _recordatorio_ler_alimentos_personalizados(refeicao)

    for alimento in personalizados:
        if alimento not in opcoes:
            if "Outro" in opcoes:
                opcoes.insert(max(0, len(opcoes) - 1), alimento)
            else:
                opcoes.append(alimento)

    if "Outro" not in opcoes:
        opcoes.append("Outro")

    return opcoes


    if not opcoes:
        opcoes = list(OPCOES_ALIMENTOS_RECORDATORIO)

    if "Outro" not in opcoes:
        opcoes.append("Outro")

    return opcoes



OPCOES_BEBIDAS_RECORDATORIO = [
    "Não informado",
    "Água",
    "Café",
    "Café sem açúcar",
    "Café com açúcar",
    "Café com adoçante",
    "Café com leite",
    "Chá",
    "Leite",
    "Leite integral",
    "Leite desnatado",
    "Leite sem lactose",
    "Bebida vegetal",
    "Achocolatado",
    "Suco natural",
    "Suco industrializado",
    "Refrigerante",
    "Água de coco",
    "Isotônico",
    "Vitamina de frutas",
    "Whey protein",
    "Outro",
]






# ===== COMPATIBILIDADE: OPÇÕES AUXILIARES DO RECORDATÓRIO =====
# Listas usadas por card_refeicao_recordatorio() e recordatorio_view().
# Mantidas separadas da nova lista de alimentos por tipo de refeição.

OPCOES_BEBIDAS_RECORDATORIO = [
    "Não informado",
    "Água",
    "Café",
    "Café sem açúcar",
    "Café com açúcar",
    "Café com adoçante",
    "Café com leite",
    "Chá",
    "Leite",
    "Leite integral",
    "Leite desnatado",
    "Leite sem lactose",
    "Bebida vegetal",
    "Achocolatado",
    "Suco natural",
    "Suco industrializado",
    "Refrigerante",
    "Água de coco",
    "Isotônico",
    "Vitamina de frutas",
    "Whey protein",
    "Outro",
]

OPCOES_CARACTERISTICAS_REFEICAO = [
    "Não informado",
    "Caseira",
    "Restaurante",
    "Self-service",
    "Marmita",
    "Lanche rápido",
    "Industrializada",
    "Ultraprocessada",
    "Frita",
    "Grelhada",
    "Cozida",
    "Assada",
    "Crua",
    "Com açúcar",
    "Sem açúcar",
    "Com adoçante",
    "Rica em proteína",
    "Rica em carboidrato",
    "Rica em gordura",
    "Rica em fibras",
    "Baixa ingestão",
    "Alta ingestão",
    "Pré-treino",
    "Pós-treino",
    "Fora de casa",
    "Outro",
]

OPCOES_OBSERVACOES_RECORDATORIO = [
    "Não informado",
    "Sem fome",
    "Com fome",
    "Muita fome",
    "Comeu rápido",
    "Comeu devagar",
    "Comeu fora de casa",
    "Comeu em restaurante",
    "Comeu assistindo TV/celular",
    "Sentiu saciedade",
    "Sentiu estufamento",
    "Sentiu azia",
    "Sentiu gases",
    "Sentiu náusea",
    "Vontade de doce",
    "Vontade de salgado",
    "Beliscou entre refeições",
    "Pulou refeição",
    "Refeição incompleta",
    "Boa aceitação",
    "Baixa aceitação",
    "Pré-treino",
    "Pós-treino",
    "Outro",
]

OPCOES_HORARIOS_REFEICAO = [
    "Não informado",
    "Antes das 06h",
    "06h - 08h",
    "08h - 10h",
    "10h - 12h",
    "12h - 14h",
    "14h - 16h",
    "16h - 18h",
    "18h - 20h",
    "20h - 22h",
    "Após 22h",
]

OPCOES_QUANTIDADE_REFEICAO = [
    "Não informado",
    "Pequena",
    "Média",
    "Grande",
    "Muito grande",
    "Pouca quantidade",
    "Quantidade habitual",
    "Repetiu",
    "Não terminou",
    "Outro",
]

# ===== FIM COMPATIBILIDADE: OPÇÕES AUXILIARES DO RECORDATÓRIO =====


def card_refeicao_recordatorio(page, titulo):
    horario = campo_hora_dropdown(f"Horário - {titulo}", width=190)
    alimentos_box, alimentos_sel = multiselect_dropdown(
        page,
        f"Alimentos - {titulo}",
        opcoes_recordatorio_por_refeicao(titulo),
        width=620,
    )
    bebidas_box, bebidas_sel = multiselect_dropdown(
        page,
        f"Bebidas - {titulo}",
        OPCOES_BEBIDAS_RECORDATORIO,
        width=620,
    )
    caracteristicas_box, caracteristicas_sel = multiselect_dropdown(
        page,
        f"Características - {titulo}",
        OPCOES_CARACTERISTICAS_REFEICAO,
        width=620,
    )

    controle = app_card(
        ft.Column(
            spacing=14,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(titulo, size=18, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                        horario,
                    ],
                ),
                alimentos_box,
                bebidas_box,
                caracteristicas_box,
            ],
        ),
        padding=20,
    )

    return controle, {
        "horario": horario,
        "alimentos": alimentos_sel,
        "bebidas": bebidas_sel,
        "caracteristicas": caracteristicas_sel,
    }





# ===== COMPATIBILIDADE: MONTAGEM DO TEXTO DO RECORDATÓRIO =====
def _recordatorio_extrair_valores(valor):
    """
    Extrai valores de listas, controles Flet, dicionários ou strings.
    Usado para montar o texto final de cada refeição.
    """
    if valor is None:
        return []

    if isinstance(valor, dict):
        acumulado = []
        for chave in [
            "alimentos",
            "bebidas",
            "caracteristicas",
            "observacoes",
            "horario",
            "quantidade",
            "value",
            "values",
            "selected",
            "selecionados",
        ]:
            if chave in valor:
                acumulado.extend(_recordatorio_extrair_valores(valor.get(chave)))
        return acumulado

    if isinstance(valor, (list, tuple, set)):
        acumulado = []
        for item in valor:
            acumulado.extend(_recordatorio_extrair_valores(item))
        return acumulado

    if hasattr(valor, "value"):
        return _recordatorio_extrair_valores(getattr(valor, "value", None))

    texto = str(valor or "").strip()

    if not texto:
        return []

    if texto.lower() in {
        "não informado",
        "nao informado",
        "nenhum item selecionado",
        "none",
        "null",
    }:
        return []

    return [texto]


def montar_texto_refeicao(*partes, **kwargs):
    """
    Monta uma frase única para a refeição.

    Aceita chamadas antigas e novas:
    - montar_texto_refeicao(alimentos, bebidas, caracteristicas, observacoes)
    - montar_texto_refeicao(ctrl_dict)
    - montar_texto_refeicao(..., horario=...)
    """
    labels = [
        "Alimentos",
        "Bebidas",
        "Características",
        "Observações",
        "Horário",
        "Quantidade",
    ]

    blocos = []

    for idx, parte in enumerate(partes):
        valores = _recordatorio_extrair_valores(parte)

        if not valores:
            continue

        # Remove duplicados preservando ordem
        vistos = set()
        limpos = []

        for v in valores:
            vn = str(v).strip()
            if not vn:
                continue

            chave = vn.lower()

            if chave in vistos:
                continue

            vistos.add(chave)
            limpos.append(vn)

        if not limpos:
            continue

        label = labels[idx] if idx < len(labels) else "Itens"
        blocos.append(f"{label}: {', '.join(limpos)}")

    for chave, valor in kwargs.items():
        valores = _recordatorio_extrair_valores(valor)

        if valores:
            blocos.append(f"{str(chave).replace('_', ' ').title()}: {', '.join(valores)}")

    return " | ".join(blocos)


# Alias defensivo caso alguma parte do código use variação de nome.
montar_texto_recordatorio_refeicao = montar_texto_refeicao
# ===== FIM COMPATIBILIDADE: MONTAGEM DO TEXTO DO RECORDATÓRIO =====


def recordatorio_view(page):
    paciente_control = paciente_dropdown_padrao()
    data_registro = campo_data_calendario(page, "Data do registro", data_hoje_br(), width=190)

    desjejum_card, desjejum_ctrl = card_refeicao_recordatorio(page, "Desjejum")
    lanche_manha_card, lanche_manha_ctrl = card_refeicao_recordatorio(page, "Lanche da manhã")
    almoco_card, almoco_ctrl = card_refeicao_recordatorio(page, "Almoço")
    lanche_tarde_card, lanche_tarde_ctrl = card_refeicao_recordatorio(page, "Lanche da tarde")
    jantar_card, jantar_ctrl = card_refeicao_recordatorio(page, "Jantar")
    ceia_card, ceia_ctrl = card_refeicao_recordatorio(page, "Ceia")

    observacoes_box, observacoes_sel = multiselect_dropdown(
        page,
        "Observações gerais do recordatório",
        OPCOES_OBSERVACOES_RECORDATORIO,
        width=620,
    )

    def texto_refeicao(ctrl):
        return montar_texto_refeicao(
            ctrl["horario"],
            ctrl["alimentos"],
            ctrl["bebidas"],
            ctrl["caracteristicas"],
        )

    def salvar_recordatorio(e):
        paciente_id = paciente_control.value

        if not paciente_id:
            mostrar_snackbar(page, "Selecione um paciente.", COR_ALERTA)
            return

        registro = {
            "paciente_id": paciente_id,
            "data_registro": valor_controle(data_registro),
            "desjejum": texto_refeicao(desjejum_ctrl),
            "lanche_manha": texto_refeicao(lanche_manha_ctrl),
            "almoco": texto_refeicao(almoco_ctrl),
            "lanche_tarde": texto_refeicao(lanche_tarde_ctrl),
            "jantar": texto_refeicao(jantar_ctrl),
            "ceia": texto_refeicao(ceia_ctrl),
            "observacoes": valores_multiselect(observacoes_sel),
        }

        RECORDATORIOS_MOCK.append(registro)
        mostrar_snackbar(page, "Recordatório alimentar salvo com sucesso.", COR_NORMAL)

    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=18,
        expand=True,
        controls=[
            app_card(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text("Recordatório alimentar", size=26, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                                ft.Text(
                                    "Registro habitual das refeições com seleções padronizadas.",
                                    size=13,
                                    color=COR_TEXTO_FRACO,
                                ),
                            ],
                        ),
                        ft.FilledButton(
                            content="Salvar recordatório",
                            icon=ft.Icons.SAVE,
                            on_click=salvar_recordatorio,
                            style=ft.ButtonStyle(
                                bgcolor=COR_PRIMARIA,
                                color="white",
                                shape=ft.RoundedRectangleBorder(radius=12),
                            ),
                        ),
                    ],
                ),
                padding=24,
            ),

            app_card(
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Text("Identificação", size=18, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                        ft.Row(
                            spacing=14,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                paciente_control,
                                data_registro,
                            ],
                        ),
                    ],
                ),
                padding=20,
            ),

            desjejum_card,
            lanche_manha_card,
            almoco_card,
            lanche_tarde_card,
            jantar_card,
            ceia_card,

            app_card(
                ft.Column(
                    spacing=14,
                    controls=[
                        ft.Text("Observações gerais", size=18, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                        observacoes_box,
                    ],
                ),
                padding=20,
            ),
        ],
    )




# ============================================================
# LISTAS PADRONIZADAS - AVALIAÇÃO ANTROPOMÉTRICA
# ============================================================

OPCOES_PROTOCOLO_ANTROPOMETRIA = [
    "Não informado",
    "Avaliação inicial",
    "Reavaliação",
    "Acompanhamento mensal",
    "Acompanhamento quinzenal",
    "Avaliação pré-plano alimentar",
    "Avaliação pós-intervenção",
    "Avaliação esportiva",
    "Avaliação clínica",
]

OPCOES_CONDICAO_MEDICAO = [
    "Não informado",
    "Em jejum",
    "Sem jejum",
    "Após refeição leve",
    "Após refeição pesada",
    "Após treino",
    "Antes do treino",
    "Com retenção hídrica referida",
    "Com queixa de inchaço",
    "Dia atípico",
]

OPCOES_TIPO_BALANCA = [
    "Não informado",
    "Balança digital simples",
    "Balança mecânica",
    "Balança de bioimpedância",
    "Balança profissional",
    "Informado pelo paciente",
]

OPCOES_ROUPA_MEDICAO = [
    "Não informado",
    "Roupa leve",
    "Roupa comum",
    "Roupa pesada",
    "Sem calçado",
    "Com calçado",
    "Peso informado pelo paciente",
]

OPCOES_LOCAL_CINTURA = [
    "Não informado",
    "Menor circunferência abdominal",
    "Linha umbilical",
    "Ponto médio entre última costela e crista ilíaca",
    "Maior circunferência abdominal",
    "Medida informada pelo paciente",
]

OPCOES_OBSERVACOES_ANTROPOMETRIA = [
    "Sem observações relevantes",
    "Paciente refere retenção de líquidos",
    "Paciente refere constipação",
    "Paciente refere inchaço abdominal",
    "Paciente realizou treino antes da avaliação",
    "Paciente realizou refeição próxima da avaliação",
    "Sono ruim na noite anterior",
    "Ciclo menstrual pode influenciar medida",
    "Uso de roupa pode interferir no peso",
    "Medida de cintura precisa ser reavaliada",
    "Peso informado pelo paciente",
    "Altura informada pelo paciente",
    "Cintura informada pelo paciente",
    "Avaliação realizada em condição não padronizada",
    "Boa condição para comparação futura",
]

OPCOES_OBJETIVO_ANTROPOMETRIA = [
    "Não informado",
    "Emagrecimento",
    "Ganho de massa muscular",
    "Manutenção de peso",
    "Redução de cintura",
    "Melhora de composição corporal",
    "Acompanhamento clínico",
    "Acompanhamento esportivo",
    "Controle de risco cardiometabólico",
]




def antropometria_view(page):
    paciente_control = paciente_dropdown_padrao()
    data_avaliacao = campo_data_calendario(page, "Data da avaliação", data_hoje_br(), width=190)

    protocolo = dropdown_opcoes("Tipo de avaliação", OPCOES_PROTOCOLO_ANTROPOMETRIA, width=280)
    objetivo = dropdown_opcoes("Objetivo antropométrico", OPCOES_OBJETIVO_ANTROPOMETRIA, width=300)
    condicao_medicao = dropdown_opcoes("Condição da medição", OPCOES_CONDICAO_MEDICAO, width=300)
    tipo_balanca = dropdown_opcoes("Tipo de balança", OPCOES_TIPO_BALANCA, width=280)
    roupa_medicao = dropdown_opcoes("Roupa/calçado na medição", OPCOES_ROUPA_MEDICAO, width=300)
    local_cintura = dropdown_opcoes("Local da medida da cintura", OPCOES_LOCAL_CINTURA, width=360)

    peso = ft.TextField(label="Peso em kg", width=180, border_radius=12)
    altura = ft.TextField(label="Altura em m ou cm", width=180, border_radius=12)
    cintura = ft.TextField(label="Circunferência da cintura em cm", width=260, border_radius=12)

    observacoes_box, observacoes_sel = multiselect_dropdown(
        page,
        "Observações antropométricas",
        OPCOES_OBSERVACOES_ANTROPOMETRIA,
        width=620,
    )

    resultado_area = ft.Column(spacing=12)

    def atualizar_preview(e=None):
        paciente = obter_paciente_por_id(paciente_control.value)
        sexo = paciente.get("sexo", "") if paciente else ""

        imc = calcular_imc(peso.value, altura.value)
        classificacao = classificar_imc(imc)
        risco = risco_cintura(cintura.value, sexo)

        resultado_area.controls = [
            ft.ResponsiveRow(
                columns=12,
                spacing=16,
                run_spacing=16,
                controls=[
                    ft.Container(
                        col={"xs": 12, "md": 4},
                        content=app_card(
                            ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text("IMC", size=13, color=COR_TEXTO_FRACO),
                                    ft.Text(str(imc) if imc else "-", size=28, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                                ],
                            ),
                            padding=18,
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "md": 4},
                        content=app_card(
                            ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text("Classificação", size=13, color=COR_TEXTO_FRACO),
                                    ft.Text(classificacao, size=20, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                                ],
                            ),
                            padding=18,
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "md": 4},
                        content=app_card(
                            ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text("Risco cintura", size=13, color=COR_TEXTO_FRACO),
                                    ft.Text(
                                        risco,
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color=COR_ALERTA if "risco" in str(risco).lower() else COR_NORMAL,
                                    ),
                                ],
                            ),
                            padding=18,
                        ),
                    ),
                ],
            )
        ]

        page.update()

    def salvar_antropometria(e):
        paciente_id = paciente_control.value

        if not paciente_id:
            mostrar_snackbar(page, "Selecione um paciente.", COR_ALERTA)
            return

        paciente = obter_paciente_por_id(paciente_id)
        sexo = paciente.get("sexo", "") if paciente else ""

        imc = calcular_imc(peso.value, altura.value)
        classificacao = classificar_imc(imc)
        risco = risco_cintura(cintura.value, sexo)

        ANTROPOMETRIAS_MOCK.append(
            {
                "paciente_id": paciente_id,
                "data_avaliacao": valor_controle(data_avaliacao),
                "tipo_avaliacao": protocolo.value,
                "objetivo_antropometrico": objetivo.value,
                "condicao_medicao": condicao_medicao.value,
                "tipo_balanca": tipo_balanca.value,
                "roupa_medicao": roupa_medicao.value,
                "local_cintura": local_cintura.value,
                "peso": peso.value,
                "altura": altura.value,
                "circunferencia_cintura": cintura.value,
                "imc": imc,
                "classificacao_imc": classificacao,
                "risco_cintura": risco,
                "observacoes": valores_multiselect(observacoes_sel),
            }
        )

        atualizar_preview()
        mostrar_snackbar(page, "Avaliação antropométrica salva com sucesso.", COR_NORMAL)

    peso.on_change = atualizar_preview
    altura.on_change = atualizar_preview
    cintura.on_change = atualizar_preview
    paciente_control.on_change = atualizar_preview

    atualizar_preview()

    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=18,
        expand=True,
        controls=[
            app_card(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text("Avaliação antropométrica", size=26, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                                ft.Text(
                                    "Peso, altura, cintura e contexto padronizado da medição.",
                                    size=13,
                                    color=COR_TEXTO_FRACO,
                                ),
                            ],
                        ),
                        ft.FilledButton(
                            content="Salvar avaliação",
                            icon=ft.Icons.SAVE,
                            on_click=salvar_antropometria,
                            style=ft.ButtonStyle(
                                bgcolor=COR_PRIMARIA,
                                color="white",
                                shape=ft.RoundedRectangleBorder(radius=12),
                            ),
                        ),
                    ],
                ),
                padding=24,
            ),

            app_card(
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Text("Identificação", size=18, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                        ft.Row(
                            spacing=14,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                paciente_control,
                                data_avaliacao,
                            ],
                        ),
                    ],
                ),
                padding=20,
            ),

            app_card(
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Text("Contexto da avaliação", size=18, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                        ft.ResponsiveRow(
                            columns=12,
                            spacing=14,
                            run_spacing=14,
                            controls=[
                                ft.Container(col={"xs": 12, "md": 4}, content=protocolo),
                                ft.Container(col={"xs": 12, "md": 4}, content=objetivo),
                                ft.Container(col={"xs": 12, "md": 4}, content=condicao_medicao),
                                ft.Container(col={"xs": 12, "md": 4}, content=tipo_balanca),
                                ft.Container(col={"xs": 12, "md": 4}, content=roupa_medicao),
                                ft.Container(col={"xs": 12, "md": 4}, content=local_cintura),
                            ],
                        ),
                    ],
                ),
                padding=20,
            ),

            app_card(
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Text("Medidas", size=18, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                        ft.ResponsiveRow(
                            columns=12,
                            spacing=14,
                            run_spacing=14,
                            controls=[
                                ft.Container(col={"xs": 12, "md": 3}, content=peso),
                                ft.Container(col={"xs": 12, "md": 3}, content=altura),
                                ft.Container(col={"xs": 12, "md": 4}, content=cintura),
                            ],
                        ),
                        observacoes_box,
                    ],
                ),
                padding=20,
            ),

            resultado_area,
        ],
    )



# ===== PATCH: DIAGNÓSTICO NUTRICIONAL INTELIGENTE NO PDF NUTRICIONAL =====
def _pdf_adicionar_diagnostico_inteligente_nutricao(story, exames, h2, body, small):
    """
    Adiciona ao relatório nutricional PDF o diagnóstico nutricional.
    """
    try:
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from xml.sax.saxutils import escape as xml_escape
    except Exception:
        return

    try:
        from diagnostico_nutricional_inteligente import gerar_diagnostico_inteligente
    except Exception as exc:
        story.append(Paragraph("Diagnóstico nutricional", h2))
        story.append(Paragraph(f"Módulo indisponível: {xml_escape(str(exc))}", body))
        story.append(Spacer(1, 10))
        return

    try:
        diag = gerar_diagnostico_inteligente(exames or [])
    except Exception as exc:
        story.append(Paragraph("Diagnóstico nutricional", h2))
        story.append(Paragraph(f"Não foi possível gerar o diagnóstico inteligente: {xml_escape(str(exc))}", body))
        story.append(Spacer(1, 10))
        return

    def safe(valor):
        return xml_escape(str(valor or ""))

    total = diag.get("total_exames_analisados", 0)
    alteracoes = diag.get("total_alteracoes", 0)
    alertas_qtd = diag.get("total_alertas_combinados", 0)

    story.append(Paragraph("Diagnóstico nutricional", h2))

    story.append(Paragraph(
        safe(
            f"Foram analisados {total} exame(s). "
            f"A análise identificou {alteracoes} resultado(s) fora da referência laboratorial "
            f"e {alertas_qtd} alerta(s) combinado(s)."
        ),
        body,
    ))
    story.append(Spacer(1, 8))

    alertas = diag.get("alertas", []) or []

    if alertas:
        story.append(Paragraph("Alertas combinados prioritários", h2))

        dados_alertas = [["Alerta", "Possível diagnóstico/alteração", "Conduta sugerida"]]

        for alerta in alertas[:6]:
            dados_alertas.append([
                Paragraph(safe(alerta.get("titulo", "")), small),
                Paragraph(safe(alerta.get("possivel_condicao", "")), small),
                Paragraph(safe(alerta.get("conduta", "")), small),
            ])

        tabela_alertas = Table(
            dados_alertas,
            colWidths=[4.0 * cm, 5.2 * cm, 7.0 * cm],
            repeatRows=1,
        )

        tabela_alertas.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111827")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D1D5DB")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))

        story.append(tabela_alertas)
        story.append(Spacer(1, 10))

    story.append(Paragraph(
        "Nota: este diagnóstico é um apoio técnico nutricional. Não substitui diagnóstico médico, "
        "avaliação clínica individualizada ou prescrição medicamentosa.",
        body,
    ))
    story.append(Spacer(1, 14))
# ===== FIM PATCH: DIAGNÓSTICO NUTRICIONAL INTELIGENTE NO PDF NUTRICIONAL =====


def resumo_nutricional_view(page):
    """Ponte automática: rota antiga de Nutrição redirecionada para a visão completa com gráficos."""
    _page = locals().get('page')
    if _page is None:
        valores = list(locals().values())
        _page = valores[0] if valores else None
    return nutricao_view(_page)

def inicializar_base_flet():
    DATA_FLET_DIR.mkdir(parents=True, exist_ok=True)

    for nome_arquivo, cabecalho in CSV_SCHEMA_FLET.items():
        destino = DATA_FLET_DIR / nome_arquivo
        origem = DATA_ANTIGO_DIR / nome_arquivo

        if destino.exists():
            continue

        with destino.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=cabecalho)
            writer.writeheader()
        print(f"[DATA_FLET] Criado vazio: {nome_arquivo}")


def caminho_csv_flet(nome_arquivo):
    inicializar_base_flet()
    return DATA_FLET_DIR / nome_arquivo


def ler_csv_data_flet(nome_arquivo):
    caminho = caminho_csv_flet(nome_arquivo)

    try:
        with caminho.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    except UnicodeDecodeError:
        with caminho.open("r", encoding="latin-1", newline="") as f:
            return list(csv.DictReader(f))
    except Exception as exc:
        print(f"[DATA_FLET] Erro ao ler {nome_arquivo}: {exc}")
        return []


def exames_data_flet_por_paciente(paciente_id):
    exames = ler_csv_data_flet("exames.csv")

    return [
        e for e in exames
        if str(e.get("paciente_id", "")).strip() == str(paciente_id).strip()
    ]


def analises_data_flet_por_paciente(paciente_id):
    analises = ler_csv_data_flet("analise_exames.csv")

    return [
        a for a in analises
        if str(a.get("paciente_id", "")).strip() == str(paciente_id).strip()
    ]


def status_paciente_data_flet(paciente_id):
    exames = exames_data_flet_por_paciente(paciente_id)
    analises = analises_data_flet_por_paciente(paciente_id)

    if not exames:
        return "Sem exames"

    if not analises:
        return "Sem análise"

    achou_alerta = False

    for item in analises:
        texto = " ".join(str(v or "") for v in item.values()).lower()

        if "crítico" in texto or "critico" in texto:
            return "Crítico"

        if (
            "alto" in texto
            or "baixo" in texto
            or "alterado" in texto
            or "fora" in texto
            or "atenção" in texto
            or "atencao" in texto
        ):
            achou_alerta = True

    return "Atenção" if achou_alerta else "Normal"


def atualizar_pacientes_csv_real_definitivo():
    """
    Mantém o nome antigo apenas por compatibilidade.
    A fonte real agora é data_flet/pacientes.csv.
    """
    global PACIENTES_MOCK

    try:
        PACIENTES_MOCK
    except NameError:
        PACIENTES_MOCK = []

    pacientes_csv = ler_csv_data_flet("pacientes.csv")
    pacientes = []

    for row in pacientes_csv:
        paciente_id = str(row.get("paciente_id", "")).strip()
        nome = str(row.get("nome", "")).strip()

        if not paciente_id or not nome:
            continue

        exames = exames_data_flet_por_paciente(paciente_id)

        datas = [
            str(e.get("data_exame") or e.get("data") or "").strip()
            for e in exames
            if str(e.get("data_exame") or e.get("data") or "").strip()
        ]

        ultimo_exame = sorted(datas)[-1] if datas else "-"

        pacientes.append(
            {
                "id": paciente_id,
                "nome": nome,
                "idade": str(row.get("idade", "")).strip() or "-",
                "data_nascimento": str(row.get("data_nascimento", "")).strip(),
                "sexo": str(row.get("sexo", "Não informado")).strip() or "Não informado",
                "telefone": str(row.get("telefone", "")).strip(),
                "email": str(row.get("email", "")).strip(),
                "profissao": str(row.get("profissao", "")).strip(),
                "horario_trabalho": str(row.get("horario_trabalho", "")).strip(),
                "observacoes": str(row.get("observacoes", "")).strip(),
                "ultimo_exame": ultimo_exame,
                "status": status_paciente_data_flet(paciente_id),
                "exames": len(exames),
                "origem": "DATA_FLET",
            }
        )

    PACIENTES_MOCK.clear()
    PACIENTES_MOCK.extend(pacientes)

    if PACIENTES_MOCK:
        ids = [str(p["id"]) for p in PACIENTES_MOCK]
        atual = str(globals().get("PACIENTE_SELECIONADO_ID", ""))

        if atual not in ids:
            globals()["PACIENTE_SELECIONADO_ID"] = str(PACIENTES_MOCK[0]["id"])
    else:
        globals()["PACIENTE_SELECIONADO_ID"] = ""

    print(f"[DATA_FLET] Pacientes carregados na UI: {len(PACIENTES_MOCK)}")
    print("[DATA_FLET] Nomes:", [p["nome"] for p in PACIENTES_MOCK[:10]])

    return PACIENTES_MOCK





# ============================================================
# FONTE ÚNICA DATA_FLET - PACIENTE, EXAMES, ANAMNESE E HISTÓRICO
# ============================================================

def data_flet_dir_unico():
    pasta = Path(__file__).resolve().parent / "data_flet"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def csv_data_flet_unico(nome_arquivo):
    return data_flet_dir_unico() / nome_arquivo


def ler_csv_data_flet_unico(nome_arquivo, colunas=None):
    caminho = csv_data_flet_unico(nome_arquivo)

    if not caminho.exists():
        with caminho.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=colunas or [])
            writer.writeheader()
        return []

    try:
        with caminho.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    except UnicodeDecodeError:
        with caminho.open("r", encoding="latin-1", newline="") as f:
            return list(csv.DictReader(f))
    except Exception as exc:
        print(f"[DATA_FLET] Erro lendo {nome_arquivo}: {exc}")
        return []


def normalizar_data_iso_ou_br(valor):
    valor = str(valor or "").strip()

    if not valor:
        return ""

    if "/" in valor:
        partes = valor.split("/")
        if len(partes) == 3:
            dd, mm, yyyy = partes
            if len(yyyy) == 4:
                return f"{yyyy}-{mm.zfill(2)}-{dd.zfill(2)}"

    return valor


def data_iso_para_br_seguro(valor):
    valor = str(valor or "").strip()

    if not valor:
        return "-"

    if "/" in valor:
        return valor

    partes = valor.split("-")
    if len(partes) == 3:
        yyyy, mm, dd = partes
        return f"{dd.zfill(2)}/{mm.zfill(2)}/{yyyy}"

    return valor


def obter_paciente_por_id(paciente_id):
    paciente_id = str(paciente_id or "").strip()

    for p in ler_csv_data_flet_unico("pacientes.csv"):
        if str(p.get("paciente_id", "")).strip() == paciente_id:
            return {
                "id": str(p.get("paciente_id", "")).strip(),
                "nome": str(p.get("nome", "")).strip(),
                "idade": str(p.get("idade", "")).strip() or "-",
                "data_nascimento": str(p.get("data_nascimento", "")).strip(),
                "sexo": str(p.get("sexo", "Não informado")).strip() or "Não informado",
                "telefone": str(p.get("telefone", "")).strip(),
                "email": str(p.get("email", "")).strip(),
                "profissao": str(p.get("profissao", "")).strip(),
                "horario_trabalho": str(p.get("horario_trabalho", "")).strip(),
                "observacoes": str(p.get("observacoes", "")).strip(),
            }

    for p in globals().get("PACIENTES_MOCK", []):
        if str(p.get("id", "")) == paciente_id:
            return p

    return None


def nome_paciente_por_id(paciente_id):
    paciente = obter_paciente_por_id(paciente_id)
    return paciente.get("nome", "Paciente") if paciente else "Paciente"



# ============================================================
# AJUSTE VISUAL - NOME DO EXAME NO HISTÓRICO
# ============================================================

def nome_exame_para_exibicao(item):
    """
    Retorna o melhor nome disponível para exibir no histórico.
    Compatível com importação de PDF, cadastro manual e versões antigas.
    """
    if not isinstance(item, dict):
        return "-"

    campos = [
        "nome_exame",
        "nome_padronizado",
        "nome",
        "exame",
        "analito",
        "tipo_exame",
        "descricao",
    ]

    for campo in campos:
        valor = str(item.get(campo) or "").strip()
        if valor:
            return valor

    return "-"


def garantir_nome_exame_item(item):
    """
    Preenche todos os aliases de nome do exame para evitar telas com coluna Exame vazia.
    """
    if not isinstance(item, dict):
        return item

    nome = nome_exame_para_exibicao(item)

    if nome and nome != "-":
        item["nome_exame"] = item.get("nome_exame") or nome
        item["nome_padronizado"] = item.get("nome_padronizado") or nome
        item["nome"] = item.get("nome") or nome
        item["exame"] = item.get("exame") or nome
        item["analito"] = item.get("analito") or nome
        item["tipo_exame"] = item.get("tipo_exame") or nome
        item["descricao"] = item.get("descricao") or nome

    return item


def buscar_resultados_paciente(paciente_id):
    """
    Fonte oficial para Dashboard, Nutrição e PDF.
    Lê sempre data_flet/analise_exames.csv.
    """
    paciente_id = str(paciente_id or "").strip()

    linhas = ler_csv_data_flet_unico(
        "analise_exames.csv",
        [
            "analise_id", "paciente_id", "data_exame", "nome_exame", "nome_padronizado",
            "resultado", "unidade", "valor_min", "valor_max", "status",
            "mensagem", "fonte_referencia"
        ],
    )

    resultados = []

    for row in linhas:
        if str(row.get("paciente_id", "")).strip() != paciente_id:
            continue

        nome = (
            row.get("nome_exame")
            or row.get("nome_padronizado")
            or row.get("exame_nome")
            or ""
        )

        valor_min = str(row.get("valor_min", "")).strip()
        valor_max = str(row.get("valor_max", "")).strip()

        referencia = str(row.get("referencia", "")).strip()
        if not referencia and (valor_min or valor_max):
            referencia = f"{valor_min} - {valor_max}".strip(" -")

        status = str(row.get("status", "")).strip()

        if status.lower() == "acima":
            status = "Alto"
        elif status.lower() == "abaixo":
            status = "Baixo"

        data_exame = normalizar_data_iso_ou_br(row.get("data_exame", "") or row.get("data", ""))

        resultados.append(
            {
                "paciente_id": paciente_id,
                "data": data_exame,
                "data_exame": data_exame,
                "exame_nome": str(nome).strip(),
                "nome_exame": str(nome).strip(),
                "nome_padronizado": str(row.get("nome_padronizado", nome)).strip(),
                "resultado": str(row.get("resultado", "")).strip(),
                "unidade": str(row.get("unidade", "")).strip(),
                "referencia": referencia,
                "valor_min": valor_min,
                "valor_max": valor_max,
                "status": status or "Sem análise",
                "observacao": str(row.get("mensagem", "") or row.get("observacoes", "")).strip(),
                "observacoes": str(row.get("mensagem", "") or row.get("observacoes", "")).strip(),
                "fonte": str(row.get("fonte_referencia", "")).strip(),
                "fonte_referencia": str(row.get("fonte_referencia", "")).strip(),
            }
        )

    resultados.sort(key=lambda x: x.get("data", ""))
    return resultados


def resultados_por_paciente_data(paciente_id, data_iso):
    data_iso = normalizar_data_iso_ou_br(data_iso)

    return [
        r for r in buscar_resultados_paciente(paciente_id)
        if normalizar_data_iso_ou_br(r.get("data", "")) == data_iso
    ]


def carregar_anamneses_paciente_data_flet(paciente_id):
    paciente_id = str(paciente_id or "").strip()

    linhas = ler_csv_data_flet_unico("anamnese.csv")

    return [
        row for row in linhas
        if str(row.get("paciente_id", "")).strip() == paciente_id
    ]


def carregar_recordatorios_paciente_data_flet(paciente_id):
    paciente_id = str(paciente_id or "").strip()

    linhas = ler_csv_data_flet_unico("recordatorio_habitual.csv")

    return [
        row for row in linhas
        if str(row.get("paciente_id", "")).strip() == paciente_id
    ]


def carregar_antropometrias_paciente_data_flet(paciente_id):
    paciente_id = str(paciente_id or "").strip()

    linhas = ler_csv_data_flet_unico("antropometria.csv")

    return [
        row for row in linhas
        if str(row.get("paciente_id", "")).strip() == paciente_id
    ]


def dados_paciente_integrados(paciente_id):
    paciente = obter_paciente_por_id(paciente_id) or {}

    anamneses = carregar_anamneses_paciente_data_flet(paciente_id)
    recordatorios = carregar_recordatorios_paciente_data_flet(paciente_id)
    antropometrias = carregar_antropometrias_paciente_data_flet(paciente_id)
    exames = buscar_resultados_paciente(paciente_id)

    return {
        "paciente": paciente,
        "anamneses": anamneses,
        "anamnese": anamneses[-1] if anamneses else {},
        "recordatorios": recordatorios,
        "recordatorio": recordatorios[-1] if recordatorios else {},
        "antropometrias": antropometrias,
        "antropometria": antropometrias[-1] if antropometrias else {},
        "exames": exames,
        "resultados": exames,
    }


def contar_status_resultados_data_flet(resultados):
    normais = 0
    alterados = 0
    criticos = 0

    for r in resultados:
        status = str(r.get("status", "")).lower()

        if "crít" in status or "crit" in status:
            criticos += 1
        elif "alto" in status or "baixo" in status or "acima" in status or "abaixo" in status or "alter" in status:
            alterados += 1
        elif "normal" in status:
            normais += 1

    return normais, alterados, criticos


def atualizar_pacientes_csv_real_definitivo():
    """
    Atualiza a lista de pacientes sempre usando data_flet.
    Também calcula contagem real de exames pelo CSV.
    """
    global PACIENTES_MOCK

    try:
        PACIENTES_MOCK
    except NameError:
        PACIENTES_MOCK = []

    pacientes_csv = ler_csv_data_flet_unico("pacientes.csv")
    pacientes = []

    for row in pacientes_csv:
        paciente_id = str(row.get("paciente_id", "")).strip()
        nome = str(row.get("nome", "")).strip()

        if not paciente_id or not nome:
            continue

        resultados = buscar_resultados_paciente(paciente_id)
        normais, alterados, criticos = contar_status_resultados_data_flet(resultados)

        datas = [
            r.get("data", "")
            for r in resultados
            if r.get("data", "")
        ]

        ultimo_exame = data_iso_para_br_seguro(sorted(datas)[-1]) if datas else "-"

        if criticos:
            status = "Crítico"
        elif alterados:
            status = "Atenção"
        elif resultados:
            status = "Normal"
        else:
            status = "Sem exames"

        pacientes.append(
            {
                "id": paciente_id,
                "nome": nome,
                "idade": str(row.get("idade", "")).strip() or "-",
                "data_nascimento": str(row.get("data_nascimento", "")).strip(),
                "sexo": str(row.get("sexo", "Não informado")).strip() or "Não informado",
                "telefone": str(row.get("telefone", "")).strip(),
                "email": str(row.get("email", "")).strip(),
                "profissao": str(row.get("profissao", "")).strip(),
                "horario_trabalho": str(row.get("horario_trabalho", "")).strip(),
                "observacoes": str(row.get("observacoes", "")).strip(),
                "ultimo_exame": ultimo_exame,
                "status": status,
                "exames": len(resultados),
                "origem": "DATA_FLET",
            }
        )

    PACIENTES_MOCK.clear()
    PACIENTES_MOCK.extend(pacientes)

    if PACIENTES_MOCK:
        ids = [str(p["id"]) for p in PACIENTES_MOCK]
        atual = str(globals().get("PACIENTE_SELECIONADO_ID", ""))

        if atual not in ids:
            globals()["PACIENTE_SELECIONADO_ID"] = str(PACIENTES_MOCK[0]["id"])
    else:
        globals()["PACIENTE_SELECIONADO_ID"] = ""

    print(f"[DATA_FLET] Pacientes carregados na UI: {len(PACIENTES_MOCK)}")
    print("[DATA_FLET] Pacientes:", [(p["id"], p["nome"], p["exames"]) for p in PACIENTES_MOCK])

    return PACIENTES_MOCK





# ============================================================
# CATÁLOGO CLÍNICO FLEURY - CARREGADO DE DATA_FLET
# ============================================================

def _slug_catalogo_fleury(txt):
    import unicodedata
    import re
    txt = str(txt or "")
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode("ascii")
    txt = txt.lower()
    txt = re.sub(r"[^a-z0-9]+", "_", txt).strip("_")
    return txt


def carregar_catalogo_fleury_data_flet():
    caminho = Path(__file__).resolve().parent / "data_flet" / "referencias_exames.csv"

    if not caminho.exists():
        return []

    try:
        with caminho.open("r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
    except UnicodeDecodeError:
        with caminho.open("r", encoding="latin-1", newline="") as f:
            rows = list(csv.DictReader(f))
    except Exception as exc:
        print(f"[CATALOGO FLEURY] Erro ao ler referências: {exc}")
        return []

    catalogo = []

    for r in rows:
        nome = str(r.get("nome_exame") or r.get("nome") or "").strip()

        if not nome:
            continue

        grupo = str(r.get("grupo") or "Exames laboratoriais").strip()
        unidade = str(r.get("unidade") or "").strip()
        referencia = str(r.get("referencia") or r.get("referencia_texto") or "").strip()
        fonte = str(r.get("fonte_referencia") or r.get("fonte") or "").strip()
        status = str(r.get("status") or "Completa").strip()

        catalogo.append({
            "id": _slug_catalogo_fleury(nome),
            "nome": nome,
            "grupo": grupo,
            "unidade": unidade,
            "referencia": referencia,
            "fonte": fonte,
            "status": status,
        })

    return catalogo


def aplicar_catalogo_fleury_nas_listas_do_app():
    """
    Atualiza automaticamente listas globais de exames/referências existentes no app.
    Não depende do nome exato da variável.
    """
    catalogo = carregar_catalogo_fleury_data_flet()

    if not catalogo:
        print("[CATALOGO FLEURY] Nenhum item carregado.")
        return

    adicionados = 0

    for nome_global, valor in list(globals().items()):
        if not isinstance(valor, list):
            continue

        if not valor:
            continue

        if not all(isinstance(x, dict) for x in valor[: min(len(valor), 5)]):
            continue

        chaves = set()
        for item in valor[: min(len(valor), 10)]:
            chaves.update(item.keys())

        # Lista simples para dropdown de exames: id, nome, grupo, referencia
        if {"id", "nome", "grupo", "referencia"}.issubset(chaves) and "unidade" not in chaves:
            nomes_existentes = {str(x.get("nome", "")).strip().lower() for x in valor}

            for e in catalogo:
                if e["nome"].lower() not in nomes_existentes:
                    valor.append({
                        "id": e["id"],
                        "nome": e["nome"],
                        "grupo": e["grupo"],
                        "referencia": e["referencia"],
                    })
                    nomes_existentes.add(e["nome"].lower())
                    adicionados += 1

        # Lista completa de referências: id, nome, grupo, unidade, referencia, fonte, status
        elif {"id", "nome", "grupo", "unidade", "referencia"}.issubset(chaves):
            nomes_existentes = {
                (str(x.get("nome", "")).strip().lower(), str(x.get("unidade", "")).strip().lower())
                for x in valor
            }

            for e in catalogo:
                chave = (e["nome"].lower(), e["unidade"].lower())

                if chave not in nomes_existentes:
                    valor.append({
                        "id": e["id"],
                        "nome": e["nome"],
                        "grupo": e["grupo"],
                        "unidade": e["unidade"],
                        "referencia": e["referencia"],
                        "fonte": e["fonte"],
                        "status": e["status"],
                    })
                    nomes_existentes.add(chave)
                    adicionados += 1

    print(f"[CATALOGO FLEURY] Itens carregados: {len(catalogo)} | adicionados às listas do app: {adicionados}")


def main_original_nutrisoft(page: ft.Page):
    page.title = "NutriSoft"
    page.bgcolor = COR_BG
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    selected_index = 0

    content_area = ft.Container(
        expand=True,
        padding=24,
        content=None,
    )

    def abrir_exames_com_paciente(e=None, paciente_id=None):
        if paciente_id:
            globals()["PACIENTE_SELECIONADO_ID"] = str(paciente_id)
        content_area.content = exames_view(page)
        nav.selected_index = 2
        page.update()


    def abrir_detalhe_paciente(paciente):
        content_area.content = detalhe_paciente_view(
            paciente,
            on_voltar=lambda e: trocar_tela(1),
            on_novo_exame=lambda e: trocar_tela(2),
            on_excluir=lambda p: confirmar_exclusao_paciente(
                page,
                p,
                on_voltar=lambda e: trocar_tela(1),
            ),
        )
        page.update()


    def trocar_tela(index):
        nonlocal selected_index
        selected_index = index
        nav.selected_index = index

        if index == 0:
            content_area.content = dashboard_view(
                page,
                on_novo_exame=abrir_exames_com_paciente,
                on_excluir=lambda p: confirmar_exclusao_paciente(
                    page,
                    p,
                    on_voltar=lambda e: trocar_tela(0),
                ),
            )
        elif index == 1:
            content_area.content = pacientes_view(on_abrir=abrir_detalhe_paciente)
        elif index == 2:
            content_area.content = exames_view(page)
        elif index == 3:
            content_area.content = anamnese_view(page)
        elif index == 4:
            content_area.content = recordatorio_view(page)
        elif index == 5:
            content_area.content = antropometria_view(page)
        elif index == 6:
            content_area.content = resumo_nutricional_view(page)
        elif index == 7:
            content_area.content = referencias_view(page)
        elif index == 8:
            content_area.content = placeholder_view(
                "Configurações",
                "Aqui entram preferências, backup, importação e parâmetros do sistema.",
            )

        page.update()

    def on_nav_change(e):
        trocar_tela(e.control.selected_index)

    nav = ft.NavigationRail(
        selected_index=selected_index,
        extended=True,
        min_width=80,
        min_extended_width=230,
        bgcolor="#FFFFFF",
        group_alignment=-0.85,
        on_change=on_nav_change,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED,
                selected_icon=ft.Icons.DASHBOARD,
                label="Dashboard",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PERSON_OUTLINE,
                selected_icon=ft.Icons.PERSON,
                label="Pacientes",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.BIOTECH_OUTLINED,
                selected_icon=ft.Icons.BIOTECH,
                # Exames agrupados por categoria e ordenados por prioridade
                label="Exames",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.ARTICLE_OUTLINED,
                selected_icon=ft.Icons.ARTICLE,
                label="Anamnese",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.RESTAURANT_MENU_OUTLINED,
                selected_icon=ft.Icons.RESTAURANT_MENU,
                label="Recordatório",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.MONITOR_WEIGHT_OUTLINED,
                selected_icon=ft.Icons.MONITOR_WEIGHT,
                label="Antropometria",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.INSIGHTS_OUTLINED,
                selected_icon=ft.Icons.INSIGHTS,
                label="Nutrição",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.MENU_BOOK_OUTLINED,
                selected_icon=ft.Icons.MENU_BOOK,
                label="Referências",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Configurações",
            ),
        ],
    )

    sidebar = ft.Container(
        width=260,
        bgcolor="#FFFFFF",
        padding=ft.Padding.only(top=22, bottom=18),
        content=ft.Column(
            spacing=18,
            controls=[
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=22),
                    content=ft.Row(
                        spacing=12,
                        controls=[
                            ft.Container(
                                width=42,
                                height=42,
                                border_radius=14,
                                bgcolor=COR_PRIMARIA,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Text(
                                    "N",
                                    color="white",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ),
                            ft.Column(
                                spacing=0,
                                controls=[
                                    ft.Text(
                                        "NutriSoft",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color=COR_TEXTO,
                                    ),
                                    ft.Text(
                                        "Análise clínica",
                                        size=12,
                                        color=COR_TEXTO_FRACO,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                ft.Divider(height=1, color="#E5E7EB"),
                ft.Container(
                    expand=True,
                    content=nav,
                ),
            ],
        ),
    )

    content_area.content = dashboard_view(
        page,
        on_novo_exame=abrir_exames_com_paciente,
        on_excluir=lambda p: confirmar_exclusao_paciente(
            page,
            p,
            on_voltar=lambda e: trocar_tela(0),
        ),
    )

    page.add(
        ft.Row(
            expand=True,
            spacing=0,
            controls=[
                sidebar,
                ft.VerticalDivider(width=1, color="#E5E7EB"),
                content_area,
            ],
        )
    )



# ============================================================
# FONTE ÚNICA DATA_FLET - EXAMES / DASHBOARD / PACIENTES
# ============================================================

def _nf_txt(valor):
    import unicodedata
    import re
    txt = str(valor or "").strip()
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode("ascii")
    txt = re.sub(r"\s+", " ", txt)
    return txt.lower().strip()


def _csv_flet(nome):
    return Path(__file__).resolve().parent / "data_flet" / nome


def _ler_csv_flet(nome):
    caminho = _csv_flet(nome)

    if not caminho.exists():
        return []

    try:
        with caminho.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    except UnicodeDecodeError:
        with caminho.open("r", encoding="latin-1", newline="") as f:
            return list(csv.DictReader(f))
    except Exception as exc:
        print(f"[DATA_FLET] Erro ao ler {nome}: {exc}")
        return []


def _data_para_iso(valor):
    valor = str(valor or "").strip()

    if not valor:
        return ""

    if re.match(r"^\d{4}-\d{2}-\d{2}$", valor):
        return valor

    for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(valor, fmt).strftime("%Y-%m-%d")
        except Exception:
            pass

    return valor


def _data_para_br(valor):
    valor = str(valor or "").strip()

    if not valor:
        return "-"

    if re.match(r"^\d{2}/\d{2}/\d{4}$", valor):
        return valor

    try:
        return datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return valor


def _numero_float_flet(valor):
    valor = str(valor or "").strip()
    valor = re.sub(r"[^0-9,.\-]", "", valor)

    if not valor:
        return None

    if "," in valor:
        valor = valor.replace(".", "").replace(",", ".")

    try:
        return float(valor)
    except Exception:
        return None


def _status_padrao_exame(status):
    st = str(status or "").strip().lower()

    if st in ["normal", "ok", "dentro", "dentro da referência", "dentro da referencia"]:
        return "Normal"

    if st in ["alto", "acima", "acima da referência", "acima da referencia"]:
        return "Alto"

    if st in ["baixo", "abaixo", "abaixo da referência", "abaixo da referencia"]:
        return "Baixo"

    if st:
        return str(status).strip()

    return "Sem análise"


def _indice_referencias_flet():
    refs = _ler_csv_flet("referencias_exames.csv")
    idx = {}

    for r in refs:
        nomes = [
            r.get("nome"),
            r.get("nome_exame"),
            r.get("nome_padronizado"),
        ]

        for nome in nomes:
            if nome:
                idx[_nf_txt(nome)] = r

    return idx


def _referencia_texto_linha(row, ref=None):
    ref = ref or {}

    texto = (
        row.get("referencia")
        or row.get("referencia_texto")
        or ref.get("referencia")
        or ref.get("referencia_texto")
        or ""
    )

    if texto:
        return str(texto)

    vmin = row.get("valor_min") or ref.get("valor_min") or ""
    vmax = row.get("valor_max") or ref.get("valor_max") or ""
    unidade = row.get("unidade") or ref.get("unidade") or ""

    if vmin and vmax:
        return f"{vmin} a {vmax} {unidade}".strip()

    if vmin and not vmax:
        return f">= {vmin} {unidade}".strip()

    if vmax and not vmin:
        return f"<= {vmax} {unidade}".strip()

    return "Sem referência"


def _linha_analise_para_resultado(row, ref_idx=None):
    ref_idx = ref_idx or {}
    nome = (
        row.get("nome_padronizado")
        or row.get("nome_exame")
        or row.get("nome")
        or row.get("exame")
        or ""
    ).strip()

    ref = ref_idx.get(_nf_txt(nome), {})

    data_iso = _data_para_iso(row.get("data_exame") or row.get("data") or "")
    data_br = _data_para_br(data_iso)

    unidade = row.get("unidade") or ref.get("unidade") or ""
    resultado = row.get("resultado") or row.get("valor") or ""
    status = _status_padrao_exame(row.get("status"))

    fonte = (
        row.get("fonte_referencia")
        or row.get("fonte")
        or ref.get("fonte_referencia")
        or ref.get("fonte")
        or ""
    )

    referencia = _referencia_texto_linha(row, ref)

    grupo = row.get("grupo") or ref.get("grupo") or "Exames laboratoriais"

    item = {
        "id": row.get("analise_id") or row.get("exame_id") or "",
        "paciente_id": str(row.get("paciente_id") or "").strip(),
        "data": data_br,
        "data_br": data_br,
        "data_iso": data_iso,
        "data_exame": data_iso,
        "nome": nome,
        "nome_exame": row.get("nome_exame") or nome,
        "nome_padronizado": nome,
        "exame": nome,
        "exame_nome": nome,
        "grupo": grupo,
        "resultado": resultado,
        "valor": resultado,
        "unidade": unidade,
        "referencia": referencia,
        "fonte": fonte,
        "fonte_referencia": fonte,
        "status": status,
        "mensagem": row.get("mensagem") or "",
        "observacao": row.get("mensagem") or row.get("observacoes") or "",
        "observacoes": row.get("mensagem") or row.get("observacoes") or "",
    }

    return item



# ============================================================
# AJUSTE VISUAL - NOME DO EXAME NO HISTÓRICO
# ============================================================

def nome_exame_para_exibicao(item):
    """
    Retorna o melhor nome disponível para exibir no histórico.
    Compatível com importação de PDF, cadastro manual e versões antigas.
    """
    if not isinstance(item, dict):
        return "-"

    campos = [
        "nome_exame",
        "nome_padronizado",
        "nome",
        "exame",
        "analito",
        "tipo_exame",
        "descricao",
    ]

    for campo in campos:
        valor = str(item.get(campo) or "").strip()
        if valor:
            return valor

    return "-"


def garantir_nome_exame_item(item):
    """
    Preenche todos os aliases de nome do exame para evitar telas com coluna Exame vazia.
    """
    if not isinstance(item, dict):
        return item

    nome = nome_exame_para_exibicao(item)

    if nome and nome != "-":
        item["nome_exame"] = item.get("nome_exame") or nome
        item["nome_padronizado"] = item.get("nome_padronizado") or nome
        item["nome"] = item.get("nome") or nome
        item["exame"] = item.get("exame") or nome
        item["analito"] = item.get("analito") or nome
        item["tipo_exame"] = item.get("tipo_exame") or nome
        item["descricao"] = item.get("descricao") or nome

    return item


def buscar_resultados_paciente(paciente_id=None):
    """
    Fonte única para Dashboard, Pacientes, Nutrição e Detalhe:
    data_flet/analise_exames.csv.
    Se análise estiver vazia, usa data_flet/exames.csv como fallback.
    """
    paciente_id = str(paciente_id or "").strip()
    ref_idx = _indice_referencias_flet()

    rows = _ler_csv_flet("analise_exames.csv")

    if not rows:
        rows_exames = _ler_csv_flet("exames.csv")
        rows = []

        for r in rows_exames:
            nome = r.get("nome_exame") or r.get("nome") or ""
            ref = ref_idx.get(_nf_txt(nome), {})

            valor_min = ref.get("valor_min", "")
            valor_max = ref.get("valor_max", "")
            resultado = r.get("resultado", "")

            status = "Sem análise"
            v = _numero_float_flet(resultado)
            vmin = _numero_float_flet(valor_min)
            vmax = _numero_float_flet(valor_max)

            if v is not None:
                if vmin is not None and v < vmin:
                    status = "Baixo"
                elif vmax is not None and v > vmax:
                    status = "Alto"
                else:
                    status = "Normal"

            rows.append({
                "analise_id": r.get("exame_id", ""),
                "paciente_id": r.get("paciente_id", ""),
                "data_exame": r.get("data_exame", ""),
                "nome_exame": nome,
                "nome_padronizado": nome,
                "resultado": resultado,
                "unidade": r.get("unidade") or ref.get("unidade", ""),
                "valor_min": valor_min,
                "valor_max": valor_max,
                "status": status,
                "mensagem": r.get("observacoes", ""),
                "fonte_referencia": ref.get("fonte_referencia") or ref.get("fonte", ""),
            })

    itens = []

    for r in rows:
        pid = str(r.get("paciente_id") or "").strip()

        if paciente_id and pid != paciente_id:
            continue

        item = _linha_analise_para_resultado(r, ref_idx)
        itens.append(garantir_nome_exame_item(item))

    itens.sort(key=lambda x: (x.get("data_iso") or "", x.get("nome") or ""))

    return itens


def resultados_por_paciente_data(paciente_id, data_exame):
    data_iso = _data_para_iso(data_exame)

    return [
        r for r in buscar_resultados_paciente(paciente_id)
        if _data_para_iso(r.get("data_exame") or r.get("data_iso") or r.get("data")) == data_iso
    ]


def carregar_exames_data_flet_para_memoria():
    """
    Sincroniza RESULTADOS_EXAMES_MOCK e EXAMES_CADASTRADOS_MOCK com data_flet.
    Isso corrige telas antigas que ainda dependem de memória.
    """
    resultados = buscar_resultados_paciente()

    if "RESULTADOS_EXAMES_MOCK" in globals():
        try:
            RESULTADOS_EXAMES_MOCK.clear()
            RESULTADOS_EXAMES_MOCK.extend(resultados)
        except Exception:
            globals()["RESULTADOS_EXAMES_MOCK"] = resultados

    if "EXAMES_CADASTRADOS_MOCK" in globals():
        try:
            EXAMES_CADASTRADOS_MOCK.clear()

            for r in resultados:
                pid = str(r.get("paciente_id") or "").strip()
                data_iso = _data_para_iso(r.get("data_exame") or r.get("data_iso") or r.get("data"))
                nome = str(r.get("nome_exame") or r.get("nome") or "").strip()

                if not pid or not data_iso or not nome:
                    continue

                chave = f"{pid}|{data_iso}"

                if chave not in EXAMES_CADASTRADOS_MOCK:
                    EXAMES_CADASTRADOS_MOCK[chave] = []

                if nome not in EXAMES_CADASTRADOS_MOCK[chave]:
                    EXAMES_CADASTRADOS_MOCK[chave].append(nome)

        except Exception as exc:
            print(f"[DATA_FLET] Falha ao sincronizar exames cadastrados: {exc}")

    print(f"[DATA_FLET] Resultados sincronizados para memória/interface: {len(resultados)}")
    return resultados


def atualizar_pacientes_csv_real_definitivo():
    """
    Recarrega pacientes e seus contadores sempre a partir de data_flet.
    """
    pacientes_csv = _ler_csv_flet("pacientes.csv")
    pacientes = []

    for r in pacientes_csv:
        pid = str(r.get("paciente_id") or r.get("id") or "").strip()

        if not pid:
            continue

        resultados = buscar_resultados_paciente(pid)
        alterados = [
            x for x in resultados
            if _status_padrao_exame(x.get("status")) not in ["Normal", "Sem análise"]
        ]

        datas = [x.get("data_iso") for x in resultados if x.get("data_iso")]
        ultimo_iso = max(datas) if datas else ""
        ultimo_br = _data_para_br(ultimo_iso) if ultimo_iso else "-"

        if not resultados:
            status = "Sem exames"
        elif alterados:
            status = "Atenção"
        else:
            status = "Normal"

        nome = str(r.get("nome") or "").strip()
        idade = str(r.get("idade") or "").strip()

        paciente = {
            **r,
            "id": pid,
            "paciente_id": pid,
            "nome": nome,
            "idade": idade,
            "sexo": r.get("sexo", ""),
            "exames": len(resultados),
            "total_exames": len(resultados),
            "resultados_lancados": len(resultados),
            "resultados": resultados,
            "normais": len([x for x in resultados if _status_padrao_exame(x.get("status")) == "Normal"]),
            "alterados": len(alterados),
            "ultimo_exame": ultimo_br,
            "ultima_data_exame": ultimo_br,
            "status": status,
        }

        pacientes.append(paciente)

    if "PACIENTES_MOCK" in globals():
        try:
            PACIENTES_MOCK.clear()
            PACIENTES_MOCK.extend(pacientes)
        except Exception:
            globals()["PACIENTES_MOCK"] = pacientes

    print(f"[DATA_FLET] Pacientes carregados na UI: {len(pacientes)}")
    print("[DATA_FLET] Exames por paciente:", [(p.get("nome"), p.get("exames")) for p in pacientes])

    return pacientes


def obter_paciente_por_id(paciente_id):
    paciente_id = str(paciente_id or "").strip()

    for p in atualizar_pacientes_csv_real_definitivo():
        if str(p.get("id") or p.get("paciente_id") or "").strip() == paciente_id:
            return p

    return None


def nome_paciente_por_id(paciente_id):
    p = obter_paciente_por_id(paciente_id)

    if p:
        return p.get("nome", "")

    return ""


def sincronizar_data_flet_para_interface():
    carregar_exames_data_flet_para_memoria()
    atualizar_pacientes_csv_real_definitivo()




# ============================================================
# RELATÓRIO PDF E SEÇÃO NUTRIÇÃO - VERSÃO CLÍNICA
# ============================================================

def _ns_data_dir():
    return Path(__file__).resolve().parent / "data_flet"


def _ns_csv_path(nome):
    return _ns_data_dir() / nome


def _ns_ler_csv(nome):
    caminho = _ns_csv_path(nome)

    if not caminho.exists():
        return []

    try:
        with caminho.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    except UnicodeDecodeError:
        with caminho.open("r", encoding="latin-1", newline="") as f:
            return list(csv.DictReader(f))
    except Exception as exc:
        print(f"[NUTRICAO] Erro ao ler {nome}: {exc}")
        return []


def _ns_float(valor):
    valor = str(valor or "").strip()
    valor = re.sub(r"[^0-9,.\-]", "", valor)

    if not valor:
        return None

    if "," in valor:
        valor = valor.replace(".", "").replace(",", ".")

    try:
        return float(valor)
    except Exception:
        return None


def _ns_data_br(valor):
    valor = str(valor or "").strip()

    if not valor:
        return "-"

    if re.match(r"^\d{2}/\d{2}/\d{4}$", valor):
        return valor

    try:
        return datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return valor


def _ns_status(valor):
    st = str(valor or "").strip().lower()

    if st in ["normal", "ok", "dentro", "dentro da referência", "dentro da referencia"]:
        return "Normal"

    if st in ["alto", "acima", "acima da referência", "acima da referencia"]:
        return "Alto"

    if st in ["baixo", "abaixo", "abaixo da referência", "abaixo da referencia"]:
        return "Baixo"

    if st in ["crítico", "critico"]:
        return "Crítico"

    if st:
        return str(valor).strip()

    return "Sem análise"


def _ns_status_alterado(valor):
    return _ns_status(valor) not in ["Normal", "Sem análise"]


def _ns_nome_exame(item):
    if "nome_exame_para_exibicao" in globals():
        try:
            return nome_exame_para_exibicao(item)
        except Exception:
            pass

    for campo in ["nome_exame", "nome_padronizado", "nome", "exame", "exame_nome", "analito"]:
        v = str(item.get(campo) or "").strip()
        if v:
            return v

    return "-"


def _ns_obter_paciente(paciente):
    if isinstance(paciente, dict):
        return paciente

    paciente_id = str(paciente or "").strip()

    if "obter_paciente_por_id" in globals():
        try:
            p = obter_paciente_por_id(paciente_id)
            if p:
                return p
        except Exception:
            pass

    if "obter_paciente" in globals():
        try:
            p = obter_paciente(paciente_id)
            if p:
                return p
        except Exception:
            pass

    for r in _ns_ler_csv("pacientes.csv"):
        pid = str(r.get("paciente_id") or r.get("id") or "").strip()
        if pid == paciente_id:
            r["id"] = pid
            r["paciente_id"] = pid
            return r

    return {"id": paciente_id, "paciente_id": paciente_id, "nome": "Paciente", "idade": ""}


def _ns_resultados_paciente(paciente_id):
    paciente_id = str(paciente_id or "").strip()

    if "buscar_resultados_paciente" in globals():
        try:
            resultados = buscar_resultados_paciente(paciente_id)
            if resultados:
                return resultados
        except Exception as exc:
            print(f"[NUTRICAO] Falha em buscar_resultados_paciente: {exc}")

    rows = _ns_ler_csv("analise_exames.csv")
    resultados = []

    for r in rows:
        if str(r.get("paciente_id") or "").strip() != paciente_id:
            continue

        nome = r.get("nome_exame") or r.get("nome_padronizado") or r.get("nome") or "-"
        unidade = r.get("unidade") or ""
        resultado = r.get("resultado") or ""

        resultados.append({
            "id": r.get("analise_id") or "",
            "paciente_id": paciente_id,
            "data": _ns_data_br(r.get("data_exame") or r.get("data") or ""),
            "data_exame": r.get("data_exame") or r.get("data") or "",
            "nome_exame": nome,
            "nome_padronizado": r.get("nome_padronizado") or nome,
            "nome": nome,
            "exame": nome,
        "exame_nome": nome,
            "resultado": resultado,
            "unidade": unidade,
            "referencia": r.get("referencia") or r.get("mensagem") or "",
            "valor_min": r.get("valor_min") or "",
            "valor_max": r.get("valor_max") or "",
            "status": _ns_status(r.get("status")),
            "mensagem": r.get("mensagem") or "",
            "fonte_referencia": r.get("fonte_referencia") or "",
        })

    return resultados


def _ns_ultimo_registro(nome_csv, paciente_id):
    rows = [
        r for r in _ns_ler_csv(nome_csv)
        if str(r.get("paciente_id") or r.get("id_paciente") or r.get("id") or "").strip() == str(paciente_id)
    ]

    if not rows:
        return {}

    def chave(r):
        return str(r.get("data") or r.get("data_registro") or r.get("data_avaliacao") or r.get("data_anamnese") or "")

    rows.sort(key=chave, reverse=True)
    return rows[0]


def _ns_analise_antropometrica(paciente):
    paciente_id = str(paciente.get("id") or paciente.get("paciente_id") or "")
    antro = _ns_ultimo_registro("antropometria.csv", paciente_id)

    peso = _ns_float(
        antro.get("peso")
        or antro.get("peso_kg")
        or antro.get("massa")
        or paciente.get("peso")
    )

    altura = _ns_float(
        antro.get("altura")
        or antro.get("altura_m")
        or antro.get("altura_cm")
        or paciente.get("altura")
    )

    cintura = _ns_float(
        antro.get("cintura")
        or antro.get("circunferencia_cintura")
        or antro.get("cc")
    )

    sexo = str(paciente.get("sexo") or antro.get("sexo") or "").upper()

    if altura and altura > 3:
        altura_m = altura / 100
        altura_cm = altura
    elif altura:
        altura_m = altura
        altura_cm = altura * 100
    else:
        altura_m = None
        altura_cm = None

    imc = None
    classificacao = "Dados insuficientes"

    if peso and altura_m:
        imc = peso / (altura_m ** 2)

        if imc < 18.5:
            classificacao = "Baixo peso"
        elif imc < 25:
            classificacao = "Eutrofia"
        elif imc < 30:
            classificacao = "Sobrepeso"
        elif imc < 35:
            classificacao = "Obesidade grau I"
        elif imc < 40:
            classificacao = "Obesidade grau II"
        else:
            classificacao = "Obesidade grau III"

    risco_cintura = "Não avaliado"

    if cintura:
        if sexo.startswith("F"):
            risco_cintura = "Aumentado" if cintura >= 80 else "Sem aumento relevante"
            if cintura >= 88:
                risco_cintura = "Muito aumentado"
        else:
            risco_cintura = "Aumentado" if cintura >= 94 else "Sem aumento relevante"
            if cintura >= 102:
                risco_cintura = "Muito aumentado"

    resumo = []

    if imc:
        resumo.append(f"IMC estimado: {imc:.1f} kg/m² - {classificacao}.")
    else:
        resumo.append("IMC não calculado por ausência de peso e/ou altura cadastrados.")

    if cintura:
        resumo.append(f"Circunferência de cintura: {cintura:.1f} cm - risco {risco_cintura.lower()}.")
    else:
        resumo.append("Circunferência de cintura não cadastrada.")

    if peso:
        resumo.append(f"Peso registrado: {peso:.1f} kg.")
    else:
        resumo.append("Peso não cadastrado.")

    return {
        "registro": antro,
        "peso": peso,
        "altura_cm": altura_cm,
        "altura_m": altura_m,
        "cintura": cintura,
        "imc": imc,
        "classificacao": classificacao,
        "risco_cintura": risco_cintura,
        "resumo": resumo,
    }


def _ns_texto_registro(reg):
    return " ".join([str(v or "") for v in reg.values()]).lower()


def _ns_fator_atividade(anamnese):
    texto = _ns_texto_registro(anamnese)

    if any(t in texto for t in ["muito ativo", "intenso", "alta intensidade", "atleta"]):
        return 1.725, "Intensa"

    if any(t in texto for t in ["moderado", "moderada", "3 vezes", "4 vezes", "5 vezes"]):
        return 1.55, "Moderada"

    if any(t in texto for t in ["leve", "caminhada", "1 vez", "2 vezes"]):
        return 1.375, "Leve"

    if any(t in texto for t in ["sedent", "não pratica", "nao pratica"]):
        return 1.2, "Sedentária"

    return 1.375, "Leve/estimada"


def _ns_objetivo(anamnese):
    texto = _ns_texto_registro(anamnese)

    if any(t in texto for t in ["emagrecer", "perda de peso", "reduzir peso", "redução de peso", "definição"]):
        return "Redução de peso"

    if any(t in texto for t in ["ganho de peso", "hipertrofia", "massa muscular", "ganhar massa"]):
        return "Ganho de massa"

    if any(t in texto for t in ["manutenção", "manutencao", "qualidade de vida"]):
        return "Manutenção"

    return "Não informado"


def _ns_estimativa_ingestao_recordatorio(recordatorio):
    if not recordatorio:
        return None, "Recordatório não cadastrado."

    for campo in ["kcal", "calorias", "total_kcal", "valor_calorico", "energia"]:
        v = _ns_float(recordatorio.get(campo))
        if v:
            return v, f"Valor energético informado no campo {campo}."

    refeicoes = {
        "desjejum": 350,
        "cafe_manha": 350,
        "lanche_manha": 180,
        "almoco": 700,
        "lanche_tarde": 220,
        "jantar": 650,
        "ceia": 150,
    }

    total = 0
    encontrou = False

    for campo, base in refeicoes.items():
        texto = str(recordatorio.get(campo) or "").strip().lower()

        if not texto:
            continue

        encontrou = True
        kcal = base

        if any(t in texto for t in ["fritura", "pizza", "hamburg", "salgado", "doce", "refrigerante"]):
            kcal += 250

        if any(t in texto for t in ["salada", "legume", "fruta", "iogurte", "light"]):
            kcal -= 80

        total += max(80, kcal)

    if encontrou:
        return total, "Estimativa heurística baseada nas refeições descritas no recordatório."

    return None, "Recordatório cadastrado, porém sem refeições interpretáveis."


def _ns_analise_calorica(paciente, antropometria):
    paciente_id = str(paciente.get("id") or paciente.get("paciente_id") or "")
    anamnese = _ns_ultimo_registro("anamnese.csv", paciente_id)
    recordatorio = _ns_ultimo_registro("recordatorio_habitual.csv", paciente_id)

    peso = antropometria.get("peso")
    altura_cm = antropometria.get("altura_cm")
    idade = _ns_float(paciente.get("idade"))
    sexo = str(paciente.get("sexo") or "").upper()

    fator, nivel = _ns_fator_atividade(anamnese)
    objetivo = _ns_objetivo(anamnese)

    if not peso or not altura_cm or not idade:
        return {
            "calculado": False,
            "motivo": "Dados insuficientes para estimar gasto calórico: informe peso, altura e idade.",
            "atividade": nivel,
            "objetivo": objetivo,
            "basal": None,
            "manutencao": None,
            "ingestao": None,
            "meta": None,
            "diferenca": None,
            "fonte_ingestao": "Sem cálculo.",
        }

    if sexo.startswith("F"):
        basal = (10 * peso) + (6.25 * altura_cm) - (5 * idade) - 161
    else:
        basal = (10 * peso) + (6.25 * altura_cm) - (5 * idade) + 5

    manutencao = basal * fator
    ingestao, fonte_ingestao = _ns_estimativa_ingestao_recordatorio(recordatorio)

    if objetivo == "Redução de peso":
        meta = manutencao - 500
    elif objetivo == "Ganho de massa":
        meta = manutencao + 300
    else:
        meta = manutencao

    diferenca = None

    if ingestao:
        diferenca = ingestao - meta

    return {
        "calculado": True,
        "atividade": nivel,
        "objetivo": objetivo,
        "basal": basal,
        "manutencao": manutencao,
        "ingestao": ingestao,
        "meta": meta,
        "diferenca": diferenca,
        "fonte_ingestao": fonte_ingestao,
    }


def _ns_resumo_exames(resultados):
    total = len(resultados)
    normais = len([r for r in resultados if _ns_status(r.get("status")) == "Normal"])
    alterados = len([r for r in resultados if _ns_status_alterado(r.get("status"))])
    sem = len([r for r in resultados if _ns_status(r.get("status")) == "Sem análise"])

    return {
        "total": total,
        "normais": normais,
        "alterados": alterados,
        "sem": sem,
    }


def _ns_barra_pdf(titulo, dados):
    largura = 450
    altura = 150
    d = Drawing(largura, altura)

    max_val = max([v for _, v, _ in dados] + [1])
    x0 = 35
    base = 30
    bar_w = 70
    gap = 45

    d.add(String(0, 130, titulo, fontSize=12, fillColor=HexColor("#111827")))

    for i, (label, valor, cor) in enumerate(dados):
        x = x0 + i * (bar_w + gap)
        h = (valor / max_val) * 80 if max_val else 0

        d.add(Rect(x, base, bar_w, h, fillColor=HexColor(cor), strokeColor=HexColor(cor)))
        d.add(String(x + 20, base + h + 8, str(int(round(valor))), fontSize=10, fillColor=HexColor("#111827")))
        d.add(String(x, 10, label, fontSize=9, fillColor=HexColor("#374151")))

    return d


def _ns_paragrafo(txt, style):
    return Paragraph(xml_escape(str(txt or "")), style)


def gerar_pdf_analise_paciente(paciente):
    paciente = _ns_obter_paciente(paciente)
    paciente_id = str(paciente.get("id") or paciente.get("paciente_id") or "")
    nome_paciente = str(paciente.get("nome") or "Paciente").strip()

    resultados = _ns_resultados_paciente(paciente_id)
    resumo = _ns_resumo_exames(resultados)
    alterados = [r for r in resultados if _ns_status_alterado(r.get("status"))]

    antropometria = _ns_analise_antropometrica(paciente)
    calorias = _ns_analise_calorica(paciente, antropometria)

    rel_dir = SysPath(__file__).resolve().parent / "relatorios"
    rel_dir.mkdir(parents=True, exist_ok=True)

    nome_arquivo = re.sub(r"[^A-Za-z0-9_-]+", "_", nome_paciente).strip("_")
    caminho_pdf = rel_dir / f"analise_nutricional_{nome_arquivo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    doc = SimpleDocTemplate(
        str(caminho_pdf),
        pagesize=A4,
        rightMargin=1.4 * cm,
        leftMargin=1.4 * cm,
        topMargin=1.3 * cm,
        bottomMargin=1.3 * cm,
    )

    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "TituloNS",
        parent=styles["Title"],
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=HexColor("#111827"),
        spaceAfter=14,
    )

    h2 = ParagraphStyle(
        "H2NS",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=HexColor("#111827"),
        spaceBefore=10,
        spaceAfter=8,
    )

    body = ParagraphStyle(
        "BodyNS",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
        textColor=HexColor("#374151"),
    )

    small = ParagraphStyle(
        "SmallNS",
        parent=styles["BodyText"],
        fontSize=7,
        leading=9,
        textColor=HexColor("#374151"),
    )

    story = []

    story.append(Paragraph("NutriSoft - Relatório Nutricional e Clínico", title))
    story.append(_ns_paragrafo(f"Paciente: {nome_paciente}", body))
    story.append(_ns_paragrafo(f"Idade: {paciente.get('idade', '-')} anos", body))
    story.append(_ns_paragrafo(f"Data de emissão: {datetime.now().strftime('%d/%m/%Y %H:%M')}", body))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Exames alterados", h2))

    if alterados:
        rows = [[
            _ns_paragrafo("Data", small),
            _ns_paragrafo("Exame", small),
            _ns_paragrafo("Resultado", small),
            _ns_paragrafo("Referência", small),
            _ns_paragrafo("Status", small),
        ]]

        for r in alterados:
            resultado_txt = f'{r.get("resultado", "")} {r.get("unidade", "")}'.strip()
            referencia_txt = str(r.get("referencia") or r.get("mensagem") or "-")
            rows.append([
                _ns_paragrafo(_ns_data_br(r.get("data_exame") or r.get("data")), small),
                _ns_paragrafo(_ns_nome_exame(r), small),
                _ns_paragrafo(resultado_txt, small),
                _ns_paragrafo(referencia_txt, small),
                _ns_paragrafo(_ns_status(r.get("status")), small),
            ])

        tabela_alt = Table(
            rows,
            colWidths=[2.1 * cm, 4.2 * cm, 2.8 * cm, 7.0 * cm, 2.0 * cm],
            repeatRows=1,
        )

        tabela_alt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#F3F4F6")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.25, HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))

        story.append(tabela_alt)
    else:
        story.append(_ns_paragrafo("Não foram identificados exames fora da referência.", body))

    story.append(Spacer(1, 10))

    story.append(Paragraph("Análise antropométrica", h2))

    for frase in antropometria["resumo"]:
        story.append(_ns_paragrafo(f"- {frase}", body))

    story.append(Spacer(1, 8))

    story.append(Paragraph("Análise do gasto calórico", h2))

    if calorias["calculado"]:
        rows_cal = [
            [_ns_paragrafo("Indicador", small), _ns_paragrafo("Estimativa", small)],
            [_ns_paragrafo("Gasto basal estimado", small), f'{calorias["basal"]:.0f} kcal/dia'],
            [_ns_paragrafo("Gasto total de manutenção", small), f'{calorias["manutencao"]:.0f} kcal/dia'],
            [_ns_paragrafo("Nível de atividade", small), calorias["atividade"]],
            [_ns_paragrafo("Objetivo do tratamento", small), calorias["objetivo"]],
            [_ns_paragrafo("Meta calórica sugerida", small), f'{calorias["meta"]:.0f} kcal/dia'],
        ]

        if calorias["ingestao"]:
            rows_cal.append([_ns_paragrafo("Ingestão estimada pelo recordatório", small), f'{calorias["ingestao"]:.0f} kcal/dia'])
            rows_cal.append([_ns_paragrafo("Diferença ingestão x meta", small), f'{calorias["diferenca"]:.0f} kcal/dia'])
        else:
            rows_cal.append([_ns_paragrafo("Ingestão estimada pelo recordatório", small), "Dados insuficientes"])

        tabela_cal = Table(rows_cal, colWidths=[8.5 * cm, 5.0 * cm])
        tabela_cal.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#F3F4F6")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.25, HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))

        story.append(tabela_cal)
        story.append(Spacer(1, 8))
        story.append(_ns_paragrafo(f'Base da ingestão: {calorias["fonte_ingestao"]}', body))

        graf_cal = [
            ("Manut.", calorias["manutencao"], "#2563EB"),
            ("Meta", calorias["meta"], "#16A34A"),
        ]

        if calorias["ingestao"]:
            graf_cal.insert(1, ("Ingest.", calorias["ingestao"], "#F59E0B"))

        story.append(Spacer(1, 8))
        story.append(_ns_barra_pdf("Comparativo calórico", graf_cal))
    else:
        story.append(_ns_paragrafo(calorias["motivo"], body))
        story.append(_ns_paragrafo(f'Nível de atividade informado/estimado: {calorias["atividade"]}.', body))
        story.append(_ns_paragrafo(f'Objetivo informado/estimado: {calorias["objetivo"]}.', body))

    story.append(Spacer(1, 12))

    _exames_diag_pdf = (
        locals().get("exames")
        or locals().get("exames_paciente")
        or locals().get("resultados")
        or locals().get("resultados_exames")
        or []
    )
    _pdf_adicionar_diagnostico_inteligente_nutricao(story, _exames_diag_pdf, h2, body, small)
    story.append(Spacer(1, 8))
    story.append(Paragraph("Observações importantes", h2))
    story.append(_ns_paragrafo(
        "Este relatório organiza os dados cadastrados no sistema e compara automaticamente os exames com as faixas de referência disponíveis. "
        "As estimativas calóricas são apoio técnico para acompanhamento nutricional e dependem da qualidade da anamnese, antropometria e recordatório alimentar. "
        "A interpretação clínica definitiva deve ser realizada por profissional habilitado.",
        body,
    ))

    doc.build(story)

    return str(caminho_pdf)


def _ns_flet_card(conteudo, padding=20):
    if "app_card" in globals():
        try:
            return app_card(conteudo, padding=padding)
        except Exception:
            pass

    return ft.Container(
        bgcolor="#FFFFFF",
        border_radius=18,
        padding=padding,
        content=conteudo,
    )


def _ns_flet_metric(titulo, valor, subtitulo="", cor="#111827"):
    return _ns_flet_card(
        ft.Column(
            spacing=6,
            controls=[
                ft.Text(titulo, size=13, color="#64748B"),
                ft.Text(str(valor), size=28, weight=ft.FontWeight.BOLD, color=cor),
                ft.Text(subtitulo, size=11, color="#64748B") if subtitulo else ft.Container(height=1),
            ],
        ),
        padding=18,
    )


def _ns_flet_barras_exames(resumo):
    dados = [
        ("Total", resumo["total"], "#2563EB"),
        ("Normais", resumo["normais"], "#16A34A"),
        ("Alterados", resumo["alterados"], "#F59E0B"),
    ]

    max_val = max([v for _, v, _ in dados] + [1])

    barras = []

    for label, valor, cor in dados:
        altura = 40 + int((valor / max_val) * 120)

        barras.append(
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.END,
                spacing=8,
                controls=[
                    ft.Text(str(valor), size=13, weight=ft.FontWeight.BOLD, color="#111827"),
                    ft.Container(width=58, height=altura, border_radius=12, bgcolor=cor),
                    ft.Text(label, size=12, color="#64748B"),
                ],
            )
        )

    return _ns_flet_card(
        ft.Column(
            spacing=14,
            controls=[
                ft.Text("Dashboard de exames", size=18, weight=ft.FontWeight.BOLD, color="#111827"),
                ft.Container(
                    height=230,
                    bgcolor="#F8FAFC",
                    border_radius=16,
                    padding=20,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        controls=barras,
                    ),
                ),
            ],
        )
    )


def _ns_flet_barras_calorias(calorias):
    if not calorias.get("calculado"):
        return _ns_flet_card(
            ft.Column(
                spacing=8,
                controls=[
                    ft.Text("Comparativo calórico", size=18, weight=ft.FontWeight.BOLD, color="#111827"),
                    ft.Text(calorias.get("motivo", "Dados insuficientes."), size=13, color="#64748B"),
                ],
            )
        )

    dados = [
        ("Manutenção", calorias["manutencao"], "#2563EB"),
        ("Meta", calorias["meta"], "#16A34A"),
    ]

    if calorias.get("ingestao"):
        dados.insert(1, ("Ingestão", calorias["ingestao"], "#F59E0B"))

    max_val = max([v for _, v, _ in dados if v] + [1])

    barras = []

    for label, valor, cor in dados:
        altura = 40 + int((valor / max_val) * 130)

        barras.append(
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.END,
                spacing=8,
                controls=[
                    ft.Text(f"{valor:.0f}", size=13, weight=ft.FontWeight.BOLD, color="#111827"),
                    ft.Container(width=70, height=altura, border_radius=12, bgcolor=cor),
                    ft.Text(label, size=12, color="#64748B"),
                ],
            )
        )

    return _ns_flet_card(
        ft.Column(
            spacing=14,
            controls=[
                ft.Text("Comparativo calórico", size=18, weight=ft.FontWeight.BOLD, color="#111827"),
                ft.Text(
                    f'Objetivo: {calorias["objetivo"]} • Atividade: {calorias["atividade"]}',
                    size=13,
                    color="#64748B",
                ),
                ft.Container(
                    height=250,
                    bgcolor="#F8FAFC",
                    border_radius=16,
                    padding=20,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        controls=barras,
                    ),
                ),
                ft.Text(f'Base da ingestão: {calorias["fonte_ingestao"]}', size=12, color="#64748B"),
            ],
        )
    )


def _ns_flet_tabela_alterados(alterados):
    if not alterados:
        return _ns_flet_card(
            ft.Column(
                spacing=8,
                controls=[
                    ft.Text("Exames alterados", size=18, weight=ft.FontWeight.BOLD, color="#111827"),
                    ft.Text("Não foram identificados exames fora da referência.", size=13, color="#64748B"),
                ],
            )
        )

    rows = []

    for r in alterados:
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(_ns_data_br(r.get("data_exame") or r.get("data")), size=12)),
                    ft.DataCell(ft.Text(_ns_nome_exame(r), size=12)),
                    ft.DataCell(ft.Text(f'{r.get("resultado", "")} {r.get("unidade", "")}', size=12)),
                    ft.DataCell(ft.Text(_ns_status(r.get("status")), size=12)),
                ]
            )
        )

    return _ns_flet_card(
        ft.Column(
            spacing=14,
            controls=[
                ft.Text("Exames alterados", size=18, weight=ft.FontWeight.BOLD, color="#111827"),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Data")),
                        ft.DataColumn(ft.Text("Exame")),
                        ft.DataColumn(ft.Text("Resultado")),
                        ft.DataColumn(ft.Text("Status")),
                    ],
                    rows=rows,
                    heading_row_color="#F8FAFC",
                    border_radius=12,
                ),
            ],
        )
    )


def _ns_flet_antropometria(antropometria):
    controles = [
        ft.Text("Análise antropométrica", size=18, weight=ft.FontWeight.BOLD, color="#111827"),
    ]

    for frase in antropometria["resumo"]:
        controles.append(ft.Text(f"• {frase}", size=13, color="#374151"))

    return _ns_flet_card(ft.Column(spacing=8, controls=controles))


def _ns_flet_calorias(calorias):
    controles = [
        ft.Text("Análise do gasto calórico", size=18, weight=ft.FontWeight.BOLD, color="#111827"),
    ]

    if calorias.get("calculado"):
        controles.extend([
            ft.Text(f'Gasto basal estimado: {calorias["basal"]:.0f} kcal/dia', size=13, color="#374151"),
            ft.Text(f'Gasto de manutenção: {calorias["manutencao"]:.0f} kcal/dia', size=13, color="#374151"),
            ft.Text(f'Meta calórica sugerida: {calorias["meta"]:.0f} kcal/dia', size=13, color="#374151"),
            ft.Text(
                f'Ingestão estimada: {calorias["ingestao"]:.0f} kcal/dia' if calorias.get("ingestao") else "Ingestão estimada: dados insuficientes no recordatório.",
                size=13,
                color="#374151",
            ),
        ])

        if calorias.get("diferenca") is not None:
            controles.append(
                ft.Text(f'Diferença ingestão x meta: {calorias["diferenca"]:.0f} kcal/dia', size=13, color="#374151")
            )
    else:
        controles.append(ft.Text(calorias.get("motivo", "Dados insuficientes."), size=13, color="#64748B"))

    controles.append(ft.Text(f'Objetivo: {calorias.get("objetivo", "-")}', size=13, color="#64748B"))
    controles.append(ft.Text(f'Atividade: {calorias.get("atividade", "-")}', size=13, color="#64748B"))

    return _ns_flet_card(ft.Column(spacing=8, controls=controles))


def nutricao_view(page):
    pacientes = []

    try:
        pacientes = atualizar_pacientes_csv_real_definitivo()
    except Exception:
        pacientes = globals().get("PACIENTES_MOCK", [])

    opcoes = []

    for p in pacientes:
        pid = str(p.get("id") or p.get("paciente_id") or "")
        nome = str(p.get("nome") or "")
        idade = str(p.get("idade") or "")
        if pid:
            opcoes.append(ft.dropdown.Option(key=pid, text=f"{nome} - {idade} anos" if idade else nome))

    paciente_dropdown = ft.Dropdown(
        label="Paciente",
        width=420,
        options=opcoes,
        value=opcoes[0].key if opcoes else None,
        border_radius=12,
    )

    painel = ft.Column(spacing=16)

    def atualizar(e=None):
        pid = paciente_dropdown.value

        if not pid:
            painel.controls = [
                _ns_flet_card(
                    ft.Text("Nenhum paciente selecionado.", size=14, color="#64748B")
                )
            ]
            page.update()
            return

        paciente = _ns_obter_paciente(pid)
        resultados = _ns_resultados_paciente(pid)
        resumo = _ns_resumo_exames(resultados)
        alterados = [r for r in resultados if _ns_status_alterado(r.get("status"))]
        antropometria = _ns_analise_antropometrica(paciente)
        calorias = _ns_analise_calorica(paciente, antropometria)

        painel.controls = [
            ft.Row(
                spacing=16,
                controls=[
                    _ns_flet_metric("Resultados", resumo["total"], "Total de exames analisados", "#2563EB"),
                    _ns_flet_metric("Normais", resumo["normais"], "Dentro da referência", "#16A34A"),
                    _ns_flet_metric("Alterados", resumo["alterados"], "Fora da referência", "#F59E0B"),
                ],
            ),
            _ns_flet_barras_exames(resumo),
            _ns_flet_tabela_alterados(alterados),
            _ns_flet_antropometria(antropometria),
            _ns_flet_calorias(calorias),
            _ns_flet_barras_calorias(calorias),
        ]

        page.update()

    aplicar_btn = ft.FilledButton(
        content=ft.Text("Atualizar análise", color="white"),
        on_click=atualizar,
        style=ft.ButtonStyle(
            bgcolor=globals().get("COR_PRIMARIA", "#2563EB"),
            color="white",
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )

    atualizar()

    return ft.Column(
        spacing=18,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            _ns_flet_card(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text("Nutrição", size=28, weight=ft.FontWeight.BOLD, color="#111827"),
                                ft.Text(
                                    "Análise integrada de exames, antropometria, gasto calórico, anamnese e recordatório.",
                                    size=13,
                                    color="#64748B",
                                ),
                            ],
                        ),
                        ft.Row(spacing=10, controls=[paciente_dropdown, aplicar_btn]),
                    ],
                )
            ),
            painel,
        ],
    )




# ============================================================
# PERSISTÊNCIA DATA_FLET - ANAMNESE / RECORDATÓRIO / ANTROPOMETRIA
# ============================================================

_CARREGANDO_NUTRI_DATA_FLET = False

COLUNAS_ANAMNESE_DATA_FLET = [
    "paciente_id", "data_anamnese", "queixa_principal", "historia_doenca_atual",
    "sintomas", "historia_patologica_pregressa", "historia_familiar",
    "numero_filhos_idades", "amamentou", "atividade_fisica",
    "horario_atividade_fisica", "consumo_alcool", "tabagismo", "qualidade_sono",
    "hora_acordar", "hora_dormir", "comportamento_peso", "disposicao_fisica",
    "funcionamento_intestinal", "funcionamento_urinario", "internacoes_cirurgias",
    "medicamentos_suplementos", "intolerancia_alergia_alimentar", "denticao",
    "mastigacao", "quem_cozinha", "apetite", "horario_mais_fome",
    "ingestao_agua_dia", "tratamento_nutricional_anterior", "qual_tratamento",
    "objetivo_nutricional", "alimentos_preferidos", "habito_beliscar",
    "alimentos_que_nao_gosta", "habitos_fim_de_semana", "dificuldades_adesao",
]

COLUNAS_RECORDATORIO_DATA_FLET = [
    "paciente_id", "data_registro", "desjejum", "lanche_manha", "almoco",
    "lanche_tarde", "jantar", "ceia", "observacoes",
]

COLUNAS_ANTROPOMETRIA_DATA_FLET = [
    "paciente_id", "data_avaliacao", "tipo_avaliacao", "objetivo_antropometrico",
    "condicao_medicao", "tipo_balanca", "roupa_medicao", "local_cintura",
    "peso", "altura", "circunferencia_cintura", "imc", "classificacao_imc",
    "risco_cintura", "observacoes",
]


def _df_pasta():
    pasta = Path(__file__).resolve().parent / "data_flet"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def _df_csv(nome):
    return _df_pasta() / nome


def _df_hoje_iso():
    return datetime.now().strftime("%Y-%m-%d")


def _df_normalizar_data(valor):
    valor = str(valor or "").strip()

    if not valor:
        return _df_hoje_iso()

    if re.match(r"^\d{4}-\d{2}-\d{2}$", valor):
        return valor

    for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(valor, fmt).strftime("%Y-%m-%d")
        except Exception:
            pass

    return valor


def _df_str(valor):
    if valor is None:
        return ""

    if isinstance(valor, (list, tuple, set)):
        return "; ".join([_df_str(v) for v in valor if _df_str(v)])

    if isinstance(valor, dict):
        return "; ".join([f"{k}: {_df_str(v)}" for k, v in valor.items() if _df_str(v)])

    return str(valor).strip()


def _df_ler_csv(nome, colunas):
    caminho = _df_csv(nome)

    if not caminho.exists():
        with caminho.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=colunas)
            writer.writeheader()
        return []

    try:
        with caminho.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except UnicodeDecodeError:
        with caminho.open("r", encoding="latin-1", newline="") as f:
            reader = csv.DictReader(f)
            return list(reader)


def _df_escrever_csv(nome, colunas, rows):
    caminho = _df_csv(nome)

    with caminho.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=colunas)
        writer.writeheader()

        for r in rows:
            writer.writerow({c: r.get(c, "") for c in colunas})


def _df_upsert(nome, colunas, row, chaves):
    rows = _df_ler_csv(nome, colunas)

    def key(r):
        return tuple(str(r.get(c, "")).strip().lower() for c in chaves)

    chave_nova = key(row)
    atualizou = False
    saida = []

    for r in rows:
        if key(r) == chave_nova:
            base = dict(r)
            base.update(row)
            saida.append(base)
            atualizou = True
        else:
            saida.append(r)

    if not atualizou:
        saida.append(row)

    _df_escrever_csv(nome, colunas, saida)


def _df_primeiro(registro, *campos):
    if not isinstance(registro, dict):
        return ""

    for campo in campos:
        if campo in registro:
            valor = _df_str(registro.get(campo))
            if valor:
                return valor

    return ""


def _df_paciente_id(registro):
    pid = _df_primeiro(
        registro,
        "paciente_id", "id_paciente", "paciente", "id", "paciente_codigo", "codigo_paciente"
    )

    if pid:
        return pid

    return str(globals().get("PACIENTE_SELECIONADO_ID", "") or "").strip()


def _df_map_anamnese(registro):
    return {
        "paciente_id": _df_paciente_id(registro),
        "data_anamnese": _df_normalizar_data(_df_primeiro(registro, "data_anamnese", "data", "data_registro")),
        "queixa_principal": _df_primeiro(registro, "queixa_principal", "queixa", "objetivo", "objetivo_principal"),
        "historia_doenca_atual": _df_primeiro(registro, "historia_doenca_atual", "historia_atual", "doenca_atual"),
        "sintomas": _df_primeiro(registro, "sintomas", "sintomas_atuais"),
        "historia_patologica_pregressa": _df_primeiro(registro, "historia_patologica_pregressa", "historia_pregressa"),
        "historia_familiar": _df_primeiro(registro, "historia_familiar", "antecedentes_familiares"),
        "numero_filhos_idades": _df_primeiro(registro, "numero_filhos_idades", "filhos"),
        "amamentou": _df_primeiro(registro, "amamentou", "amamentacao"),
        "atividade_fisica": _df_primeiro(registro, "atividade_fisica", "atividade", "exercicio", "pratica_atividade_fisica"),
        "horario_atividade_fisica": _df_primeiro(registro, "horario_atividade_fisica", "horario_atividade", "horario_exercicio"),
        "consumo_alcool": _df_primeiro(registro, "consumo_alcool", "alcool"),
        "tabagismo": _df_primeiro(registro, "tabagismo", "fumo"),
        "qualidade_sono": _df_primeiro(registro, "qualidade_sono", "sono"),
        "hora_acordar": _df_primeiro(registro, "hora_acordar", "acordar"),
        "hora_dormir": _df_primeiro(registro, "hora_dormir", "dormir"),
        "comportamento_peso": _df_primeiro(registro, "comportamento_peso", "peso_historico", "evolucao_peso"),
        "disposicao_fisica": _df_primeiro(registro, "disposicao_fisica", "disposicao"),
        "funcionamento_intestinal": _df_primeiro(registro, "funcionamento_intestinal", "intestino"),
        "funcionamento_urinario": _df_primeiro(registro, "funcionamento_urinario", "urinario"),
        "internacoes_cirurgias": _df_primeiro(registro, "internacoes_cirurgias", "cirurgias", "internacoes"),
        "medicamentos_suplementos": _df_primeiro(registro, "medicamentos_suplementos", "medicamentos", "suplementos"),
        "intolerancia_alergia_alimentar": _df_primeiro(registro, "intolerancia_alergia_alimentar", "intolerancia", "alergia", "alergias"),
        "denticao": _df_primeiro(registro, "denticao", "dentição"),
        "mastigacao": _df_primeiro(registro, "mastigacao", "mastigação"),
        "quem_cozinha": _df_primeiro(registro, "quem_cozinha", "cozinha"),
        "apetite": _df_primeiro(registro, "apetite"),
        "horario_mais_fome": _df_primeiro(registro, "horario_mais_fome", "horario_fome"),
        "ingestao_agua_dia": _df_primeiro(registro, "ingestao_agua_dia", "agua", "ingestao_agua", "hidratação", "hidratacao"),
        "tratamento_nutricional_anterior": _df_primeiro(registro, "tratamento_nutricional_anterior", "tratamento_anterior"),
        "qual_tratamento": _df_primeiro(registro, "qual_tratamento", "tratamento"),
        "objetivo_nutricional": _df_primeiro(registro, "objetivo_nutricional", "objetivo", "objetivos"),
        "alimentos_preferidos": _df_primeiro(registro, "alimentos_preferidos", "preferidos"),
        "habito_beliscar": _df_primeiro(registro, "habito_beliscar", "beliscar"),
        "alimentos_que_nao_gosta": _df_primeiro(registro, "alimentos_que_nao_gosta", "nao_gosta", "não_gosta"),
        "habitos_fim_de_semana": _df_primeiro(registro, "habitos_fim_de_semana", "fim_de_semana"),
        "dificuldades_adesao": _df_primeiro(registro, "dificuldades_adesao", "dificuldades", "adesao", "adesão"),
    }


def _df_map_recordatorio(registro):
    return {
        "paciente_id": _df_paciente_id(registro),
        "data_registro": _df_normalizar_data(_df_primeiro(registro, "data_registro", "data", "data_recordatorio")),
        "desjejum": _df_primeiro(registro, "desjejum", "cafe_manha", "café_da_manhã", "cafe_da_manha"),
        "lanche_manha": _df_primeiro(registro, "lanche_manha", "colacao"),
        "almoco": _df_primeiro(registro, "almoco", "almoço"),
        "lanche_tarde": _df_primeiro(registro, "lanche_tarde"),
        "jantar": _df_primeiro(registro, "jantar"),
        "ceia": _df_primeiro(registro, "ceia"),
        "observacoes": _df_primeiro(registro, "observacoes", "observação", "observacao", "obs"),
    }


def _df_map_antropometria(registro):
    return {
        "paciente_id": _df_paciente_id(registro),
        "data_avaliacao": _df_normalizar_data(_df_primeiro(registro, "data_avaliacao", "data", "data_registro")),
        "tipo_avaliacao": _df_primeiro(registro, "tipo_avaliacao", "tipo", "avaliacao"),
        "objetivo_antropometrico": _df_primeiro(registro, "objetivo_antropometrico", "objetivo"),
        "condicao_medicao": _df_primeiro(registro, "condicao_medicao", "condicao", "condição"),
        "tipo_balanca": _df_primeiro(registro, "tipo_balanca", "balanca", "balança"),
        "roupa_medicao": _df_primeiro(registro, "roupa_medicao", "roupa"),
        "local_cintura": _df_primeiro(registro, "local_cintura", "cintura_local"),
        "peso": _df_primeiro(registro, "peso", "peso_kg"),
        "altura": _df_primeiro(registro, "altura", "altura_m", "altura_cm"),
        "circunferencia_cintura": _df_primeiro(registro, "circunferencia_cintura", "cintura", "cc"),
        "imc": _df_primeiro(registro, "imc"),
        "classificacao_imc": _df_primeiro(registro, "classificacao_imc", "classificação_imc", "classificacao"),
        "risco_cintura": _df_primeiro(registro, "risco_cintura", "risco"),
        "observacoes": _df_primeiro(registro, "observacoes", "observacao", "observação", "obs"),
    }


def persistir_anamnese_data_flet(registro):
    row = _df_map_anamnese(registro)

    if not row["paciente_id"]:
        print("[DATA_FLET] Anamnese não salva: paciente_id ausente.")
        return

    _df_upsert("anamnese.csv", COLUNAS_ANAMNESE_DATA_FLET, row, ["paciente_id", "data_anamnese"])
    print(f"[DATA_FLET] Anamnese salva: paciente {row['paciente_id']} em {row['data_anamnese']}")


def persistir_recordatorio_data_flet(registro):
    row = _df_map_recordatorio(registro)

    if not row["paciente_id"]:
        print("[DATA_FLET] Recordatório não salvo: paciente_id ausente.")
        return

    _df_upsert("recordatorio_habitual.csv", COLUNAS_RECORDATORIO_DATA_FLET, row, ["paciente_id", "data_registro"])
    print(f"[DATA_FLET] Recordatório salvo: paciente {row['paciente_id']} em {row['data_registro']}")


def persistir_antropometria_data_flet(registro):
    row = _df_map_antropometria(registro)

    if not row["paciente_id"]:
        print("[DATA_FLET] Antropometria não salva: paciente_id ausente.")
        return

    _df_upsert("antropometria.csv", COLUNAS_ANTROPOMETRIA_DATA_FLET, row, ["paciente_id", "data_avaliacao"])
    print(f"[DATA_FLET] Antropometria salva: paciente {row['paciente_id']} em {row['data_avaliacao']}")


class ListaAnamnesePersistente(list):
    def append(self, item):
        super().append(item)
        if not _CARREGANDO_NUTRI_DATA_FLET:
            persistir_anamnese_data_flet(item)


class ListaRecordatorioPersistente(list):
    def append(self, item):
        super().append(item)
        if not _CARREGANDO_NUTRI_DATA_FLET:
            persistir_recordatorio_data_flet(item)


class ListaAntropometriaPersistente(list):
    def append(self, item):
        super().append(item)
        if not _CARREGANDO_NUTRI_DATA_FLET:
            persistir_antropometria_data_flet(item)


def carregar_dados_nutricionais_data_flet_para_memoria():
    global _CARREGANDO_NUTRI_DATA_FLET
    _CARREGANDO_NUTRI_DATA_FLET = True

    try:
        if "ANAMNESES_MOCK" in globals():
            ANAMNESES_MOCK.clear()
            ANAMNESES_MOCK.extend(_df_ler_csv("anamnese.csv", COLUNAS_ANAMNESE_DATA_FLET))

        if "RECORDATORIOS_MOCK" in globals():
            RECORDATORIOS_MOCK.clear()
            RECORDATORIOS_MOCK.extend(_df_ler_csv("recordatorio_habitual.csv", COLUNAS_RECORDATORIO_DATA_FLET))

        if "ANTROPOMETRIAS_MOCK" in globals():
            ANTROPOMETRIAS_MOCK.clear()
            ANTROPOMETRIAS_MOCK.extend(_df_ler_csv("antropometria.csv", COLUNAS_ANTROPOMETRIA_DATA_FLET))

    finally:
        _CARREGANDO_NUTRI_DATA_FLET = False


def ativar_persistencia_nutricional_data_flet():
    global ANAMNESES_MOCK, RECORDATORIOS_MOCK, ANTROPOMETRIAS_MOCK

    if "ANAMNESES_MOCK" in globals() and not isinstance(ANAMNESES_MOCK, ListaAnamnesePersistente):
        ANAMNESES_MOCK = ListaAnamnesePersistente(ANAMNESES_MOCK)

    if "RECORDATORIOS_MOCK" in globals() and not isinstance(RECORDATORIOS_MOCK, ListaRecordatorioPersistente):
        RECORDATORIOS_MOCK = ListaRecordatorioPersistente(RECORDATORIOS_MOCK)

    if "ANTROPOMETRIAS_MOCK" in globals() and not isinstance(ANTROPOMETRIAS_MOCK, ListaAntropometriaPersistente):
        ANTROPOMETRIAS_MOCK = ListaAntropometriaPersistente(ANTROPOMETRIAS_MOCK)

    carregar_dados_nutricionais_data_flet_para_memoria()

    print("[DATA_FLET] Persistência nutricional ativada.")
    print(f"[DATA_FLET] Anamneses: {len(globals().get('ANAMNESES_MOCK', []))}")
    print(f"[DATA_FLET] Recordatórios: {len(globals().get('RECORDATORIOS_MOCK', []))}")
    print(f"[DATA_FLET] Antropometrias: {len(globals().get('ANTROPOMETRIAS_MOCK', []))}")




# ============================================================
# NUTRIÇÃO FINAL - PAINEL COMPLETO COM GRÁFICOS E INSIGHTS
# ============================================================

def _nutri_csv(nome):
    caminho = Path(__file__).resolve().parent / "data_flet" / nome
    if not caminho.exists():
        return []

    try:
        with caminho.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    except UnicodeDecodeError:
        with caminho.open("r", encoding="latin-1", newline="") as f:
            return list(csv.DictReader(f))
    except Exception as exc:
        print(f"[NUTRIÇÃO] Erro ao ler {nome}: {exc}")
        return []


def _nutri_float(valor):
    valor = str(valor or "").strip()
    valor = re.sub(r"[^0-9,.\-]", "", valor)

    if not valor:
        return None

    if "," in valor:
        valor = valor.replace(".", "").replace(",", ".")

    try:
        return float(valor)
    except Exception:
        return None


def _nutri_data_br(valor):
    valor = str(valor or "").strip()

    if not valor:
        return "-"

    if re.match(r"^\d{2}/\d{2}/\d{4}$", valor):
        return valor

    try:
        return datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return valor


def _nutri_card(content, padding=20):
    if "app_card" in globals():
        try:
            return app_card(content, padding=padding)
        except Exception:
            pass

    return ft.Container(
        bgcolor="#FFFFFF",
        border_radius=18,
        padding=padding,
        content=content,
    )


def _nutri_status(status):
    st = str(status or "").strip().lower()

    if st in ["normal", "ok", "dentro", "dentro da referência", "dentro da referencia"]:
        return "Normal"

    if st in ["alto", "acima", "acima da referência", "acima da referencia"]:
        return "Alto"

    if st in ["baixo", "abaixo", "abaixo da referência", "abaixo da referencia"]:
        return "Baixo"

    if st in ["critico", "crítico"]:
        return "Crítico"

    if st:
        return str(status).strip()

    return "Sem análise"


def _nutri_alterado(status):
    return _nutri_status(status) not in ["Normal", "Sem análise"]


def _nutri_nome_exame(row):
    for campo in [
        "nome_exame",
        "nome_padronizado",
        "nome",
        "exame",
        "exame_nome",
        "analito",
    ]:
        valor = str(row.get(campo) or "").strip()
        if valor and valor.lower() != "none":
            return valor

    return "-"


def _nutri_pacientes():
    pacientes = []

    for r in _nutri_csv("pacientes.csv"):
        pid = str(r.get("paciente_id") or r.get("id") or "").strip()

        if not pid:
            continue

        r["id"] = pid
        r["paciente_id"] = pid
        pacientes.append(r)

    return pacientes


def _nutri_paciente(pid):
    pid = str(pid or "").strip()

    for p in _nutri_pacientes():
        if str(p.get("paciente_id") or p.get("id") or "").strip() == pid:
            return p

    return {"id": pid, "paciente_id": pid, "nome": "Paciente", "idade": ""}


def _nutri_exames(pid):
    pid = str(pid or "").strip()
    exames = []

    for r in _nutri_csv("analise_exames.csv"):
        if str(r.get("paciente_id") or "").strip() != pid:
            continue

        nome = _nutri_nome_exame(r)

        exames.append({
            "paciente_id": pid,
            "data_exame": r.get("data_exame") or r.get("data") or "",
            "data": _nutri_data_br(r.get("data_exame") or r.get("data") or ""),
            "nome_exame": nome,
            "nome_padronizado": r.get("nome_padronizado") or nome,
            "exame_nome": nome,
            "nome": nome,
            "exame": nome,
        "exame_nome": nome,
            "resultado": r.get("resultado") or "",
            "unidade": r.get("unidade") or "",
            "valor_min": r.get("valor_min") or "",
            "valor_max": r.get("valor_max") or "",
            "status": _nutri_status(r.get("status")),
            "mensagem": r.get("mensagem") or "",
            "referencia": r.get("referencia") or r.get("mensagem") or "",
            "fonte_referencia": r.get("fonte_referencia") or "",
        })

    return exames


def _nutri_registros(nome_csv, pid):
    pid = str(pid or "").strip()
    rows = []

    for r in _nutri_csv(nome_csv):
        rid = str(r.get("paciente_id") or r.get("id_paciente") or r.get("id") or "").strip()
        if rid == pid:
            rows.append(r)

    def chave(row):
        return str(
            row.get("data")
            or row.get("data_registro")
            or row.get("data_avaliacao")
            or row.get("data_anamnese")
            or ""
        )

    rows.sort(key=chave, reverse=True)
    return rows


def _nutri_ultimo(nome_csv, pid):
    rows = _nutri_registros(nome_csv, pid)
    return rows[0] if rows else {}


def _nutri_resumo_exames(exames):
    total = len(exames)
    normais = len([e for e in exames if _nutri_status(e.get("status")) == "Normal"])
    alterados = len([e for e in exames if _nutri_alterado(e.get("status"))])
    sem = len([e for e in exames if _nutri_status(e.get("status")) == "Sem análise"])

    return {
        "total": total,
        "normais": normais,
        "alterados": alterados,
        "sem": sem,
    }


def _nutri_analise_antropometrica(paciente, antropometria):
    peso = _nutri_float(antropometria.get("peso") or paciente.get("peso"))
    altura = _nutri_float(antropometria.get("altura") or paciente.get("altura"))
    cintura = _nutri_float(
        antropometria.get("circunferencia_cintura")
        or antropometria.get("cintura")
        or antropometria.get("cc")
    )

    sexo = str(paciente.get("sexo") or "").upper()

    if altura and altura > 3:
        altura_cm = altura
        altura_m = altura / 100
    elif altura:
        altura_m = altura
        altura_cm = altura * 100
    else:
        altura_m = None
        altura_cm = None

    imc = None
    classificacao = "Dados insuficientes"

    if peso and altura_m:
        imc = peso / (altura_m ** 2)

        if imc < 18.5:
            classificacao = "Baixo peso"
        elif imc < 25:
            classificacao = "Eutrofia"
        elif imc < 30:
            classificacao = "Sobrepeso"
        elif imc < 35:
            classificacao = "Obesidade grau I"
        elif imc < 40:
            classificacao = "Obesidade grau II"
        else:
            classificacao = "Obesidade grau III"

    risco = "Não avaliado"

    if cintura:
        if sexo.startswith("F"):
            risco = "Sem aumento relevante"
            if cintura >= 80:
                risco = "Aumentado"
            if cintura >= 88:
                risco = "Muito aumentado"
        else:
            risco = "Sem aumento relevante"
            if cintura >= 94:
                risco = "Aumentado"
            if cintura >= 102:
                risco = "Muito aumentado"

    insights = []

    if peso:
        insights.append(f"Peso atual registrado: {peso:.1f} kg.")

    if altura_cm:
        insights.append(f"Altura utilizada no cálculo: {altura_cm:.0f} cm.")

    if imc:
        insights.append(f"IMC atual: {imc:.1f} kg/m² — {classificacao}.")
        if imc >= 25:
            insights.append("O IMC sugere atenção à composição corporal, balanço energético e acompanhamento de cintura.")
        else:
            insights.append("IMC sem alerta automático relevante, devendo ser acompanhado junto à composição corporal e objetivo.")
    else:
        insights.append("IMC não calculado por ausência de peso e/ou altura.")

    if cintura:
        insights.append(f"Circunferência de cintura: {cintura:.1f} cm — risco {risco.lower()}.")
    else:
        insights.append("Circunferência de cintura não cadastrada; incluir nas próximas avaliações.")

    return {
        "peso": peso,
        "altura_cm": altura_cm,
        "altura_m": altura_m,
        "cintura": cintura,
        "imc": imc,
        "classificacao": classificacao,
        "risco": risco,
        "insights": insights,
    }


def _nutri_texto(row):
    return " ".join([str(v or "") for v in row.values()]).lower()


def _nutri_fator_atividade(anamnese):
    texto = _nutri_texto(anamnese)

    if any(t in texto for t in ["muito ativo", "intenso", "alta intensidade", "atleta", "diário", "diario"]):
        return 1.725, "Intensa"

    if any(t in texto for t in ["moderado", "moderada", "musculação", "musculacao", "3 vezes", "4 vezes", "5 vezes"]):
        return 1.55, "Moderada"

    if any(t in texto for t in ["luta", "artes marciais", "caminhada", "leve", "1x", "1 vez", "2 vezes"]):
        return 1.375, "Leve"

    if any(t in texto for t in ["sedent", "não pratica", "nao pratica"]):
        return 1.2, "Sedentária"

    return 1.375, "Leve/estimada"


def _nutri_objetivo(anamnese):
    texto = _nutri_texto(anamnese)

    if any(t in texto for t in ["ganho de massa", "hipertrofia", "massa muscular", "performance"]):
        return "Ganho de massa/performance"

    if any(t in texto for t in ["emagrecer", "perda de peso", "redução de peso", "reducao de peso", "definição", "definicao"]):
        return "Redução de peso"

    if any(t in texto for t in ["manutenção", "manutencao", "preventivo", "qualidade de vida"]):
        return "Manutenção/prevenção"

    return "Não informado"


def _nutri_estimar_ingestao(recordatorio):
    if not recordatorio:
        return None, "Recordatório não cadastrado."

    for campo in ["kcal", "calorias", "total_kcal", "energia"]:
        v = _nutri_float(recordatorio.get(campo))
        if v:
            return v, f"Valor informado no campo {campo}."

    refeicoes = {
        "desjejum": 350,
        "lanche_manha": 180,
        "almoco": 700,
        "lanche_tarde": 250,
        "jantar": 650,
        "ceia": 150,
    }

    total = 0
    encontrou = False

    for campo, base in refeicoes.items():
        texto = str(recordatorio.get(campo) or "").lower().strip()

        if not texto or texto == "não informado" or texto == "nao informado":
            continue

        encontrou = True
        kcal = base

        if any(t in texto for t in ["biscoito", "bolo", "pizza", "hamb", "salgado", "doce", "manteiga", "queijo"]):
            kcal += 180

        if any(t in texto for t in ["arroz", "feijão", "feijao", "pão", "pao", "tapioca", "massa"]):
            kcal += 120

        if any(t in texto for t in ["carne", "frango", "ovo", "peixe"]):
            kcal += 140

        if any(t in texto for t in ["salada", "legume", "fruta", "verdura"]):
            kcal -= 70

        total += max(80, kcal)

    if encontrou:
        return total, "Estimativa heurística baseada nos alimentos descritos no recordatório."

    return None, "Recordatório sem refeições interpretáveis."


def _nutri_analise_calorica(paciente, anamnese, recordatorio, antro):
    peso = antro.get("peso")
    altura_cm = antro.get("altura_cm")
    idade = _nutri_float(paciente.get("idade"))
    sexo = str(paciente.get("sexo") or "").upper()

    fator, atividade = _nutri_fator_atividade(anamnese)
    objetivo = _nutri_objetivo(anamnese)

    if not peso or not altura_cm or not idade:
        return {
            "calculado": False,
            "atividade": atividade,
            "objetivo": objetivo,
            "basal": 0,
            "manutencao": 0,
            "ingestao": 0,
            "meta": 0,
            "diferenca": None,
            "fonte": "Dados insuficientes.",
            "insights": [
                "Não foi possível calcular gasto calórico por falta de peso, altura ou idade.",
            ],
        }

    if sexo.startswith("F"):
        basal = (10 * peso) + (6.25 * altura_cm) - (5 * idade) - 161
    else:
        basal = (10 * peso) + (6.25 * altura_cm) - (5 * idade) + 5

    manutencao = basal * fator
    ingestao, fonte = _nutri_estimar_ingestao(recordatorio)

    if objetivo == "Redução de peso":
        meta = manutencao - 500
    elif objetivo == "Ganho de massa/performance":
        meta = manutencao + 300
    else:
        meta = manutencao

    diferenca = ingestao - meta if ingestao else None

    insights = [
        f"Gasto basal estimado: {basal:.0f} kcal/dia.",
        f"Gasto total estimado para manutenção: {manutencao:.0f} kcal/dia.",
        f"Nível de atividade considerado: {atividade}.",
        f"Objetivo considerado: {objetivo}.",
        f"Meta calórica sugerida: {meta:.0f} kcal/dia.",
    ]

    if ingestao:
        insights.append(f"Ingestão estimada pelo recordatório: {ingestao:.0f} kcal/dia.")

        if diferenca > 250:
            insights.append("A ingestão estimada está acima da meta; avaliar ajuste de porções, gorduras e alimentos ultraprocessados.")
        elif diferenca < -250:
            insights.append("A ingestão estimada está abaixo da meta; avaliar risco de baixa energia, fome, baixa adesão ou queda de performance.")
        else:
            insights.append("A ingestão estimada está próxima da meta calculada.")
    else:
        insights.append("Sem ingestão estimada confiável; registrar porções no recordatório para melhorar o cálculo.")

    return {
        "calculado": True,
        "atividade": atividade,
        "objetivo": objetivo,
        "basal": basal,
        "manutencao": manutencao,
        "ingestao": ingestao or 0,
        "meta": meta,
        "diferenca": diferenca,
        "fonte": fonte,
        "insights": insights,
    }



# ===== PATCH: DIAGNÓSTICO NUTRICIONAL INTELIGENTE NA TELA NUTRIÇÃO =====

# ===== PATCH: TABELA DE ANÁLISE DOS EXAMES NA TELA NUTRIÇÃO =====
def _nutri_texto_tabela(valor, largura, negrito=False):
    return ft.Container(
        width=largura,
        padding=ft.Padding.symmetric(horizontal=4, vertical=4),
        content=ft.Text(
            str(valor or ""),
            size=11,
            color="#111827",
            weight=ft.FontWeight.BOLD if negrito else ft.FontWeight.NORMAL,
        ),
    )


def _nutri_tabela_diagnostico_exames(exames):
    """
    Renderiza a análise dos exames em tabela, no mesmo conceito do relatório PDF.

    Substitui os cards soltos de insights por uma visão tabular:
    Exame | Interpretação | Possível alteração | Conduta | Complementares.
    """
    try:
        from diagnostico_nutricional_inteligente import gerar_diagnostico_inteligente
    except Exception as exc:
        return ft.Container(
            bgcolor="#FFFFFF",
            border_radius=18,
            padding=20,
            content=ft.Text(
                f"Diagnóstico nutricional indisponível: {exc}",
                size=13,
                color="#B91C1C",
            ),
        )

    try:
        diag = gerar_diagnostico_inteligente(exames or [])
    except Exception as exc:
        return ft.Container(
            bgcolor="#FFFFFF",
            border_radius=18,
            padding=20,
            content=ft.Text(
                f"Não foi possível gerar a análise dos exames: {exc}",
                size=13,
                color="#B91C1C",
            ),
        )

    total = diag.get("total_exames_analisados", 0)
    alteracoes = diag.get("total_alteracoes", 0)
    alertas = diag.get("total_alertas_combinados", 0)
    sugestoes = diag.get("sugestoes", []) or []

    linhas = []

    if sugestoes:
        for item in sugestoes:
            linhas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(_nutri_texto_tabela(item.get("exame", ""), 125)),
                        ft.DataCell(_nutri_texto_tabela(item.get("interpretacao", ""), 135)),
                        ft.DataCell(_nutri_texto_tabela(item.get("possivel_condicao", ""), 220)),
                        ft.DataCell(_nutri_texto_tabela(item.get("conduta", ""), 260)),
                        ft.DataCell(_nutri_texto_tabela(item.get("complementares", ""), 210)),
                    ]
                )
            )
    else:
        linhas.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(_nutri_texto_tabela("Sem alterações", 125)),
                    ft.DataCell(_nutri_texto_tabela("Dentro da referência", 135)),
                    ft.DataCell(_nutri_texto_tabela("Nenhum exame fora da referência laboratorial foi identificado.", 220)),
                    ft.DataCell(_nutri_texto_tabela("Manter acompanhamento evolutivo conforme sintomas, rotina alimentar e histórico clínico.", 260)),
                    ft.DataCell(_nutri_texto_tabela("", 210)),
                ]
            )
        )

    tabela = ft.DataTable(
        heading_row_color="#F3F4F6",
        data_row_color="#FFFFFF",
        column_spacing=8,
        horizontal_margin=8,
        columns=[
            ft.DataColumn(_nutri_texto_tabela("Exame", 125, negrito=True)),
            ft.DataColumn(_nutri_texto_tabela("Interpretação", 135, negrito=True)),
            ft.DataColumn(_nutri_texto_tabela("Possível alteração", 220, negrito=True)),
            ft.DataColumn(_nutri_texto_tabela("Conduta / possível tratamento nutricional", 260, negrito=True)),
            ft.DataColumn(_nutri_texto_tabela("Complementares", 210, negrito=True)),
        ],
        rows=linhas,
    )

    return ft.Container(
        bgcolor="#FFFFFF",
        border_radius=18,
        padding=20,
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Text(
                    "Análise dos exames",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#111827",
                ),
                ft.Text(
                    f"{total} exame(s) analisado(s) • {alteracoes} resultado(s) fora da referência laboratorial • {alertas} alerta(s) combinado(s)",
                    size=12,
                    color="#6B7280",
                ),
                ft.Container(
                    bgcolor="#F9FAFB",
                    border_radius=12,
                    padding=8,
                    content=ft.Row(
                        scroll=ft.ScrollMode.AUTO,
                        controls=[tabela],
                    ),
                ),
                ft.Text(
                    "Nota: análise de apoio nutricional. Não substitui avaliação clínica, diagnóstico médico ou prescrição medicamentosa.",
                    size=11,
                    color="#6B7280",
                ),
            ],
        ),
    )
# ===== FIM PATCH: TABELA DE ANÁLISE DOS EXAMES NA TELA NUTRIÇÃO =====



# ===== PATCH: CONVERTER INSIGHTS EM TABELA DE ANÁLISE DOS EXAMES =====
def _nutri_parse_insight_para_linha(texto):
    """
    Converte um insight textual do diagnóstico em linha de tabela.

    Esperado:
    Exame — Interpretação. Possível alteração... Conduta: ... Complementares: ...
    """
    texto = str(texto or "").strip().lstrip("•").strip()

    if not texto:
        return None

    # Ignora resumo, nota e hábitos/anamnese.
    ignorar = [
        "Resumo:",
        "Nota:",
        "Objetivo/",
        "Qualidade do sono",
        "Ingestão hídrica",
        "Intolerância",
        "Recordatório",
        "Refeições",
        "Diagnóstico nutricional",
        "Nenhum exame fora",
    ]

    if any(texto.startswith(prefixo) for prefixo in ignorar):
        return None

    if "—" not in texto:
        return None

    exame, resto = texto.split("—", 1)
    exame = exame.strip()
    resto = resto.strip()

    interpretacao = ""
    possivel = ""
    conduta = ""
    complementares = ""

    if "." in resto:
        interpretacao, resto = resto.split(".", 1)
        interpretacao = interpretacao.strip()
        resto = resto.strip()
    else:
        interpretacao = resto.strip()
        resto = ""

    if "Conduta:" in resto:
        possivel, resto = resto.split("Conduta:", 1)
        possivel = possivel.strip()
        resto = resto.strip()
    else:
        possivel = resto.strip()
        resto = ""

    if "Complementares:" in resto:
        conduta, complementares = resto.split("Complementares:", 1)
        conduta = conduta.strip()
        complementares = complementares.strip()
    else:
        conduta = resto.strip()

    return {
        "exame": exame,
        "interpretacao": interpretacao,
        "possivel": possivel,
        "conduta": conduta,
        "complementares": complementares,
    }


def _nutri_cell_tabela(valor, largura, negrito=False):
    return ft.Container(
        width=largura,
        padding=ft.Padding.symmetric(horizontal=4, vertical=5),
        content=ft.Text(
            str(valor or ""),
            size=11,
            color="#111827",
            weight=ft.FontWeight.BOLD if negrito else ft.FontWeight.NORMAL,
        ),
    )


def _nutri_tabela_analise_a_partir_de_insights(itens):
    """
    Substitui os cards de insights por uma tabela visual equivalente ao relatório.
    """
    itens = list(itens or [])

    linhas_parseadas = []

    for item in itens:
        linha = _nutri_parse_insight_para_linha(item)
        if linha:
            linhas_parseadas.append(linha)

    rows = []

    if linhas_parseadas:
        for linha in linhas_parseadas:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(_nutri_cell_tabela(linha["exame"], 130)),
                        ft.DataCell(_nutri_cell_tabela(linha["interpretacao"], 140)),
                        ft.DataCell(_nutri_cell_tabela(linha["possivel"], 250)),
                        ft.DataCell(_nutri_cell_tabela(linha["conduta"], 270)),
                        ft.DataCell(_nutri_cell_tabela(linha["complementares"], 220)),
                    ]
                )
            )
    else:
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(_nutri_cell_tabela("Sem alterações", 130)),
                    ft.DataCell(_nutri_cell_tabela("Dentro da referência", 140)),
                    ft.DataCell(_nutri_cell_tabela("Nenhum exame fora da referência laboratorial foi identificado.", 250)),
                    ft.DataCell(_nutri_cell_tabela("Manter acompanhamento evolutivo conforme sintomas, rotina alimentar e histórico clínico.", 270)),
                    ft.DataCell(_nutri_cell_tabela("", 220)),
                ]
            )
        )

    tabela = ft.DataTable(
        heading_row_color="#F3F4F6",
        data_row_color="#FFFFFF",
        column_spacing=8,
        horizontal_margin=8,
        columns=[
            ft.DataColumn(_nutri_cell_tabela("Exame", 130, negrito=True)),
            ft.DataColumn(_nutri_cell_tabela("Interpretação", 140, negrito=True)),
            ft.DataColumn(_nutri_cell_tabela("Possível alteração", 250, negrito=True)),
            ft.DataColumn(_nutri_cell_tabela("Conduta / possível tratamento nutricional", 270, negrito=True)),
            ft.DataColumn(_nutri_cell_tabela("Complementares", 220, negrito=True)),
        ],
        rows=rows,
    )

    return ft.Container(
        bgcolor="#FFFFFF",
        border_radius=18,
        padding=20,
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Text(
                    "Análise dos exames",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#111827",
                ),
                ft.Text(
                    "Resultados fora da referência laboratorial com interpretação, conduta e complementares.",
                    size=12,
                    color="#6B7280",
                ),
                ft.Container(
                    bgcolor="#F9FAFB",
                    border_radius=12,
                    padding=8,
                    content=ft.Row(
                        scroll=ft.ScrollMode.AUTO,
                        controls=[tabela],
                    ),
                ),
                ft.Text(
                    "Nota: análise de apoio nutricional. Não substitui avaliação clínica, diagnóstico médico ou prescrição medicamentosa.",
                    size=11,
                    color="#6B7280",
                ),
            ],
        ),
    )
# ===== FIM PATCH: CONVERTER INSIGHTS EM TABELA DE ANÁLISE DOS EXAMES =====


def _diagnostico_nutricional_inteligente_para_insights(exames):
    """
    Converte o diagnóstico nutricional em cards objetivos para a tela Nutrição.

    UX:
    - Um card por exame alterado.
    - Texto direto, sem repetir nome do exame dentro da explicação.
    - Conduta e complementares no mesmo card.
    """
    try:
        from diagnostico_nutricional_inteligente import gerar_diagnostico_inteligente
    except Exception as exc:
        return [f"Diagnóstico nutricional indisponível: {exc}"]

    try:
        diag = gerar_diagnostico_inteligente(exames)
    except Exception as exc:
        return [f"Não foi possível gerar o diagnóstico nutricional: {exc}"]

    total = diag.get("total_exames_analisados", 0)
    alteracoes = diag.get("total_alteracoes", 0)
    alertas_qtd = diag.get("total_alertas_combinados", 0)

    linhas = [
        (
            f"Resumo: {total} exame(s) analisado(s), "
            f"{alteracoes} resultado(s) fora da referência laboratorial "
            f"e {alertas_qtd} alerta(s) combinado(s)."
        )
    ]

    sugestoes = diag.get("sugestoes", []) or []

    if not sugestoes:
        linhas.append(
            "Nenhum exame fora da referência laboratorial foi identificado. "
            "Manter acompanhamento evolutivo conforme sintomas, rotina alimentar e histórico clínico."
        )
        return linhas

    for item in sugestoes[:12]:
        exame = str(item.get("exame") or "Exame").strip()
        interpretacao = str(item.get("interpretacao") or "").strip()
        condicao = str(item.get("possivel_condicao") or "").strip()
        conduta = str(item.get("conduta") or "").strip()
        complementares = str(item.get("complementares") or "").strip()

        partes = []

        if condicao:
            partes.append(condicao)

        if conduta:
            partes.append(f"Conduta: {conduta}")

        if complementares:
            partes.append(f"Complementares: {complementares}")

        corpo = " ".join(partes).strip()

        if interpretacao and corpo:
            linhas.append(f"{exame} — {interpretacao}. {corpo}")
        elif interpretacao:
            linhas.append(f"{exame} — {interpretacao}.")
        elif corpo:
            linhas.append(f"{exame} — {corpo}")

    linhas.append(
        "Nota: apoio nutricional. Não substitui avaliação clínica, diagnóstico médico ou prescrição medicamentosa."
    )

    return linhas



def _nutri_insights_exames(exames):
    return _diagnostico_nutricional_inteligente_para_insights(exames)


def _nutri_insights_habitos(anamnese, recordatorio):
    insights = []

    agua = str(anamnese.get("ingestao_agua_dia") or "").strip()
    sono = str(anamnese.get("qualidade_sono") or "").strip()
    objetivo = str(anamnese.get("objetivo_nutricional") or anamnese.get("queixa_principal") or "").strip()
    intolerancia = str(anamnese.get("intolerancia_alergia_alimentar") or "").strip()

    if objetivo:
        insights.append(f"Objetivo/queixa principal: {objetivo}.")

    if sono:
        insights.append(f"Qualidade do sono: {sono}.")

    if agua:
        insights.append(f"Ingestão hídrica registrada: {agua}.")
        if "menos" in agua.lower() or "500" in agua.lower():
            insights.append("Prioridade: aumentar hidratação de forma progressiva, principalmente por haver densidade urinária elevada.")

    if intolerancia:
        insights.append(f"Intolerância/alergia alimentar registrada: {intolerancia}. Ajustar plano alimentar para preservar adesão e conforto gastrointestinal.")

    texto_recordatorio = _nutri_texto(recordatorio)

    if any(t in texto_recordatorio for t in ["biscoito", "bolo", "salgado"]):
        insights.append("Recordatório mostra beliscos com biscoitos/bolo/salgados; avaliar troca planejada para lanches com melhor densidade nutricional.")

    if any(t in texto_recordatorio for t in ["arroz", "feijão", "frango", "carne"]):
        insights.append("Recordatório possui refeições principais estruturadas com carboidrato e proteína, bom ponto de partida para ajuste de porções.")

    return insights or ["Anamnese/recordatório ainda precisam de mais detalhes para insights comportamentais."]


def _nutri_prioridades(exames, antro, calorias, anamnese):
    prioridades = []

    if any("densidade" in _nutri_nome_exame(e).lower() and _nutri_alterado(e.get("status")) for e in exames):
        prioridades.append("Hidratação: definir meta diária progressiva e monitorar resposta pela urina/densidade urinária.")

    if any("colesterol total" in _nutri_nome_exame(e).lower() and _nutri_alterado(e.get("status")) for e in exames):
        prioridades.append("Perfil lipídico: aumentar fibras, ajustar gorduras, reduzir ultraprocessados e acompanhar nova coleta.")

    if any("plaqueta" in _nutri_nome_exame(e).lower() and _nutri_alterado(e.get("status")) for e in exames):
        prioridades.append("Plaquetas baixas: registrar como alerta clínico e orientar correlação médica se persistente.")

    if antro.get("imc") and antro["imc"] >= 25:
        prioridades.append("Composição corporal: acompanhar peso, cintura e adesão; alinhar superávit controlado se objetivo for ganho de massa.")

    if calorias.get("calculado") and calorias.get("objetivo") == "Ganho de massa/performance":
        prioridades.append("Ganho de massa/performance: garantir proteína adequada, treino progressivo e superávit calórico leve.")

    agua = str(anamnese.get("ingestao_agua_dia") or "").lower()
    if "menos" in agua or "500" in agua:
        prioridades.append("Baixa ingestão hídrica: meta inicial pode ser fracionar água ao longo do dia antes de grandes mudanças alimentares.")

    return prioridades or ["Manter acompanhamento preventivo e revisar metas a cada nova avaliação."]


def _nutri_metric(titulo, valor, subtitulo="", cor="#111827"):
    return _nutri_card(
        ft.Column(
            spacing=6,
            controls=[
                ft.Text(titulo, size=13, color="#64748B"),
                ft.Text(str(valor), size=28, weight=ft.FontWeight.BOLD, color=cor),
                ft.Text(subtitulo, size=11, color="#64748B") if subtitulo else ft.Container(height=1),
            ],
        ),
        padding=18,
    )


def _nutri_bar_chart(titulo, dados, descricao=""):
    max_val = max([v for _, v, _ in dados if v is not None] + [1])

    barras = []

    for label, valor, cor in dados:
        valor = valor or 0
        altura = 35 + int((valor / max_val) * 135)

        barras.append(
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.END,
                spacing=8,
                controls=[
                    ft.Text(f"{valor:.0f}", size=13, weight=ft.FontWeight.BOLD, color="#111827"),
                    ft.Container(width=68, height=altura, bgcolor=cor, border_radius=12),
                    ft.Text(label, size=12, color="#64748B"),
                ],
            )
        )

    controls = [
        ft.Text(titulo, size=18, weight=ft.FontWeight.BOLD, color="#111827"),
    ]

    if descricao:
        controls.append(ft.Text(descricao, size=13, color="#64748B"))

    controls.append(
        ft.Container(
            height=260,
            bgcolor="#F8FAFC",
            border_radius=16,
            padding=20,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                vertical_alignment=ft.CrossAxisAlignment.END,
                controls=barras,
            ),
        )
    )

    return _nutri_card(ft.Column(spacing=14, controls=controls))


def _nutri_lista(titulo, itens, subtitulo=""):
    if str(titulo or "").strip() == "Insights de apoio nutricional":
        return _nutri_tabela_analise_a_partir_de_insights(itens)

    controls = [
        ft.Text(titulo, size=18, weight=ft.FontWeight.BOLD, color="#111827"),
    ]

    if subtitulo:
        controls.append(ft.Text(subtitulo, size=13, color="#64748B"))

    for item in itens:
        controls.append(
            ft.Container(
                bgcolor="#F8FAFC",
                border_radius=12,
                padding=12,
                content=ft.Text(f"• {item}", size=13, color="#374151"),
            )
        )

    return _nutri_card(ft.Column(spacing=10, controls=controls))


def _nutri_tabela_alterados(alterados):
    if not alterados:
        return _nutri_lista("Exames alterados", ["Nenhum exame fora da referência automática."])

    rows = []

    for e in alterados:
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(_nutri_data_br(e.get("data_exame") or e.get("data")), size=12)),
                    ft.DataCell(ft.Text(_nutri_nome_exame(e), size=12)),
                    ft.DataCell(ft.Text(f'{e.get("resultado", "")} {e.get("unidade", "")}'.strip(), size=12)),
                    ft.DataCell(ft.Text(_nutri_status(e.get("status")), size=12)),
                ]
            )
        )

    return _nutri_card(
        ft.Column(
            spacing=14,
            controls=[
                ft.Text("Exames alterados", size=18, weight=ft.FontWeight.BOLD, color="#111827"),
                ft.Text("Lista focada apenas nos exames fora da referência.", size=13, color="#64748B"),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Data")),
                        ft.DataColumn(ft.Text("Exame")),
                        ft.DataColumn(ft.Text("Resultado")),
                        ft.DataColumn(ft.Text("Status")),
                    ],
                    rows=rows,
                    heading_row_color="#F8FAFC",
                    border_radius=12,
                ),
            ],
        )
    )


def _nutri_gerar_pdf(page, paciente):
    try:
        caminho = gerar_pdf_analise_paciente(paciente)
        if "mostrar_snackbar" in globals():
            mostrar_snackbar(page, f"PDF gerado: {caminho}", globals().get("COR_NORMAL", "#16A34A"))
        else:
            print("PDF gerado:", caminho)
    except Exception as exc:
        if "mostrar_snackbar" in globals():
            mostrar_snackbar(page, f"Erro ao gerar PDF: {exc}", globals().get("COR_CRITICO", "#DC2626"))
        else:
            print("Erro ao gerar PDF:", exc)


def nutricao_view(page):
    pacientes = _nutri_pacientes()

    opcoes = []

    for p in pacientes:
        pid = str(p.get("paciente_id") or p.get("id") or "").strip()
        nome = str(p.get("nome") or "").strip()
        idade = str(p.get("idade") or "").strip()

        if pid:
            opcoes.append(ft.dropdown.Option(key=pid, text=f"{nome} - {idade} anos" if idade else nome))

    paciente_dropdown = ft.Dropdown(
        label="Paciente",
        width=420,
        options=opcoes,
        value=opcoes[0].key if opcoes else None,
        border_radius=12,
    )

    painel = ft.Column(spacing=16)

    def montar(e=None, atualizar_pagina=True):
        pid = paciente_dropdown.value

        if not pid:
            painel.controls = [_nutri_lista("Análise nutricional", ["Nenhum paciente selecionado."])]
            if atualizar_pagina:
                page.update()
            return

        paciente = _nutri_paciente(pid)
        exames = _nutri_exames(pid)
        resumo = _nutri_resumo_exames(exames)
        alterados = [e for e in exames if _nutri_alterado(e.get("status"))]

        anamnese = _nutri_ultimo("anamnese.csv", pid)
        recordatorio = _nutri_ultimo("recordatorio_habitual.csv", pid)
        antropometria_reg = _nutri_ultimo("antropometria.csv", pid)

        antro = _nutri_analise_antropometrica(paciente, antropometria_reg)
        calorias = _nutri_analise_calorica(paciente, anamnese, recordatorio, antro)

        qtd_anamnese = len(_nutri_registros("anamnese.csv", pid))
        qtd_recordatorio = len(_nutri_registros("recordatorio_habitual.csv", pid))
        qtd_antropometria = len(_nutri_registros("antropometria.csv", pid))

        dados_caloricos = [
            ("Manutenção", calorias.get("manutencao") or 0, "#2563EB"),
            ("Meta", calorias.get("meta") or 0, "#16A34A"),
        ]

        if calorias.get("ingestao"):
            dados_caloricos.insert(1, ("Ingestão", calorias.get("ingestao") or 0, "#F59E0B"))

        painel.controls = [
            ft.Row(
                spacing=16,
                controls=[
                    _nutri_metric("Resultados", resumo["total"], "Exames analisados", "#2563EB"),
                    _nutri_metric("Normais", resumo["normais"], "Dentro da referência", "#16A34A"),
                    _nutri_metric("Alterados", resumo["alterados"], "Fora da referência", "#F59E0B"),
                ],
            ),
            _nutri_card(
                ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text(str(paciente.get("nome") or "Paciente"), size=24, weight=ft.FontWeight.BOLD, color="#111827"),
                        ft.Text(
                            f"Anamneses: {qtd_anamnese} • Recordatórios: {qtd_recordatorio} • Antropometrias: {qtd_antropometria} • Exames: {resumo['total']}",
                            size=13,
                            color="#64748B",
                        ),
                    ],
                )
            ),
            _nutri_bar_chart(
                "Dashboard de exames",
                [
                    ("Total", resumo["total"], "#2563EB"),
                    ("Normais", resumo["normais"], "#16A34A"),
                    ("Alterados", resumo["alterados"], "#F59E0B"),
                ],
                "Quantidade total de exames, exames normais e exames alterados.",
            ),
            _nutri_tabela_alterados(alterados),
            _nutri_lista(
                "Insights de apoio nutricional",
                _nutri_insights_exames(exames) + _nutri_insights_habitos(anamnese, recordatorio),
                "Leitura integrada de exames, anamnese e recordatório.",
            ),
            _nutri_lista(
                "Prioridades sugeridas de conduta",
                _nutri_prioridades(exames, antro, calorias, anamnese),
                "Sugestões objetivas para orientar o plano alimentar e o acompanhamento.",
            ),
            _nutri_lista(
                "Análise antropométrica",
                antro["insights"],
                "Baseada no último registro antropométrico do paciente.",
            ),
            _nutri_lista(
                "Análise do gasto calórico",
                calorias["insights"],
                "Estimativa baseada em peso, altura, idade, sexo, atividade, objetivo e recordatório.",
            ),
            _nutri_bar_chart(
                "Comparativo calórico",
                dados_caloricos,
                "Comparação entre manutenção, ingestão estimada e meta conforme objetivo do tratamento.",
            ),
            _nutri_card(
                ft.Column(
                    spacing=10,
                    controls=[
                        ft.Text("Ações recomendadas no sistema", size=18, weight=ft.FontWeight.BOLD, color="#111827"),
                        ft.Text("• Atualizar anamnese quando houver mudança de objetivo, sono, treino, sintomas ou medicações.", size=13, color="#374151"),
                        ft.Text("• Registrar porções no recordatório para melhorar a estimativa calórica.", size=13, color="#374151"),
                        ft.Text("• Repetir antropometria periodicamente para acompanhar peso, cintura e evolução.", size=13, color="#374151"),
                        ft.Text("• Reavaliar exames alterados em nova coleta e acompanhar tendência.", size=13, color="#374151"),
                        ft.Row(
                            controls=[
                                ft.OutlinedButton(
                                    content="Gerar PDF desta análise",
                                    icon=ft.Icons.PICTURE_AS_PDF,
                                    on_click=lambda ev: _nutri_gerar_pdf(page, paciente),
                                    style=ft.ButtonStyle(
                                        color=globals().get("COR_PRIMARIA", "#2563EB"),
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                    ),
                                )
                            ]
                        ),
                    ],
                )
            ),
        ]

        if atualizar_pagina:
            page.update()

    atualizar_btn = ft.FilledButton(
        content=ft.Text("Atualizar", color="white"),
        on_click=montar,
        style=ft.ButtonStyle(
            bgcolor=globals().get("COR_PRIMARIA", "#2563EB"),
            color="white",
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )

    montar(atualizar_pagina=False)

    return ft.Column(
        spacing=18,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            _nutri_card(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text("Análise nutricional", size=28, weight=ft.FontWeight.BOLD, color="#111827"),
                                ft.Text(
                                    "Painel integrado com exames, antropometria, anamnese, recordatório, calorias e insights clínicos.",
                                    size=13,
                                    color="#64748B",
                                ),
                            ],
                        ),
                        ft.Row(
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                paciente_dropdown,
                                atualizar_btn,
                            ],
                        ),
                    ],
                )
            ),
            painel,
        ],
    )


# Aliases para garantir que qualquer rota antiga chame a tela final.
def nutricao_page(page):
    return nutricao_view(page)


def analise_nutricional_view(page):
    return nutricao_view(page)


def nutricao_clinica_view(page):
    return nutricao_view(page)




# ============================================================
# NUTRIÇÃO - VISÃO COMPLETA COM GRÁFICOS DO RELATÓRIO PDF
# ============================================================

def _ng_ler_csv(nome):
    caminho = Path(__file__).resolve().parent / "data_flet" / nome

    if not caminho.exists():
        return []

    try:
        with caminho.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    except UnicodeDecodeError:
        with caminho.open("r", encoding="latin-1", newline="") as f:
            return list(csv.DictReader(f))
    except Exception as exc:
        print(f"[NUTRIÇÃO] Erro ao ler {nome}: {exc}")
        return []


def _ng_float(valor):
    valor = str(valor or "").strip()
    valor = re.sub(r"[^0-9,.\-]", "", valor)

    if not valor:
        return None

    if "," in valor:
        valor = valor.replace(".", "").replace(",", ".")

    try:
        return float(valor)
    except Exception:
        return None


def _ng_data_br(valor):
    valor = str(valor or "").strip()

    if not valor:
        return "-"

    if re.match(r"^\d{2}/\d{2}/\d{4}$", valor):
        return valor

    try:
        return datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return valor


def _ng_card(content, padding=20):
    if "app_card" in globals():
        try:
            return app_card(content, padding=padding)
        except Exception:
            pass

    return ft.Container(
        bgcolor="#FFFFFF",
        border_radius=18,
        padding=padding,
        content=content,
    )


def _ng_status(status):
    st = str(status or "").strip().lower()

    if st in ["normal", "ok", "dentro", "dentro da referência", "dentro da referencia"]:
        return "Normal"

    if st in ["alto", "acima", "acima da referência", "acima da referencia"]:
        return "Alto"

    if st in ["baixo", "abaixo", "abaixo da referência", "abaixo da referencia"]:
        return "Baixo"

    if st in ["crítico", "critico"]:
        return "Crítico"

    if st:
        return str(status).strip()

    return "Sem análise"


def _ng_alterado(status):
    return _ng_status(status) not in ["Normal", "Sem análise"]


def _ng_nome_exame(row):
    for campo in ["nome_exame", "nome_padronizado", "nome", "exame", "exame_nome", "analito"]:
        valor = str(row.get(campo) or "").strip()
        if valor and valor.lower() != "none":
            return valor

    return "-"


def _ng_pacientes():
    pacientes = []

    for r in _ng_ler_csv("pacientes.csv"):
        pid = str(r.get("paciente_id") or r.get("id") or "").strip()

        if pid:
            r["id"] = pid
            r["paciente_id"] = pid
            pacientes.append(r)

    return pacientes


def _ng_paciente(pid):
    pid = str(pid or "").strip()

    for p in _ng_pacientes():
        if str(p.get("paciente_id") or p.get("id") or "").strip() == pid:
            return p

    return {"id": pid, "paciente_id": pid, "nome": "Paciente", "idade": ""}


def _ng_exames(pid):
    pid = str(pid or "").strip()
    exames = []

    for r in _ng_ler_csv("analise_exames.csv"):
        if str(r.get("paciente_id") or "").strip() != pid:
            continue

        nome = _ng_nome_exame(r)

        exames.append({
            **r,
            "nome_exame": nome,
            "nome_padronizado": r.get("nome_padronizado") or nome,
            "nome": nome,
            "exame": nome,
            "exame_nome": nome,
            "data": _ng_data_br(r.get("data_exame") or r.get("data")),
            "status": _ng_status(r.get("status")),
        })

    return exames


def _ng_registros(nome_csv, pid):
    pid = str(pid or "").strip()
    rows = []

    for r in _ng_ler_csv(nome_csv):
        rid = str(r.get("paciente_id") or r.get("id_paciente") or r.get("id") or "").strip()
        if rid == pid:
            rows.append(r)

    def chave(row):
        return str(
            row.get("data")
            or row.get("data_registro")
            or row.get("data_avaliacao")
            or row.get("data_anamnese")
            or ""
        )

    rows.sort(key=chave, reverse=True)
    return rows


def _ng_ultimo(nome_csv, pid):
    rows = _ng_registros(nome_csv, pid)
    return rows[0] if rows else {}


def _ng_resumo_exames(exames):
    total = len(exames)
    normais = len([e for e in exames if _ng_status(e.get("status")) == "Normal"])
    alterados = len([e for e in exames if _ng_alterado(e.get("status"))])

    return {
        "total": total,
        "normais": normais,
        "alterados": alterados,
    }


def _ng_analise_antropometrica(paciente, antropometria):
    peso = _ng_float(antropometria.get("peso") or paciente.get("peso"))
    altura = _ng_float(antropometria.get("altura") or paciente.get("altura"))
    cintura = _ng_float(
        antropometria.get("circunferencia_cintura")
        or antropometria.get("cintura")
        or antropometria.get("cc")
    )

    sexo = str(paciente.get("sexo") or "").upper()

    if altura and altura > 3:
        altura_cm = altura
        altura_m = altura / 100
    elif altura:
        altura_m = altura
        altura_cm = altura * 100
    else:
        altura_m = None
        altura_cm = None

    imc = None
    classificacao = "Dados insuficientes"

    if peso and altura_m:
        imc = peso / (altura_m ** 2)

        if imc < 18.5:
            classificacao = "Baixo peso"
        elif imc < 25:
            classificacao = "Eutrofia"
        elif imc < 30:
            classificacao = "Sobrepeso"
        elif imc < 35:
            classificacao = "Obesidade grau I"
        elif imc < 40:
            classificacao = "Obesidade grau II"
        else:
            classificacao = "Obesidade grau III"

    risco = "Não avaliado"

    if cintura:
        if sexo.startswith("F"):
            risco = "Sem aumento relevante"
            if cintura >= 80:
                risco = "Aumentado"
            if cintura >= 88:
                risco = "Muito aumentado"
        else:
            risco = "Sem aumento relevante"
            if cintura >= 94:
                risco = "Aumentado"
            if cintura >= 102:
                risco = "Muito aumentado"

    insights = []

    if peso:
        insights.append(f"Peso atual registrado: {peso:.1f} kg.")

    if altura_cm:
        insights.append(f"Altura utilizada no cálculo: {altura_cm:.0f} cm.")

    if imc:
        insights.append(f"IMC atual: {imc:.1f} kg/m² — {classificacao}.")
    else:
        insights.append("IMC não calculado por ausência de peso e/ou altura.")

    if cintura:
        insights.append(f"Circunferência de cintura: {cintura:.1f} cm — risco {risco.lower()}.")
    else:
        insights.append("Circunferência de cintura não cadastrada.")

    return {
        "peso": peso,
        "altura_cm": altura_cm,
        "imc": imc,
        "classificacao": classificacao,
        "cintura": cintura,
        "risco": risco,
        "insights": insights,
    }


def _ng_texto(row):
    return " ".join([str(v or "") for v in row.values()]).lower()


def _ng_fator_atividade(anamnese):
    texto = _ng_texto(anamnese)

    if any(t in texto for t in ["muito ativo", "intenso", "alta intensidade", "atleta", "diário", "diario"]):
        return 1.725, "Intensa"

    if any(t in texto for t in ["moderado", "moderada", "musculação", "musculacao", "3 vezes", "4 vezes", "5 vezes"]):
        return 1.55, "Moderada"

    if any(t in texto for t in ["luta", "artes marciais", "caminhada", "leve", "1x", "1 vez", "2 vezes"]):
        return 1.375, "Leve"

    if any(t in texto for t in ["sedent", "não pratica", "nao pratica"]):
        return 1.2, "Sedentária"

    return 1.375, "Leve/estimada"


def _ng_objetivo(anamnese):
    texto = _ng_texto(anamnese)

    if any(t in texto for t in ["ganho de massa", "hipertrofia", "massa muscular", "performance"]):
        return "Ganho de massa"

    if any(t in texto for t in ["emagrecer", "perda de peso", "redução de peso", "reducao de peso", "definição", "definicao"]):
        return "Redução de peso"

    if any(t in texto for t in ["manutenção", "manutencao", "preventivo", "qualidade de vida"]):
        return "Manutenção"

    return "Não informado"


def _ng_estimar_ingestao(recordatorio):
    if not recordatorio:
        return None, "Recordatório não cadastrado."

    for campo in ["kcal", "calorias", "total_kcal", "energia"]:
        v = _ng_float(recordatorio.get(campo))
        if v:
            return v, f"Valor informado no campo {campo}."

    refeicoes = {
        "desjejum": 350,
        "lanche_manha": 180,
        "almoco": 700,
        "lanche_tarde": 250,
        "jantar": 650,
        "ceia": 150,
    }

    total = 0
    encontrou = False

    for campo, base in refeicoes.items():
        texto = str(recordatorio.get(campo) or "").lower().strip()

        if not texto or texto in ["não informado", "nao informado"]:
            continue

        encontrou = True
        kcal = base

        if any(t in texto for t in ["biscoito", "bolo", "pizza", "hamb", "salgado", "doce", "manteiga", "queijo"]):
            kcal += 180

        if any(t in texto for t in ["arroz", "feijão", "feijao", "pão", "pao", "tapioca", "massa"]):
            kcal += 120

        if any(t in texto for t in ["carne", "frango", "ovo", "peixe"]):
            kcal += 140

        if any(t in texto for t in ["salada", "legume", "fruta", "verdura"]):
            kcal -= 70

        total += max(80, kcal)

    if encontrou:
        return total, "Estimativa heurística baseada nos alimentos descritos no recordatório."

    return None, "Recordatório sem refeições interpretáveis."


def _ng_analise_calorica(paciente, anamnese, recordatorio, antro):
    peso = antro.get("peso")
    altura_cm = antro.get("altura_cm")
    idade = _ng_float(paciente.get("idade"))
    sexo = str(paciente.get("sexo") or "").upper()

    fator, atividade = _ng_fator_atividade(anamnese)
    objetivo = _ng_objetivo(anamnese)

    if not peso or not altura_cm or not idade:
        return {
            "calculado": False,
            "basal": 0,
            "manutencao": 0,
            "ingestao": 0,
            "meta": 0,
            "diferenca": None,
            "atividade": atividade,
            "objetivo": objetivo,
            "fonte": "Dados insuficientes.",
            "insights": ["Não foi possível calcular gasto calórico por falta de peso, altura ou idade."],
        }

    if sexo.startswith("F"):
        basal = (10 * peso) + (6.25 * altura_cm) - (5 * idade) - 161
    else:
        basal = (10 * peso) + (6.25 * altura_cm) - (5 * idade) + 5

    manutencao = basal * fator
    ingestao, fonte = _ng_estimar_ingestao(recordatorio)

    if objetivo == "Redução de peso":
        meta = manutencao - 500
    elif objetivo == "Ganho de massa":
        meta = manutencao + 300
    else:
        meta = manutencao

    diferenca = ingestao - meta if ingestao else None

    insights = [
        f"Gasto basal estimado: {basal:.0f} kcal/dia.",
        f"Gasto total de manutenção: {manutencao:.0f} kcal/dia.",
        f"Nível de atividade considerado: {atividade}.",
        f"Objetivo do tratamento: {objetivo}.",
        f"Meta calórica sugerida: {meta:.0f} kcal/dia.",
    ]

    if ingestao:
        insights.append(f"Ingestão estimada pelo recordatório: {ingestao:.0f} kcal/dia.")

        if diferenca is not None:
            insights.append(f"Diferença ingestão x meta: {diferenca:.0f} kcal/dia.")

    else:
        insights.append("Ingestão estimada indisponível; detalhar porções no recordatório.")

    return {
        "calculado": True,
        "basal": basal,
        "manutencao": manutencao,
        "ingestao": ingestao or 0,
        "meta": meta,
        "diferenca": diferenca,
        "atividade": atividade,
        "objetivo": objetivo,
        "fonte": fonte,
        "insights": insights,
    }


def _ng_insights_exames(exames):
    return _diagnostico_nutricional_inteligente_para_insights(exames)


def _ng_insights_habitos(anamnese, recordatorio):
    insights = []

    agua = str(anamnese.get("ingestao_agua_dia") or "").strip()
    sono = str(anamnese.get("qualidade_sono") or "").strip()
    objetivo = str(anamnese.get("objetivo_nutricional") or anamnese.get("queixa_principal") or "").strip()
    intolerancia = str(anamnese.get("intolerancia_alergia_alimentar") or "").strip()

    if objetivo:
        insights.append(f"Objetivo/queixa principal: {objetivo}.")

    if sono:
        insights.append(f"Qualidade do sono: {sono}.")

    if agua:
        insights.append(f"Ingestão hídrica registrada: {agua}.")

    if intolerancia:
        insights.append(f"Intolerância/alergia alimentar registrada: {intolerancia}.")

    texto_recordatorio = _ng_texto(recordatorio)

    if any(t in texto_recordatorio for t in ["biscoito", "bolo", "salgado"]):
        insights.append("Recordatório mostra beliscos com biscoitos/bolo/salgados; avaliar troca planejada para lanches com melhor densidade nutricional.")

    if any(t in texto_recordatorio for t in ["arroz", "feijão", "frango", "carne"]):
        insights.append("Refeições principais têm base estruturada com carboidrato e proteína; ajustar porções conforme meta calórica.")

    return insights or ["Anamnese e recordatório ainda precisam de mais detalhes."]


def _ng_prioridades(exames, antro, calorias, anamnese):
    prioridades = []

    if any("densidade" in _ng_nome_exame(e).lower() and _ng_alterado(e.get("status")) for e in exames):
        prioridades.append("Hidratação: definir meta diária progressiva e monitorar urina/densidade urinária.")

    if any("colesterol total" in _ng_nome_exame(e).lower() and _ng_alterado(e.get("status")) for e in exames):
        prioridades.append("Perfil lipídico: aumentar fibras, ajustar gorduras e reduzir ultraprocessados.")

    if any("plaqueta" in _ng_nome_exame(e).lower() and _ng_alterado(e.get("status")) for e in exames):
        prioridades.append("Plaquetas baixas: registrar como alerta clínico e orientar acompanhamento médico se persistente.")

    if antro.get("imc") and antro["imc"] >= 25:
        prioridades.append("Composição corporal: acompanhar peso, cintura e adesão ao plano.")

    if calorias.get("objetivo") == "Ganho de massa":
        prioridades.append("Ganho de massa: manter superávit leve, proteína adequada e progressão do treino.")

    agua = str(anamnese.get("ingestao_agua_dia") or "").lower()

    if "menos" in agua or "500" in agua:
        prioridades.append("Baixa ingestão hídrica: iniciar meta simples e fracionada ao longo do dia.")

    return prioridades or ["Manter acompanhamento preventivo e revisar metas na próxima consulta."]


def _ng_metric(titulo, valor, subtitulo="", cor="#111827"):
    return _ng_card(
        ft.Column(
            spacing=6,
            controls=[
                ft.Text(titulo, size=13, color="#64748B"),
                ft.Text(str(valor), size=30, weight=ft.FontWeight.BOLD, color=cor),
                ft.Text(subtitulo, size=11, color="#64748B") if subtitulo else ft.Container(height=1),
            ],
        ),
        padding=18,
    )


def _ng_bar_chart(titulo, dados, descricao=""):
    max_val = max([v for _, v, _ in dados if v is not None] + [1])

    barras = []

    for label, valor, cor in dados:
        valor = valor or 0
        altura = 36 + int((valor / max_val) * 135)

        barras.append(
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.END,
                spacing=8,
                controls=[
                    ft.Text(f"{valor:.0f}", size=14, weight=ft.FontWeight.BOLD, color="#111827"),
                    ft.Container(width=76, height=altura, bgcolor=cor, border_radius=12),
                    ft.Text(label, size=12, color="#64748B", text_align=ft.TextAlign.CENTER),
                ],
            )
        )

    controls = [
        ft.Text(titulo, size=18, weight=ft.FontWeight.BOLD, color="#111827"),
    ]

    if descricao:
        controls.append(ft.Text(descricao, size=13, color="#64748B"))

    controls.append(
        ft.Container(
            height=275,
            bgcolor="#F8FAFC",
            border_radius=16,
            padding=20,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                vertical_alignment=ft.CrossAxisAlignment.END,
                controls=barras,
            ),
        )
    )

    return _ng_card(ft.Column(spacing=14, controls=controls))


def _ng_lista(titulo, itens, subtitulo=""):
    if str(titulo or "").strip() == "Insights de apoio nutricional":
        return _nutri_tabela_analise_a_partir_de_insights(itens)

    controls = [ft.Text(titulo, size=18, weight=ft.FontWeight.BOLD, color="#111827")]

    if subtitulo:
        controls.append(ft.Text(subtitulo, size=13, color="#64748B"))

    for item in itens:
        controls.append(
            ft.Container(
                bgcolor="#F8FAFC",
                border_radius=12,
                padding=12,
                content=ft.Text(f"• {item}", size=13, color="#374151"),
            )
        )

    return _ng_card(ft.Column(spacing=10, controls=controls))


def _ng_tabela_alterados(alterados):
    if not alterados:
        return _ng_lista("Exames alterados", ["Nenhum exame fora da referência automática."])

    rows = []

    for e in alterados:
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(_ng_data_br(e.get("data_exame") or e.get("data")), size=12)),
                    ft.DataCell(ft.Text(_ng_nome_exame(e), size=12)),
                    ft.DataCell(ft.Text(f'{e.get("resultado", "")} {e.get("unidade", "")}'.strip(), size=12)),
                    ft.DataCell(ft.Text(_ng_status(e.get("status")), size=12)),
                ]
            )
        )

    return _ng_card(
        ft.Column(
            spacing=14,
            controls=[
                ft.Text("Exames alterados", size=18, weight=ft.FontWeight.BOLD, color="#111827"),
                ft.Text("Lista focada apenas nos exames fora da referência.", size=13, color="#64748B"),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Data")),
                        ft.DataColumn(ft.Text("Exame")),
                        ft.DataColumn(ft.Text("Resultado")),
                        ft.DataColumn(ft.Text("Status")),
                    ],
                    rows=rows,
                    heading_row_color="#F8FAFC",
                    border_radius=12,
                ),
            ],
        )
    )


def _ng_gerar_pdf(page, paciente):
    try:
        caminho = gerar_pdf_analise_paciente(paciente)
        if "mostrar_snackbar" in globals():
            mostrar_snackbar(page, f"PDF gerado: {caminho}", globals().get("COR_NORMAL", "#16A34A"))
        else:
            print("PDF gerado:", caminho)
    except Exception as exc:
        if "mostrar_snackbar" in globals():
            mostrar_snackbar(page, f"Erro ao gerar PDF: {exc}", globals().get("COR_CRITICO", "#DC2626"))
        else:
            print("Erro ao gerar PDF:", exc)


def nutricao_view(page):
    pacientes = _ng_pacientes()

    opcoes = []

    for p in pacientes:
        pid = str(p.get("paciente_id") or p.get("id") or "").strip()
        nome = str(p.get("nome") or "").strip()
        idade = str(p.get("idade") or "").strip()

        if pid:
            opcoes.append(ft.dropdown.Option(key=pid, text=f"{nome} - {idade} anos" if idade else nome))

    paciente_dropdown = ft.Dropdown(
        label="Paciente",
        width=420,
        options=opcoes,
        value=opcoes[0].key if opcoes else None,
        border_radius=12,
    )

    painel = ft.Column(spacing=16)

    def montar(e=None):
        pid = paciente_dropdown.value

        if not pid:
            painel.controls = [_ng_lista("Análise nutricional", ["Nenhum paciente selecionado."])]
            page.update()
            return

        paciente = _ng_paciente(pid)
        exames = _ng_exames(pid)
        resumo = _ng_resumo_exames(exames)
        alterados = [e for e in exames if _ng_alterado(e.get("status"))]

        anamnese = _ng_ultimo("anamnese.csv", pid)
        recordatorio = _ng_ultimo("recordatorio_habitual.csv", pid)
        antropometria_reg = _ng_ultimo("antropometria.csv", pid)

        antro = _ng_analise_antropometrica(paciente, antropometria_reg)
        calorias = _ng_analise_calorica(paciente, anamnese, recordatorio, antro)

        qtd_anamnese = len(_ng_registros("anamnese.csv", pid))
        qtd_recordatorio = len(_ng_registros("recordatorio_habitual.csv", pid))
        qtd_antropometria = len(_ng_registros("antropometria.csv", pid))

        dados_caloricos = [
            ("Manutenção", calorias.get("manutencao") or 0, "#2563EB"),
            ("Meta", calorias.get("meta") or 0, "#16A34A"),
        ]

        if calorias.get("ingestao"):
            dados_caloricos.insert(1, ("Ingestão", calorias.get("ingestao") or 0, "#F59E0B"))

        painel.controls = [
            ft.Row(
                spacing=16,
                controls=[
                    _ng_metric("Resultados", resumo["total"], "Exames analisados", "#2563EB"),
                    _ng_metric("Normais", resumo["normais"], "Dentro da referência", "#16A34A"),
                    _ng_metric("Alterados", resumo["alterados"], "Fora da referência", "#F59E0B"),
                ],
            ),
            _ng_card(
                ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text(str(paciente.get("nome") or "Paciente"), size=24, weight=ft.FontWeight.BOLD, color="#111827"),
                        ft.Text(
                            f"Anamneses: {qtd_anamnese} • Recordatórios: {qtd_recordatorio} • Antropometrias: {qtd_antropometria} • Exames: {resumo['total']}",
                            size=13,
                            color="#64748B",
                        ),
                    ],
                )
            ),
            _ng_bar_chart(
                "Resumo dos exames",
                [
                    ("Total", resumo["total"], "#2563EB"),
                    ("Normais", resumo["normais"], "#16A34A"),
                    ("Alterados", resumo["alterados"], "#F59E0B"),
                ],
                "Mesmo gráfico do relatório PDF: total de exames, normais e alterados.",
            ),
            _ng_tabela_alterados(alterados),
            _ng_lista(
                "Insights de apoio nutricional",
                _ng_insights_exames(exames) + _ng_insights_habitos(anamnese, recordatorio),
                "Leitura integrada de exames, anamnese e recordatório.",
            ),
            _ng_lista(
                "Prioridades sugeridas de conduta",
                _ng_prioridades(exames, antro, calorias, anamnese),
                "Sugestões para orientar plano alimentar e acompanhamento.",
            ),
            _ng_lista(
                "Análise antropométrica",
                antro["insights"],
                "Baseada no último registro antropométrico.",
            ),
            _ng_lista(
                "Análise do gasto calórico",
                calorias["insights"],
                "Estimativa baseada em peso, altura, idade, sexo, atividade, objetivo e recordatório.",
            ),
            _ng_bar_chart(
                "Comparativo calórico",
                dados_caloricos,
                "Mesmo gráfico do relatório PDF: manutenção, ingestão estimada e meta calórica.",
            ),
            _ng_card(
                ft.Column(
                    spacing=10,
                    controls=[
                        ft.Text("Ações recomendadas no sistema", size=18, weight=ft.FontWeight.BOLD, color="#111827"),
                        ft.Text("• Atualizar anamnese quando houver mudança de objetivo, sono, treino, sintomas ou medicações.", size=13, color="#374151"),
                        ft.Text("• Registrar porções no recordatório para melhorar a estimativa calórica.", size=13, color="#374151"),
                        ft.Text("• Repetir antropometria periodicamente para acompanhar peso, cintura e evolução.", size=13, color="#374151"),
                        ft.Text("• Reavaliar exames alterados em nova coleta e acompanhar tendência.", size=13, color="#374151"),
                        ft.Row(
                            controls=[
                                ft.OutlinedButton(
                                    content="Gerar PDF desta análise",
                                    icon=ft.Icons.PICTURE_AS_PDF,
                                    on_click=lambda ev: _ng_gerar_pdf(page, paciente),
                                    style=ft.ButtonStyle(
                                        color=globals().get("COR_PRIMARIA", "#2563EB"),
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                    ),
                                )
                            ]
                        ),
                    ],
                )
            ),
        ]

        page.update()

    atualizar_btn = ft.FilledButton(
        content=ft.Text("Atualizar", color="white"),
        on_click=montar,
        style=ft.ButtonStyle(
            bgcolor=globals().get("COR_PRIMARIA", "#2563EB"),
            color="white",
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )

    # Montagem inicial sem page.update para evitar update antes do controle entrar na página.
    pid = paciente_dropdown.value
    if pid:
        paciente = _ng_paciente(pid)
        exames = _ng_exames(pid)
        resumo = _ng_resumo_exames(exames)
        painel.controls = [
            _ng_metric("Carregando análise", "OK", f"{resumo['total']} exames disponíveis", "#2563EB"),
        ]

    return ft.Column(
        spacing=18,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            _ng_card(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text("Análise nutricional", size=28, weight=ft.FontWeight.BOLD, color="#111827"),
                                ft.Text(
                                    "Painel integrado com os mesmos gráficos do relatório PDF, exames alterados, antropometria, calorias e insights.",
                                    size=13,
                                    color="#64748B",
                                ),
                            ],
                        ),
                        ft.Row(
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                paciente_dropdown,
                                atualizar_btn,
                            ],
                        ),
                    ],
                )
            ),
            painel,
        ],
    )


def nutricao_page(page):
    return nutricao_view(page)


def analise_nutricional_view(page):
    return nutricao_view(page)


def nutricao_clinica_view(page):
    return nutricao_view(page)



# Aliases finais de Nutrição - garantem que rotas antigas apontem para a visão completa
def nutricao_page(page):
    return nutricao_view(page)

def analise_nutricional_view(page):
    return nutricao_view(page)

def nutricao_clinica_view(page):
    return nutricao_view(page)



# ============================================================
# NUTRIÇÃO RENDER FINAL - DASHBOARD COMPLETO E PRONTO NA ABERTURA
# ============================================================

def _nr_csv(nome):
    caminho = Path(__file__).resolve().parent / "data_flet" / nome
    if not caminho.exists():
        return []
    try:
        with caminho.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    except UnicodeDecodeError:
        with caminho.open("r", encoding="latin-1", newline="") as f:
            return list(csv.DictReader(f))


def _nr_float(valor):
    valor = str(valor or "").strip()
    valor = re.sub(r"[^0-9,.\-]", "", valor)
    if not valor:
        return None
    if "," in valor:
        valor = valor.replace(".", "").replace(",", ".")
    try:
        return float(valor)
    except Exception:
        return None


def _nr_data_br(valor):
    valor = str(valor or "").strip()
    if not valor:
        return "-"
    if re.match(r"^\d{2}/\d{2}/\d{4}$", valor):
        return valor
    try:
        return datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return valor


def _nr_card(content, padding=20):
    if "app_card" in globals():
        try:
            return app_card(content, padding=padding)
        except Exception:
            pass
    return ft.Container(bgcolor="#FFFFFF", border_radius=18, padding=padding, content=content)


def _nr_status(status):
    st = str(status or "").strip().lower()
    if st in ["normal", "ok", "dentro", "dentro da referência", "dentro da referencia"]:
        return "Normal"
    if st in ["alto", "acima", "acima da referência", "acima da referencia"]:
        return "Alto"
    if st in ["baixo", "abaixo", "abaixo da referência", "abaixo da referencia"]:
        return "Baixo"
    if st in ["crítico", "critico"]:
        return "Crítico"
    return str(status or "Sem análise").strip()


def _nr_alterado(status):
    return _nr_status(status) not in ["Normal", "Sem análise"]


def _nr_nome_exame(row):
    for campo in ["nome_exame", "nome_padronizado", "nome", "exame", "exame_nome", "analito"]:
        valor = str(row.get(campo) or "").strip()
        if valor and valor.lower() != "none":
            return valor
    return "-"


def _nr_pacientes():
    pacientes = []
    for r in _nr_csv("pacientes.csv"):
        pid = str(r.get("paciente_id") or r.get("id") or "").strip()
        if pid:
            r["id"] = pid
            r["paciente_id"] = pid
            pacientes.append(r)
    return pacientes


def _nr_exames(pid):
    exames = []
    pid = str(pid or "").strip()

    for r in _nr_csv("analise_exames.csv"):
        if str(r.get("paciente_id") or "").strip() != pid:
            continue

        nome = _nr_nome_exame(r)

        exames.append({
            **r,
            "nome_exame": nome,
            "nome_padronizado": r.get("nome_padronizado") or nome,
            "nome": nome,
            "exame": nome,
            "exame_nome": nome,
            "data": _nr_data_br(r.get("data_exame") or r.get("data")),
            "status": _nr_status(r.get("status")),
        })

    return exames


def _nr_paciente(pid):
    for p in _nr_pacientes():
        if str(p.get("paciente_id") or p.get("id")) == str(pid):
            return p
    return {"id": pid, "paciente_id": pid, "nome": "Paciente", "idade": ""}


def _nr_registros(nome_csv, pid):
    rows = []
    for r in _nr_csv(nome_csv):
        if str(r.get("paciente_id") or r.get("id_paciente") or r.get("id") or "").strip() == str(pid):
            rows.append(r)

    def chave(row):
        return str(
            row.get("data")
            or row.get("data_registro")
            or row.get("data_avaliacao")
            or row.get("data_anamnese")
            or ""
        )

    rows.sort(key=chave, reverse=True)
    return rows


def _nr_ultimo(nome_csv, pid):
    rows = _nr_registros(nome_csv, pid)
    return rows[0] if rows else {}


def _nr_resumo(exames):
    return {
        "total": len(exames),
        "normais": len([e for e in exames if _nr_status(e.get("status")) == "Normal"]),
        "alterados": len([e for e in exames if _nr_alterado(e.get("status"))]),
    }


def _nr_antropometria(paciente, registro):
    peso = _nr_float(registro.get("peso") or paciente.get("peso"))
    altura = _nr_float(registro.get("altura") or paciente.get("altura"))
    cintura = _nr_float(registro.get("circunferencia_cintura") or registro.get("cintura") or registro.get("cc"))
    sexo = str(paciente.get("sexo") or "").upper()

    if altura and altura > 3:
        altura_cm = altura
        altura_m = altura / 100
    elif altura:
        altura_m = altura
        altura_cm = altura * 100
    else:
        altura_m = None
        altura_cm = None

    imc = None
    classificacao = "Dados insuficientes"

    if peso and altura_m:
        imc = peso / (altura_m ** 2)
        if imc < 18.5:
            classificacao = "Baixo peso"
        elif imc < 25:
            classificacao = "Eutrofia"
        elif imc < 30:
            classificacao = "Sobrepeso"
        elif imc < 35:
            classificacao = "Obesidade grau I"
        elif imc < 40:
            classificacao = "Obesidade grau II"
        else:
            classificacao = "Obesidade grau III"

    risco = "Não avaliado"
    if cintura:
        if sexo.startswith("F"):
            risco = "Aumentado" if cintura >= 80 else "Sem aumento relevante"
            if cintura >= 88:
                risco = "Muito aumentado"
        else:
            risco = "Aumentado" if cintura >= 94 else "Sem aumento relevante"
            if cintura >= 102:
                risco = "Muito aumentado"

    insights = []
    if peso:
        insights.append(f"Peso atual registrado: {peso:.1f} kg.")
    if altura_cm:
        insights.append(f"Altura utilizada no cálculo: {altura_cm:.0f} cm.")
    if imc:
        insights.append(f"IMC atual: {imc:.1f} kg/m² — {classificacao}.")
    else:
        insights.append("IMC não calculado por ausência de peso e/ou altura.")
    if cintura:
        insights.append(f"Circunferência de cintura: {cintura:.1f} cm — risco {risco.lower()}.")
    else:
        insights.append("Circunferência de cintura não cadastrada.")

    return {
        "peso": peso,
        "altura_cm": altura_cm,
        "imc": imc,
        "classificacao": classificacao,
        "cintura": cintura,
        "risco": risco,
        "insights": insights,
    }


def _nr_texto(row):
    return " ".join([str(v or "") for v in row.values()]).lower()


def _nr_fator_atividade(anamnese):
    texto = _nr_texto(anamnese)
    if any(t in texto for t in ["muito ativo", "intenso", "alta intensidade", "atleta", "diário", "diario"]):
        return 1.725, "Intensa"
    if any(t in texto for t in ["moderado", "moderada", "musculação", "musculacao", "3 vezes", "4 vezes", "5 vezes"]):
        return 1.55, "Moderada"
    if any(t in texto for t in ["luta", "artes marciais", "caminhada", "leve", "1x", "1 vez", "2 vezes"]):
        return 1.375, "Leve"
    if any(t in texto for t in ["sedent", "não pratica", "nao pratica"]):
        return 1.2, "Sedentária"
    return 1.375, "Leve/estimada"


def _nr_objetivo(anamnese):
    texto = _nr_texto(anamnese)
    if any(t in texto for t in ["ganho de massa", "hipertrofia", "massa muscular", "performance"]):
        return "Ganho de massa"
    if any(t in texto for t in ["emagrecer", "perda de peso", "redução de peso", "reducao de peso", "definição", "definicao"]):
        return "Redução de peso"
    if any(t in texto for t in ["manutenção", "manutencao", "preventivo", "qualidade de vida"]):
        return "Manutenção"
    return "Não informado"


def _nr_estimar_ingestao(recordatorio):
    if not recordatorio:
        return None, "Recordatório não cadastrado."

    refeicoes = {
        "desjejum": 350,
        "lanche_manha": 180,
        "almoco": 700,
        "lanche_tarde": 250,
        "jantar": 650,
        "ceia": 150,
    }

    total = 0
    encontrou = False

    for campo, base in refeicoes.items():
        texto = str(recordatorio.get(campo) or "").lower().strip()
        if not texto or texto in ["não informado", "nao informado"]:
            continue

        encontrou = True
        kcal = base

        if any(t in texto for t in ["biscoito", "bolo", "pizza", "hamb", "salgado", "doce", "manteiga", "queijo"]):
            kcal += 180
        if any(t in texto for t in ["arroz", "feijão", "feijao", "pão", "pao", "tapioca", "massa"]):
            kcal += 120
        if any(t in texto for t in ["carne", "frango", "ovo", "peixe"]):
            kcal += 140
        if any(t in texto for t in ["salada", "legume", "fruta", "verdura"]):
            kcal -= 70

        total += max(80, kcal)

    if encontrou:
        return total, "Estimativa heurística baseada nos alimentos descritos no recordatório."

    return None, "Recordatório sem refeições interpretáveis."


def _nr_calorias(paciente, anamnese, recordatorio, antro):
    peso = antro.get("peso")
    altura_cm = antro.get("altura_cm")
    idade = _nr_float(paciente.get("idade"))
    sexo = str(paciente.get("sexo") or "").upper()
    fator, atividade = _nr_fator_atividade(anamnese)
    objetivo = _nr_objetivo(anamnese)

    if not peso or not altura_cm or not idade:
        return {
            "basal": 0,
            "manutencao": 0,
            "ingestao": 0,
            "meta": 0,
            "diferenca": None,
            "atividade": atividade,
            "objetivo": objetivo,
            "fonte": "Dados insuficientes.",
            "insights": ["Não foi possível calcular gasto calórico por falta de peso, altura ou idade."],
        }

    if sexo.startswith("F"):
        basal = (10 * peso) + (6.25 * altura_cm) - (5 * idade) - 161
    else:
        basal = (10 * peso) + (6.25 * altura_cm) - (5 * idade) + 5

    manutencao = basal * fator
    ingestao, fonte = _nr_estimar_ingestao(recordatorio)

    if objetivo == "Redução de peso":
        meta = manutencao - 500
    elif objetivo == "Ganho de massa":
        meta = manutencao + 300
    else:
        meta = manutencao

    diferenca = ingestao - meta if ingestao else None

    insights = [
        f"Gasto basal estimado: {basal:.0f} kcal/dia.",
        f"Gasto total de manutenção: {manutencao:.0f} kcal/dia.",
        f"Nível de atividade considerado: {atividade}.",
        f"Objetivo do tratamento: {objetivo}.",
        f"Meta calórica sugerida: {meta:.0f} kcal/dia.",
    ]

    if ingestao:
        insights.append(f"Ingestão estimada pelo recordatório: {ingestao:.0f} kcal/dia.")
        insights.append(f"Diferença ingestão x meta: {diferenca:.0f} kcal/dia.")
    else:
        insights.append("Ingestão estimada indisponível; detalhar porções no recordatório.")

    return {
        "basal": basal,
        "manutencao": manutencao,
        "ingestao": ingestao or 0,
        "meta": meta,
        "diferenca": diferenca,
        "atividade": atividade,
        "objetivo": objetivo,
        "fonte": fonte,
        "insights": insights,
    }


def _nr_insights_exames(exames):
    return _diagnostico_nutricional_inteligente_para_insights(exames)


def _nr_insights_habitos(anamnese, recordatorio):
    insights = []
    agua = str(anamnese.get("ingestao_agua_dia") or "").strip()
    sono = str(anamnese.get("qualidade_sono") or "").strip()
    objetivo = str(anamnese.get("objetivo_nutricional") or anamnese.get("queixa_principal") or "").strip()
    intolerancia = str(anamnese.get("intolerancia_alergia_alimentar") or "").strip()

    if objetivo:
        insights.append(f"Objetivo/queixa principal: {objetivo}.")
    if sono:
        insights.append(f"Qualidade do sono: {sono}.")
    if agua:
        insights.append(f"Ingestão hídrica registrada: {agua}.")
    if intolerancia:
        insights.append(f"Intolerância/alergia alimentar registrada: {intolerancia}.")

    texto_recordatorio = _nr_texto(recordatorio)
    if any(t in texto_recordatorio for t in ["biscoito", "bolo", "salgado"]):
        insights.append("Recordatório mostra beliscos com biscoitos/bolo/salgados; avaliar troca planejada para lanches com melhor densidade nutricional.")
    if any(t in texto_recordatorio for t in ["arroz", "feijão", "frango", "carne"]):
        insights.append("Refeições principais têm base estruturada com carboidrato e proteína; ajustar porções conforme meta calórica.")

    return insights or ["Anamnese e recordatório ainda precisam de mais detalhes."]


def _nr_prioridades(exames, antro, calorias, anamnese):
    prioridades = []

    if any("densidade" in _nr_nome_exame(e).lower() and _nr_alterado(e.get("status")) for e in exames):
        prioridades.append("Hidratação: definir meta diária progressiva e monitorar urina/densidade urinária.")
    if any("colesterol total" in _nr_nome_exame(e).lower() and _nr_alterado(e.get("status")) for e in exames):
        prioridades.append("Perfil lipídico: aumentar fibras, ajustar gorduras e reduzir ultraprocessados.")
    if any("plaqueta" in _nr_nome_exame(e).lower() and _nr_alterado(e.get("status")) for e in exames):
        prioridades.append("Plaquetas baixas: registrar como alerta clínico e orientar acompanhamento médico se persistente.")
    if antro.get("imc") and antro["imc"] >= 25:
        prioridades.append("Composição corporal: acompanhar peso, cintura e adesão ao plano.")
    if calorias.get("objetivo") == "Ganho de massa":
        prioridades.append("Ganho de massa: manter superávit leve, proteína adequada e progressão do treino.")

    agua = str(anamnese.get("ingestao_agua_dia") or "").lower()
    if "menos" in agua or "500" in agua:
        prioridades.append("Baixa ingestão hídrica: iniciar meta simples e fracionada ao longo do dia.")

    return prioridades or ["Manter acompanhamento preventivo e revisar metas na próxima consulta."]


def _nr_metric(titulo, valor, subtitulo="", cor="#111827"):
    return _nr_card(
        ft.Column(
            spacing=6,
            controls=[
                ft.Text(titulo, size=13, color="#64748B"),
                ft.Text(str(valor), size=30, weight=ft.FontWeight.BOLD, color=cor),
                ft.Text(subtitulo, size=11, color="#64748B") if subtitulo else ft.Container(height=1),
            ],
        ),
        padding=18,
    )


def _nr_bar_chart(titulo, dados, descricao=""):
    max_val = max([v for _, v, _ in dados if v is not None] + [1])
    barras = []

    for label, valor, cor in dados:
        valor = valor or 0
        altura = 36 + int((valor / max_val) * 135)

        barras.append(
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.END,
                spacing=8,
                controls=[
                    ft.Text(f"{valor:.0f}", size=14, weight=ft.FontWeight.BOLD, color="#111827"),
                    ft.Container(width=76, height=altura, bgcolor=cor, border_radius=12),
                    ft.Text(label, size=12, color="#64748B", text_align=ft.TextAlign.CENTER),
                ],
            )
        )

    return _nr_card(
        ft.Column(
            spacing=14,
            controls=[
                ft.Text(titulo, size=18, weight=ft.FontWeight.BOLD, color="#111827"),
                ft.Text(descricao, size=13, color="#64748B") if descricao else ft.Container(height=1),
                ft.Container(
                    height=275,
                    bgcolor="#F8FAFC",
                    border_radius=16,
                    padding=20,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        controls=barras,
                    ),
                ),
            ],
        )
    )


def _nr_lista(titulo, itens, subtitulo=""):
    if str(titulo or "").strip() == "Insights de apoio nutricional":
        return _nutri_tabela_analise_a_partir_de_insights(itens)

    controls = [ft.Text(titulo, size=18, weight=ft.FontWeight.BOLD, color="#111827")]
    if subtitulo:
        controls.append(ft.Text(subtitulo, size=13, color="#64748B"))

    for item in itens:
        controls.append(
            ft.Container(
                bgcolor="#F8FAFC",
                border_radius=12,
                padding=12,
                content=ft.Text(f"• {item}", size=13, color="#374151"),
            )
        )

    return _nr_card(ft.Column(spacing=10, controls=controls))


def _nr_tabela_alterados(alterados):
    if not alterados:
        return _nr_lista("Exames alterados", ["Nenhum exame fora da referência automática."])

    rows = []
    for e in alterados:
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(_nr_data_br(e.get("data_exame") or e.get("data")), size=12)),
                    ft.DataCell(ft.Text(_nr_nome_exame(e), size=12)),
                    ft.DataCell(ft.Text(f'{e.get("resultado", "")} {e.get("unidade", "")}'.strip(), size=12)),
                    ft.DataCell(ft.Text(_nr_status(e.get("status")), size=12)),
                ]
            )
        )

    return _nr_card(
        ft.Column(
            spacing=14,
            controls=[
                ft.Text("Exames alterados", size=18, weight=ft.FontWeight.BOLD, color="#111827"),
                ft.Text("Lista focada apenas nos exames fora da referência.", size=13, color="#64748B"),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Data")),
                        ft.DataColumn(ft.Text("Exame")),
                        ft.DataColumn(ft.Text("Resultado")),
                        ft.DataColumn(ft.Text("Status")),
                    ],
                    rows=rows,
                    heading_row_color="#F8FAFC",
                    border_radius=12,
                ),
            ],
        )
    )


def _nr_montar_painel(pid, page=None):
    paciente = _nr_paciente(pid)
    exames = _nr_exames(pid)
    resumo = _nr_resumo(exames)
    alterados = [e for e in exames if _nr_alterado(e.get("status"))]

    anamnese = _nr_ultimo("anamnese.csv", pid)
    recordatorio = _nr_ultimo("recordatorio_habitual.csv", pid)
    antropometria_reg = _nr_ultimo("antropometria.csv", pid)

    antro = _nr_antropometria(paciente, antropometria_reg)
    calorias = _nr_calorias(paciente, anamnese, recordatorio, antro)

    qtd_anamnese = len(_nr_registros("anamnese.csv", pid))
    qtd_recordatorio = len(_nr_registros("recordatorio_habitual.csv", pid))
    qtd_antropometria = len(_nr_registros("antropometria.csv", pid))

    dados_caloricos = [
        ("Manutenção", calorias.get("manutencao") or 0, "#2563EB"),
        ("Meta", calorias.get("meta") or 0, "#16A34A"),
    ]

    if calorias.get("ingestao"):
        dados_caloricos.insert(1, ("Ingestão", calorias.get("ingestao") or 0, "#F59E0B"))

    def gerar_pdf(ev):
        try:
            caminho = gerar_pdf_analise_paciente(paciente)
            if page and "mostrar_snackbar" in globals():
                mostrar_snackbar(page, f"PDF gerado: {caminho}", globals().get("COR_NORMAL", "#16A34A"))
            else:
                print("PDF gerado:", caminho)
        except Exception as exc:
            if page and "mostrar_snackbar" in globals():
                mostrar_snackbar(page, f"Erro ao gerar PDF: {exc}", globals().get("COR_CRITICO", "#DC2626"))
            else:
                print("Erro ao gerar PDF:", exc)

    return [
        ft.Row(
            spacing=16,
            controls=[
                _nr_metric("Resultados", resumo["total"], "Exames analisados", "#2563EB"),
                _nr_metric("Normais", resumo["normais"], "Dentro da referência", "#16A34A"),
                _nr_metric("Alterados", resumo["alterados"], "Fora da referência", "#F59E0B"),
            ],
        ),
        _nr_card(
            ft.Column(
                spacing=8,
                controls=[
                    ft.Text(str(paciente.get("nome") or "Paciente"), size=24, weight=ft.FontWeight.BOLD, color="#111827"),
                    ft.Text(
                        f"Anamneses: {qtd_anamnese} • Recordatórios: {qtd_recordatorio} • Antropometrias: {qtd_antropometria} • Exames: {resumo['total']}",
                        size=13,
                        color="#64748B",
                    ),
                ],
            )
        ),
        _nr_bar_chart(
            "Resumo dos exames",
            [
                ("Total", resumo["total"], "#2563EB"),
                ("Normais", resumo["normais"], "#16A34A"),
                ("Alterados", resumo["alterados"], "#F59E0B"),
            ],
            "Mesmo gráfico do relatório PDF: total de exames, normais e alterados.",
        ),
        _nr_tabela_alterados(alterados),
        _nr_lista(
            "Insights de apoio nutricional",
            _nr_insights_exames(exames) + _nr_insights_habitos(anamnese, recordatorio),
            "Leitura integrada de exames, anamnese e recordatório.",
        ),
        _nr_lista(
            "Prioridades sugeridas de conduta",
            _nr_prioridades(exames, antro, calorias, anamnese),
            "Sugestões para orientar plano alimentar e acompanhamento.",
        ),
        _nr_lista(
            "Análise antropométrica",
            antro["insights"],
            "Baseada no último registro antropométrico.",
        ),
        _nr_lista(
            "Análise do gasto calórico",
            calorias["insights"],
            "Estimativa baseada em peso, altura, idade, sexo, atividade, objetivo e recordatório.",
        ),
        _nr_bar_chart(
            "Comparativo calórico",
            dados_caloricos,
            "Mesmo gráfico do relatório PDF: manutenção, ingestão estimada e meta calórica.",
        ),
        _nr_card(
            ft.Column(
                spacing=10,
                controls=[
                    ft.Text("Ações recomendadas no sistema", size=18, weight=ft.FontWeight.BOLD, color="#111827"),
                    ft.Text("• Atualizar anamnese quando houver mudança de objetivo, sono, treino, sintomas ou medicações.", size=13, color="#374151"),
                    ft.Text("• Registrar porções no recordatório para melhorar a estimativa calórica.", size=13, color="#374151"),
                    ft.Text("• Repetir antropometria periodicamente para acompanhar peso, cintura e evolução.", size=13, color="#374151"),
                    ft.Text("• Reavaliar exames alterados em nova coleta e acompanhar tendência.", size=13, color="#374151"),
                    ft.Row(
                        controls=[
                            ft.FilledButton(
                                content=ft.Text("Gerar Cardápio", color="white"),
                                icon=ft.Icons.RESTAURANT_MENU,
                                on_click=lambda ev: abrir_popup_cardapio(page, paciente),
                                style=ft.ButtonStyle(
                                    bgcolor=globals().get("COR_PRIMARIA", "#2563EB"),
                                    color="white",
                                    shape=ft.RoundedRectangleBorder(radius=12),
                                ),
                            ),
                            ft.OutlinedButton(
                                content="Gerar PDF desta análise",
                                icon=ft.Icons.PICTURE_AS_PDF,
                                on_click=gerar_pdf,
                                style=ft.ButtonStyle(
                                    color=globals().get("COR_PRIMARIA", "#2563EB"),
                                    shape=ft.RoundedRectangleBorder(radius=12),
                                ),
                            )
                        ]
                    ),
                ],
            )
        ),
    ]


def nutricao_view(page):
    pacientes = _nr_pacientes()

    # Seleciona por padrão o paciente com mais exames.
    melhor_pid = None
    melhor_qtd = -1

    for p in pacientes:
        pid = str(p.get("paciente_id") or p.get("id") or "").strip()
        qtd = len(_nr_exames(pid))
        if qtd > melhor_qtd:
            melhor_qtd = qtd
            melhor_pid = pid

    opcoes = []
    for p in pacientes:
        pid = str(p.get("paciente_id") or p.get("id") or "").strip()
        nome = str(p.get("nome") or "").strip()
        idade = str(p.get("idade") or "").strip()
        if pid:
            opcoes.append(ft.dropdown.Option(key=pid, text=f"{nome} - {idade} anos" if idade else nome))

    paciente_dropdown = ft.Dropdown(
        label="Paciente",
        width=420,
        options=opcoes,
        value=melhor_pid or (opcoes[0].key if opcoes else None),
        border_radius=12,
    )

    painel = ft.Column(spacing=16)

    if paciente_dropdown.value:
        painel.controls = _nr_montar_painel(paciente_dropdown.value, page)

    def atualizar(ev=None):
        painel.controls = _nr_montar_painel(paciente_dropdown.value, page)
        page.update()

    atualizar_btn = ft.FilledButton(
        content=ft.Text("Atualizar", color="white"),
        on_click=atualizar,
        style=ft.ButtonStyle(
            bgcolor=globals().get("COR_PRIMARIA", "#2563EB"),
            color="white",
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )

    return ft.Column(
        spacing=18,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            _nr_card(
                ft.Column(
                    spacing=16,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text("Análise nutricional", size=28, weight=ft.FontWeight.BOLD, color="#111827"),
                                ft.Text(
                                    "Painel integrado com os mesmos gráficos do relatório PDF, exames alterados, antropometria, calorias e insights.",
                                    size=13,
                                    color="#64748B",
                                ),
                            ],
                        ),
                        ft.Container(
                            bgcolor="#F8FAFC",
                            border_radius=14,
                            padding=12,
                            content=ft.Row(
                                spacing=10,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    paciente_dropdown,
                                    atualizar_btn,
                                ],
                            ),
                        ),
                    ],
                )
            ),
            painel,
        ],
    )


def nutricao_page(page):
    return nutricao_view(page)


def analise_nutricional_view(page):
    return nutricao_view(page)


def nutricao_clinica_view(page):
    return nutricao_view(page)




# ============================================================
# POPUP INICIAL - INSTRUÇÕES DE USO
# ============================================================

def _popup_inicio_preferencias_path():
    pasta = Path(__file__).resolve().parent / "data_flet"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta / "preferencias_inicio.csv"


def _popup_inicio_desativado():
    caminho = _popup_inicio_preferencias_path()

    if not caminho.exists():
        return False

    try:
        with caminho.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if str(row.get("chave", "")).strip() == "mostrar_popup_inicio":
                    return str(row.get("valor", "")).strip().lower() in ["false", "0", "nao", "não"]
    except Exception:
        return False

    return False


def _salvar_popup_inicio_desativado():
    caminho = _popup_inicio_preferencias_path()

    with caminho.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["chave", "valor"])
        writer.writeheader()
        writer.writerow({"chave": "mostrar_popup_inicio", "valor": "false"})


def abrir_popup_instrucoes_nutrisoft(page):
    if _popup_inicio_desativado():
        return

    nao_mostrar = ft.Checkbox(
        label="Não mostrar novamente nesta instalação",
        value=False,
    )

    def fechar_popup(e=None):
        try:
            if nao_mostrar.value:
                _salvar_popup_inicio_desativado()
        except Exception as exc:
            print(f"[POPUP INÍCIO] Não foi possível salvar preferência: {exc}")

        dialog.open = False
        try:
            page.update()
        except Exception:
            pass

    def item_instrucao(numero, titulo, texto):
        return ft.Container(
            bgcolor="#F8FAFC",
            border_radius=12,
            padding=12,
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(
                        width=34,
                        height=34,
                        border_radius=17,
                        bgcolor="#2563EB",
                        alignment=ft.Alignment.CENTER,
                        content=ft.Text(str(numero), color="white", weight=ft.FontWeight.BOLD),
                    ),
                    ft.Column(
                        spacing=4,
                        expand=True,
                        controls=[
                            ft.Text(titulo, size=14, weight=ft.FontWeight.BOLD, color="#111827"),
                            ft.Text(texto, size=12, color="#64748B"),
                        ],
                    ),
                ],
            ),
        )

    conteudo = ft.Container(
        width=680,
        height=560,
        content=ft.Column(
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text(
                    "Bem-vindo ao NutriSoft",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color="#111827",
                ),
                ft.Text(
                    "Este sistema organiza o acompanhamento nutricional do paciente, integrando cadastro, anamnese, recordatório, antropometria, exames laboratoriais, análise nutricional e relatório PDF.",
                    size=13,
                    color="#64748B",
                ),
                item_instrucao(
                    1,
                    "Comece pelo paciente",
                    "Cadastre um novo paciente ou selecione um paciente existente. Todas as informações clínicas ficam vinculadas ao paciente selecionado.",
                ),
                item_instrucao(
                    2,
                    "Preencha a base nutricional",
                    "Use as telas Anamnese, Recordatório e Antropometria para registrar hábitos, rotina alimentar, medidas corporais, objetivo do tratamento e pontos de atenção.",
                ),
                item_instrucao(
                    3,
                    "Cadastre ou importe exames",
                    "Na tela Exames, você pode lançar resultados manualmente ou importar um PDF de laboratório. O sistema gera uma prévia antes de salvar e depois limpa o diretório temporário de carga.",
                ),
                item_instrucao(
                    4,
                    "Acompanhe o Dashboard",
                    "O Dashboard mostra os principais resultados, status do paciente, exames normais, alterados e histórico laboratorial.",
                ),
                item_instrucao(
                    5,
                    "Use a visão Nutrição",
                    "A tela Nutrição reúne exames, antropometria, gasto calórico, recordatório, anamnese, gráficos e insights para apoiar a conduta da nutricionista.",
                ),
                item_instrucao(
                    6,
                    "Gere o relatório PDF",
                    "O relatório consolida o resumo de exames, lista apenas os exames alterados, apresenta análise antropométrica, gasto calórico e gráficos comparativos.",
                ),
                ft.Container(
                    bgcolor="#EFF6FF",
                    border_radius=12,
                    padding=12,
                    content=ft.Text(
                        "Importante: os dados ficam salvos em data_flet/*.csv. Evite apagar essa pasta sem backup.",
                        size=12,
                        color="#1D4ED8",
                        weight=ft.FontWeight.BOLD,
                    ),
                ),
                nao_mostrar,
            ],
        ),
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Instruções de uso", weight=ft.FontWeight.BOLD),
        content=conteudo,
        actions=[
            ft.TextButton(
                content=ft.Text("Fechar e começar"),
                on_click=fechar_popup,
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    try:
        page.overlay.append(dialog)
    except Exception:
        pass

    dialog.open = True

    try:
        page.update()
    except Exception:
        pass



def main(page):
    """Wrapper de inicialização do NutriSoft com popup inicial."""
    main_original_nutrisoft(page)

    try:
        abrir_popup_instrucoes_nutrisoft(page)
    except Exception as exc:
        print(f"[POPUP INÍCIO] Erro ao abrir instruções: {exc}")




# ============================================================
# CARDÁPIO - GERADOR BASEADO NA TACO
# ============================================================

COLUNAS_TACO_CARDAPIO = [
    "alimento_id", "alimento", "grupo", "kcal_100g", "proteina_100g",
    "carbo_100g", "lipidios_100g", "fibra_100g", "fonte"
]

COLUNAS_CARDAPIOS = [
    "cardapio_id", "paciente_id", "paciente_nome", "data_geracao",
    "objetivo", "meta_kcal", "total_kcal", "total_proteina",
    "total_carbo", "total_lipidios", "total_fibra", "observacoes"
]

COLUNAS_CARDAPIO_ITENS = [
    "cardapio_id", "refeicao", "horario", "alimento", "gramas",
    "kcal", "proteina", "carbo", "lipidios", "fibra", "observacao"
]


def _cp_data_dir():
    pasta = Path(__file__).resolve().parent / "data_flet"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def _cp_csv_path(nome):
    return _cp_data_dir() / nome


def _cp_float(valor, padrao=0.0):
    valor = str(valor or "").strip()
    valor = re.sub(r"[^0-9,.\-]", "", valor)

    if not valor:
        return padrao

    if "," in valor:
        valor = valor.replace(".", "").replace(",", ".")

    try:
        return float(valor)
    except Exception:
        return padrao


def _cp_ler_csv(nome):
    caminho = _cp_csv_path(nome)

    if not caminho.exists():
        return []

    try:
        with caminho.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    except UnicodeDecodeError:
        with caminho.open("r", encoding="latin-1", newline="") as f:
            return list(csv.DictReader(f))
    except Exception as exc:
        print(f"[CARDÁPIO] Erro ao ler {nome}: {exc}")
        return []


def _cp_escrever_csv(nome, colunas, rows):
    caminho = _cp_csv_path(nome)

    with caminho.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=colunas)
        writer.writeheader()
        for r in rows:
            writer.writerow({c: r.get(c, "") for c in colunas})


def _cp_append_csv(nome, colunas, row):
    caminho = _cp_csv_path(nome)
    existe = caminho.exists()

    with caminho.open("a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=colunas)

        if not existe or caminho.stat().st_size == 0:
            writer.writeheader()

        writer.writerow({c: row.get(c, "") for c in colunas})


def inicializar_base_taco_cardapio():
    """
    Base inicial editável com alimentos mais usados no gerador.
    Valores por 100g baseados na TACO/UNICAMP - 4ª edição.
    A nutricionista pode ampliar manualmente este CSV depois.
    """
    caminho = _cp_csv_path("taco_alimentos.csv")

    if caminho.exists():
        rows = _cp_ler_csv("taco_alimentos.csv")
        if rows:
            return

    fonte = "TACO/UNICAMP 4ª ed. revisada e ampliada, 2011 - Tabela 1, composição por 100g"

    alimentos = [
        ["arroz_tipo_1_cozido", "Arroz, tipo 1, cozido", "Cereais e derivados", 128, 2.5, 28.1, 0.2, 1.6, fonte],
        ["feijao_carioca_cozido", "Feijão carioca, cozido", "Leguminosas", 76, 4.8, 13.6, 0.5, 8.5, fonte],
        ["frango_coxa_sem_pele_cozida", "Frango, coxa, sem pele, cozida", "Carnes e derivados", 167, 26.9, 0.0, 5.8, 0.0, fonte],
        ["carne_patinho_grelhado", "Carne bovina, patinho, sem gordura, grelhado", "Carnes e derivados", 219, 35.9, 0.0, 7.3, 0.0, fonte],
        ["ovo_cozido", "Ovo de galinha, inteiro, cozido", "Ovos e derivados", 146, 13.3, 0.6, 9.5, 0.0, fonte],
        ["pao_integral", "Pão, trigo, forma, integral", "Cereais e derivados", 253, 9.4, 49.9, 3.7, 6.9, fonte],
        ["pao_frances", "Pão, trigo, francês", "Cereais e derivados", 300, 8.0, 58.6, 3.1, 2.3, fonte],
        ["banana_prata", "Banana, prata, crua", "Frutas", 98, 1.3, 26.0, 0.1, 2.0, fonte],
        ["aveia_flocos", "Aveia, flocos, crua", "Cereais e derivados", 394, 13.9, 66.6, 8.5, 9.1, fonte],
        ["acai_polpa_congelada", "Açaí, polpa, congelada", "Frutas", 58, 0.8, 6.2, 3.9, 2.6, fonte],
        ["mandioca_cozida", "Mandioca, cozida", "Tubérculos", 125, 0.6, 30.1, 0.3, 1.6, fonte],
        ["batata_doce_cozida", "Batata, doce, cozida", "Tubérculos", 77, 0.6, 18.4, 0.1, 2.2, fonte],
        ["tomate_cru", "Tomate, com semente, cru", "Verduras e hortaliças", 15, 1.1, 3.1, 0.2, 1.2, fonte],
        ["couve_refogada", "Couve, manteiga, refogada", "Verduras e hortaliças", 90, 1.7, 8.7, 6.6, 5.7, fonte],
        ["azeite_oliva", "Azeite, de oliva, extra virgem", "Gorduras e óleos", 884, 0.0, 0.0, 100.0, 0.0, fonte],
        ["mamao_papaia", "Mamão, Papaia, cru", "Frutas", 40, 0.5, 10.4, 0.1, 1.0, fonte],
        ["laranja_pera", "Laranja, pêra, crua", "Frutas", 37, 1.0, 8.9, 0.1, 0.8, fonte],
        ["biscoito_maisena", "Biscoito, doce, maisena", "Cereais e derivados", 443, 8.1, 75.2, 12.0, 2.1, fonte],
        ["biscoito_cream_cracker", "Biscoito, salgado, cream cracker", "Cereais e derivados", 432, 10.1, 68.7, 14.4, 2.5, fonte],
        ["bolo_chocolate", "Bolo, pronto, chocolate", "Produtos açucarados", 410, 6.2, 54.7, 18.5, 1.4, fonte],
        ["suco_laranja_pera", "Laranja, pêra, suco", "Bebidas", 33, 0.7, 7.6, 0.1, 0.0, fonte],
        ["cafe_sem_acucar", "Café, infusão, sem açúcar", "Bebidas", 9, 0.7, 1.5, 0.1, 0.0, fonte],
        ["sardinha_assada", "Sardinha, assada", "Pescados", 164, 32.2, 0.0, 3.0, 0.0, fonte],
        ["salmao_grelhado", "Salmão, sem pele, fresco, grelhado", "Pescados", 243, 26.1, 0.0, 14.5, 0.0, fonte],
    ]

    rows = []

    for item in alimentos:
        rows.append({
            "alimento_id": item[0],
            "alimento": item[1],
            "grupo": item[2],
            "kcal_100g": item[3],
            "proteina_100g": item[4],
            "carbo_100g": item[5],
            "lipidios_100g": item[6],
            "fibra_100g": item[7],
            "fonte": item[8],
        })

    _cp_escrever_csv("taco_alimentos.csv", COLUNAS_TACO_CARDAPIO, rows)
    print(f"[CARDÁPIO] Base TACO inicial criada: {len(rows)} alimentos.")


def _cp_base_alimentos():
    inicializar_base_taco_cardapio()
    return _cp_ler_csv("taco_alimentos.csv")


def _cp_alimento_por_id(alimento_id):
    alimento_id = str(alimento_id or "").strip()

    for a in _cp_base_alimentos():
        if str(a.get("alimento_id") or "").strip() == alimento_id:
            return a

    return None


def _cp_item(alimento_id, gramas, refeicao, horario="", observacao=""):
    alimento = _cp_alimento_por_id(alimento_id)

    if not alimento:
        return None

    g = _cp_float(gramas)
    fator = g / 100.0

    return {
        "refeicao": refeicao,
        "horario": horario,
        "alimento_id": alimento_id,
        "alimento": alimento.get("alimento", ""),
        "gramas": round(g, 1),
        "kcal": round(_cp_float(alimento.get("kcal_100g")) * fator, 1),
        "proteina": round(_cp_float(alimento.get("proteina_100g")) * fator, 1),
        "carbo": round(_cp_float(alimento.get("carbo_100g")) * fator, 1),
        "lipidios": round(_cp_float(alimento.get("lipidios_100g")) * fator, 1),
        "fibra": round(_cp_float(alimento.get("fibra_100g")) * fator, 1),
        "observacao": observacao,
        "fonte": alimento.get("fonte", ""),
    }


def _cp_totais(itens):
    return {
        "kcal": round(sum(_cp_float(i.get("kcal")) for i in itens), 1),
        "proteina": round(sum(_cp_float(i.get("proteina")) for i in itens), 1),
        "carbo": round(sum(_cp_float(i.get("carbo")) for i in itens), 1),
        "lipidios": round(sum(_cp_float(i.get("lipidios")) for i in itens), 1),
        "fibra": round(sum(_cp_float(i.get("fibra")) for i in itens), 1),
    }


def _cp_obter_contexto_paciente(paciente):
    pid = str(paciente.get("paciente_id") or paciente.get("id") or "").strip()

    anamnese = {}
    recordatorio = {}
    antropometria = {}

    if "_nr_ultimo" in globals():
        try:
            anamnese = _nr_ultimo("anamnese.csv", pid)
            recordatorio = _nr_ultimo("recordatorio_habitual.csv", pid)
            antropometria = _nr_ultimo("antropometria.csv", pid)
        except Exception:
            pass

    if not anamnese:
        rows = [r for r in _cp_ler_csv("anamnese.csv") if str(r.get("paciente_id") or "") == pid]
        anamnese = rows[-1] if rows else {}

    if not recordatorio:
        rows = [r for r in _cp_ler_csv("recordatorio_habitual.csv") if str(r.get("paciente_id") or "") == pid]
        recordatorio = rows[-1] if rows else {}

    if not antropometria:
        rows = [r for r in _cp_ler_csv("antropometria.csv") if str(r.get("paciente_id") or "") == pid]
        antropometria = rows[-1] if rows else {}

    antro_calc = {}

    if "_nr_antropometria" in globals():
        try:
            antro_calc = _nr_antropometria(paciente, antropometria)
        except Exception:
            antro_calc = {}

    calorias = {}

    if "_nr_calorias" in globals():
        try:
            calorias = _nr_calorias(paciente, anamnese, recordatorio, antro_calc)
        except Exception:
            calorias = {}

    meta = _cp_float(calorias.get("meta"), 0)

    if not meta:
        meta = 2000

    return {
        "paciente_id": pid,
        "anamnese": anamnese,
        "recordatorio": recordatorio,
        "antropometria": antropometria,
        "antro_calc": antro_calc,
        "calorias": calorias,
        "meta_kcal": round(meta, 0),
        "objetivo": calorias.get("objetivo") or anamnese.get("objetivo_nutricional") or "Não informado",
    }


def _cp_possui_lactose(contexto):
    texto = " ".join([
        str(contexto.get("anamnese", {}).get("intolerancia_alergia_alimentar", "")),
        str(contexto.get("recordatorio", {})),
    ]).lower()

    return "lactose" in texto


def gerar_cardapio_para_paciente(paciente, meta_kcal=None):
    contexto = _cp_obter_contexto_paciente(paciente)

    meta = _cp_float(meta_kcal, contexto.get("meta_kcal") or 2000)
    objetivo = str(contexto.get("objetivo") or "Não informado")
    lactose = _cp_possui_lactose(contexto)

    # Modelo base próximo de 2400 kcal para paciente adulto ativo leve/moderado.
    modelo = [
        ("Desjejum", "06:00", "pao_integral", 80, "Fonte de carboidrato com mais fibra."),
        ("Desjejum", "06:00", "ovo_cozido", 100, "Proteína no café da manhã."),
        ("Desjejum", "06:00", "banana_prata", 100, "Fruta prática para energia e potássio."),
        ("Desjejum", "06:00", "cafe_sem_acucar", 150, "Manter sem açúcar se houver controle glicêmico/lipídico."),

        ("Lanche da manhã", "09:30", "acai_polpa_congelada", 150, "Usar sem xarope para reduzir açúcar."),
        ("Lanche da manhã", "09:30", "aveia_flocos", 25, "Aumenta fibra e densidade nutricional."),

        ("Almoço", "12:30", "arroz_tipo_1_cozido", 170, "Ajustar porção conforme evolução do peso e treino."),
        ("Almoço", "12:30", "feijao_carioca_cozido", 120, "Fibra e proteína vegetal."),
        ("Almoço", "12:30", "frango_coxa_sem_pele_cozida", 160, "Proteína principal."),
        ("Almoço", "12:30", "tomate_cru", 100, "Salada/vegetais."),
        ("Almoço", "12:30", "azeite_oliva", 5, "Gordura boa em pequena quantidade."),

        ("Lanche da tarde", "15:30", "mandioca_cozida", 130, "Carboidrato energético."),
        ("Lanche da tarde", "15:30", "ovo_cozido", 50, "Complemento proteico."),
        ("Lanche da tarde", "15:30", "laranja_pera", 150, "Fruta e vitamina C."),

        ("Jantar", "19:30", "arroz_tipo_1_cozido", 140, "Pode alternar com batata-doce/mandioca."),
        ("Jantar", "19:30", "carne_patinho_grelhado", 140, "Proteína magra."),
        ("Jantar", "19:30", "couve_refogada", 100, "Vegetal com fibras e micronutrientes."),
        ("Jantar", "19:30", "azeite_oliva", 5, "Usar pouco óleo no preparo."),

        ("Ceia", "21:30", "mamao_papaia", 150, "Opção leve para fechar o dia."),
        ("Ceia", "21:30", "aveia_flocos", 20, "Fibra e saciedade."),
    ]

    itens = []

    for refeicao, horario, alimento_id, gramas, obs in modelo:
        item = _cp_item(alimento_id, gramas, refeicao, horario, obs)
        if item:
            itens.append(item)

    total_base = _cp_totais(itens).get("kcal") or 1
    escala = meta / total_base

    # Evita distorções extremas. A nutricionista pode ajustar depois.
    if escala < 0.80:
        escala = 0.80
    if escala > 1.20:
        escala = 1.20

    itens_ajustados = []

    for i in itens:
        gramas = _cp_float(i.get("gramas"))

        # Mantém azeite e café mais estáveis; ajusta mais os alimentos sólidos.
        if i.get("alimento_id") in ["azeite_oliva", "cafe_sem_acucar"]:
            nova_grama = gramas
        else:
            nova_grama = round(gramas * escala / 5) * 5

        item = _cp_item(
            i.get("alimento_id"),
            nova_grama,
            i.get("refeicao"),
            i.get("horario"),
            i.get("observacao"),
        )

        if item:
            itens_ajustados.append(item)

    totais = _cp_totais(itens_ajustados)

    observacoes = [
        "Cardápio gerado automaticamente como rascunho técnico para revisão da nutricionista.",
        "As quantidades foram calculadas com base na meta calórica estimada e na TACO/UNICAMP por 100g.",
        "Ajustar preferências, rotina, horários, sintomas, exames e evolução do paciente antes da entrega final.",
    ]

    if lactose:
        observacoes.append("Paciente com intolerância/alergia à lactose registrada: cardápio inicial evita leite/queijos como base.")

    if "ganho" in objetivo.lower():
        observacoes.append("Objetivo sugere ganho de massa/performance: priorizar proteína em todas as refeições e progressão do treino.")
    elif "redução" in objetivo.lower() or "reducao" in objetivo.lower():
        observacoes.append("Objetivo sugere redução de peso: revisar saciedade, fibras, ultraprocessados e aderência.")

    return {
        "cardapio_id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "paciente_id": contexto.get("paciente_id"),
        "paciente_nome": paciente.get("nome", "Paciente"),
        "data_geracao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "objetivo": objetivo,
        "meta_kcal": round(meta, 0),
        "itens": itens_ajustados,
        "totais": totais,
        "observacoes": observacoes,
        "fonte": "TACO/UNICAMP 4ª edição revisada e ampliada, 2011.",
    }


def salvar_cardapio_data_flet(cardapio):
    totais = cardapio.get("totais", {})
    cardapio_id = cardapio.get("cardapio_id") or datetime.now().strftime("%Y%m%d%H%M%S")

    _cp_append_csv("cardapios.csv", COLUNAS_CARDAPIOS, {
        "cardapio_id": cardapio_id,
        "paciente_id": cardapio.get("paciente_id"),
        "paciente_nome": cardapio.get("paciente_nome"),
        "data_geracao": cardapio.get("data_geracao"),
        "objetivo": cardapio.get("objetivo"),
        "meta_kcal": cardapio.get("meta_kcal"),
        "total_kcal": totais.get("kcal"),
        "total_proteina": totais.get("proteina"),
        "total_carbo": totais.get("carbo"),
        "total_lipidios": totais.get("lipidios"),
        "total_fibra": totais.get("fibra"),
        "observacoes": " | ".join(cardapio.get("observacoes", [])),
    })

    for item in cardapio.get("itens", []):
        _cp_append_csv("cardapio_itens.csv", COLUNAS_CARDAPIO_ITENS, {
            "cardapio_id": cardapio_id,
            "refeicao": item.get("refeicao"),
            "horario": item.get("horario"),
            "alimento": item.get("alimento"),
            "gramas": item.get("gramas"),
            "kcal": item.get("kcal"),
            "proteina": item.get("proteina"),
            "carbo": item.get("carbo"),
            "lipidios": item.get("lipidios"),
            "fibra": item.get("fibra"),
            "observacao": item.get("observacao"),
        })

    print(f"[CARDÁPIO] Cardápio salvo: {cardapio_id}")
    return cardapio_id


def gerar_pdf_cardapio_paciente(paciente, cardapio):
    rel_dir = Path(__file__).resolve().parent / "relatorios"
    rel_dir.mkdir(parents=True, exist_ok=True)

    nome_limpo = re.sub(r"[^A-Za-z0-9_-]+", "_", str(paciente.get("nome") or "Paciente")).strip("_")
    caminho_pdf = rel_dir / f"cardapio_{nome_limpo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    doc = SimpleDocTemplate(
        str(caminho_pdf),
        pagesize=A4,
        rightMargin=1.4 * cm,
        leftMargin=1.4 * cm,
        topMargin=1.3 * cm,
        bottomMargin=1.3 * cm,
    )

    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "CardapioTitle",
        parent=styles["Title"],
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=HexColor("#111827"),
        spaceAfter=14,
    )

    h2 = ParagraphStyle(
        "CardapioH2",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=HexColor("#111827"),
        spaceBefore=10,
        spaceAfter=8,
    )

    body = ParagraphStyle(
        "CardapioBody",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
        textColor=HexColor("#374151"),
    )

    small = ParagraphStyle(
        "CardapioSmall",
        parent=styles["BodyText"],
        fontSize=7,
        leading=9,
        textColor=HexColor("#374151"),
    )

    def P(txt, style=body):
        return Paragraph(xml_escape(str(txt or "")), style)

    story = []

    story.append(Paragraph("NutriSoft - Cardápio do Paciente", title))
    story.append(P(f"Paciente: {cardapio.get('paciente_nome')}"))
    story.append(P(f"Objetivo: {cardapio.get('objetivo')}"))
    story.append(P(f"Meta calórica: {cardapio.get('meta_kcal')} kcal/dia"))
    story.append(P(f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}"))
    story.append(Spacer(1, 10))

    totais = cardapio.get("totais", {})

    resumo = Table(
        [
            [P("Energia", small), P("Proteína", small), P("Carboidrato", small), P("Lipídeos", small), P("Fibra", small)],
            [
                f"{totais.get('kcal', 0):.0f} kcal",
                f"{totais.get('proteina', 0):.1f} g",
                f"{totais.get('carbo', 0):.1f} g",
                f"{totais.get('lipidios', 0):.1f} g",
                f"{totais.get('fibra', 0):.1f} g",
            ],
        ],
        colWidths=[3.3 * cm, 3.3 * cm, 3.3 * cm, 3.3 * cm, 3.3 * cm],
    )

    resumo.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#F3F4F6")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.25, HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))

    story.append(resumo)
    story.append(Spacer(1, 10))

    refeicoes = []
    for item in cardapio.get("itens", []):
        r = item.get("refeicao")
        if r not in refeicoes:
            refeicoes.append(r)

    for refeicao in refeicoes:
        story.append(Paragraph(refeicao, h2))

        rows = [[
            P("Horário", small),
            P("Alimento", small),
            P("Qtd.", small),
            P("kcal", small),
            P("Prot.", small),
            P("Carb.", small),
            P("Gord.", small),
        ]]

        for item in [i for i in cardapio.get("itens", []) if i.get("refeicao") == refeicao]:
            rows.append([
                P(item.get("horario"), small),
                P(item.get("alimento"), small),
                P(f"{item.get('gramas')} g", small),
                P(f"{item.get('kcal')}", small),
                P(f"{item.get('proteina')} g", small),
                P(f"{item.get('carbo')} g", small),
                P(f"{item.get('lipidios')} g", small),
            ])

        tabela = Table(
            rows,
            colWidths=[1.8 * cm, 6.0 * cm, 1.6 * cm, 1.5 * cm, 1.6 * cm, 1.6 * cm, 1.6 * cm],
            repeatRows=1,
        )

        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#F8FAFC")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.25, HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))

        story.append(tabela)
        story.append(Spacer(1, 8))

    story.append(Paragraph("Orientações", h2))

    for obs in cardapio.get("observacoes", []):
        story.append(P(f"• {obs}"))

    story.append(Spacer(1, 8))
    story.append(P("Fonte nutricional: TACO/UNICAMP - Tabela Brasileira de Composição de Alimentos, 4ª edição revisada e ampliada, 2011. Valores calculados proporcionalmente por 100g de parte comestível.", small))
    story.append(P("Observação: este cardápio é um rascunho técnico para revisão e assinatura da nutricionista responsável.", small))

    doc.build(story)

    return str(caminho_pdf)


def _cp_texto_total_cardapio(cardapio):
    totais = cardapio.get("totais", {})

    return (
        f"Total: {totais.get('kcal', 0):.0f} kcal • "
        f"Proteína: {totais.get('proteina', 0):.1f} g • "
        f"Carboidrato: {totais.get('carbo', 0):.1f} g • "
        f"Gorduras: {totais.get('lipidios', 0):.1f} g • "
        f"Fibra: {totais.get('fibra', 0):.1f} g"
    )


def abrir_popup_cardapio(page, paciente):
    inicializar_base_taco_cardapio()

    contexto = _cp_obter_contexto_paciente(paciente)
    cardapio_atual = {"dados": None}

    meta_field = ft.TextField(
        label="Meta calórica diária",
        value=str(int(_cp_float(contexto.get("meta_kcal"), 2000))),
        width=180,
        border_radius=12,
    )

    objetivo_field = ft.TextField(
        label="Objetivo",
        value=str(contexto.get("objetivo") or "Não informado"),
        width=360,
        border_radius=12,
    )

    resumo_text = ft.Text(
        "Clique em Gerar prévia para montar o cardápio.",
        size=13,
        color="#64748B",
    )

    painel_cardapio = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO)

    def montar_tabela(cardapio):
        painel_cardapio.controls.clear()

        totais = cardapio.get("totais", {})
        resumo_text.value = _cp_texto_total_cardapio(cardapio)

        painel_cardapio.controls.append(
            ft.Container(
                bgcolor="#EFF6FF",
                border_radius=12,
                padding=12,
                content=ft.Text(
                    _cp_texto_total_cardapio(cardapio),
                    size=13,
                    color="#1D4ED8",
                    weight=ft.FontWeight.BOLD,
                ),
            )
        )

        refeicoes = []
        for item in cardapio.get("itens", []):
            ref = item.get("refeicao")
            if ref not in refeicoes:
                refeicoes.append(ref)

        for refeicao in refeicoes:
            rows = []

            itens_ref = [i for i in cardapio.get("itens", []) if i.get("refeicao") == refeicao]

            for item in itens_ref:
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(item.get("horario", "")), size=12)),
                            ft.DataCell(ft.Text(str(item.get("alimento", "")), size=12)),
                            ft.DataCell(ft.Text(f'{item.get("gramas")} g', size=12)),
                            ft.DataCell(ft.Text(f'{item.get("kcal")}', size=12)),
                            ft.DataCell(ft.Text(f'{item.get("proteina")} g', size=12)),
                            ft.DataCell(ft.Text(f'{item.get("carbo")} g', size=12)),
                            ft.DataCell(ft.Text(f'{item.get("lipidios")} g', size=12)),
                        ]
                    )
                )

            painel_cardapio.controls.append(
                ft.Container(
                    bgcolor="#FFFFFF",
                    border_radius=14,
                    padding=14,
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Text(refeicao, size=18, weight=ft.FontWeight.BOLD, color="#111827"),
                            ft.DataTable(
                                columns=[
                                    ft.DataColumn(ft.Text("Hora")),
                                    ft.DataColumn(ft.Text("Alimento")),
                                    ft.DataColumn(ft.Text("Qtd.")),
                                    ft.DataColumn(ft.Text("kcal")),
                                    ft.DataColumn(ft.Text("Prot.")),
                                    ft.DataColumn(ft.Text("Carb.")),
                                    ft.DataColumn(ft.Text("Gord.")),
                                ],
                                rows=rows,
                                heading_row_color="#F8FAFC",
                                border_radius=12,
                            ),
                        ],
                    ),
                )
            )

        painel_cardapio.controls.append(
            ft.Container(
                bgcolor="#F8FAFC",
                border_radius=12,
                padding=12,
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Text("Orientações para revisão", size=14, weight=ft.FontWeight.BOLD, color="#111827"),
                        *[
                            ft.Text(f"• {obs}", size=12, color="#374151")
                            for obs in cardapio.get("observacoes", [])
                        ],
                    ],
                ),
            )
        )

    def gerar_previa(e=None):
        cardapio = gerar_cardapio_para_paciente(
            paciente,
            meta_kcal=_cp_float(meta_field.value, contexto.get("meta_kcal") or 2000),
        )

        if objetivo_field.value:
            cardapio["objetivo"] = objetivo_field.value

        cardapio_atual["dados"] = cardapio
        montar_tabela(cardapio)
        page.update()

    def salvar_cardapio(e=None):
        cardapio = cardapio_atual.get("dados")

        if not cardapio:
            gerar_previa()
            cardapio = cardapio_atual.get("dados")

        try:
            cardapio_id = salvar_cardapio_data_flet(cardapio)

            if "mostrar_snackbar" in globals():
                mostrar_snackbar(page, f"Cardápio salvo: {cardapio_id}", globals().get("COR_NORMAL", "#16A34A"))
            else:
                print(f"Cardápio salvo: {cardapio_id}")
        except Exception as exc:
            if "mostrar_snackbar" in globals():
                mostrar_snackbar(page, f"Erro ao salvar cardápio: {exc}", globals().get("COR_CRITICO", "#DC2626"))
            else:
                print("Erro ao salvar cardápio:", exc)

    def exportar_pdf(e=None):
        cardapio = cardapio_atual.get("dados")

        if not cardapio:
            gerar_previa()
            cardapio = cardapio_atual.get("dados")

        try:
            caminho = gerar_pdf_cardapio_paciente(paciente, cardapio)

            if "mostrar_snackbar" in globals():
                mostrar_snackbar(page, f"PDF do cardápio gerado: {caminho}", globals().get("COR_NORMAL", "#16A34A"))
            else:
                print("PDF do cardápio gerado:", caminho)
        except Exception as exc:
            if "mostrar_snackbar" in globals():
                mostrar_snackbar(page, f"Erro ao gerar PDF do cardápio: {exc}", globals().get("COR_CRITICO", "#DC2626"))
            else:
                print("Erro ao gerar PDF do cardápio:", exc)

    def fechar(e=None):
        dialog.open = False
        page.update()

    conteudo = ft.Container(
        width=980,
        height=680,
        content=ft.Column(
            spacing=14,
            controls=[
                ft.Text(
                    f"Paciente: {paciente.get('nome', 'Paciente')}",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color="#111827",
                ),
                ft.Text(
                    "Monte uma prévia de cardápio com base na meta calórica, dados do paciente e alimentos da TACO.",
                    size=13,
                    color="#64748B",
                ),
                ft.Container(
                    bgcolor="#F8FAFC",
                    border_radius=14,
                    padding=12,
                    content=ft.Row(
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            meta_field,
                            objetivo_field,
                            ft.FilledButton(
                                content=ft.Text("Gerar prévia", color="white"),
                                on_click=gerar_previa,
                                style=ft.ButtonStyle(
                                    bgcolor=globals().get("COR_PRIMARIA", "#2563EB"),
                                    color="white",
                                    shape=ft.RoundedRectangleBorder(radius=12),
                                ),
                            ),
                        ],
                    ),
                ),
                resumo_text,
                ft.Container(
                    expand=True,
                    bgcolor="#F3F4F6",
                    border_radius=16,
                    padding=12,
                    content=painel_cardapio,
                ),
            ],
        ),
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Gerar Cardápio", weight=ft.FontWeight.BOLD),
        content=conteudo,
        actions=[
            ft.TextButton(content=ft.Text("Salvar"), on_click=salvar_cardapio),
            ft.TextButton(content=ft.Text("Exportar PDF"), on_click=exportar_pdf),
            ft.TextButton(content=ft.Text("Fechar"), on_click=fechar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialog)
    dialog.open = True
    gerar_previa()
    page.update()




# ============================================================
# CARDÁPIO EDITÁVEL - ALTERAR / INCLUIR / EXCLUIR ALIMENTOS
# ============================================================

def abrir_popup_cardapio(page, paciente):
    inicializar_base_taco_cardapio()

    contexto = _cp_obter_contexto_paciente(paciente)
    alimentos_base = _cp_base_alimentos()

    cardapio_atual = {
        "dados": gerar_cardapio_para_paciente(
            paciente,
            meta_kcal=_cp_float(contexto.get("meta_kcal"), 2000),
        )
    }

    refeicoes_padrao = [
        "Desjejum",
        "Lanche da manhã",
        "Almoço",
        "Lanche da tarde",
        "Jantar",
        "Ceia",
    ]

    alimento_options = [
        ft.dropdown.Option(
            key=str(a.get("alimento_id")),
            text=str(a.get("alimento")),
        )
        for a in alimentos_base
        if str(a.get("alimento_id") or "").strip()
    ]

    refeicao_options = [
        ft.dropdown.Option(key=r, text=r)
        for r in refeicoes_padrao
    ]

    meta_field = ft.TextField(
        label="Meta calórica diária",
        value=str(int(_cp_float(contexto.get("meta_kcal"), 2000))),
        width=180,
        border_radius=12,
    )

    objetivo_field = ft.TextField(
        label="Objetivo",
        value=str(contexto.get("objetivo") or "Não informado"),
        width=360,
        border_radius=12,
    )

    nova_refeicao = ft.Dropdown(
        label="Refeição",
        width=170,
        options=refeicao_options,
        value="Almoço",
        border_radius=12,
    )

    novo_horario = ft.TextField(
        label="Horário",
        value="12:30",
        width=100,
        border_radius=12,
    )

    novo_alimento = ft.Dropdown(
        label="Alimento TACO",
        width=360,
        options=alimento_options,
        value=alimento_options[0].key if alimento_options else None,
        border_radius=12,
    )

    nova_quantidade = ft.TextField(
        label="Gramas",
        value="100",
        width=100,
        border_radius=12,
    )

    resumo_text = ft.Text(
        "",
        size=13,
        color="#64748B",
        weight=ft.FontWeight.BOLD,
    )

    painel_editor = ft.Column(
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
    )

    editores = []

    def alimento_id_por_nome(nome):
        nome = str(nome or "").strip()

        for a in alimentos_base:
            if str(a.get("alimento") or "").strip() == nome:
                return str(a.get("alimento_id") or "").strip()

        return alimento_options[0].key if alimento_options else ""

    def recalcular_dos_editores():
        itens = []

        for ed in editores:
            alimento_id = ed["alimento"].value
            gramas = _cp_float(ed["gramas"].value, 0)

            if not alimento_id or gramas <= 0:
                continue

            item = _cp_item(
                alimento_id,
                gramas,
                ed["refeicao"].value,
                ed["horario"].value,
                ed.get("observacao", ""),
            )

            if item:
                itens.append(item)

        cardapio = cardapio_atual.get("dados") or {}
        cardapio["itens"] = itens
        cardapio["totais"] = _cp_totais(itens)
        cardapio["meta_kcal"] = round(_cp_float(meta_field.value, contexto.get("meta_kcal") or 2000), 0)
        cardapio["objetivo"] = objetivo_field.value or contexto.get("objetivo") or "Não informado"
        cardapio["paciente_id"] = str(paciente.get("paciente_id") or paciente.get("id") or "")
        cardapio["paciente_nome"] = paciente.get("nome", "Paciente")
        cardapio["data_geracao"] = cardapio.get("data_geracao") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cardapio["cardapio_id"] = cardapio.get("cardapio_id") or datetime.now().strftime("%Y%m%d%H%M%S")

        if not cardapio.get("observacoes"):
            cardapio["observacoes"] = [
                "Cardápio revisado pela nutricionista a partir da base TACO.",
                "Valores nutricionais calculados proporcionalmente por 100g de parte comestível.",
            ]

        cardapio_atual["dados"] = cardapio
        return cardapio

    def atualizar_resumo():
        cardapio = cardapio_atual.get("dados") or {}
        totais = cardapio.get("totais", {})
        resumo_text.value = (
            f"Total: {_cp_float(totais.get('kcal')):.0f} kcal • "
            f"Proteína: {_cp_float(totais.get('proteina')):.1f} g • "
            f"Carboidrato: {_cp_float(totais.get('carbo')):.1f} g • "
            f"Gorduras: {_cp_float(totais.get('lipidios')):.1f} g • "
            f"Fibra: {_cp_float(totais.get('fibra')):.1f} g"
        )

    def renderizar_editor():
        painel_editor.controls.clear()
        editores.clear()

        cardapio = cardapio_atual.get("dados") or {}
        itens = cardapio.get("itens", [])

        if not itens:
            painel_editor.controls.append(
                ft.Container(
                    bgcolor="#FEF2F2",
                    border_radius=12,
                    padding=12,
                    content=ft.Text(
                        "Nenhum alimento no cardápio. Inclua um alimento da TACO para começar.",
                        size=13,
                        color="#991B1B",
                    ),
                )
            )
            atualizar_resumo()
            return

        for idx, item in enumerate(itens):
            alimento_id = str(item.get("alimento_id") or "").strip()

            if not alimento_id:
                alimento_id = alimento_id_por_nome(item.get("alimento"))

            refeicao_dd = ft.Dropdown(
                label="Refeição",
                width=145,
                options=refeicao_options,
                value=item.get("refeicao") if item.get("refeicao") in refeicoes_padrao else "Almoço",
                border_radius=12,
            )

            horario_tf = ft.TextField(
                label="Hora",
                width=85,
                value=str(item.get("horario") or ""),
                border_radius=12,
            )

            alimento_dd = ft.Dropdown(
                label="Alimento",
                width=350,
                options=alimento_options,
                value=alimento_id,
                border_radius=12,
            )

            gramas_tf = ft.TextField(
                label="g",
                width=85,
                value=str(item.get("gramas") or "100"),
                border_radius=12,
            )

            nutrientes_txt = ft.Text(
                f'{_cp_float(item.get("kcal")):.0f} kcal | '
                f'P {_cp_float(item.get("proteina")):.1f}g | '
                f'C {_cp_float(item.get("carbo")):.1f}g | '
                f'G {_cp_float(item.get("lipidios")):.1f}g',
                size=12,
                color="#475569",
            )

            def excluir_item(e, indice=idx):
                cardapio = recalcular_dos_editores()
                itens_atuais = cardapio.get("itens", [])

                if 0 <= indice < len(itens_atuais):
                    del itens_atuais[indice]

                cardapio["itens"] = itens_atuais
                cardapio["totais"] = _cp_totais(itens_atuais)
                cardapio_atual["dados"] = cardapio

                renderizar_editor()
                atualizar_resumo()
                page.update()

            excluir_btn = ft.TextButton(
                content=ft.Text("Excluir", color="#DC2626"),
                on_click=excluir_item,
            )

            editores.append({
                "refeicao": refeicao_dd,
                "horario": horario_tf,
                "alimento": alimento_dd,
                "gramas": gramas_tf,
                "observacao": item.get("observacao", ""),
            })

            painel_editor.controls.append(
                ft.Container(
                    bgcolor="#FFFFFF",
                    border_radius=14,
                    padding=12,
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Row(
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    refeicao_dd,
                                    horario_tf,
                                    alimento_dd,
                                    gramas_tf,
                                    excluir_btn,
                                ],
                            ),
                            ft.Container(
                                bgcolor="#F8FAFC",
                                border_radius=10,
                                padding=8,
                                content=nutrientes_txt,
                            ),
                        ],
                    ),
                )
            )

        atualizar_resumo()

    def recalcular_click(e=None):
        cardapio = recalcular_dos_editores()

        # Recalcula cada item para atualizar kcal/proteína/carbo/gordura após troca de alimento ou quantidade.
        cardapio["itens"] = [
            _cp_item(
                ed["alimento"].value,
                _cp_float(ed["gramas"].value, 0),
                ed["refeicao"].value,
                ed["horario"].value,
                ed.get("observacao", ""),
            )
            for ed in editores
            if ed["alimento"].value and _cp_float(ed["gramas"].value, 0) > 0
        ]

        cardapio["itens"] = [i for i in cardapio["itens"] if i]
        cardapio["totais"] = _cp_totais(cardapio["itens"])
        cardapio_atual["dados"] = cardapio

        renderizar_editor()
        atualizar_resumo()
        page.update()

    def adicionar_alimento(e=None):
        cardapio = recalcular_dos_editores()

        item = _cp_item(
            novo_alimento.value,
            _cp_float(nova_quantidade.value, 100),
            nova_refeicao.value or "Almoço",
            novo_horario.value or "",
            "Incluído manualmente pela nutricionista.",
        )

        if item:
            cardapio.setdefault("itens", []).append(item)
            cardapio["totais"] = _cp_totais(cardapio["itens"])
            cardapio_atual["dados"] = cardapio

        renderizar_editor()
        atualizar_resumo()
        page.update()

    def gerar_previa_nova(e=None):
        cardapio = gerar_cardapio_para_paciente(
            paciente,
            meta_kcal=_cp_float(meta_field.value, contexto.get("meta_kcal") or 2000),
        )

        cardapio["objetivo"] = objetivo_field.value or contexto.get("objetivo") or "Não informado"
        cardapio_atual["dados"] = cardapio

        renderizar_editor()
        atualizar_resumo()
        page.update()

    def salvar_cardapio(e=None):
        recalcular_click()
        cardapio = cardapio_atual.get("dados")

        try:
            cardapio_id = salvar_cardapio_data_flet(cardapio)

            if "mostrar_snackbar" in globals():
                mostrar_snackbar(page, f"Cardápio salvo: {cardapio_id}", globals().get("COR_NORMAL", "#16A34A"))
            else:
                print(f"Cardápio salvo: {cardapio_id}")
        except Exception as exc:
            if "mostrar_snackbar" in globals():
                mostrar_snackbar(page, f"Erro ao salvar cardápio: {exc}", globals().get("COR_CRITICO", "#DC2626"))
            else:
                print("Erro ao salvar cardápio:", exc)

    def exportar_pdf(e=None):
        recalcular_click()
        cardapio = cardapio_atual.get("dados")

        try:
            caminho = gerar_pdf_cardapio_paciente(paciente, cardapio)

            if "mostrar_snackbar" in globals():
                mostrar_snackbar(page, f"PDF do cardápio gerado: {caminho}", globals().get("COR_NORMAL", "#16A34A"))
            else:
                print("PDF do cardápio gerado:", caminho)
        except Exception as exc:
            if "mostrar_snackbar" in globals():
                mostrar_snackbar(page, f"Erro ao gerar PDF do cardápio: {exc}", globals().get("COR_CRITICO", "#DC2626"))
            else:
                print("Erro ao gerar PDF do cardápio:", exc)

    def fechar(e=None):
        dialog.open = False
        page.update()

    renderizar_editor()
    atualizar_resumo()

    conteudo = ft.Container(
        width=1060,
        height=720,
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Text(
                    f"Paciente: {paciente.get('nome', 'Paciente')}",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color="#111827",
                ),
                ft.Text(
                    "A nutricionista pode alterar alimentos, ajustar quantidades, incluir novos itens da TACO e excluir alimentos antes de salvar ou exportar.",
                    size=13,
                    color="#64748B",
                ),
                ft.Container(
                    bgcolor="#F8FAFC",
                    border_radius=14,
                    padding=12,
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Row(
                                spacing=10,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    meta_field,
                                    objetivo_field,
                                    ft.FilledButton(
                                        content=ft.Text("Gerar prévia", color="white"),
                                        on_click=gerar_previa_nova,
                                        style=ft.ButtonStyle(
                                            bgcolor=globals().get("COR_PRIMARIA", "#2563EB"),
                                            color="white",
                                            shape=ft.RoundedRectangleBorder(radius=12),
                                        ),
                                    ),
                                    ft.OutlinedButton(
                                        content="Recalcular",
                                        on_click=recalcular_click,
                                        style=ft.ButtonStyle(
                                            color=globals().get("COR_PRIMARIA", "#2563EB"),
                                            shape=ft.RoundedRectangleBorder(radius=12),
                                        ),
                                    ),
                                ],
                            ),
                            resumo_text,
                        ],
                    ),
                ),
                ft.Container(
                    bgcolor="#ECFDF5",
                    border_radius=14,
                    padding=12,
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Text("Incluir alimento da TACO", size=15, weight=ft.FontWeight.BOLD, color="#065F46"),
                            ft.Row(
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    nova_refeicao,
                                    novo_horario,
                                    novo_alimento,
                                    nova_quantidade,
                                    ft.FilledButton(
                                        content=ft.Text("Adicionar", color="white"),
                                        on_click=adicionar_alimento,
                                        style=ft.ButtonStyle(
                                            bgcolor="#16A34A",
                                            color="white",
                                            shape=ft.RoundedRectangleBorder(radius=12),
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                ft.Container(
                    expand=True,
                    bgcolor="#F3F4F6",
                    border_radius=16,
                    padding=12,
                    content=painel_editor,
                ),
            ],
        ),
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Gerar Cardápio", weight=ft.FontWeight.BOLD),
        content=conteudo,
        actions=[
            ft.TextButton(content=ft.Text("Salvar"), on_click=salvar_cardapio),
            ft.TextButton(content=ft.Text("Exportar PDF"), on_click=exportar_pdf),
            ft.TextButton(content=ft.Text("Fechar"), on_click=fechar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()




# ============================================================
# CARDÁPIO EDITÁVEL V2 - RECOMENDADO X PRESCRITO + DROPDOWNS
# ============================================================

def _cp_recomendacoes_cardapio(paciente, contexto, meta_kcal):
    meta = _cp_float(meta_kcal, 2000)
    antro = contexto.get("antro_calc", {}) or {}
    anamnese = contexto.get("anamnese", {}) or {}

    peso = _cp_float(antro.get("peso"), 0)

    if not peso:
        peso = _cp_float(contexto.get("antropometria", {}).get("peso"), 0)

    objetivo = str(contexto.get("objetivo") or anamnese.get("objetivo_nutricional") or "").lower()

    if "ganho" in objetivo or "massa" in objetivo or "performance" in objetivo:
        prot_min = 1.6
        prot_max = 2.0
    elif "redu" in objetivo or "emagrec" in objetivo or "peso" in objetivo:
        prot_min = 1.6
        prot_max = 2.2
    else:
        prot_min = 1.2
        prot_max = 1.6

    if peso <= 0:
        peso = 70

    proteina_min = peso * prot_min
    proteina_max = peso * prot_max

    carbo_min = (meta * 0.40) / 4
    carbo_max = (meta * 0.55) / 4

    gordura_min = (meta * 0.25) / 9
    gordura_max = (meta * 0.35) / 9

    fibra_min = max(25, (meta / 1000) * 14)
    fibra_max = 45

    return {
        "kcal": {"min": meta * 0.95, "max": meta * 1.05, "unidade": "kcal"},
        "proteina": {"min": proteina_min, "max": proteina_max, "unidade": "g"},
        "carbo": {"min": carbo_min, "max": carbo_max, "unidade": "g"},
        "lipidios": {"min": gordura_min, "max": gordura_max, "unidade": "g"},
        "fibra": {"min": fibra_min, "max": fibra_max, "unidade": "g"},
    }


def _cp_status_recomendacao(valor, faixa):
    valor = _cp_float(valor, 0)
    minimo = _cp_float(faixa.get("min"), 0)
    maximo = _cp_float(faixa.get("max"), 0)

    if valor < minimo:
        return "Baixo", "#F59E0B"

    if valor > maximo:
        return "Alto", "#DC2626"

    return "OK", "#16A34A"


def _cp_texto_faixa(faixa):
    return f"{_cp_float(faixa.get('min')):.0f} a {_cp_float(faixa.get('max')):.0f} {faixa.get('unidade', '')}"


def _cp_atualizar_recomendacoes_cardapio(cardapio, paciente, contexto):
    meta = _cp_float(cardapio.get("meta_kcal"), contexto.get("meta_kcal") or 2000)
    cardapio["recomendacoes"] = _cp_recomendacoes_cardapio(paciente, contexto, meta)
    return cardapio


def _cp_card_recomendacao(titulo, valor, faixa, unidade=None):
    unidade = unidade or faixa.get("unidade", "")
    status, cor = _cp_status_recomendacao(valor, faixa)

    return ft.Container(
        bgcolor="#FFFFFF",
        border_radius=14,
        padding=12,
        width=170,
        content=ft.Column(
            spacing=5,
            controls=[
                ft.Text(titulo, size=12, color="#64748B"),
                ft.Text(f"{_cp_float(valor):.0f} {unidade}", size=20, weight=ft.FontWeight.BOLD, color="#111827"),
                ft.Text(f"Rec.: {_cp_texto_faixa(faixa)}", size=11, color="#64748B"),
                ft.Container(
                    bgcolor=cor,
                    border_radius=20,
                    padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                    content=ft.Text(status, size=11, color="#FFFFFF", weight=ft.FontWeight.BOLD),
                ),
            ],
        ),
    )


def gerar_pdf_cardapio_paciente(paciente, cardapio):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import HexColor
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from xml.sax.saxutils import escape as xml_escape

    rel_dir = Path(__file__).resolve().parent / "relatorios"
    rel_dir.mkdir(parents=True, exist_ok=True)

    nome_limpo = re.sub(r"[^A-Za-z0-9_-]+", "_", str(paciente.get("nome") or "Paciente")).strip("_")
    caminho_pdf = rel_dir / f"cardapio_{nome_limpo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    doc = SimpleDocTemplate(
        str(caminho_pdf),
        pagesize=A4,
        rightMargin=1.3 * cm,
        leftMargin=1.3 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )

    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "CardapioTitleV2",
        parent=styles["Title"],
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=HexColor("#111827"),
        spaceAfter=14,
    )

    h2 = ParagraphStyle(
        "CardapioH2V2",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=HexColor("#111827"),
        spaceBefore=10,
        spaceAfter=8,
    )

    body = ParagraphStyle(
        "CardapioBodyV2",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
        textColor=HexColor("#374151"),
    )

    small = ParagraphStyle(
        "CardapioSmallV2",
        parent=styles["BodyText"],
        fontSize=7,
        leading=9,
        textColor=HexColor("#374151"),
    )

    def P(txt, style=body):
        return Paragraph(xml_escape(str(txt or "")), style)

    story = []
    totais = cardapio.get("totais", {})
    recomendacoes = cardapio.get("recomendacoes", {})

    story.append(Paragraph("NutriSoft - Cardápio do Paciente", title))
    story.append(P(f"Paciente: {cardapio.get('paciente_nome')}"))
    story.append(P(f"Objetivo: {cardapio.get('objetivo')}"))
    story.append(P(f"Meta calórica: {cardapio.get('meta_kcal')} kcal/dia"))
    story.append(P(f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}"))
    story.append(Spacer(1, 10))

    rows_rec = [[P("Nutriente", small), P("Recomendado", small), P("Cardápio", small), P("Status", small)]]

    mapa = [
        ("Energia", "kcal", "kcal"),
        ("Proteína", "proteina", "g"),
        ("Carboidrato", "carbo", "g"),
        ("Gorduras", "lipidios", "g"),
        ("Fibra", "fibra", "g"),
    ]

    for nome, chave, unidade in mapa:
        faixa = recomendacoes.get(chave, {"min": 0, "max": 0, "unidade": unidade})
        valor = totais.get(chave, 0)
        status, _ = _cp_status_recomendacao(valor, faixa)

        rows_rec.append([
            P(nome, small),
            P(_cp_texto_faixa(faixa), small),
            P(f"{_cp_float(valor):.1f} {unidade}", small),
            P(status, small),
        ])

    tabela_rec = Table(rows_rec, colWidths=[4.0 * cm, 5.0 * cm, 4.0 * cm, 3.0 * cm])
    tabela_rec.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#F3F4F6")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.25, HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))

    story.append(Paragraph("Recomendado x Cardápio", h2))
    story.append(tabela_rec)
    story.append(Spacer(1, 10))

    refeicoes = []
    for item in cardapio.get("itens", []):
        r = item.get("refeicao")
        if r not in refeicoes:
            refeicoes.append(r)

    for refeicao in refeicoes:
        story.append(Paragraph(refeicao, h2))

        rows = [[
            P("Horário", small),
            P("Alimento", small),
            P("Qtd.", small),
            P("kcal", small),
            P("Prot.", small),
            P("Carb.", small),
            P("Gord.", small),
        ]]

        for item in [i for i in cardapio.get("itens", []) if i.get("refeicao") == refeicao]:
            rows.append([
                P(item.get("horario"), small),
                P(item.get("alimento"), small),
                P(f"{item.get('gramas')} g", small),
                P(item.get("kcal"), small),
                P(f"{item.get('proteina')} g", small),
                P(f"{item.get('carbo')} g", small),
                P(f"{item.get('lipidios')} g", small),
            ])

        tabela = Table(
            rows,
            colWidths=[1.7 * cm, 6.0 * cm, 1.5 * cm, 1.4 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm],
            repeatRows=1,
        )

        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#F8FAFC")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.25, HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))

        story.append(tabela)
        story.append(Spacer(1, 8))

    story.append(Paragraph("Orientações", h2))

    for obs in cardapio.get("observacoes", []):
        story.append(P(f"• {obs}"))

    story.append(Spacer(1, 8))
    story.append(P("Fonte nutricional: TACO/UNICAMP - Tabela Brasileira de Composição de Alimentos, 4ª edição revisada e ampliada, 2011. Valores calculados proporcionalmente por 100g de parte comestível.", small))
    story.append(P("Observação: este cardápio é um rascunho técnico para revisão e assinatura da nutricionista responsável.", small))

    doc.build(story)
    return str(caminho_pdf)


def abrir_popup_cardapio(page, paciente):
    inicializar_base_taco_cardapio()

    contexto = _cp_obter_contexto_paciente(paciente)
    alimentos_base = _cp_base_alimentos()

    cardapio_inicial = gerar_cardapio_para_paciente(
        paciente,
        meta_kcal=_cp_float(contexto.get("meta_kcal"), 2000),
    )

    cardapio_inicial = _cp_atualizar_recomendacoes_cardapio(cardapio_inicial, paciente, contexto)

    cardapio_atual = {
        "dados": cardapio_inicial
    }

    refeicoes_padrao = [
        "Todas",
        "Desjejum",
        "Lanche da manhã",
        "Almoço",
        "Lanche da tarde",
        "Jantar",
        "Ceia",
    ]

    grupos = sorted(set([str(a.get("grupo") or "Outros") for a in alimentos_base]))
    grupos_options = [ft.dropdown.Option(key="Todos", text="Todos os grupos")] + [
        ft.dropdown.Option(key=g, text=g) for g in grupos
    ]

    def alimento_options_por_grupo(grupo="Todos"):
        filtrados = []

        for a in alimentos_base:
            if grupo != "Todos" and str(a.get("grupo") or "") != grupo:
                continue

            filtrados.append(
                ft.dropdown.Option(
                    key=str(a.get("alimento_id")),
                    text=str(a.get("alimento")),
                )
            )

        return filtrados

    refeicao_options = [
        ft.dropdown.Option(key=r, text=r)
        for r in refeicoes_padrao
    ]

    meta_field = ft.TextField(
        label="Meta calórica diária",
        value=str(int(_cp_float(contexto.get("meta_kcal"), 2000))),
        width=180,
        border_radius=12,
    )

    objetivo_field = ft.TextField(
        label="Objetivo",
        value=str(contexto.get("objetivo") or "Não informado"),
        width=360,
        border_radius=12,
    )

    visualizacao_refeicao = ft.Dropdown(
        label="Visualizar refeição",
        width=220,
        options=refeicao_options,
        value="Todas",
        border_radius=12,
    )

    nova_refeicao = ft.Dropdown(
        label="Refeição",
        width=170,
        options=[ft.dropdown.Option(key=r, text=r) for r in refeicoes_padrao if r != "Todas"],
        value="Almoço",
        border_radius=12,
    )

    novo_horario = ft.TextField(
        label="Horário",
        value="12:30",
        width=100,
        border_radius=12,
    )

    novo_grupo = ft.Dropdown(
        label="Grupo TACO",
        width=230,
        options=grupos_options,
        value="Todos",
        border_radius=12,
    )

    novo_alimento = ft.Dropdown(
        label="Alimento TACO",
        width=360,
        options=alimento_options_por_grupo("Todos"),
        border_radius=12,
    )

    if novo_alimento.options:
        novo_alimento.value = novo_alimento.options[0].key

    nova_quantidade = ft.TextField(
        label="Gramas",
        value="100",
        width=100,
        border_radius=12,
    )

    resumo_text = ft.Text(
        "",
        size=13,
        color="#64748B",
        weight=ft.FontWeight.BOLD,
    )

    painel_recomendacoes = ft.Row(spacing=10, wrap=True)
    painel_editor = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    editores = []

    def atualizar_dropdown_alimentos(e=None):
        novo_alimento.options = alimento_options_por_grupo(novo_grupo.value or "Todos")
        novo_alimento.value = novo_alimento.options[0].key if novo_alimento.options else None
        page.update()

    novo_grupo.on_change = atualizar_dropdown_alimentos

    def alimento_id_por_nome(nome):
        nome = str(nome or "").strip()

        for a in alimentos_base:
            if str(a.get("alimento") or "").strip() == nome:
                return str(a.get("alimento_id") or "").strip()

        return novo_alimento.options[0].key if novo_alimento.options else ""

    def atualizar_resumo_e_recomendacoes():
        cardapio = cardapio_atual.get("dados") or {}
        cardapio = _cp_atualizar_recomendacoes_cardapio(cardapio, paciente, contexto)
        cardapio_atual["dados"] = cardapio

        totais = cardapio.get("totais", {})
        recomendacoes = cardapio.get("recomendacoes", {})

        resumo_text.value = (
            f"Cardápio atual: {_cp_float(totais.get('kcal')):.0f} kcal • "
            f"Proteína {_cp_float(totais.get('proteina')):.1f} g • "
            f"Carboidrato {_cp_float(totais.get('carbo')):.1f} g • "
            f"Gorduras {_cp_float(totais.get('lipidios')):.1f} g • "
            f"Fibra {_cp_float(totais.get('fibra')):.1f} g"
        )

        painel_recomendacoes.controls = [
            _cp_card_recomendacao("Energia", totais.get("kcal"), recomendacoes.get("kcal", {}), "kcal"),
            _cp_card_recomendacao("Proteína", totais.get("proteina"), recomendacoes.get("proteina", {}), "g"),
            _cp_card_recomendacao("Carboidrato", totais.get("carbo"), recomendacoes.get("carbo", {}), "g"),
            _cp_card_recomendacao("Gorduras", totais.get("lipidios"), recomendacoes.get("lipidios", {}), "g"),
            _cp_card_recomendacao("Fibra", totais.get("fibra"), recomendacoes.get("fibra", {}), "g"),
        ]

    def atualizar_itens_visiveis():
        cardapio = cardapio_atual.get("dados") or {}
        itens = list(cardapio.get("itens", []))

        for ed in editores:
            idx = ed["idx"]

            if idx < 0 or idx >= len(itens):
                continue

            alimento_id = ed["alimento"].value
            gramas = _cp_float(ed["gramas"].value, 0)

            if not alimento_id or gramas <= 0:
                continue

            item = _cp_item(
                alimento_id,
                gramas,
                ed["refeicao"].value,
                ed["horario"].value,
                ed.get("observacao", ""),
            )

            if item:
                itens[idx] = item

        cardapio["itens"] = itens
        cardapio["totais"] = _cp_totais(itens)
        cardapio["meta_kcal"] = round(_cp_float(meta_field.value, contexto.get("meta_kcal") or 2000), 0)
        cardapio["objetivo"] = objetivo_field.value or contexto.get("objetivo") or "Não informado"
        cardapio["paciente_id"] = str(paciente.get("paciente_id") or paciente.get("id") or "")
        cardapio["paciente_nome"] = paciente.get("nome", "Paciente")
        cardapio["data_geracao"] = cardapio.get("data_geracao") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cardapio["cardapio_id"] = cardapio.get("cardapio_id") or datetime.now().strftime("%Y%m%d%H%M%S")

        if not cardapio.get("observacoes"):
            cardapio["observacoes"] = [
                "Cardápio revisado pela nutricionista a partir da base TACO.",
                "Valores nutricionais calculados proporcionalmente por 100g de parte comestível.",
            ]

        cardapio_atual["dados"] = _cp_atualizar_recomendacoes_cardapio(cardapio, paciente, contexto)
        return cardapio_atual["dados"]

    def renderizar_editor():
        painel_editor.controls.clear()
        editores.clear()

        cardapio = cardapio_atual.get("dados") or {}
        itens = list(cardapio.get("itens", []))
        filtro = visualizacao_refeicao.value or "Todas"

        itens_filtrados = []

        for idx, item in enumerate(itens):
            if filtro != "Todas" and item.get("refeicao") != filtro:
                continue
            itens_filtrados.append((idx, item))

        if not itens_filtrados:
            painel_editor.controls.append(
                ft.Container(
                    bgcolor="#FEF2F2",
                    border_radius=12,
                    padding=12,
                    content=ft.Text(
                        "Nenhum alimento nesta visualização. Inclua um alimento da TACO para começar.",
                        size=13,
                        color="#991B1B",
                    ),
                )
            )
            atualizar_resumo_e_recomendacoes()
            return

        refeicoes_renderizadas = []

        for idx, item in itens_filtrados:
            refeicao = item.get("refeicao")

            if refeicao not in refeicoes_renderizadas:
                refeicoes_renderizadas.append(refeicao)
                painel_editor.controls.append(
                    ft.Text(refeicao, size=18, weight=ft.FontWeight.BOLD, color="#111827")
                )

            alimento_id = str(item.get("alimento_id") or "").strip()

            if not alimento_id:
                alimento_id = alimento_id_por_nome(item.get("alimento"))

            refeicao_dd = ft.Dropdown(
                label="Refeição",
                width=145,
                options=[ft.dropdown.Option(key=r, text=r) for r in refeicoes_padrao if r != "Todas"],
                value=item.get("refeicao") if item.get("refeicao") in refeicoes_padrao else "Almoço",
                border_radius=12,
            )

            horario_tf = ft.TextField(
                label="Hora",
                width=85,
                value=str(item.get("horario") or ""),
                border_radius=12,
            )

            alimento_dd = ft.Dropdown(
                label="Alimento",
                width=350,
                options=alimento_options_por_grupo("Todos"),
                value=alimento_id,
                border_radius=12,
            )

            gramas_tf = ft.TextField(
                label="g",
                width=85,
                value=str(item.get("gramas") or "100"),
                border_radius=12,
            )

            nutrientes_txt = ft.Text(
                f'{_cp_float(item.get("kcal")):.0f} kcal | '
                f'P {_cp_float(item.get("proteina")):.1f}g | '
                f'C {_cp_float(item.get("carbo")):.1f}g | '
                f'G {_cp_float(item.get("lipidios")):.1f}g | '
                f'Fibra {_cp_float(item.get("fibra")):.1f}g',
                size=12,
                color="#475569",
            )

            def excluir_item(e, indice=idx):
                atualizar_itens_visiveis()
                cardapio = cardapio_atual.get("dados") or {}
                itens_atuais = list(cardapio.get("itens", []))

                if 0 <= indice < len(itens_atuais):
                    del itens_atuais[indice]

                cardapio["itens"] = itens_atuais
                cardapio["totais"] = _cp_totais(itens_atuais)
                cardapio_atual["dados"] = _cp_atualizar_recomendacoes_cardapio(cardapio, paciente, contexto)

                renderizar_editor()
                atualizar_resumo_e_recomendacoes()
                page.update()

            excluir_btn = ft.TextButton(
                content=ft.Text("Excluir", color="#DC2626"),
                on_click=excluir_item,
            )

            editores.append({
                "idx": idx,
                "refeicao": refeicao_dd,
                "horario": horario_tf,
                "alimento": alimento_dd,
                "gramas": gramas_tf,
                "observacao": item.get("observacao", ""),
            })

            painel_editor.controls.append(
                ft.Container(
                    bgcolor="#FFFFFF",
                    border_radius=14,
                    padding=12,
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Row(
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    refeicao_dd,
                                    horario_tf,
                                    alimento_dd,
                                    gramas_tf,
                                    excluir_btn,
                                ],
                            ),
                            ft.Container(
                                bgcolor="#F8FAFC",
                                border_radius=10,
                                padding=8,
                                content=nutrientes_txt,
                            ),
                        ],
                    ),
                )
            )

        atualizar_resumo_e_recomendacoes()

    def trocar_visualizacao(e=None):
        atualizar_itens_visiveis()
        renderizar_editor()
        page.update()

    visualizacao_refeicao.on_change = trocar_visualizacao

    def recalcular_click(e=None):
        atualizar_itens_visiveis()
        renderizar_editor()
        atualizar_resumo_e_recomendacoes()
        page.update()

    def adicionar_alimento(e=None):
        atualizar_itens_visiveis()

        cardapio = cardapio_atual.get("dados") or {}
        itens = list(cardapio.get("itens", []))

        item = _cp_item(
            novo_alimento.value,
            _cp_float(nova_quantidade.value, 100),
            nova_refeicao.value or "Almoço",
            novo_horario.value or "",
            "Incluído manualmente pela nutricionista.",
        )

        if item:
            itens.append(item)
            cardapio["itens"] = itens
            cardapio["totais"] = _cp_totais(itens)
            cardapio_atual["dados"] = _cp_atualizar_recomendacoes_cardapio(cardapio, paciente, contexto)

        visualizacao_refeicao.value = nova_refeicao.value or "Todas"
        renderizar_editor()
        atualizar_resumo_e_recomendacoes()
        page.update()

    def gerar_previa_nova(e=None):
        cardapio = gerar_cardapio_para_paciente(
            paciente,
            meta_kcal=_cp_float(meta_field.value, contexto.get("meta_kcal") or 2000),
        )

        cardapio["objetivo"] = objetivo_field.value or contexto.get("objetivo") or "Não informado"
        cardapio_atual["dados"] = _cp_atualizar_recomendacoes_cardapio(cardapio, paciente, contexto)

        visualizacao_refeicao.value = "Todas"
        renderizar_editor()
        atualizar_resumo_e_recomendacoes()
        page.update()

    def salvar_cardapio(e=None):
        atualizar_itens_visiveis()
        cardapio = cardapio_atual.get("dados")

        try:
            cardapio_id = salvar_cardapio_data_flet(cardapio)

            if "mostrar_snackbar" in globals():
                mostrar_snackbar(page, f"Cardápio salvo: {cardapio_id}", globals().get("COR_NORMAL", "#16A34A"))
            else:
                print(f"Cardápio salvo: {cardapio_id}")
        except Exception as exc:
            if "mostrar_snackbar" in globals():
                mostrar_snackbar(page, f"Erro ao salvar cardápio: {exc}", globals().get("COR_CRITICO", "#DC2626"))
            else:
                print("Erro ao salvar cardápio:", exc)

    def exportar_pdf(e=None):
        atualizar_itens_visiveis()
        cardapio = cardapio_atual.get("dados")

        try:
            caminho = gerar_pdf_cardapio_paciente(paciente, cardapio)

            if "mostrar_snackbar" in globals():
                mostrar_snackbar(page, f"PDF do cardápio gerado: {caminho}", globals().get("COR_NORMAL", "#16A34A"))
            else:
                print("PDF do cardápio gerado:", caminho)
        except Exception as exc:
            if "mostrar_snackbar" in globals():
                mostrar_snackbar(page, f"Erro ao gerar PDF do cardápio: {exc}", globals().get("COR_CRITICO", "#DC2626"))
            else:
                print("Erro ao gerar PDF do cardápio:", exc)

    def fechar(e=None):
        dialog.open = False
        page.update()

    renderizar_editor()
    atualizar_resumo_e_recomendacoes()

    conteudo = ft.Container(
        width=1120,
        height=760,
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Text(
                    f"Paciente: {paciente.get('nome', 'Paciente')}",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color="#111827",
                ),
                ft.Text(
                    "Acompanhe o recomendado x prescrito enquanto ajusta alimentos, quantidades e refeições.",
                    size=13,
                    color="#64748B",
                ),
                ft.Container(
                    bgcolor="#F8FAFC",
                    border_radius=14,
                    padding=12,
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Row(
                                spacing=10,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    meta_field,
                                    objetivo_field,
                                    visualizacao_refeicao,
                                    ft.FilledButton(
                                        content=ft.Text("Gerar prévia", color="white"),
                                        on_click=gerar_previa_nova,
                                        style=ft.ButtonStyle(
                                            bgcolor=globals().get("COR_PRIMARIA", "#2563EB"),
                                            color="white",
                                            shape=ft.RoundedRectangleBorder(radius=12),
                                        ),
                                    ),
                                    ft.OutlinedButton(
                                        content="Recalcular",
                                        on_click=recalcular_click,
                                        style=ft.ButtonStyle(
                                            color=globals().get("COR_PRIMARIA", "#2563EB"),
                                            shape=ft.RoundedRectangleBorder(radius=12),
                                        ),
                                    ),
                                ],
                            ),
                            resumo_text,
                            painel_recomendacoes,
                        ],
                    ),
                ),
                ft.Container(
                    bgcolor="#ECFDF5",
                    border_radius=14,
                    padding=12,
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Text("Incluir alimento da TACO", size=15, weight=ft.FontWeight.BOLD, color="#065F46"),
                            ft.Row(
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    nova_refeicao,
                                    novo_horario,
                                    novo_grupo,
                                    novo_alimento,
                                    nova_quantidade,
                                    ft.FilledButton(
                                        content=ft.Text("Adicionar", color="white"),
                                        on_click=adicionar_alimento,
                                        style=ft.ButtonStyle(
                                            bgcolor="#16A34A",
                                            color="white",
                                            shape=ft.RoundedRectangleBorder(radius=12),
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                ft.Container(
                    expand=True,
                    bgcolor="#F3F4F6",
                    border_radius=16,
                    padding=12,
                    content=painel_editor,
                ),
            ],
        ),
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Gerar Cardápio", weight=ft.FontWeight.BOLD),
        content=conteudo,
        actions=[
            ft.TextButton(content=ft.Text("Salvar"), on_click=salvar_cardapio),
            ft.TextButton(content=ft.Text("Exportar PDF"), on_click=exportar_pdf),
            ft.TextButton(content=ft.Text("Fechar"), on_click=fechar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()







# ============================================================
# CARDÁPIO V3 - POPUP PRINCIPAL + POPUP DE EDIÇÃO
# ============================================================

def _cpv3_status_recomendacao(valor, faixa):
    if "_cp_status_recomendacao" in globals():
        try:
            return _cp_status_recomendacao(valor, faixa)
        except Exception:
            pass

    valor = _cp_float(valor, 0)
    minimo = _cp_float(faixa.get("min"), 0)
    maximo = _cp_float(faixa.get("max"), 0)

    if valor < minimo:
        return "Baixo", "#F59E0B"
    if valor > maximo:
        return "Alto", "#DC2626"
    return "OK", "#16A34A"


def _cpv3_texto_faixa(faixa):
    if "_cp_texto_faixa" in globals():
        try:
            return _cp_texto_faixa(faixa)
        except Exception:
            pass

    return f"{_cp_float(faixa.get('min')):.0f} a {_cp_float(faixa.get('max')):.0f} {faixa.get('unidade', '')}"


def _cpv3_atualizar_recomendacoes(cardapio, paciente, contexto):
    if "_cp_atualizar_recomendacoes_cardapio" in globals():
        try:
            return _cp_atualizar_recomendacoes_cardapio(cardapio, paciente, contexto)
        except Exception:
            pass

    meta = _cp_float(cardapio.get("meta_kcal"), contexto.get("meta_kcal") or 2000)
    cardapio["recomendacoes"] = {
        "kcal": {"min": meta * 0.95, "max": meta * 1.05, "unidade": "kcal"},
        "proteina": {"min": 90, "max": 150, "unidade": "g"},
        "carbo": {"min": (meta * 0.40) / 4, "max": (meta * 0.55) / 4, "unidade": "g"},
        "lipidios": {"min": (meta * 0.25) / 9, "max": (meta * 0.35) / 9, "unidade": "g"},
        "fibra": {"min": 25, "max": 45, "unidade": "g"},
    }
    return cardapio


def _cpv3_card_status(titulo, valor, faixa, unidade):
    status, cor = _cpv3_status_recomendacao(valor, faixa)

    return ft.Container(
        width=170,
        bgcolor="#FFFFFF",
        border_radius=14,
        padding=12,
        content=ft.Column(
            spacing=5,
            controls=[
                ft.Text(titulo, size=12, color="#64748B"),
                ft.Text(f"{_cp_float(valor):.0f} {unidade}", size=20, weight=ft.FontWeight.BOLD, color="#111827"),
                ft.Text(f"Rec.: {_cpv3_texto_faixa(faixa)}", size=11, color="#64748B"),
                ft.Container(
                    bgcolor=cor,
                    border_radius=20,
                    padding=ft.Padding.symmetric(horizontal=10, vertical=5),
                    content=ft.Text(status, size=11, color="#FFFFFF", weight=ft.FontWeight.BOLD),
                ),
            ],
        ),
    )


def _cpv3_resumo_texto(cardapio):
    totais = cardapio.get("totais", {})
    return (
        f"{_cp_float(totais.get('kcal')):.0f} kcal • "
        f"Proteína {_cp_float(totais.get('proteina')):.1f} g • "
        f"Carboidrato {_cp_float(totais.get('carbo')):.1f} g • "
        f"Gorduras {_cp_float(totais.get('lipidios')):.1f} g • "
        f"Fibra {_cp_float(totais.get('fibra')):.1f} g"
    )


def abrir_popup_cardapio(page, paciente):
    inicializar_base_taco_cardapio()

    contexto = _cp_obter_contexto_paciente(paciente)
    alimentos_base = _cp_base_alimentos()

    estado = {
        "cardapio": _cpv3_atualizar_recomendacoes(
            gerar_cardapio_para_paciente(
                paciente,
                meta_kcal=_cp_float(contexto.get("meta_kcal"), 2000),
            ),
            paciente,
            contexto,
        ),
        "editado": False,
        "preview_dialog": None,
        "edit_dialog": None,
    }

    refeicoes_padrao = [
        "Desjejum",
        "Lanche da manhã",
        "Almoço",
        "Lanche da tarde",
        "Jantar",
        "Ceia",
    ]

    grupos = sorted(set([str(a.get("grupo") or "Outros") for a in alimentos_base]))

    def opcoes_grupo():
        return [ft.dropdown.Option(key="Todos", text="Todos os grupos")] + [
            ft.dropdown.Option(key=g, text=g) for g in grupos
        ]

    def opcoes_alimentos(grupo="Todos"):
        ops = []
        for a in alimentos_base:
            if grupo != "Todos" and str(a.get("grupo") or "") != grupo:
                continue
            ops.append(ft.dropdown.Option(key=str(a.get("alimento_id")), text=str(a.get("alimento"))))
        return ops

    def alimento_id_por_nome(nome):
        nome = str(nome or "").strip()
        for a in alimentos_base:
            if str(a.get("alimento") or "").strip() == nome:
                return str(a.get("alimento_id") or "").strip()
        ops = opcoes_alimentos("Todos")
        return ops[0].key if ops else ""

    def refeicoes_do_cardapio(cardapio):
        refs = []
        for item in cardapio.get("itens", []):
            ref = item.get("refeicao")
            if ref and ref not in refs:
                refs.append(ref)
        return refs

    def card_recomendado_vs_cardapio(cardapio):
        cardapio = _cpv3_atualizar_recomendacoes(cardapio, paciente, contexto)
        totais = cardapio.get("totais", {})
        rec = cardapio.get("recomendacoes", {})

        return ft.Container(
            bgcolor="#F8FAFC",
            border_radius=16,
            padding=14,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Text("Recomendado x Cardápio", size=18, weight=ft.FontWeight.BOLD, color="#111827"),
                    ft.Text(
                        "Use estes indicadores para validar se as alterações continuam dentro da faixa recomendada.",
                        size=12,
                        color="#64748B",
                    ),
                    ft.Row(
                        spacing=10,
                        wrap=True,
                        controls=[
                            _cpv3_card_status("Energia", totais.get("kcal"), rec.get("kcal", {}), "kcal"),
                            _cpv3_card_status("Proteína", totais.get("proteina"), rec.get("proteina", {}), "g"),
                            _cpv3_card_status("Carboidrato", totais.get("carbo"), rec.get("carbo", {}), "g"),
                            _cpv3_card_status("Gorduras", totais.get("lipidios"), rec.get("lipidios", {}), "g"),
                            _cpv3_card_status("Fibra", totais.get("fibra"), rec.get("fibra", {}), "g"),
                        ],
                    ),
                ],
            ),
        )

    def tabela_refeicao(refeicao, itens):
        rows = []

        for item in itens:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(item.get("horario") or ""), size=12)),
                        ft.DataCell(ft.Text(str(item.get("alimento") or ""), size=12)),
                        ft.DataCell(ft.Text(f'{item.get("gramas")} g', size=12)),
                        ft.DataCell(ft.Text(f'{_cp_float(item.get("kcal")):.0f}', size=12)),
                        ft.DataCell(ft.Text(f'{_cp_float(item.get("proteina")):.1f} g', size=12)),
                        ft.DataCell(ft.Text(f'{_cp_float(item.get("carbo")):.1f} g', size=12)),
                        ft.DataCell(ft.Text(f'{_cp_float(item.get("lipidios")):.1f} g', size=12)),
                    ]
                )
            )

        return ft.Container(
            bgcolor="#FFFFFF",
            border_radius=16,
            padding=14,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Text(refeicao, size=18, weight=ft.FontWeight.BOLD, color="#111827"),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Hora")),
                            ft.DataColumn(ft.Text("Alimento")),
                            ft.DataColumn(ft.Text("Qtd.")),
                            ft.DataColumn(ft.Text("kcal")),
                            ft.DataColumn(ft.Text("Prot.")),
                            ft.DataColumn(ft.Text("Carb.")),
                            ft.DataColumn(ft.Text("Gord.")),
                        ],
                        rows=rows,
                        heading_row_color="#F8FAFC",
                        border_radius=12,
                    ),
                ],
            ),
        )

    def conteudo_preview():
        cardapio = estado["cardapio"]
        cardapio = _cpv3_atualizar_recomendacoes(cardapio, paciente, contexto)
        estado["cardapio"] = cardapio

        itens = cardapio.get("itens", [])

        blocos = [
            ft.Text(
                f"Paciente: {paciente.get('nome', 'Paciente')}",
                size=18,
                weight=ft.FontWeight.BOLD,
                color="#111827",
            ),
            ft.Text(
                f"Objetivo: {cardapio.get('objetivo')} • Meta: {_cp_float(cardapio.get('meta_kcal')):.0f} kcal/dia",
                size=13,
                color="#64748B",
            ),
            ft.Container(
                bgcolor="#EFF6FF",
                border_radius=14,
                padding=12,
                content=ft.Text(
                    f"Cardápio atual: {_cpv3_resumo_texto(cardapio)}",
                    size=13,
                    color="#1D4ED8",
                    weight=ft.FontWeight.BOLD,
                ),
            ),
        ]

        if estado["editado"]:
            blocos.append(card_recomendado_vs_cardapio(cardapio))
        else:
            blocos.append(
                ft.Container(
                    bgcolor="#F8FAFC",
                    border_radius=14,
                    padding=12,
                    content=ft.Text(
                        "Revise o cardápio abaixo. Para ajustar alimentos e quantidades, clique em Alterar Cardápio.",
                        size=13,
                        color="#64748B",
                    ),
                )
            )

        for ref in refeicoes_do_cardapio(cardapio):
            itens_ref = [i for i in itens if i.get("refeicao") == ref]
            blocos.append(tabela_refeicao(ref, itens_ref))

        blocos.append(
            ft.Container(
                bgcolor="#F8FAFC",
                border_radius=14,
                padding=12,
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Text("Orientações", size=15, weight=ft.FontWeight.BOLD, color="#111827"),
                        *[
                            ft.Text(f"• {obs}", size=12, color="#374151")
                            for obs in cardapio.get("observacoes", [])
                        ],
                    ],
                ),
            )
        )

        return ft.Container(
            width=1060,
            height=720,
            content=ft.Column(
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
                controls=blocos,
            ),
        )

    def atualizar_preview():
        dialog = estado.get("preview_dialog")
        if not dialog:
            return

        dialog.content = conteudo_preview()

        if estado["editado"]:
            dialog.actions = [
                ft.TextButton(content=ft.Text("Exportar PDF"), on_click=exportar_pdf_e_fechar),
                ft.TextButton(content=ft.Text("Alterar"), on_click=lambda e: abrir_editor()),
                ft.TextButton(content=ft.Text("Finalizar"), on_click=finalizar_e_fechar),
            ]
        else:
            dialog.actions = [
                ft.TextButton(content=ft.Text("Alterar Cardápio"), on_click=lambda e: abrir_editor()),
                ft.TextButton(content=ft.Text("Fechar"), on_click=fechar_preview),
            ]

        page.update()

    def fechar_preview(e=None):
        if estado.get("preview_dialog"):
            estado["preview_dialog"].open = False
        page.update()

    def finalizar_e_fechar(e=None):
        try:
            salvar_cardapio_data_flet(estado["cardapio"])
            if "mostrar_snackbar" in globals():
                mostrar_snackbar(page, "Cardápio salvo com sucesso.", globals().get("COR_NORMAL", "#16A34A"))
        except Exception as exc:
            if "mostrar_snackbar" in globals():
                mostrar_snackbar(page, f"Erro ao salvar cardápio: {exc}", globals().get("COR_CRITICO", "#DC2626"))
            else:
                print("Erro ao salvar cardápio:", exc)

        if estado.get("edit_dialog"):
            estado["edit_dialog"].open = False
        if estado.get("preview_dialog"):
            estado["preview_dialog"].open = False
        page.update()

    def exportar_pdf_e_fechar(e=None):
        try:
            salvar_cardapio_data_flet(estado["cardapio"])
            caminho = gerar_pdf_cardapio_paciente(paciente, estado["cardapio"])

            if "mostrar_snackbar" in globals():
                mostrar_snackbar(page, f"PDF do cardápio gerado: {caminho}", globals().get("COR_NORMAL", "#16A34A"))
            else:
                print("PDF do cardápio gerado:", caminho)

            if estado.get("edit_dialog"):
                estado["edit_dialog"].open = False
            if estado.get("preview_dialog"):
                estado["preview_dialog"].open = False
            page.update()

        except Exception as exc:
            if "mostrar_snackbar" in globals():
                mostrar_snackbar(page, f"Erro ao exportar PDF: {exc}", globals().get("COR_CRITICO", "#DC2626"))
            else:
                print("Erro ao exportar PDF:", exc)

    def abrir_editor():
        cardapio_base = estado["cardapio"]
        itens_edicao = [dict(i) for i in cardapio_base.get("itens", [])]

        filtro_refeicao = ft.Dropdown(
            label="Visualizar refeição",
            width=220,
            options=[ft.dropdown.Option(key="Todas", text="Todas")] + [
                ft.dropdown.Option(key=r, text=r) for r in refeicoes_padrao
            ],
            value="Todas",
            border_radius=12,
        )

        novo_grupo = ft.Dropdown(
            label="Grupo TACO",
            width=230,
            options=opcoes_grupo(),
            value="Todos",
            border_radius=12,
        )

        novo_alimento = ft.Dropdown(
            label="Alimento TACO",
            width=350,
            options=opcoes_alimentos("Todos"),
            border_radius=12,
        )

        if novo_alimento.options:
            novo_alimento.value = novo_alimento.options[0].key

        nova_refeicao = ft.Dropdown(
            label="Refeição",
            width=170,
            options=[ft.dropdown.Option(key=r, text=r) for r in refeicoes_padrao],
            value="Almoço",
            border_radius=12,
        )

        novo_horario = ft.TextField(label="Horário", value="12:30", width=100, border_radius=12)
        nova_quantidade = ft.TextField(label="Gramas", value="100", width=100, border_radius=12)

        editor_col = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        resumo_editor = ft.Text("", size=13, color="#64748B", weight=ft.FontWeight.BOLD)

        editores = []

        def atualizar_options_alimento(e=None):
            novo_alimento.options = opcoes_alimentos(novo_grupo.value or "Todos")
            novo_alimento.value = novo_alimento.options[0].key if novo_alimento.options else None
            page.update()

        novo_grupo.on_change = atualizar_options_alimento

        def aplicar_editores_em_lista():
            nonlocal itens_edicao

            novos = list(itens_edicao)

            for ed in editores:
                idx = ed["idx"]

                if idx < 0 or idx >= len(novos):
                    continue

                item = _cp_item(
                    ed["alimento"].value,
                    _cp_float(ed["gramas"].value, 0),
                    ed["refeicao"].value,
                    ed["horario"].value,
                    ed.get("observacao", ""),
                )

                if item:
                    novos[idx] = item

            itens_edicao = novos

        def resumo_itens():
            totais = _cp_totais(itens_edicao)
            resumo_editor.value = (
                f"Edição atual: {_cp_float(totais.get('kcal')):.0f} kcal • "
                f"Proteína {_cp_float(totais.get('proteina')):.1f} g • "
                f"Carboidrato {_cp_float(totais.get('carbo')):.1f} g • "
                f"Gorduras {_cp_float(totais.get('lipidios')):.1f} g • "
                f"Fibra {_cp_float(totais.get('fibra')):.1f} g"
            )

        def render_editor():
            editor_col.controls.clear()
            editores.clear()

            filtro = filtro_refeicao.value or "Todas"

            itens_filtrados = []
            for idx, item in enumerate(itens_edicao):
                if filtro != "Todas" and item.get("refeicao") != filtro:
                    continue
                itens_filtrados.append((idx, item))

            if not itens_filtrados:
                editor_col.controls.append(
                    ft.Container(
                        bgcolor="#FEF2F2",
                        border_radius=12,
                        padding=12,
                        content=ft.Text(
                            "Nenhum alimento nesta refeição. Inclua um alimento abaixo.",
                            size=13,
                            color="#991B1B",
                        ),
                    )
                )
                resumo_itens()
                return

            refeicao_renderizada = None

            for idx, item in itens_filtrados:
                if item.get("refeicao") != refeicao_renderizada:
                    refeicao_renderizada = item.get("refeicao")
                    editor_col.controls.append(
                        ft.Text(refeicao_renderizada, size=18, weight=ft.FontWeight.BOLD, color="#111827")
                    )

                alimento_id = str(item.get("alimento_id") or "").strip()
                if not alimento_id:
                    alimento_id = alimento_id_por_nome(item.get("alimento"))

                refeicao_dd = ft.Dropdown(
                    label="Refeição",
                    width=150,
                    options=[ft.dropdown.Option(key=r, text=r) for r in refeicoes_padrao],
                    value=item.get("refeicao") if item.get("refeicao") in refeicoes_padrao else "Almoço",
                    border_radius=12,
                )

                horario_tf = ft.TextField(
                    label="Hora",
                    width=90,
                    value=str(item.get("horario") or ""),
                    border_radius=12,
                )

                alimento_dd = ft.Dropdown(
                    label="Alimento",
                    width=410,
                    options=opcoes_alimentos("Todos"),
                    value=alimento_id,
                    border_radius=12,
                )

                gramas_tf = ft.TextField(
                    label="g",
                    width=90,
                    value=str(item.get("gramas") or "100"),
                    border_radius=12,
                )

                nutrientes = ft.Text(
                    f'{_cp_float(item.get("kcal")):.0f} kcal | '
                    f'P {_cp_float(item.get("proteina")):.1f}g | '
                    f'C {_cp_float(item.get("carbo")):.1f}g | '
                    f'G {_cp_float(item.get("lipidios")):.1f}g | '
                    f'Fibra {_cp_float(item.get("fibra")):.1f}g',
                    size=12,
                    color="#475569",
                )

                def excluir_item(e, indice=idx):
                    aplicar_editores_em_lista()
                    if 0 <= indice < len(itens_edicao):
                        del itens_edicao[indice]
                    render_editor()
                    page.update()

                editores.append({
                    "idx": idx,
                    "refeicao": refeicao_dd,
                    "horario": horario_tf,
                    "alimento": alimento_dd,
                    "gramas": gramas_tf,
                    "observacao": item.get("observacao", ""),
                })

                editor_col.controls.append(
                    ft.Container(
                        bgcolor="#FFFFFF",
                        border_radius=14,
                        padding=12,
                        content=ft.Column(
                            spacing=8,
                            controls=[
                                ft.Row(
                                    spacing=8,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        refeicao_dd,
                                        horario_tf,
                                        alimento_dd,
                                        gramas_tf,
                                        ft.TextButton(
                                            content=ft.Text("Excluir", color="#DC2626"),
                                            on_click=excluir_item,
                                        ),
                                    ],
                                ),
                                ft.Container(
                                    bgcolor="#F8FAFC",
                                    border_radius=10,
                                    padding=8,
                                    content=nutrientes,
                                ),
                            ],
                        ),
                    )
                )

            resumo_itens()

        def trocar_filtro(e=None):
            aplicar_editores_em_lista()
            render_editor()
            page.update()

        filtro_refeicao.on_change = trocar_filtro

        def recalcular_editor(e=None):
            aplicar_editores_em_lista()
            render_editor()
            page.update()

        def adicionar_item(e=None):
            aplicar_editores_em_lista()

            item = _cp_item(
                novo_alimento.value,
                _cp_float(nova_quantidade.value, 100),
                nova_refeicao.value or "Almoço",
                novo_horario.value or "",
                "Incluído manualmente pela nutricionista.",
            )

            if item:
                itens_edicao.append(item)

            filtro_refeicao.value = nova_refeicao.value or "Todas"
            render_editor()
            page.update()

        def salvar_edicao(e=None):
            aplicar_editores_em_lista()

            cardapio = estado["cardapio"]
            cardapio["itens"] = itens_edicao
            cardapio["totais"] = _cp_totais(itens_edicao)
            cardapio["meta_kcal"] = _cp_float(cardapio.get("meta_kcal"), contexto.get("meta_kcal") or 2000)
            cardapio["objetivo"] = cardapio.get("objetivo") or contexto.get("objetivo") or "Não informado"
            cardapio = _cpv3_atualizar_recomendacoes(cardapio, paciente, contexto)

            estado["cardapio"] = cardapio
            estado["editado"] = True

            if estado.get("edit_dialog"):
                estado["edit_dialog"].open = False

            atualizar_preview()
            page.update()

        def cancelar_edicao(e=None):
            if estado.get("edit_dialog"):
                estado["edit_dialog"].open = False
            page.update()

        render_editor()

        conteudo_editor = ft.Container(
            width=1120,
            height=740,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Text("Alterar cardápio", size=20, weight=ft.FontWeight.BOLD, color="#111827"),
                    ft.Text(
                        "Edite alimentos, quantidades, horários e refeições. Depois clique em Salvar alterações.",
                        size=13,
                        color="#64748B",
                    ),
                    ft.Container(
                        bgcolor="#F8FAFC",
                        border_radius=14,
                        padding=12,
                        content=ft.Row(
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                filtro_refeicao,
                                resumo_editor,
                                ft.OutlinedButton(
                                    content="Recalcular",
                                    on_click=recalcular_editor,
                                    style=ft.ButtonStyle(
                                        color=globals().get("COR_PRIMARIA", "#2563EB"),
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                    ),
                                ),
                            ],
                        ),
                    ),
                    ft.Container(
                        bgcolor="#ECFDF5",
                        border_radius=14,
                        padding=12,
                        content=ft.Column(
                            spacing=10,
                            controls=[
                                ft.Text("Incluir alimento da TACO", size=15, weight=ft.FontWeight.BOLD, color="#065F46"),
                                ft.Row(
                                    spacing=8,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        nova_refeicao,
                                        novo_horario,
                                        novo_grupo,
                                        novo_alimento,
                                        nova_quantidade,
                                        ft.FilledButton(
                                            content=ft.Text("Adicionar", color="white"),
                                            on_click=adicionar_item,
                                            style=ft.ButtonStyle(
                                                bgcolor="#16A34A",
                                                color="white",
                                                shape=ft.RoundedRectangleBorder(radius=12),
                                            ),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        bgcolor="#F3F4F6",
                        border_radius=16,
                        padding=12,
                        content=editor_col,
                    ),
                ],
            ),
        )

        edit_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Alterar Cardápio", weight=ft.FontWeight.BOLD),
            content=conteudo_editor,
            actions=[
                ft.TextButton(content=ft.Text("Salvar alterações"), on_click=salvar_edicao),
                ft.TextButton(content=ft.Text("Cancelar"), on_click=cancelar_edicao),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        estado["edit_dialog"] = edit_dialog
        page.overlay.append(edit_dialog)
        edit_dialog.open = True
        page.update()

    preview_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Gerar Cardápio", weight=ft.FontWeight.BOLD),
        content=conteudo_preview(),
        actions=[
            ft.TextButton(content=ft.Text("Alterar Cardápio"), on_click=lambda e: abrir_editor()),
            ft.TextButton(content=ft.Text("Fechar"), on_click=fechar_preview),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    estado["preview_dialog"] = preview_dialog
    page.overlay.append(preview_dialog)
    preview_dialog.open = True
    page.update()




# ============================================================
# PATCH DEFINITIVO - BOTÃO ADICIONAR NOVO PACIENTE
# ============================================================

def _np_csv_pacientes_path():
    if "caminho_csv_flet" in globals():
        return caminho_csv_flet("pacientes.csv")
    return Path(__file__).resolve().parent / "data_flet" / "pacientes.csv"


def _np_colunas_pacientes():
    try:
        return CSV_SCHEMA_FLET.get("pacientes.csv", [
            "paciente_id", "data_cadastro", "nome", "data_nascimento", "idade",
            "sexo", "telefone", "email", "profissao", "horario_trabalho", "observacoes"
        ])
    except Exception:
        return [
            "paciente_id", "data_cadastro", "nome", "data_nascimento", "idade",
            "sexo", "telefone", "email", "profissao", "horario_trabalho", "observacoes"
        ]


def _np_ler_pacientes_csv():
    import csv

    caminho = _np_csv_pacientes_path()
    caminho.parent.mkdir(parents=True, exist_ok=True)

    if not caminho.exists():
        return []

    try:
        with caminho.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    except Exception as exc:
        print(f"[NOVO PACIENTE] Erro ao ler pacientes.csv: {exc}")
        return []


def _np_proximo_id_paciente():
    maior = 0

    for row in _np_ler_pacientes_csv():
        valor = str(row.get("paciente_id", "")).strip()

        try:
            maior = max(maior, int(valor))
        except Exception:
            pass

    return str(maior + 1).zfill(4)


def _np_data_iso(valor):
    from datetime import datetime

    valor = str(valor or "").strip()

    if not valor:
        return ""

    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(valor, fmt).strftime("%Y-%m-%d")
        except Exception:
            pass

    return valor


def _np_calcular_idade(data_iso):
    from datetime import datetime, date

    data_iso = str(data_iso or "").strip()

    if not data_iso:
        return ""

    try:
        nasc = datetime.strptime(data_iso, "%Y-%m-%d").date()
        hoje = date.today()
        idade = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
        return str(idade)
    except Exception:
        return ""


def _np_mostrar_msg(page, msg, cor="#16A34A"):
    try:
        if "mostrar_snackbar" in globals():
            mostrar_snackbar(page, msg, cor)
            return

        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()
    except Exception:
        print(msg)


def _np_salvar_paciente_csv(dados):
    import csv
    from datetime import datetime

    caminho = _np_csv_pacientes_path()
    caminho.parent.mkdir(parents=True, exist_ok=True)

    colunas = _np_colunas_pacientes()

    novo_id = _np_proximo_id_paciente()
    data_nascimento = _np_data_iso(dados.get("data_nascimento"))
    idade = _np_calcular_idade(data_nascimento)

    row = {
        "paciente_id": novo_id,
        "data_cadastro": datetime.now().strftime("%Y-%m-%d"),
        "nome": str(dados.get("nome") or "").strip(),
        "data_nascimento": data_nascimento,
        "idade": idade,
        "sexo": str(dados.get("sexo") or "Não informado").strip(),
        "telefone": str(dados.get("telefone") or "").strip(),
        "email": str(dados.get("email") or "").strip(),
        "profissao": str(dados.get("profissao") or "").strip(),
        "horario_trabalho": str(dados.get("horario_trabalho") or "").strip(),
        "observacoes": str(dados.get("observacoes") or "").strip(),
    }

    precisa_header = (not caminho.exists()) or caminho.stat().st_size == 0

    with caminho.open("a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=colunas)

        if precisa_header:
            writer.writeheader()

        writer.writerow({c: row.get(c, "") for c in colunas})

    globals()["PACIENTE_SELECIONADO_ID"] = novo_id

    try:
        atualizar_pacientes_csv_real_definitivo()
    except Exception as exc:
        print(f"[NOVO PACIENTE] Paciente salvo, mas falhou atualização de memória: {exc}")

    return novo_id


def abrir_popup_novo_paciente_data_flet(page, atualizar_lista_callback=None):
    nome = ft.TextField(label="Nome completo", width=520, border_radius=12)
    nascimento = ft.TextField(label="Data de nascimento", hint_text="dd/mm/aaaa", width=180, border_radius=12)
    sexo = ft.Dropdown(
        label="Sexo",
        width=180,
        value="Não informado",
        border_radius=12,
        options=[
            ft.dropdown.Option("Não informado"),
            ft.dropdown.Option("Masculino"),
            ft.dropdown.Option("Feminino"),
            ft.dropdown.Option("Outro"),
        ],
    )
    telefone = ft.TextField(label="Telefone", width=220, border_radius=12)
    email = ft.TextField(label="E-mail", width=300, border_radius=12)
    profissao = ft.TextField(label="Profissão", width=300, border_radius=12)
    horario = ft.TextField(label="Horário de trabalho", width=220, border_radius=12)
    observacoes = ft.TextField(label="Observações", width=700, multiline=True, min_lines=3, max_lines=5, border_radius=12)

    erro_text = ft.Text("", size=12, color="#DC2626")

    def fechar(e=None):
        dialog.open = False
        page.update()

    def salvar(e=None):
        if not str(nome.value or "").strip():
            erro_text.value = "Informe o nome completo do paciente."
            page.update()
            return

        try:
            novo_id = _np_salvar_paciente_csv({
                "nome": nome.value,
                "data_nascimento": nascimento.value,
                "sexo": sexo.value,
                "telefone": telefone.value,
                "email": email.value,
                "profissao": profissao.value,
                "horario_trabalho": horario.value,
                "observacoes": observacoes.value,
            })

            dialog.open = False

            if atualizar_lista_callback:
                try:
                    atualizar_lista_callback()
                except Exception as exc:
                    print(f"[NOVO PACIENTE] Falha ao atualizar lista: {exc}")

            _np_mostrar_msg(page, f"Paciente cadastrado com sucesso: {novo_id}", "#16A34A")
            page.update()

        except Exception as exc:
            erro_text.value = f"Erro ao salvar paciente: {exc}"
            print(f"[NOVO PACIENTE] Erro ao salvar paciente: {exc}")
            page.update()

    conteudo = ft.Container(
        width=760,
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Text(
                    "Cadastre os dados básicos do paciente. Depois, complemente com Anamnese, Recordatório, Antropometria e Exames.",
                    size=13,
                    color="#64748B",
                ),
                nome,
                ft.Row(spacing=10, controls=[nascimento, sexo, telefone]),
                ft.Row(spacing=10, controls=[email, profissao]),
                horario,
                observacoes,
                erro_text,
            ],
        ),
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Adicionar Novo Paciente", weight=ft.FontWeight.BOLD),
        content=conteudo,
        actions=[
            ft.TextButton(content=ft.Text("Cancelar"), on_click=fechar),
            ft.TextButton(content=ft.Text("Salvar Paciente"), on_click=salvar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()


# Guarda a tela original e cria uma tela Pacientes com botão funcional.
try:
    _pacientes_view_original_data_flet
except NameError:
    _pacientes_view_original_data_flet = pacientes_view


def pacientes_view(on_abrir=None):
    body_container = ft.Container(
        expand=True,
        content=_pacientes_view_original_data_flet(on_abrir=on_abrir),
    )

    def atualizar_lista():
        try:
            atualizar_pacientes_csv_real_definitivo()
        except Exception as exc:
            print(f"[NOVO PACIENTE] Falha ao atualizar pacientes: {exc}")

        body_container.content = _pacientes_view_original_data_flet(on_abrir=on_abrir)

    def abrir(e=None):
        page = None

        try:
            page = e.page
        except Exception:
            pass

        if page is None:
            try:
                page = e.control.page
            except Exception:
                pass

        if page is None:
            print("[NOVO PACIENTE] Não foi possível obter page no evento.")
            return

        abrir_popup_novo_paciente_data_flet(page, atualizar_lista_callback=atualizar_lista)

    barra = ft.Container(
        bgcolor="#F8FAFC",
        border_radius=16,
        padding=14,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text("Pacientes", size=24, weight=ft.FontWeight.BOLD, color="#111827"),
                        ft.Text("Cadastre novos pacientes e acompanhe os registros existentes.", size=13, color="#64748B"),
                    ],
                ),
                ft.ElevatedButton(
                    content=ft.Text("Adicionar Novo Paciente"),
                    on_click=abrir,
                    style=ft.ButtonStyle(
                        bgcolor=globals().get("COR_PRIMARIA", "#2563EB"),
                        color="#FFFFFF",
                        shape=ft.RoundedRectangleBorder(radius=12),
                    ),
                ),
            ],
        ),
    )

    return ft.Column(
        expand=True,
        spacing=16,
        controls=[
            barra,
            body_container,
        ],
    )







# ============================================================
# CORREÇÃO FINAL - MANTER BOTÃO FUNCIONAL E OCULTAR BOTÃO RUIM
# ============================================================

def _np3_texto_controle(ctrl):
    textos = []

    for attr in ("text", "value", "label", "tooltip"):
        try:
            v = getattr(ctrl, attr, None)
            if isinstance(v, str) and v.strip():
                textos.append(v.strip())
        except Exception:
            pass

    try:
        content = getattr(ctrl, "content", None)
        if content is not None:
            textos.append(_np3_texto_controle(content))
    except Exception:
        pass

    try:
        controls = getattr(ctrl, "controls", None)
        if controls:
            for c in controls:
                textos.append(_np3_texto_controle(c))
    except Exception:
        pass

    return " ".join([t for t in textos if t])


def _np3_eh_botao(ctrl):
    nome_classe = ctrl.__class__.__name__.lower()

    if "button" in nome_classe:
        return True

    # fallback para controles clicáveis
    try:
        return hasattr(ctrl, "on_click")
    except Exception:
        return False


def _np3_ocultar_botao_original_novo_paciente(root):
    """
    Oculta apenas o botão antigo da tela original.
    Não oculta containers/rows/columns para não quebrar o layout.
    """

    visitados = set()

    def walk(ctrl):
        if ctrl is None:
            return

        cid = id(ctrl)
        if cid in visitados:
            return
        visitados.add(cid)

        texto = _np3_texto_controle(ctrl).lower()

        if _np3_eh_botao(ctrl) and (
            "novo paciente" in texto
            or "adicionar novo paciente" in texto
            or "adicionar paciente" in texto
        ):
            try:
                ctrl.visible = False
            except Exception:
                pass
            return

        try:
            content = getattr(ctrl, "content", None)
            if content is not None:
                walk(content)
        except Exception:
            pass

        try:
            controls = getattr(ctrl, "controls", None)
            if controls:
                for c in controls:
                    walk(c)
        except Exception:
            pass

    walk(root)
    return root


def pacientes_view(on_abrir=None):
    """
    Tela Pacientes definitiva:
    - Usa a tela original de pacientes.
    - Oculta o botão antigo que não funcionava.
    - Adiciona no topo o botão funcional que abre o popup correto.
    """

    try:
        atualizar_pacientes_csv_real_definitivo()
    except Exception as exc:
        print(f"[NOVO PACIENTE] Falha ao atualizar pacientes: {exc}")

    body_container = ft.Container(expand=True)

    def montar_corpo():
        tela = _pacientes_view_original_data_flet(on_abrir=on_abrir)
        _np3_ocultar_botao_original_novo_paciente(tela)
        return tela

    def atualizar_lista():
        try:
            atualizar_pacientes_csv_real_definitivo()
        except Exception as exc:
            print(f"[NOVO PACIENTE] Falha ao atualizar lista: {exc}")

        body_container.content = montar_corpo()

    def abrir(e=None):
        page = None

        try:
            page = e.page
        except Exception:
            pass

        if page is None:
            try:
                page = e.control.page
            except Exception:
                pass

        if page is None:
            try:
                page = body_container.page
            except Exception:
                pass

        if page is None:
            print("[NOVO PACIENTE] Não foi possível obter page no clique.")
            return

        abrir_popup_novo_paciente_data_flet(
            page,
            atualizar_lista_callback=atualizar_lista,
        )

    body_container.content = montar_corpo()

    barra_funcional = ft.Container(
        bgcolor="#F8FAFC",
        border_radius=16,
        padding=14,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text("Pacientes", size=24, weight=ft.FontWeight.BOLD, color="#111827"),
                        ft.Text("Cadastre novos pacientes e acompanhe os registros existentes.", size=13, color="#64748B"),
                    ],
                ),
                ft.ElevatedButton(
                    content=ft.Text("Adicionar Novo Paciente"),
                    on_click=abrir,
                    style=ft.ButtonStyle(
                        bgcolor=globals().get("COR_PRIMARIA", "#2563EB"),
                        color="#FFFFFF",
                        shape=ft.RoundedRectangleBorder(radius=12),
                    ),
                ),
            ],
        ),
    )

    return ft.Column(
        expand=True,
        spacing=16,
        controls=[
            barra_funcional,
            body_container,
        ],
    )




# ============================================================
# PATCH FINAL - REMOVER CARD REPETIDO DA TELA PACIENTES
# ============================================================

def _np5_texto_controle(ctrl):
    textos = []

    for attr in ("text", "value", "label", "tooltip"):
        try:
            v = getattr(ctrl, attr, None)
            if isinstance(v, str) and v.strip():
                textos.append(v.strip())
        except Exception:
            pass

    try:
        content = getattr(ctrl, "content", None)
        if content is not None:
            textos.append(_np5_texto_controle(content))
    except Exception:
        pass

    try:
        controls = getattr(ctrl, "controls", None)
        if controls:
            for c in controls:
                textos.append(_np5_texto_controle(c))
    except Exception:
        pass

    return " ".join([t for t in textos if t])


def _np5_eh_card_repetido_pacientes(ctrl):
    texto = _np5_texto_controle(ctrl).lower()

    # Este é o card original repetido:
    # "Pacientes" + "Visão geral dos pacientes cadastrados..." + "Novo paciente"
    if "visão geral dos pacientes cadastrados" in texto:
        return True

    if "visao geral dos pacientes cadastrados" in texto:
        return True

    if "dados carregados da base própria flet" in texto:
        return False

    return False


def _np5_remover_card_repetido_pacientes(root):
    """
    Remove o card interno repetido da tela original de pacientes,
    preservando cards de resumo e lista de pacientes.
    """

    visitados = set()

    def walk(ctrl):
        if ctrl is None:
            return ctrl

        cid = id(ctrl)
        if cid in visitados:
            return ctrl

        visitados.add(cid)

        try:
            content = getattr(ctrl, "content", None)
            if content is not None:
                if _np5_eh_card_repetido_pacientes(content):
                    ctrl.content = ft.Container(width=0, height=0, visible=False)
                else:
                    walk(content)
        except Exception:
            pass

        try:
            controls = getattr(ctrl, "controls", None)

            if controls:
                novos = []

                for c in list(controls):
                    if _np5_eh_card_repetido_pacientes(c):
                        continue

                    walk(c)
                    novos.append(c)

                ctrl.controls = novos
        except Exception:
            pass

        return ctrl

    return walk(root)


def pacientes_view(on_abrir=None):
    """
    Tela Pacientes definitiva:
    - Mantém apenas o cabeçalho funcional com "Adicionar Novo Paciente".
    - Remove o card repetido interno da tela original.
    - Mantém cards de resumo e lista de pacientes.
    """

    try:
        atualizar_pacientes_csv_real_definitivo()
    except Exception as exc:
        print(f"[PACIENTES] Falha ao atualizar pacientes: {exc}")

    body_container = ft.Container(expand=True)

    def montar_corpo():
        tela = _pacientes_view_original_data_flet(on_abrir=on_abrir)
        tela = _np5_remover_card_repetido_pacientes(tela)
        return tela

    def atualizar_lista():
        try:
            atualizar_pacientes_csv_real_definitivo()
        except Exception as exc:
            print(f"[PACIENTES] Falha ao atualizar lista: {exc}")

        body_container.content = montar_corpo()

    def abrir(e=None):
        page = None

        try:
            page = e.page
        except Exception:
            pass

        if page is None:
            try:
                page = e.control.page
            except Exception:
                pass

        if page is None:
            try:
                page = body_container.page
            except Exception:
                pass

        if page is None:
            print("[NOVO PACIENTE] Não foi possível obter page no clique.")
            return

        abrir_popup_novo_paciente_data_flet(
            page,
            atualizar_lista_callback=atualizar_lista,
        )

    body_container.content = montar_corpo()

    barra_funcional = ft.Container(
        bgcolor="#F8FAFC",
        border_radius=16,
        padding=14,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text("Pacientes", size=24, weight=ft.FontWeight.BOLD, color="#111827"),
                        ft.Text("Cadastre novos pacientes e acompanhe os registros existentes.", size=13, color="#64748B"),
                    ],
                ),
                ft.ElevatedButton(
                    content=ft.Text("Adicionar Novo Paciente"),
                    on_click=abrir,
                    style=ft.ButtonStyle(
                        bgcolor=globals().get("COR_PRIMARIA", "#2563EB"),
                        color="#FFFFFF",
                        shape=ft.RoundedRectangleBorder(radius=12),
                    ),
                ),
            ],
        ),
    )

    return ft.Column(
        expand=True,
        spacing=16,
        controls=[
            barra_funcional,
            body_container,
        ],
    )




# ============================================================
# PATCH - EDIÇÃO DE ANAMNESE / RECORDATÓRIO / ANTROPOMETRIA
# ============================================================

def _ed_csv_path(nome):
    if "caminho_csv_flet" in globals():
        return caminho_csv_flet(nome)
    return Path(__file__).resolve().parent / "data_flet" / nome


def _ed_schema(nome):
    try:
        colunas = CSV_SCHEMA_FLET.get(nome)
        if colunas:
            return list(colunas)
    except Exception:
        pass

    fallback = {
        "anamnese.csv": [
            "paciente_id", "data_anamnese", "queixa_principal", "historia_doenca_atual",
            "sintomas", "historia_patologica_pregressa", "historia_familiar",
            "numero_filhos_idades", "amamentou", "atividade_fisica",
            "horario_atividade_fisica", "consumo_alcool", "tabagismo",
            "qualidade_sono", "hora_acordar", "hora_dormir", "comportamento_peso",
            "disposicao_fisica", "funcionamento_intestinal", "funcionamento_urinario",
            "internacoes_cirurgias", "medicamentos_suplementos",
            "intolerancia_alergia_alimentar", "denticao", "mastigacao",
            "quem_cozinha", "apetite", "horario_mais_fome", "ingestao_agua_dia",
            "tratamento_nutricional_anterior", "objetivo_nutricional",
            "alimentos_preferidos", "habito_beliscar", "alimentos_que_nao_gosta",
            "habitos_fim_de_semana", "dificuldades_adesao",
        ],
        "recordatorio_habitual.csv": [
            "paciente_id", "data_registro", "desjejum", "lanche_manha", "almoco",
            "lanche_tarde", "jantar", "ceia", "observacoes",
        ],
        "antropometria.csv": [
            "paciente_id", "data_avaliacao", "tipo_avaliacao", "objetivo_antropometrico",
            "condicao_medicao", "tipo_balanca", "roupa_medicao", "local_cintura",
            "peso", "altura", "circunferencia_cintura", "imc", "classificacao_imc",
            "risco_cintura", "observacoes",
        ],
    }

    return fallback.get(nome, [])


def _ed_ler_csv(nome):
    import csv

    caminho = _ed_csv_path(nome)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    if not caminho.exists():
        return []

    try:
        with caminho.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    except Exception as exc:
        print(f"[EDIÇÃO NUTRICIONAL] Erro ao ler {nome}: {exc}")
        return []


def _ed_escrever_csv(nome, rows):
    import csv

    caminho = _ed_csv_path(nome)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    colunas = _ed_schema(nome)

    if not colunas and rows:
        colunas = list(rows[0].keys())

    with caminho.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=colunas)
        writer.writeheader()

        for row in rows:
            writer.writerow({c: row.get(c, "") for c in colunas})


def _ed_pacientes():
    pacientes = []

    try:
        atualizar_pacientes_csv_real_definitivo()
    except Exception:
        pass

    try:
        for p in PACIENTES_MOCK:
            pacientes.append({
                "id": str(p.get("id") or p.get("paciente_id") or "").strip(),
                "nome": str(p.get("nome") or "").strip(),
            })
    except Exception:
        pass

    if pacientes:
        return [p for p in pacientes if p["id"] and p["nome"]]

    rows = _ed_ler_csv("pacientes.csv")
    for row in rows:
        pacientes.append({
            "id": str(row.get("paciente_id") or "").strip(),
            "nome": str(row.get("nome") or "").strip(),
        })

    return [p for p in pacientes if p["id"] and p["nome"]]


def _ed_nome_paciente(paciente_id):
    paciente_id = str(paciente_id or "").strip()

    for p in _ed_pacientes():
        if str(p.get("id")) == paciente_id:
            return p.get("nome") or paciente_id

    return paciente_id


def _ed_paciente_atual():
    atual = str(globals().get("PACIENTE_SELECIONADO_ID", "") or "").strip()

    if atual:
        return atual

    pacientes = _ed_pacientes()
    if pacientes:
        return str(pacientes[0]["id"])

    return ""


def _ed_label(campo):
    labels = {
        "data_anamnese": "Data da anamnese",
        "queixa_principal": "Queixa principal",
        "historia_doenca_atual": "História da doença atual",
        "sintomas": "Sintomas",
        "historia_patologica_pregressa": "História patológica pregressa",
        "historia_familiar": "História familiar",
        "numero_filhos_idades": "Número de filhos / idades",
        "amamentou": "Amamentou",
        "atividade_fisica": "Atividade física",
        "horario_atividade_fisica": "Horário da atividade física",
        "consumo_alcool": "Consumo de álcool",
        "tabagismo": "Tabagismo",
        "qualidade_sono": "Qualidade do sono",
        "hora_acordar": "Hora de acordar",
        "hora_dormir": "Hora de dormir",
        "comportamento_peso": "Comportamento do peso",
        "disposicao_fisica": "Disposição física",
        "funcionamento_intestinal": "Funcionamento intestinal",
        "funcionamento_urinario": "Funcionamento urinário",
        "internacoes_cirurgias": "Internações / cirurgias",
        "medicamentos_suplementos": "Medicamentos / suplementos",
        "intolerancia_alergia_alimentar": "Intolerância / alergia alimentar",
        "denticao": "Dentição",
        "mastigacao": "Mastigação",
        "quem_cozinha": "Quem cozinha",
        "apetite": "Apetite",
        "horario_mais_fome": "Horário de mais fome",
        "ingestao_agua_dia": "Ingestão de água por dia",
        "tratamento_nutricional_anterior": "Tratamento nutricional anterior",
        "objetivo_nutricional": "Objetivo nutricional",
        "alimentos_preferidos": "Alimentos preferidos",
        "habito_beliscar": "Hábito de beliscar",
        "alimentos_que_nao_gosta": "Alimentos que não gosta",
        "habitos_fim_de_semana": "Hábitos de fim de semana",
        "dificuldades_adesao": "Dificuldades de adesão",

        "data_registro": "Data do registro",
        "desjejum": "Desjejum",
        "lanche_manha": "Lanche da manhã",
        "almoco": "Almoço",
        "lanche_tarde": "Lanche da tarde",
        "jantar": "Jantar",
        "ceia": "Ceia",

        "data_avaliacao": "Data da avaliação",
        "tipo_avaliacao": "Tipo de avaliação",
        "objetivo_antropometrico": "Objetivo antropométrico",
        "condicao_medicao": "Condição da medição",
        "tipo_balanca": "Tipo de balança",
        "roupa_medicao": "Roupa na medição",
        "local_cintura": "Local da cintura",
        "peso": "Peso",
        "altura": "Altura",
        "circunferencia_cintura": "Circunferência da cintura",
        "imc": "IMC",
        "classificacao_imc": "Classificação do IMC",
        "risco_cintura": "Risco pela cintura",
        "observacoes": "Observações",
    }

    return labels.get(campo, campo.replace("_", " ").capitalize())


def _ed_data_br(valor):
    valor = str(valor or "").strip()

    if not valor:
        return "-"

    partes = valor.split("-")
    if len(partes) == 3 and len(partes[0]) == 4:
        return f"{partes[2]}/{partes[1]}/{partes[0]}"

    return valor


def _ed_num(valor):
    try:
        return float(str(valor or "").replace(",", "."))
    except Exception:
        return 0.0


def _ed_recalcular_antropometria(row):
    peso = _ed_num(row.get("peso"))
    altura = _ed_num(row.get("altura"))
    cintura = _ed_num(row.get("circunferencia_cintura"))

    if altura > 3:
        altura = altura / 100.0

    if peso > 0 and altura > 0:
        imc = peso / (altura * altura)
        row["imc"] = f"{imc:.2f}"

        if imc < 18.5:
            row["classificacao_imc"] = "Baixo peso"
        elif imc < 25:
            row["classificacao_imc"] = "Eutrofia"
        elif imc < 30:
            row["classificacao_imc"] = "Sobrepeso"
        elif imc < 35:
            row["classificacao_imc"] = "Obesidade grau I"
        elif imc < 40:
            row["classificacao_imc"] = "Obesidade grau II"
        else:
            row["classificacao_imc"] = "Obesidade grau III"

    paciente_id = str(row.get("paciente_id") or "").strip()
    sexo = ""

    for p in _ed_ler_csv("pacientes.csv"):
        if str(p.get("paciente_id") or "").strip() == paciente_id:
            sexo = str(p.get("sexo") or "").lower()
            break

    if cintura > 0:
        if "masc" in sexo:
            if cintura >= 102:
                row["risco_cintura"] = "Risco elevado"
            elif cintura >= 94:
                row["risco_cintura"] = "Risco moderado"
            else:
                row["risco_cintura"] = "Sem risco aumentado"
        elif "fem" in sexo:
            if cintura >= 88:
                row["risco_cintura"] = "Risco elevado"
            elif cintura >= 80:
                row["risco_cintura"] = "Risco moderado"
            else:
                row["risco_cintura"] = "Sem risco aumentado"
        else:
            if cintura >= 94:
                row["risco_cintura"] = "Risco aumentado"
            else:
                row["risco_cintura"] = "Sem risco aumentado"

    return row


def _ed_snackbar(page, msg, cor="#16A34A"):
    try:
        if "mostrar_snackbar" in globals():
            mostrar_snackbar(page, msg, cor)
            return
    except Exception:
        pass

    try:
        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()
    except Exception:
        print(msg)




def _ed_id_norm(valor):
    valor = str(valor or "").strip()

    if not valor:
        return ""

    # Remove espaços, pontos e traços acidentais
    valor = valor.replace(".", "").replace("-", "").replace(" ", "")

    # Se for numérico, compara tanto sem zeros quanto com zeros
    try:
        return str(int(valor))
    except Exception:
        return valor


def _ed_id_equiv(a, b):
    a_raw = str(a or "").strip()
    b_raw = str(b or "").strip()

    if a_raw == b_raw:
        return True

    return _ed_id_norm(a_raw) == _ed_id_norm(b_raw)


def _ed_debug_registros(nome_csv, paciente_id):
    try:
        rows = _ed_ler_csv(nome_csv)
        print(f"[EDIÇÃO NUTRICIONAL] CSV={nome_csv} | paciente selecionado={paciente_id}")
        print(f"[EDIÇÃO NUTRICIONAL] Total de registros no CSV: {len(rows)}")
        print("[EDIÇÃO NUTRICIONAL] Pacientes encontrados no CSV:",
              sorted(set(str(r.get("paciente_id", "")).strip() for r in rows)))
    except Exception as exc:
        print(f"[EDIÇÃO NUTRICIONAL] Falha no debug de registros: {exc}")

def abrir_popup_edicao_registro_nutricional(page, titulo, nome_csv, data_coluna, recalcular=None):
    rows = _ed_ler_csv(nome_csv)
    colunas = _ed_schema(nome_csv)

    pacientes = _ed_pacientes()
    paciente_atual = _ed_paciente_atual()

    paciente_dd = ft.Dropdown(
        label="Paciente",
        width=420,
        value=paciente_atual,
        border_radius=12,
        options=[
            ft.dropdown.Option(key=str(p["id"]), text=p["nome"])
            for p in pacientes
        ],
    )

    registro_dd = ft.Dropdown(
        label="Registro",
        width=260,
        border_radius=12,
        options=[],
    )

    erro_txt = ft.Text("", size=12, color="#DC2626")

    campos_container = ft.Column(
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
    )

    campos = {}

    def indices_do_paciente():
        pid = str(paciente_dd.value or "").strip()

        indices = []
        for idx, row in enumerate(rows):
            if _ed_id_equiv(row.get("paciente_id"), pid):
                indices.append(idx)

        return indices

    def montar_opcoes_registro():
        indices = indices_do_paciente()
        options = []

        if not indices:
            _ed_debug_registros(nome_csv, paciente_dd.value)

        for idx in indices:
            row = rows[idx]
            data = row.get(data_coluna, "")
            texto = f"{_ed_data_br(data)}"

            if nome_csv == "antropometria.csv":
                tipo = row.get("tipo_avaliacao", "")
                if tipo:
                    texto += f" • {tipo}"

            options.append(ft.dropdown.Option(key=str(idx), text=texto))

        registro_dd.options = options
        registro_dd.value = options[-1].key if options else None

    def criar_campo(campo, valor):
        label = _ed_label(campo)

        multiline = campo in [
            "queixa_principal", "historia_doenca_atual", "sintomas",
            "historia_patologica_pregressa", "historia_familiar",
            "internacoes_cirurgias", "medicamentos_suplementos",
            "intolerancia_alergia_alimentar", "objetivo_nutricional",
            "alimentos_preferidos", "alimentos_que_nao_gosta",
            "habitos_fim_de_semana", "dificuldades_adesao",
            "desjejum", "lanche_manha", "almoco", "lanche_tarde",
            "jantar", "ceia", "observacoes",
        ]

        width = 700 if multiline else 330

        return ft.TextField(
            label=label,
            value=str(valor or ""),
            width=width,
            multiline=multiline,
            min_lines=3 if multiline else 1,
            max_lines=6 if multiline else 1,
            border_radius=12,
        )

    def carregar_campos():
        campos.clear()
        campos_container.controls.clear()

        if registro_dd.value is None:
            campos_container.controls.append(
                ft.Container(
                    bgcolor="#FEF2F2",
                    border_radius=12,
                    padding=12,
                    content=ft.Text(
                        f"Nenhum registro de {titulo.lower()} encontrado para este paciente. Verifique se há ficha salva para este paciente ou se o ID está vinculado corretamente.",
                        size=13,
                        color="#991B1B",
                    ),
                )
            )
            return

        idx = int(registro_dd.value)
        row = rows[idx]

        campos_container.controls.append(
            ft.Container(
                bgcolor="#EFF6FF",
                border_radius=12,
                padding=12,
                content=ft.Text(
                    f"Editando registro de {_ed_nome_paciente(row.get('paciente_id'))}.",
                    size=13,
                    color="#1D4ED8",
                    weight=ft.FontWeight.BOLD,
                ),
            )
        )

        linha_atual = []
        for campo in colunas:
            if campo == "paciente_id":
                continue

            controle = criar_campo(campo, row.get(campo, ""))
            campos[campo] = controle
            linha_atual.append(controle)

            if len(linha_atual) == 2:
                campos_container.controls.append(
                    ft.Row(spacing=10, wrap=True, controls=linha_atual)
                )
                linha_atual = []

        if linha_atual:
            campos_container.controls.append(
                ft.Row(spacing=10, wrap=True, controls=linha_atual)
            )

    def trocar_paciente(e=None):
        montar_opcoes_registro()
        carregar_campos()
        page.update()

    def trocar_registro(e=None):
        carregar_campos()
        page.update()

    paciente_dd.on_change = trocar_paciente
    registro_dd.on_change = trocar_registro

    def fechar(e=None):
        dialog.open = False
        page.update()

    def salvar(e=None):
        if registro_dd.value is None:
            erro_txt.value = "Não há registro selecionado para salvar."
            page.update()
            return

        try:
            idx = int(registro_dd.value)

            if idx < 0 or idx >= len(rows):
                erro_txt.value = "Registro inválido."
                page.update()
                return

            row = dict(rows[idx])
            row["paciente_id"] = str(paciente_dd.value or row.get("paciente_id") or "").strip()

            for campo, controle in campos.items():
                row[campo] = str(controle.value or "").strip()

            if recalcular:
                row = recalcular(row)

            rows[idx] = row
            _ed_escrever_csv(nome_csv, rows)

            try:
                if "carregar_dados_nutricionais_data_flet_para_memoria" in globals():
                    carregar_dados_nutricionais_data_flet_para_memoria()
            except Exception as exc:
                print(f"[EDIÇÃO NUTRICIONAL] Falha ao recarregar memória nutricional: {exc}")

            dialog.open = False
            _ed_snackbar(page, f"{titulo} atualizado com sucesso.", "#16A34A")
            page.update()

        except Exception as exc:
            erro_txt.value = f"Erro ao salvar: {exc}"
            print(f"[EDIÇÃO NUTRICIONAL] Erro ao salvar {titulo}: {exc}")
            page.update()

    montar_opcoes_registro()
    carregar_campos()

    conteudo = ft.Container(
        width=820,
        height=680,
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Text(
                    f"Selecione o paciente e o registro para editar a ficha de {titulo.lower()}.",
                    size=13,
                    color="#64748B",
                ),
                ft.Container(
                    bgcolor="#F8FAFC",
                    border_radius=14,
                    padding=12,
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            paciente_dd,
                            registro_dd,
                        ],
                    ),
                ),
                ft.Container(
                    expand=True,
                    bgcolor="#F3F4F6",
                    border_radius=14,
                    padding=12,
                    content=campos_container,
                ),
                erro_txt,
            ],
        ),
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(f"Editar {titulo}", weight=ft.FontWeight.BOLD),
        content=conteudo,
        actions=[
            ft.TextButton(content=ft.Text("Cancelar"), on_click=fechar),
            ft.TextButton(content=ft.Text("Salvar alterações"), on_click=salvar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()


def _ed_extrair_page_evento(e, fallback=None):
    try:
        if e and e.page:
            return e.page
    except Exception:
        pass

    try:
        if e and e.control and e.control.page:
            return e.control.page
    except Exception:
        pass

    try:
        if fallback and fallback.page:
            return fallback.page
    except Exception:
        pass

    return None


def _ed_wrapper_view(titulo, original_content, nome_csv, data_coluna, recalcular=None):
    container = ft.Container(expand=True, content=original_content)

    def abrir(e=None):
        page = _ed_extrair_page_evento(e, container)

        if page is None:
            print(f"[EDIÇÃO NUTRICIONAL] Não foi possível obter page para editar {titulo}.")
            return

        abrir_popup_edicao_registro_nutricional(
            page,
            titulo=titulo,
            nome_csv=nome_csv,
            data_coluna=data_coluna,
            recalcular=recalcular,
        )

    barra = ft.Container(
        bgcolor="#F8FAFC",
        border_radius=16,
        padding=14,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text(f"Edição de {titulo}", size=20, weight=ft.FontWeight.BOLD, color="#111827"),
                        ft.Text("Edite registros já cadastrados sem criar uma nova ficha.", size=13, color="#64748B"),
                    ],
                ),
                ft.ElevatedButton(
                    content=ft.Text(f"Editar {titulo}"),
                    on_click=abrir,
                    style=ft.ButtonStyle(
                        bgcolor=globals().get("COR_PRIMARIA", "#2563EB"),
                        color="#FFFFFF",
                        shape=ft.RoundedRectangleBorder(radius=12),
                    ),
                ),
            ],
        ),
    )

    return ft.Column(
        expand=True,
        spacing=16,
        controls=[
            barra,
            container,
        ],
    )


# Guarda funções originais e aplica wrappers.
if "anamnese_view" in globals():
    try:
        _ed_anamnese_view_original
    except NameError:
        _ed_anamnese_view_original = anamnese_view

    def anamnese_view(*args, **kwargs):
        original = _ed_anamnese_view_original(*args, **kwargs)
        return _ed_wrapper_view(
            "Anamnese",
            original,
            "anamnese.csv",
            "data_anamnese",
            recalcular=None,
        )


if "recordatorio_view" in globals():
    try:
        _ed_recordatorio_view_original
    except NameError:
        _ed_recordatorio_view_original = recordatorio_view

    def recordatorio_view(*args, **kwargs):
        original = _ed_recordatorio_view_original(*args, **kwargs)
        return _ed_wrapper_view(
            "Recordatório",
            original,
            "recordatorio_habitual.csv",
            "data_registro",
            recalcular=None,
        )


if "antropometria_view" in globals():
    try:
        _ed_antropometria_view_original
    except NameError:
        _ed_antropometria_view_original = antropometria_view

    def antropometria_view(*args, **kwargs):
        original = _ed_antropometria_view_original(*args, **kwargs)
        return _ed_wrapper_view(
            "Antropometria",
            original,
            "antropometria.csv",
            "data_avaliacao",
            recalcular=_ed_recalcular_antropometria,
        )




# ============================================================
# PATCH V2 - FORÇAR CARREGAMENTO DOS REGISTROS NUTRICIONAIS
# ============================================================

def _edv2_id_norm(valor):
    valor = str(valor or "").strip()

    if not valor:
        return ""

    valor = valor.replace(".", "").replace("-", "").replace(" ", "")

    try:
        return str(int(valor))
    except Exception:
        return valor


def _edv2_id_equiv(a, b):
    a = str(a or "").strip()
    b = str(b or "").strip()

    if a == b:
        return True

    return _edv2_id_norm(a) == _edv2_id_norm(b)


def _edv2_colunas_reais(nome_csv, rows):
    colunas = []

    try:
        colunas = list(_ed_schema(nome_csv))
    except Exception:
        colunas = []

    for row in rows:
        for k in row.keys():
            if k not in colunas:
                colunas.append(k)

    return colunas


def abrir_popup_edicao_registro_nutricional(page, titulo, nome_csv, data_coluna, recalcular=None):
    rows = _ed_ler_csv(nome_csv)
    colunas = _edv2_colunas_reais(nome_csv, rows)

    pacientes = _ed_pacientes()
    paciente_atual = _ed_paciente_atual()

    if not paciente_atual and pacientes:
        paciente_atual = str(pacientes[0]["id"])

    paciente_dd = ft.Dropdown(
        label="Paciente",
        width=420,
        value=paciente_atual,
        border_radius=12,
        options=[
            ft.dropdown.Option(key=str(p["id"]), text=p["nome"])
            for p in pacientes
        ],
    )

    registro_dd = ft.Dropdown(
        label="Registro",
        width=330,
        border_radius=12,
        options=[],
    )

    aviso_txt = ft.Text("", size=12, color="#B45309")
    erro_txt = ft.Text("", size=12, color="#DC2626")

    campos_container = ft.Column(
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
    )

    campos = {}
    indices_visiveis = []

    def nome_paciente_registro(row):
        pid = str(row.get("paciente_id") or "").strip()

        try:
            nome = _ed_nome_paciente(pid)
            if nome and nome != pid:
                return nome
        except Exception:
            pass

        return f"Paciente {pid}" if pid else "Paciente não informado"

    def indices_do_paciente():
        pid = str(paciente_dd.value or "").strip()

        encontrados = []

        for idx, row in enumerate(rows):
            if _edv2_id_equiv(row.get("paciente_id"), pid):
                encontrados.append(idx)

        # Fallback importante:
        # Se não encontrou pelo paciente selecionado, mas existe registro no CSV,
        # mostra todos os registros para não bloquear a edição.
        if not encontrados and rows:
            return list(range(len(rows))), True

        return encontrados, False

    def montar_opcoes_registro():
        nonlocal indices_visiveis

        indices, fallback = indices_do_paciente()
        indices_visiveis = indices

        options = []

        for idx in indices:
            row = rows[idx]
            data = row.get(data_coluna, "")
            texto = _ed_data_br(data)

            if fallback:
                texto += f" • {nome_paciente_registro(row)}"

            if nome_csv == "antropometria.csv":
                tipo = row.get("tipo_avaliacao", "")
                if tipo:
                    texto += f" • {tipo}"

            options.append(
                ft.dropdown.Option(
                    key=str(idx),
                    text=texto,
                )
            )

        registro_dd.options = options
        registro_dd.value = options[-1].key if options else None

        if fallback and rows:
            aviso_txt.value = (
                "O registro não foi localizado pelo ID do paciente selecionado. "
                "Listei os registros disponíveis para permitir a edição."
            )
        else:
            aviso_txt.value = ""

    def criar_campo(campo, valor):
        label = _ed_label(campo)

        multiline = campo in [
            "queixa_principal", "historia_doenca_atual", "sintomas",
            "historia_patologica_pregressa", "historia_familiar",
            "internacoes_cirurgias", "medicamentos_suplementos",
            "intolerancia_alergia_alimentar", "objetivo_nutricional",
            "alimentos_preferidos", "alimentos_que_nao_gosta",
            "habitos_fim_de_semana", "dificuldades_adesao",
            "desjejum", "lanche_manha", "almoco", "lanche_tarde",
            "jantar", "ceia", "observacoes",
        ]

        return ft.TextField(
            label=label,
            value=str(valor or ""),
            width=700 if multiline else 335,
            multiline=multiline,
            min_lines=3 if multiline else 1,
            max_lines=7 if multiline else 1,
            border_radius=12,
        )

    def carregar_campos():
        campos.clear()
        campos_container.controls.clear()

        if not rows:
            campos_container.controls.append(
                ft.Container(
                    bgcolor="#FEF2F2",
                    border_radius=12,
                    padding=12,
                    content=ft.Text(
                        f"Nenhum registro encontrado no arquivo {nome_csv}.",
                        size=13,
                        color="#991B1B",
                    ),
                )
            )
            return

        if registro_dd.value is None:
            campos_container.controls.append(
                ft.Container(
                    bgcolor="#FEF2F2",
                    border_radius=12,
                    padding=12,
                    content=ft.Text(
                        f"Nenhum registro de {titulo.lower()} disponível para edição.",
                        size=13,
                        color="#991B1B",
                    ),
                )
            )
            return

        idx = int(registro_dd.value)
        row = rows[idx]

        campos_container.controls.append(
            ft.Container(
                bgcolor="#EFF6FF",
                border_radius=12,
                padding=12,
                content=ft.Text(
                    f"Editando: {nome_paciente_registro(row)} • Registro: {_ed_data_br(row.get(data_coluna))}",
                    size=13,
                    color="#1D4ED8",
                    weight=ft.FontWeight.BOLD,
                ),
            )
        )

        linha = []

        for campo in colunas:
            if campo == "paciente_id":
                continue

            controle = criar_campo(campo, row.get(campo, ""))
            campos[campo] = controle
            linha.append(controle)

            if len(linha) == 2:
                campos_container.controls.append(
                    ft.Row(spacing=10, wrap=True, controls=linha)
                )
                linha = []

        if linha:
            campos_container.controls.append(
                ft.Row(spacing=10, wrap=True, controls=linha)
            )

    def trocar_paciente(e=None):
        montar_opcoes_registro()
        carregar_campos()
        page.update()

    def trocar_registro(e=None):
        carregar_campos()
        page.update()

    paciente_dd.on_change = trocar_paciente
    registro_dd.on_change = trocar_registro

    def fechar(e=None):
        dialog.open = False
        page.update()

    def salvar(e=None):
        if registro_dd.value is None:
            erro_txt.value = "Não há registro selecionado para salvar."
            page.update()
            return

        try:
            idx = int(registro_dd.value)

            if idx < 0 or idx >= len(rows):
                erro_txt.value = "Registro inválido."
                page.update()
                return

            row = dict(rows[idx])

            # Preserva o paciente_id original quando o registro foi carregado por fallback.
            if _edv2_id_equiv(row.get("paciente_id"), paciente_dd.value):
                row["paciente_id"] = str(paciente_dd.value or row.get("paciente_id") or "").strip()

            for campo, controle in campos.items():
                row[campo] = str(controle.value or "").strip()

            if recalcular:
                row = recalcular(row)

            rows[idx] = row
            _ed_escrever_csv(nome_csv, rows)

            try:
                if "carregar_dados_nutricionais_data_flet_para_memoria" in globals():
                    carregar_dados_nutricionais_data_flet_para_memoria()
            except Exception as exc:
                print(f"[EDIÇÃO NUTRICIONAL] Falha ao recarregar memória: {exc}")

            dialog.open = False
            _ed_snackbar(page, f"{titulo} atualizado com sucesso.", "#16A34A")
            page.update()

        except Exception as exc:
            erro_txt.value = f"Erro ao salvar: {exc}"
            print(f"[EDIÇÃO NUTRICIONAL] Erro ao salvar {titulo}: {exc}")
            page.update()

    montar_opcoes_registro()
    carregar_campos()

    conteudo = ft.Container(
        width=850,
        height=690,
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Text(
                    f"Selecione o paciente e o registro para editar a ficha de {titulo.lower()}.",
                    size=13,
                    color="#64748B",
                ),
                ft.Container(
                    bgcolor="#F8FAFC",
                    border_radius=14,
                    padding=12,
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            paciente_dd,
                            registro_dd,
                        ],
                    ),
                ),
                aviso_txt,
                ft.Container(
                    expand=True,
                    bgcolor="#F3F4F6",
                    border_radius=14,
                    padding=12,
                    content=campos_container,
                ),
                erro_txt,
            ],
        ),
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(f"Editar {titulo}", weight=ft.FontWeight.BOLD),
        content=conteudo,
        actions=[
            ft.TextButton(content=ft.Text("Cancelar"), on_click=fechar),
            ft.TextButton(content=ft.Text("Salvar alterações"), on_click=salvar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()




# ============================================================
# PATCH V3 - EDIÇÃO GUIADA COM DROPDOWNS E SELEÇÕES
# ============================================================

def _ed3_split_multi(valor):
    valor = str(valor or "").strip()

    if not valor or valor.lower() in ["não informado", "nao informado", "-"]:
        return []

    partes = []

    for pedaco in valor.replace("|", ";").split(";"):
        pedaco = pedaco.strip()
        if pedaco:
            partes.append(pedaco)

    return partes


def _ed3_join_multi(valores):
    valores = [str(v).strip() for v in valores if str(v).strip()]

    if not valores:
        return "Não informado"

    return "; ".join(valores)


def _ed3_option_list(lista, valor_atual=None):
    lista = list(lista or [])
    valor_atual = str(valor_atual or "").strip()

    if valor_atual and valor_atual not in lista and ";" not in valor_atual and "|" not in valor_atual:
        lista = [valor_atual] + lista

    vistos = set()
    saida = []

    for item in lista:
        item = str(item or "").strip()

        if not item or item in vistos:
            continue

        vistos.add(item)
        saida.append(ft.dropdown.Option(key=item, text=item))

    return saida


_ED3_SINGLE = {
    "amamentou": ["Não informado", "Sim", "Não", "Não se aplica"],
    "atividade_fisica": [
        "Não pratica", "Caminhada - 1x por semana", "Caminhada - 2 a 3x por semana",
        "Musculação - 1x por semana", "Musculação - 2 a 3x por semana",
        "Corrida", "Ciclismo", "Luta / Artes marciais - 1x por semana",
        "Luta / Artes marciais - 2 a 3x por semana", "Atleta / alta performance"
    ],
    "horario_atividade_fisica": ["Não informado", "Manhã", "Tarde", "Noite", "Variável"],
    "consumo_alcool": ["Não consome", "Socialmente", "Finais de semana", "Frequente", "Não informado"],
    "tabagismo": ["Não fumante", "Fumante", "Ex-fumante", "Não informado"],
    "qualidade_sono": ["Boa", "Regular", "Ruim", "Insônia", "Sono interrompido", "Não informado"],
    "comportamento_peso": ["Peso estável", "Ganho de peso", "Perda de peso", "Oscilação de peso", "Não informado"],
    "disposicao_fisica": ["Boa", "Regular", "Baixa", "Muito baixa", "Não informado"],
    "funcionamento_intestinal": ["Diário", "A cada 2 dias", "Constipação", "Diarreia", "Irregular", "Não informado"],
    "funcionamento_urinario": ["Normal", "Aumentado", "Reduzido", "Ardência", "Não informado"],
    "denticao": ["Completa", "Incompleta", "Prótese", "Aparelho ortodôntico", "Não informado"],
    "mastigacao": ["Normal", "Dificuldade para mastigar", "Mastigação rápida", "Dor ao mastigar", "Não informado"],
    "quem_cozinha": ["Próprio paciente", "Cônjuge/familiar", "Restaurante", "Marmita", "Delivery", "Não informado"],
    "apetite": ["Normal", "Aumentado", "Reduzido", "Oscilante", "Não informado"],
    "horario_mais_fome": ["Manhã", "Tarde", "Noite", "Madrugada", "Não informado"],
    "ingestao_agua_dia": [
        "Menos de 500 ml/dia", "500 ml a 1 litro/dia", "1 a 1,5 litros/dia",
        "1,5 a 2 litros/dia", "Mais de 2 litros/dia", "Não informado"
    ],
    "tratamento_nutricional_anterior": [
        "Nunca fez", "Já fez e teve boa adesão", "Já fez e teve baixa adesão",
        "Em acompanhamento atualmente", "Não informado"
    ],
    "habito_beliscar": ["Não", "Sim, beliscos variados", "Sim, doces", "Sim, salgados", "Sim, à noite", "Não informado"],

    "tipo_avaliacao": ["Avaliação inicial", "Retorno", "Reavaliação", "Acompanhamento", "Não informado"],
    "objetivo_antropometrico": [
        "Controle de risco cardiometabólico", "Ganho de massa muscular", "Redução de gordura",
        "Manutenção de peso", "Performance esportiva", "Saúde preventiva", "Não informado"
    ],
    "condicao_medicao": ["Em jejum", "Sem jejum", "Pós treino", "Pós refeição", "Não informado"],
    "tipo_balanca": ["Balança digital simples", "Bioimpedância", "Balança mecânica", "Não informado"],
    "roupa_medicao": ["Roupa leve", "Roupa de treino", "Roupa comum", "Não informado"],
    "local_cintura": ["Menor circunferência", "Linha umbilical", "Maior circunferência abdominal", "Não informado"],
}


_ED3_MULTI = {
    "queixa_principal": [
        "Acompanhamento preventivo", "Controle lipídico", "Controle glicêmico",
        "Ganho de massa muscular", "Emagrecimento", "Melhora de performance esportiva",
        "Melhora de energia/disposição", "Educação alimentar", "Saúde intestinal"
    ],
    "historia_doenca_atual": [
        "Nenhuma", "Doença cardiovascular", "Hipertensão", "Diabetes", "Resistência à insulina",
        "Dislipidemia", "Esteatose hepática", "Gastrite/Refluxo", "Ansiedade", "Estresse"
    ],
    "sintomas": [
        "Nenhum", "Cansaço", "Sono ruim", "Dor de cabeça", "Azia/Refluxo",
        "Gases", "Distensão abdominal", "Constipação", "Diarreia", "Compulsão alimentar"
    ],
    "historia_familiar": [
        "Nenhuma relevante", "Câncer", "Diabetes", "Hipertensão", "Doença cardiovascular",
        "Obesidade", "Dislipidemia", "Doença renal", "Doença tireoidiana"
    ],
    "medicamentos_suplementos": [
        "Nenhum", "Creatina", "Vitamina D", "Ômega 3", "Multivitamínico",
        "Whey protein", "Magnésio", "Antihipertensivo", "Estatina", "Antidiabético"
    ],
    "intolerancia_alergia_alimentar": [
        "Nenhuma", "Lactose", "Glúten", "Proteína do leite", "Ovo", "Frutos do mar",
        "Amendoim", "Corantes/conservantes"
    ],
    "objetivo_nutricional": [
        "Ganho de massa muscular", "Redução de gordura", "Controle de risco cardiometabólico",
        "Melhora de energia/disposição", "Performance esportiva", "Reeducação alimentar",
        "Controle intestinal", "Manutenção de peso"
    ],
    "alimentos_preferidos": [
        "Arroz", "Feijão", "Frango", "Carne vermelha", "Peixe", "Ovos", "Pão integral",
        "Tapioca", "Batata / mandioca", "Massas", "Queijos", "Açaí", "Café",
        "Suco", "Comida japonesa", "Salgados", "Pizza / hambúrguer"
    ],
    "alimentos_que_nao_gosta": [
        "Não informado", "Verduras", "Legumes", "Frutas", "Peixe", "Ovos",
        "Leite e derivados", "Feijão", "Carnes", "Alimentos integrais"
    ],
    "habitos_fim_de_semana": [
        "Mantém rotina alimentar", "Belisca mais", "Aumenta consumo de álcool",
        "Pizza / hambúrguer", "Churrasco", "Doces", "Delivery", "Refeições fora de casa"
    ],
    "dificuldades_adesao": [
        "Rotina de trabalho", "Falta de tempo", "Ansiedade", "Fome à noite",
        "Fim de semana", "Alimentação fora de casa", "Preferência por doces",
        "Preferência por salgados", "Baixa ingestão de água"
    ],
}


_ED3_FOODS = [
    "Arroz branco", "Arroz integral", "Feijão", "Frango", "Carne bovina", "Peixe",
    "Ovo", "Pão integral", "Pão francês", "Queijo", "Tapioca", "Aveia", "Banana",
    "Mamão", "Maçã", "Laranja", "Batata doce", "Mandioca", "Macarrão", "Salada",
    "Legumes", "Biscoito doce", "Biscoito salgado", "Bolo", "Açaí"
]

_ED3_BEBIDAS = [
    "Água", "Café sem açúcar", "Café com açúcar", "Suco natural", "Suco industrializado",
    "Refrigerante", "Leite", "Iogurte", "Chá"
]

_ED3_CARACTERISTICAS = [
    "Ficou satisfeito", "Ficou com fome", "Beliscou entre refeições",
    "Comeu rápido", "Comeu fora de casa", "Refeição leve", "Refeição pesada"
]


def _ed3_multiselect_control(page, label, valor, opcoes):
    tf = ft.TextField(
        label=label,
        value=str(valor or ""),
        width=620,
        multiline=True,
        min_lines=2,
        max_lines=4,
        border_radius=12,
    )

    def abrir_seletor(e=None):
        selecionados = set(_ed3_split_multi(tf.value))
        checks = []

        for op in opcoes:
            cb = ft.Checkbox(label=op, value=op in selecionados)
            checks.append(cb)

        def aplicar(ev=None):
            vals = [cb.label for cb in checks if cb.value]
            tf.value = _ed3_join_multi(vals)
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(label, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=520,
                height=460,
                content=ft.Column(
                    spacing=4,
                    scroll=ft.ScrollMode.AUTO,
                    controls=checks,
                ),
            ),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=lambda ev: fechar_dialog(dialog, page)),
                ft.TextButton(content=ft.Text("Aplicar seleção"), on_click=aplicar),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def fechar_dialog(dialog, page):
        dialog.open = False
        page.update()

    controle = ft.Column(
        spacing=6,
        controls=[
            tf,
            ft.OutlinedButton(
                content=ft.Text("Selecionar opções"),
                on_click=abrir_seletor,
                style=ft.ButtonStyle(
                    color=globals().get("COR_PRIMARIA", "#2563EB"),
                    shape=ft.RoundedRectangleBorder(radius=12),
                ),
            ),
        ],
    )

    return controle, lambda: str(tf.value or "").strip(), True


def _ed3_refeicao_control(page, label, valor, campo):
    tf = ft.TextField(
        label=label,
        value=str(valor or ""),
        width=700,
        multiline=True,
        min_lines=3,
        max_lines=6,
        border_radius=12,
    )

    horarios_padrao = {
        "desjejum": "06:00",
        "lanche_manha": "09:30",
        "almoco": "12:30",
        "lanche_tarde": "15:00",
        "jantar": "19:30",
        "ceia": "21:30",
    }

    def extrair_parte(nome):
        texto = str(tf.value or "")

        m = re.search(rf"{nome}:\s*([^|]+)", texto, flags=re.I)
        if m:
            return m.group(1).strip()

        return ""

    def abrir_montador(e=None):
        hora = ft.TextField(
            label="Horário",
            value=extrair_parte("Horário") or horarios_padrao.get(campo, ""),
            width=120,
            border_radius=12,
        )

        alimentos_checks = [
            ft.Checkbox(label=op, value=op.lower() in str(tf.value or "").lower())
            for op in _ED3_FOODS
        ]

        bebidas_checks = [
            ft.Checkbox(label=op, value=op.lower() in str(tf.value or "").lower())
            for op in _ED3_BEBIDAS
        ]

        caracteristicas_checks = [
            ft.Checkbox(label=op, value=op.lower() in str(tf.value or "").lower())
            for op in _ED3_CARACTERISTICAS
        ]

        def aplicar(ev=None):
            alimentos = [cb.label for cb in alimentos_checks if cb.value]
            bebidas = [cb.label for cb in bebidas_checks if cb.value]
            caracteristicas = [cb.label for cb in caracteristicas_checks if cb.value]

            partes = []

            if hora.value:
                partes.append(f"Horário: {hora.value}")

            if alimentos:
                partes.append(f"Alimentos: {_ed3_join_multi(alimentos)}")

            if bebidas:
                partes.append(f"Bebidas: {_ed3_join_multi(bebidas)}")

            if caracteristicas:
                partes.append(f"Características: {_ed3_join_multi(caracteristicas)}")

            tf.value = " | ".join(partes) if partes else "Não informado"
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Montar {label}", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=780,
                height=560,
                content=ft.Column(
                    spacing=12,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        hora,
                        ft.Text("Alimentos", size=14, weight=ft.FontWeight.BOLD),
                        ft.ResponsiveRow(
                            columns=12,
                            controls=[
                                ft.Container(col={"xs": 12, "md": 4}, content=cb)
                                for cb in alimentos_checks
                            ],
                        ),
                        ft.Text("Bebidas", size=14, weight=ft.FontWeight.BOLD),
                        ft.ResponsiveRow(
                            columns=12,
                            controls=[
                                ft.Container(col={"xs": 12, "md": 4}, content=cb)
                                for cb in bebidas_checks
                            ],
                        ),
                        ft.Text("Características", size=14, weight=ft.FontWeight.BOLD),
                        ft.ResponsiveRow(
                            columns=12,
                            controls=[
                                ft.Container(col={"xs": 12, "md": 4}, content=cb)
                                for cb in caracteristicas_checks
                            ],
                        ),
                    ],
                ),
            ),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=lambda ev: fechar_dialog(dialog, page)),
                ft.TextButton(content=ft.Text("Aplicar"), on_click=aplicar),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def fechar_dialog(dialog, page):
        dialog.open = False
        page.update()

    controle = ft.Column(
        spacing=6,
        controls=[
            tf,
            ft.OutlinedButton(
                content=ft.Text("Montar com seleções"),
                on_click=abrir_montador,
                style=ft.ButtonStyle(
                    color=globals().get("COR_PRIMARIA", "#2563EB"),
                    shape=ft.RoundedRectangleBorder(radius=12),
                ),
            ),
        ],
    )

    return controle, lambda: str(tf.value or "").strip(), True


def _ed3_criar_controle(page, nome_csv, campo, valor):
    label = _ed_label(campo)

    if campo in _ED3_SINGLE:
        valor = str(valor or "").strip() or "Não informado"

        dd = ft.Dropdown(
            label=label,
            width=335,
            value=valor,
            border_radius=12,
            options=_ed3_option_list(_ED3_SINGLE[campo], valor),
        )

        return dd, lambda dd=dd: str(dd.value or "").strip(), False

    if campo in _ED3_MULTI:
        return _ed3_multiselect_control(page, label, valor, _ED3_MULTI[campo])

    if nome_csv == "recordatorio_habitual.csv" and campo in [
        "desjejum", "lanche_manha", "almoco", "lanche_tarde", "jantar", "ceia"
    ]:
        return _ed3_refeicao_control(page, label, valor, campo)

    multiline = campo in [
        "historia_patologica_pregressa",
        "internacoes_cirurgias",
        "observacoes",
    ]

    width = 700 if multiline else 335

    tf = ft.TextField(
        label=label,
        value=str(valor or ""),
        width=width,
        multiline=multiline,
        min_lines=3 if multiline else 1,
        max_lines=6 if multiline else 1,
        border_radius=12,
    )

    return tf, lambda tf=tf: str(tf.value or "").strip(), multiline


def abrir_popup_edicao_registro_nutricional(page, titulo, nome_csv, data_coluna, recalcular=None):
    rows = _ed_ler_csv(nome_csv)
    colunas = _edv2_colunas_reais(nome_csv, rows) if "_edv2_colunas_reais" in globals() else _ed_schema(nome_csv)

    pacientes = _ed_pacientes()
    paciente_atual = _ed_paciente_atual()

    if not paciente_atual and pacientes:
        paciente_atual = str(pacientes[0]["id"])

    paciente_dd = ft.Dropdown(
        label="Paciente",
        width=420,
        value=paciente_atual,
        border_radius=12,
        options=[
            ft.dropdown.Option(key=str(p["id"]), text=p["nome"])
            for p in pacientes
        ],
    )

    registro_dd = ft.Dropdown(
        label="Registro",
        width=330,
        border_radius=12,
        options=[],
    )

    aviso_txt = ft.Text("", size=12, color="#B45309")
    erro_txt = ft.Text("", size=12, color="#DC2626")

    campos_container = ft.Column(
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
    )

    getters = {}

    def id_equiv(a, b):
        if "_edv2_id_equiv" in globals():
            return _edv2_id_equiv(a, b)

        return str(a or "").strip() == str(b or "").strip()

    def nome_paciente_registro(row):
        pid = str(row.get("paciente_id") or "").strip()

        try:
            nome = _ed_nome_paciente(pid)
            if nome and nome != pid:
                return nome
        except Exception:
            pass

        return f"Paciente {pid}" if pid else "Paciente não informado"

    def indices_do_paciente():
        pid = str(paciente_dd.value or "").strip()
        encontrados = []

        for idx, row in enumerate(rows):
            if id_equiv(row.get("paciente_id"), pid):
                encontrados.append(idx)

        if not encontrados and rows:
            return list(range(len(rows))), True

        return encontrados, False

    def montar_opcoes_registro():
        indices, fallback = indices_do_paciente()
        options = []

        for idx in indices:
            row = rows[idx]
            texto = _ed_data_br(row.get(data_coluna, ""))

            if fallback:
                texto += f" • {nome_paciente_registro(row)}"

            if nome_csv == "antropometria.csv":
                tipo = row.get("tipo_avaliacao", "")
                if tipo:
                    texto += f" • {tipo}"

            options.append(ft.dropdown.Option(key=str(idx), text=texto))

        registro_dd.options = options
        registro_dd.value = options[-1].key if options else None

        aviso_txt.value = (
            "O registro não foi localizado pelo ID do paciente selecionado. Listei os registros disponíveis para edição."
            if fallback and rows else ""
        )

    def carregar_campos():
        getters.clear()
        campos_container.controls.clear()

        if not rows:
            campos_container.controls.append(
                ft.Container(
                    bgcolor="#FEF2F2",
                    border_radius=12,
                    padding=12,
                    content=ft.Text(f"Nenhum registro encontrado no arquivo {nome_csv}.", size=13, color="#991B1B"),
                )
            )
            return

        if registro_dd.value is None:
            campos_container.controls.append(
                ft.Container(
                    bgcolor="#FEF2F2",
                    border_radius=12,
                    padding=12,
                    content=ft.Text(f"Nenhum registro de {titulo.lower()} disponível para edição.", size=13, color="#991B1B"),
                )
            )
            return

        idx = int(registro_dd.value)
        row = rows[idx]

        campos_container.controls.append(
            ft.Container(
                bgcolor="#EFF6FF",
                border_radius=12,
                padding=12,
                content=ft.Text(
                    f"Editando: {nome_paciente_registro(row)} • Registro: {_ed_data_br(row.get(data_coluna))}",
                    size=13,
                    color="#1D4ED8",
                    weight=ft.FontWeight.BOLD,
                ),
            )
        )

        linha = []

        for campo in colunas:
            if campo == "paciente_id":
                continue

            controle, getter, full_width = _ed3_criar_controle(page, nome_csv, campo, row.get(campo, ""))
            getters[campo] = getter

            if full_width:
                if linha:
                    campos_container.controls.append(ft.Row(spacing=10, wrap=True, controls=linha))
                    linha = []

                campos_container.controls.append(controle)
            else:
                linha.append(controle)

                if len(linha) == 2:
                    campos_container.controls.append(ft.Row(spacing=10, wrap=True, controls=linha))
                    linha = []

        if linha:
            campos_container.controls.append(ft.Row(spacing=10, wrap=True, controls=linha))

    def trocar_paciente(e=None):
        montar_opcoes_registro()
        carregar_campos()
        page.update()

    def trocar_registro(e=None):
        carregar_campos()
        page.update()

    paciente_dd.on_change = trocar_paciente
    registro_dd.on_change = trocar_registro

    def fechar(e=None):
        dialog.open = False
        page.update()

    def salvar(e=None):
        if registro_dd.value is None:
            erro_txt.value = "Não há registro selecionado para salvar."
            page.update()
            return

        try:
            idx = int(registro_dd.value)

            if idx < 0 or idx >= len(rows):
                erro_txt.value = "Registro inválido."
                page.update()
                return

            row = dict(rows[idx])

            if id_equiv(row.get("paciente_id"), paciente_dd.value):
                row["paciente_id"] = str(paciente_dd.value or row.get("paciente_id") or "").strip()

            for campo, getter in getters.items():
                row[campo] = getter()

            if recalcular:
                row = recalcular(row)

            rows[idx] = row
            _ed_escrever_csv(nome_csv, rows)

            try:
                if "carregar_dados_nutricionais_data_flet_para_memoria" in globals():
                    carregar_dados_nutricionais_data_flet_para_memoria()
            except Exception as exc:
                print(f"[EDIÇÃO NUTRICIONAL] Falha ao recarregar memória: {exc}")

            dialog.open = False
            _ed_snackbar(page, f"{titulo} atualizado com sucesso.", "#16A34A")
            page.update()

        except Exception as exc:
            erro_txt.value = f"Erro ao salvar: {exc}"
            print(f"[EDIÇÃO NUTRICIONAL] Erro ao salvar {titulo}: {exc}")
            page.update()

    montar_opcoes_registro()
    carregar_campos()

    conteudo = ft.Container(
        width=880,
        height=710,
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Text(
                    f"Selecione o paciente e o registro para editar a ficha de {titulo.lower()}.",
                    size=13,
                    color="#64748B",
                ),
                ft.Container(
                    bgcolor="#F8FAFC",
                    border_radius=14,
                    padding=12,
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            paciente_dd,
                            registro_dd,
                        ],
                    ),
                ),
                aviso_txt,
                ft.Container(
                    expand=True,
                    bgcolor="#F3F4F6",
                    border_radius=14,
                    padding=12,
                    content=campos_container,
                ),
                erro_txt,
            ],
        ),
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(f"Editar {titulo}", weight=ft.FontWeight.BOLD),
        content=conteudo,
        actions=[
            ft.TextButton(content=ft.Text("Cancelar"), on_click=fechar),
            ft.TextButton(content=ft.Text("Salvar alterações"), on_click=salvar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()




# ============================================================
# PATCH V4 - COMPLETAR SELEÇÕES DA EDIÇÃO NUTRICIONAL
# ============================================================

try:
    _ED3_SINGLE
except NameError:
    _ED3_SINGLE = {}

try:
    _ED3_MULTI
except NameError:
    _ED3_MULTI = {}

try:
    _ED3_FOODS
except NameError:
    _ED3_FOODS = []

try:
    _ED3_BEBIDAS
except NameError:
    _ED3_BEBIDAS = []

try:
    _ED3_CARACTERISTICAS
except NameError:
    _ED3_CARACTERISTICAS = []


def _ed4_add_unique(lista_atual, novos):
    base = list(lista_atual or [])
    vistos = set(str(x).strip().lower() for x in base)

    for item in novos:
        item = str(item or "").strip()
        if not item:
            continue

        chave = item.lower()
        if chave not in vistos:
            base.append(item)
            vistos.add(chave)

    return base


# -------------------------
# Campos de escolha única
# -------------------------
_ED3_SINGLE.update({
    "amamentou": [
        "Não informado",
        "Sim",
        "Não",
        "Não se aplica",
    ],

    "atividade_fisica": [
        "Não pratica",
        "Caminhada - 1x por semana",
        "Caminhada - 2 a 3x por semana",
        "Caminhada - 4 ou mais vezes por semana",
        "Musculação - 1x por semana",
        "Musculação - 2 a 3x por semana",
        "Musculação - 4 ou mais vezes por semana",
        "Corrida",
        "Ciclismo",
        "Natação",
        "Funcional / Cross training",
        "Pilates",
        "Yoga",
        "Futebol",
        "Luta / Artes marciais - 1x por semana",
        "Luta / Artes marciais - 2 a 3x por semana",
        "Atleta / alta performance",
        "Não informado",
    ],

    "horario_atividade_fisica": [
        "Não informado",
        "Manhã",
        "Tarde",
        "Noite",
        "Madrugada",
        "Variável",
    ],

    "consumo_alcool": [
        "Não consome",
        "Socialmente",
        "Finais de semana",
        "1 a 2 vezes por semana",
        "3 ou mais vezes por semana",
        "Frequente",
        "Não informado",
    ],

    "tabagismo": [
        "Não fumante",
        "Fumante",
        "Ex-fumante",
        "Uso eventual",
        "Não informado",
    ],

    "qualidade_sono": [
        "Boa",
        "Regular",
        "Ruim",
        "Insônia",
        "Sono interrompido",
        "Sono insuficiente",
        "Sono não reparador",
        "Não informado",
    ],

    "comportamento_peso": [
        "Peso estável",
        "Ganho de peso recente",
        "Perda de peso recente",
        "Oscilação de peso",
        "Dificuldade para ganhar peso",
        "Dificuldade para perder peso",
        "Não informado",
    ],

    "disposicao_fisica": [
        "Boa",
        "Regular",
        "Baixa",
        "Muito baixa",
        "Oscilante",
        "Não informado",
    ],

    "funcionamento_intestinal": [
        "Diário",
        "A cada 2 dias",
        "A cada 3 dias ou mais",
        "Constipação",
        "Diarreia",
        "Irregular",
        "Gases frequentes",
        "Distensão abdominal",
        "Não informado",
    ],

    "funcionamento_urinario": [
        "Normal",
        "Aumentado",
        "Reduzido",
        "Acorda à noite para urinar",
        "Ardência",
        "Não informado",
    ],

    "denticao": [
        "Completa",
        "Incompleta",
        "Prótese",
        "Implante",
        "Aparelho ortodôntico",
        "Dor/desconforto",
        "Não informado",
    ],

    "mastigacao": [
        "Normal",
        "Dificuldade para mastigar",
        "Mastigação rápida",
        "Mastigação lenta",
        "Dor ao mastigar",
        "Evita alimentos duros",
        "Não informado",
    ],

    "quem_cozinha": [
        "Próprio paciente",
        "Cônjuge/familiar",
        "Restaurante",
        "Marmita",
        "Delivery",
        "Refeitório da empresa",
        "Variável",
        "Não informado",
    ],

    "apetite": [
        "Normal",
        "Aumentado",
        "Reduzido",
        "Oscilante",
        "Compulsivo",
        "Sem apetite pela manhã",
        "Mais apetite à noite",
        "Não informado",
    ],

    "horario_mais_fome": [
        "Manhã",
        "Tarde",
        "Noite",
        "Madrugada",
        "Após treino",
        "Antes de dormir",
        "Não informado",
    ],

    "ingestao_agua_dia": [
        "Menos de 500 ml/dia",
        "500 ml a 1 litro/dia",
        "1 a 1,5 litros/dia",
        "1,5 a 2 litros/dia",
        "2 a 3 litros/dia",
        "Mais de 3 litros/dia",
        "Não informado",
    ],

    "tratamento_nutricional_anterior": [
        "Nunca fez",
        "Já fez e teve boa adesão",
        "Já fez e teve baixa adesão",
        "Em acompanhamento atualmente",
        "Fez por pouco tempo",
        "Abandonou acompanhamento",
        "Não informado",
    ],

    "habito_beliscar": [
        "Não",
        "Sim, beliscos variados",
        "Sim, doces",
        "Sim, salgados",
        "Sim, castanhas/frutas",
        "Sim, à noite",
        "Sim, no trabalho",
        "Sim, por ansiedade",
        "Não informado",
    ],

    "tipo_avaliacao": [
        "Avaliação inicial",
        "Retorno",
        "Reavaliação",
        "Acompanhamento",
        "Avaliação esportiva",
        "Avaliação cardiometabólica",
        "Não informado",
    ],

    "objetivo_antropometrico": [
        "Controle de risco cardiometabólico",
        "Ganho de massa muscular",
        "Redução de gordura",
        "Manutenção de peso",
        "Performance esportiva",
        "Saúde preventiva",
        "Acompanhamento clínico",
        "Não informado",
    ],

    "condicao_medicao": [
        "Em jejum",
        "Sem jejum",
        "Pós treino",
        "Pré treino",
        "Pós refeição",
        "Pela manhã",
        "À tarde",
        "À noite",
        "Não informado",
    ],

    "tipo_balanca": [
        "Balança digital simples",
        "Bioimpedância",
        "Balança mecânica",
        "Balança profissional",
        "Não informado",
    ],

    "roupa_medicao": [
        "Roupa leve",
        "Roupa de treino",
        "Roupa comum",
        "Descalço",
        "Com calçado",
        "Não informado",
    ],

    "local_cintura": [
        "Menor circunferência",
        "Linha umbilical",
        "Maior circunferência abdominal",
        "Ponto médio entre costela e crista ilíaca",
        "Não informado",
    ],
})


# -------------------------
# Campos de múltipla seleção
# -------------------------
_ED3_MULTI.update({
    "queixa_principal": [
        "Acompanhamento preventivo",
        "Controle lipídico",
        "Controle glicêmico",
        "Controle de pressão arterial",
        "Controle de peso",
        "Ganho de massa muscular",
        "Emagrecimento",
        "Melhora de performance esportiva",
        "Melhora de energia/disposição",
        "Educação alimentar",
        "Saúde intestinal",
        "Redução de gordura abdominal",
        "Organização alimentar",
    ],

    "historia_doenca_atual": [
        "Nenhuma",
        "Doença cardiovascular",
        "Hipertensão",
        "Diabetes",
        "Pré-diabetes",
        "Resistência à insulina",
        "Dislipidemia",
        "Colesterol elevado",
        "Triglicerídeos elevados",
        "Esteatose hepática",
        "Gastrite/Refluxo",
        "Ansiedade",
        "Estresse",
        "Alteração tireoidiana",
        "Doença renal",
        "Doença intestinal",
    ],

    "sintomas": [
        "Nenhum",
        "Cansaço",
        "Sono ruim",
        "Dor de cabeça",
        "Azia/Refluxo",
        "Gases",
        "Distensão abdominal",
        "Constipação",
        "Diarreia",
        "Náusea",
        "Compulsão alimentar",
        "Fome excessiva",
        "Vontade de doces",
        "Queda de energia à tarde",
        "Câimbras",
    ],

    "historia_patologica_pregressa": [
        "Nenhuma relevante",
        "Cirurgia prévia",
        "Internação prévia",
        "Hipertensão",
        "Diabetes",
        "Dislipidemia",
        "Doença cardiovascular",
        "Doença renal",
        "Doença hepática",
        "Doença tireoidiana",
        "Gastrite/Refluxo",
        "COVID-19 com sintomas prolongados",
        "Lesão ortopédica",
        "Não informado",
    ],

    "historia_familiar": [
        "Nenhuma relevante",
        "Câncer",
        "Diabetes",
        "Hipertensão",
        "Doença cardiovascular",
        "Infarto",
        "AVC",
        "Obesidade",
        "Dislipidemia",
        "Doença renal",
        "Doença tireoidiana",
        "Doença hepática",
    ],

    "internacoes_cirurgias": [
        "Nenhuma",
        "Apendicectomia",
        "Colecistectomia",
        "Cirurgia bariátrica",
        "Cirurgia ortopédica",
        "Cirurgia cardíaca",
        "Cirurgia abdominal",
        "Internação recente",
        "Internação antiga",
        "Não informado",
    ],

    "medicamentos_suplementos": [
        "Nenhum",
        "Creatina",
        "Vitamina D",
        "Ômega 3",
        "Multivitamínico",
        "Whey protein",
        "Magnésio",
        "Cafeína",
        "Colágeno",
        "Probiótico",
        "Antihipertensivo",
        "Estatina",
        "Antidiabético",
        "Antiácido",
        "Antidepressivo/Ansiolítico",
        "Hormônio tireoidiano",
    ],

    "intolerancia_alergia_alimentar": [
        "Nenhuma",
        "Lactose",
        "Glúten",
        "Proteína do leite",
        "Ovo",
        "Frutos do mar",
        "Peixe",
        "Amendoim",
        "Castanhas",
        "Soja",
        "Corantes/conservantes",
        "Não informado",
    ],

    "objetivo_nutricional": [
        "Ganho de massa muscular",
        "Redução de gordura",
        "Controle de risco cardiometabólico",
        "Melhora de energia/disposição",
        "Performance esportiva",
        "Reeducação alimentar",
        "Controle intestinal",
        "Manutenção de peso",
        "Controle lipídico",
        "Controle glicêmico",
        "Melhora de composição corporal",
    ],

    "alimentos_preferidos": [
        "Arroz",
        "Feijão",
        "Frango",
        "Carne vermelha",
        "Peixe",
        "Ovos",
        "Pão integral",
        "Pão francês",
        "Tapioca",
        "Aveia",
        "Batata / mandioca",
        "Batata doce",
        "Massas",
        "Queijos",
        "Iogurte",
        "Frutas",
        "Verduras",
        "Açaí",
        "Café",
        "Suco",
        "Comida japonesa",
        "Salgados",
        "Pizza / hambúrguer",
        "Doces",
    ],

    "alimentos_que_nao_gosta": [
        "Não informado",
        "Verduras",
        "Legumes",
        "Frutas",
        "Peixe",
        "Ovos",
        "Leite e derivados",
        "Feijão",
        "Carnes",
        "Alimentos integrais",
        "Saladas",
        "Oleaginosas",
        "Comida japonesa",
    ],

    "habitos_fim_de_semana": [
        "Mantém rotina alimentar",
        "Belisca mais",
        "Aumenta consumo de álcool",
        "Pizza / hambúrguer",
        "Churrasco",
        "Doces",
        "Delivery",
        "Refeições fora de casa",
        "Pula refeições",
        "Acorda mais tarde",
        "Reduz consumo de água",
    ],

    "dificuldades_adesao": [
        "Rotina de trabalho",
        "Falta de tempo",
        "Ansiedade",
        "Fome à noite",
        "Fim de semana",
        "Alimentação fora de casa",
        "Preferência por doces",
        "Preferência por salgados",
        "Baixa ingestão de água",
        "Falta de planejamento",
        "Custo dos alimentos",
        "Falta de apoio familiar",
        "Dificuldade para cozinhar",
    ],
})


# -------------------------
# Recordatório - alimentos
# -------------------------
_ED3_FOODS = _ed4_add_unique(_ED3_FOODS, [
    "Arroz branco",
    "Arroz integral",
    "Feijão carioca",
    "Feijão preto",
    "Lentilha",
    "Grão-de-bico",
    "Frango",
    "Carne bovina",
    "Carne suína",
    "Peixe",
    "Atum",
    "Sardinha",
    "Ovo cozido",
    "Ovo mexido",
    "Omelete",
    "Pão integral",
    "Pão francês",
    "Pão de forma",
    "Queijo",
    "Requeijão",
    "Iogurte",
    "Leite",
    "Tapioca",
    "Aveia",
    "Granola",
    "Banana",
    "Mamão",
    "Maçã",
    "Laranja",
    "Abacaxi",
    "Manga",
    "Morango",
    "Açaí",
    "Batata doce",
    "Batata inglesa",
    "Mandioca",
    "Inhame",
    "Macarrão",
    "Cuscuz",
    "Salada",
    "Alface",
    "Tomate",
    "Cenoura",
    "Beterraba",
    "Brócolis",
    "Abobrinha",
    "Legumes",
    "Castanhas",
    "Amendoim",
    "Biscoito doce",
    "Biscoito salgado",
    "Bolo",
    "Chocolate",
    "Pizza",
    "Hambúrguer",
    "Salgado",
])


_ED3_BEBIDAS = _ed4_add_unique(_ED3_BEBIDAS, [
    "Água",
    "Café sem açúcar",
    "Café com açúcar",
    "Café com leite",
    "Suco natural",
    "Suco industrializado",
    "Refrigerante",
    "Leite",
    "Iogurte",
    "Chá",
    "Água de coco",
    "Bebida alcoólica",
    "Energético",
    "Isotônico",
])


_ED3_CARACTERISTICAS = _ed4_add_unique(_ED3_CARACTERISTICAS, [
    "Ficou satisfeito",
    "Ficou com fome",
    "Beliscou entre refeições",
    "Comeu rápido",
    "Comeu devagar",
    "Comeu fora de casa",
    "Comeu no trabalho",
    "Comeu assistindo TV/celular",
    "Refeição leve",
    "Refeição pesada",
    "Sentiu sono após refeição",
    "Sentiu azia/refluxo",
    "Sentiu estufamento",
])


# -------------------------
# Melhorias visuais para data/hora e numéricos
# -------------------------
try:
    _ed3_criar_controle_original_v4
except NameError:
    _ed3_criar_controle_original_v4 = _ed3_criar_controle


def _ed3_criar_controle(page, nome_csv, campo, valor):
    label = _ed_label(campo)

    # Datas
    if campo in ["data_anamnese", "data_registro", "data_avaliacao"]:
        tf = ft.TextField(
            label=label,
            value=str(valor or ""),
            hint_text="aaaa-mm-dd ou dd/mm/aaaa",
            width=335,
            border_radius=12,
        )
        return tf, lambda tf=tf: str(tf.value or "").strip(), False

    # Horários
    if campo in ["hora_acordar", "hora_dormir"]:
        tf = ft.TextField(
            label=label,
            value=str(valor or ""),
            hint_text="hh:mm",
            width=160,
            border_radius=12,
        )
        return tf, lambda tf=tf: str(tf.value or "").strip(), False

    # Numéricos antropométricos
    if campo in ["peso", "altura", "circunferencia_cintura", "imc"]:
        tf = ft.TextField(
            label=label,
            value=str(valor or ""),
            width=180,
            border_radius=12,
        )
        return tf, lambda tf=tf: str(tf.value or "").strip(), False

    # Número de filhos/idades continua editável, mas orientado
    if campo == "numero_filhos_idades":
        tf = ft.TextField(
            label=label,
            value=str(valor or ""),
            hint_text="Ex.: 2 filhos: 20 anos e 4 anos",
            width=335,
            border_radius=12,
        )
        return tf, lambda tf=tf: str(tf.value or "").strip(), False

    return _ed3_criar_controle_original_v4(page, nome_csv, campo, valor)




# ===== PATCH SEGURO DATA_FLET: EXAMES ANALISE EXCLUSAO =====

from pathlib import Path as _patch_Path
import csv as _patch_csv
import unicodedata as _patch_unicodedata
import re as _patch_re
from datetime import datetime as _patch_datetime


def _patch_data_dir():
    return _patch_Path(__file__).resolve().parent / "data_flet"


def _patch_limpar_chave(chave):
    return str(chave or "").replace("\ufeff", "").strip()


def _patch_row(row):
    if not isinstance(row, dict):
        return {}
    return {
        _patch_limpar_chave(k): "" if v is None else str(v).strip()
        for k, v in row.items()
    }


def _patch_get(row, *chaves):
    r = _patch_row(row)
    for chave in chaves:
        chave = _patch_limpar_chave(chave)
        valor = r.get(chave, "")
        if str(valor).strip() != "":
            return str(valor).strip()
    return ""


def _patch_norm(valor):
    texto = str(valor or "").strip().lower()
    texto = _patch_unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not _patch_unicodedata.combining(c))
    texto = texto.replace("_", " ").replace("-", " ")
    texto = _patch_re.sub(r"[^a-z0-9%/., ]+", " ", texto)
    return " ".join(texto.split())


def _patch_float(valor):
    texto = str(valor or "").strip()
    if not texto:
        return None

    texto = texto.replace(" ", "")

    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    else:
        texto = texto.replace(",", ".")

    m = _patch_re.search(r"[-+]?\d+(?:\.\d+)?", texto)
    if not m:
        return None

    try:
        return float(m.group(0))
    except Exception:
        return None


def _patch_ler_csv(nome):
    caminho = _patch_data_dir() / nome
    if not caminho.exists():
        return []

    with open(caminho, newline="", encoding="utf-8-sig") as f:
        return [_patch_row(r) for r in _patch_csv.DictReader(f)]


def _patch_campos_csv(nome, fallback=None):
    caminho = _patch_data_dir() / nome

    if caminho.exists():
        try:
            with open(caminho, newline="", encoding="utf-8-sig") as f:
                reader = _patch_csv.DictReader(f)
                campos = [_patch_limpar_chave(c) for c in (reader.fieldnames or [])]
                if campos:
                    return campos
        except Exception:
            pass

    return list(fallback or [])


def _patch_salvar_csv(nome, rows, campos=None):
    caminho = _patch_data_dir() / nome
    caminho.parent.mkdir(parents=True, exist_ok=True)

    campos = [_patch_limpar_chave(c) for c in (campos or _patch_campos_csv(nome))]

    for row in rows:
        for k in _patch_row(row).keys():
            if k not in campos:
                campos.append(k)

    if not campos:
        return

    tmp = caminho.with_suffix(caminho.suffix + ".tmp")

    with open(tmp, "w", newline="", encoding="utf-8-sig") as f:
        writer = _patch_csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            row = _patch_row(row)
            writer.writerow({c: row.get(c, "") for c in campos})

    tmp.replace(caminho)


def _patch_pacientes():
    pacientes = _patch_ler_csv("pacientes.csv")
    por_id = {}
    por_nome = {}

    for p in pacientes:
        pid = _patch_get(p, "paciente_id", "id")
        if pid.isdigit() and len(pid) < 4:
            pid = pid.zfill(4)

        nome = _patch_get(p, "nome", "paciente_nome", "paciente")

        if pid:
            por_id[pid] = p
        if nome:
            por_nome[_patch_norm(nome)] = p

    return pacientes, por_id, por_nome


def _patch_pid(row):
    _, por_id, por_nome = _patch_pacientes()

    pid = _patch_get(row, "paciente_id", "id_paciente")
    if pid.isdigit() and len(pid) < 4:
        pid = pid.zfill(4)

    if pid in por_id:
        return pid

    nome = _patch_get(row, "paciente_nome", "nome_paciente", "paciente", "nome")
    if nome:
        p = por_nome.get(_patch_norm(nome))
        if p:
            pid = _patch_get(p, "paciente_id", "id")
            if pid.isdigit() and len(pid) < 4:
                pid = pid.zfill(4)
            return pid

    selecionado = str(globals().get("PACIENTE_SELECIONADO_ID", "") or "").strip()
    if selecionado.isdigit() and len(selecionado) < 4:
        selecionado = selecionado.zfill(4)

    if selecionado in por_id:
        return selecionado

    return ""


def _patch_nome_paciente(pid):
    _, por_id, _ = _patch_pacientes()
    p = por_id.get(str(pid or "").strip(), {})
    return _patch_get(p, "nome", "paciente_nome", "paciente")


def _patch_nome_exame(row):
    return (
        _patch_get(row, "nome_exame")
        or _patch_get(row, "exame")
        or _patch_get(row, "exame_nome")
        or _patch_get(row, "tipo_exame")
        or _patch_get(row, "nome_padronizado")
    )


def _patch_data_exame(row):
    return (
        _patch_get(row, "data_exame")
        or _patch_get(row, "data")
        or _patch_datetime.now().strftime("%Y-%m-%d")
    )


def _patch_refs():
    refs = {}

    for r in _patch_ler_csv("referencias_exames.csv"):
        for nome in [
            _patch_get(r, "nome_exame"),
            _patch_get(r, "nome"),
            _patch_get(r, "id"),
        ]:
            n = _patch_norm(nome)
            if n:
                refs[n] = r

    return refs


def _patch_ref(nome_exame, refs=None):
    refs = refs or _patch_refs()
    chave = _patch_norm(nome_exame)

    if chave in refs:
        return refs[chave]

    for k, r in refs.items():
        if chave and (chave in k or k in chave):
            return r

    return {}


def _patch_referencia_texto(ref, unidade=""):
    texto = _patch_get(ref, "referencia_texto") or _patch_get(ref, "referencia")
    if texto:
        return texto

    vmin = _patch_get(ref, "valor_min")
    vmax = _patch_get(ref, "valor_max")
    unidade = unidade or _patch_get(ref, "unidade")

    if vmin and vmax:
        return f"{vmin} a {vmax} {unidade}".strip()
    if vmin:
        return f">= {vmin} {unidade}".strip()
    if vmax:
        return f"<= {vmax} {unidade}".strip()

    return ""


def _patch_analisar(nome_exame, resultado, unidade, refs=None):
    refs = refs or _patch_refs()
    ref = _patch_ref(nome_exame, refs)

    if not ref:
        return {
            "nome_padronizado": nome_exame,
            "valor_min": "",
            "valor_max": "",
            "status": "Sem análise",
            "mensagem": f"{nome_exame}: referência não localizada no catálogo.",
            "fonte_referencia": "",
        }

    valor = _patch_float(resultado)
    vmin = _patch_float(_patch_get(ref, "valor_min"))
    vmax = _patch_float(_patch_get(ref, "valor_max"))

    if valor is None:
        status = "Sem análise"
    elif vmin is not None and valor < vmin:
        status = "Baixo"
    elif vmax is not None and valor > vmax:
        status = "Alto"
    elif vmin is not None or vmax is not None:
        status = "Normal"
    else:
        status = "Sem análise"

    nome_pad = _patch_get(ref, "nome_exame") or _patch_get(ref, "nome") or nome_exame
    referencia = _patch_referencia_texto(ref, unidade)

    msg = f"{nome_pad}: {resultado} {unidade}".strip()
    msg += f" - {status}"
    if referencia:
        msg += f". Referência: {referencia}"

    return {
        "nome_padronizado": nome_pad,
        "valor_min": _patch_get(ref, "valor_min"),
        "valor_max": _patch_get(ref, "valor_max"),
        "status": status,
        "mensagem": msg,
        "fonte_referencia": _patch_get(ref, "fonte_referencia") or _patch_get(ref, "fonte"),
    }


def _patch_chave(row):
    pid = _patch_pid(row) or _patch_get(row, "paciente_id", "id_paciente")
    if pid.isdigit() and len(pid) < 4:
        pid = pid.zfill(4)

    return (
        pid,
        _patch_norm(_patch_data_exame(row)),
        _patch_norm(_patch_nome_exame(row)),
        _patch_norm(_patch_get(row, "resultado", "valor")),
        _patch_norm(_patch_get(row, "unidade")),
    )


def _patch_proximo_id(rows, campo, largura=0):
    maior = 0

    for r in rows:
        valor = _patch_get(r, campo)
        m = _patch_re.search(r"\d+", str(valor or ""))
        if m:
            try:
                maior = max(maior, int(m.group(0)))
            except Exception:
                pass

    novo = maior + 1
    return str(novo).zfill(largura) if largura else str(novo)


def _patch_migrar_mock_para_csv():
    mocks = list(globals().get("RESULTADOS_EXAMES_MOCK", []) or [])
    if not mocks:
        return 0

    exames = _patch_ler_csv("exames.csv")
    analises = _patch_ler_csv("analise_exames.csv")
    refs = _patch_refs()

    chaves_exames = {_patch_chave(r) for r in exames}
    chaves_analises = {_patch_chave(r) for r in analises}

    adicionados = 0

    for m in mocks:
        pid = _patch_pid(m)
        nome_exame = _patch_nome_exame(m)
        resultado = _patch_get(m, "resultado", "valor")
        unidade = _patch_get(m, "unidade")
        data_exame = _patch_data_exame(m)

        if not pid or not nome_exame or not resultado:
            continue

        chave = (
            pid,
            _patch_norm(data_exame),
            _patch_norm(nome_exame),
            _patch_norm(resultado),
            _patch_norm(unidade),
        )

        if chave not in chaves_exames:
            exames.append({
                "exame_id": _patch_proximo_id(exames, "exame_id", 4),
                "paciente_id": pid,
                "data_exame": data_exame,
                "nome_exame": nome_exame,
                "resultado": resultado,
                "unidade": unidade,
                "observacoes": _patch_get(m, "observacoes", "obs") or "Lançado pela interface NutriSoft",
            })
            chaves_exames.add(chave)
            adicionados += 1

        if chave not in chaves_analises:
            analise = _patch_analisar(nome_exame, resultado, unidade, refs)
            analises.append({
                "analise_id": _patch_proximo_id(analises, "analise_id"),
                "paciente_id": pid,
                "data_exame": data_exame,
                "nome_exame": nome_exame,
                "nome_padronizado": analise["nome_padronizado"],
                "resultado": resultado,
                "unidade": unidade,
                "valor_min": analise["valor_min"],
                "valor_max": analise["valor_max"],
                "status": analise["status"],
                "mensagem": analise["mensagem"],
                "fonte_referencia": analise["fonte_referencia"],
            })
            chaves_analises.add(chave)

    if adicionados:
        _patch_salvar_csv(
            "exames.csv",
            exames,
            [
                "exame_id", "paciente_id", "data_exame",
                "nome_exame", "resultado", "unidade", "observacoes",
            ],
        )

        _patch_salvar_csv(
            "analise_exames.csv",
            analises,
            [
                "analise_id", "paciente_id", "data_exame", "nome_exame",
                "nome_padronizado", "resultado", "unidade", "valor_min",
                "valor_max", "status", "mensagem", "fonte_referencia",
            ],
        )

        print(f"[PATCH DATA_FLET] Resultados migrados para CSV: {adicionados}")

    return adicionados


def sincronizar_resultados_exames_mock_data_flet():
    _patch_migrar_mock_para_csv()

    analises = _patch_ler_csv("analise_exames.csv")
    refs = _patch_refs()
    resultados = []

    for r in analises:
        pid = _patch_get(r, "paciente_id", "id_paciente")
        if pid.isdigit() and len(pid) < 4:
            pid = pid.zfill(4)

        nome_exame = _patch_nome_exame(r)
        unidade = _patch_get(r, "unidade")
        resultado = _patch_get(r, "resultado", "valor")
        data_exame = _patch_data_exame(r)

        ref = _patch_ref(nome_exame, refs)
        referencia = _patch_referencia_texto(ref, unidade)

        status = _patch_get(r, "status")
        if not status:
            status = _patch_analisar(nome_exame, resultado, unidade, refs)["status"]

        item = dict(r)
        item.update({
            "paciente_id": pid,
            "id_paciente": pid,
            "paciente": _patch_nome_paciente(pid),
            "paciente_nome": _patch_nome_paciente(pid),
            "data": data_exame,
            "data_exame": data_exame,
            "exame": nome_exame,
            "nome_exame": nome_exame,
            "nome_padronizado": _patch_get(r, "nome_padronizado") or nome_exame,
            "resultado": resultado,
            "unidade": unidade,
            "referencia": referencia,
            "referencia_texto": referencia,
            "status": status,
            "mensagem": _patch_get(r, "mensagem"),
            "fonte_referencia": _patch_get(r, "fonte_referencia"),
        })

        resultados.append(item)

    globals()["RESULTADOS_EXAMES_MOCK"] = resultados

    # EXAMES_CADASTRADOS_MOCK precisa continuar sendo dict.
    # A tela de cadastro usa EXAMES_CADASTRADOS_MOCK.get((paciente_id, data), [])
    # para esconder exames já lançados naquela data.
    cadastrados = {}
    for item in resultados:
        pid = _patch_get(item, "paciente_id", "id_paciente")
        if pid.isdigit() and len(pid) < 4:
            pid = pid.zfill(4)

        data = _patch_data_exame(item)
        nome_exame = _patch_nome_exame(item)

        if not pid or not data or not nome_exame:
            continue

        chaves = [
            (pid, data),
            (str(pid), data),
        ]

        for chave in chaves:
            cadastrados.setdefault(chave, [])
            if nome_exame not in cadastrados[chave]:
                cadastrados[chave].append(nome_exame)

    globals()["EXAMES_CADASTRADOS_MOCK"] = cadastrados

    print(f"[PATCH DATA_FLET] Resultados sincronizados: {len(resultados)}")
    print(f"[PATCH DATA_FLET] Datas com exames cadastrados: {len(cadastrados)}")
    return resultados


def _patch_status_paciente(exames):
    if not exames:
        return "Sem exames"

    status = [_patch_norm(_patch_get(e, "status")) for e in exames]

    if any("critico" in s for s in status):
        return "Crítico"
    if any("alto" in s or "baixo" in s or "alterado" in s for s in status):
        return "Atenção"
    if any("normal" in s for s in status):
        return "Normal"

    return "Sem análise"


def atualizar_pacientes_csv_real_definitivo():
    sincronizar_resultados_exames_mock_data_flet()

    pacientes_csv, _, _ = _patch_pacientes()
    analises = _patch_ler_csv("analise_exames.csv")

    por_paciente = {}

    for r in analises:
        pid = _patch_get(r, "paciente_id", "id_paciente")
        if pid.isdigit() and len(pid) < 4:
            pid = pid.zfill(4)
        if pid:
            por_paciente.setdefault(pid, []).append(r)

    pacientes = []

    for p in pacientes_csv:
        pid = _patch_get(p, "paciente_id", "id")
        if pid.isdigit() and len(pid) < 4:
            pid = pid.zfill(4)

        exames = por_paciente.get(pid, [])
        datas = [_patch_data_exame(e) for e in exames if _patch_data_exame(e)]
        ultimo = max(datas) if datas else ""

        item = dict(p)
        item.update({
            "id": pid,
            "paciente_id": pid,
            "nome": _patch_get(p, "nome", "paciente_nome", "paciente"),
            "idade": _patch_get(p, "idade"),
            "sexo": _patch_get(p, "sexo"),
            "telefone": _patch_get(p, "telefone"),
            "email": _patch_get(p, "email"),
            "exames": len(exames),
            "ultimo_exame": ultimo,
            "status": _patch_status_paciente(exames),
        })

        pacientes.append(item)

    globals()["PACIENTES_MOCK"] = pacientes

    if pacientes:
        ids = [str(p.get("id", "")) for p in pacientes]
        atual = str(globals().get("PACIENTE_SELECIONADO_ID", "") or "")
        if atual not in ids:
            globals()["PACIENTE_SELECIONADO_ID"] = str(pacientes[0]["id"])

    print(f"[PATCH DATA_FLET] Pacientes carregados na UI: {len(pacientes)}")
    print("[PATCH DATA_FLET] Exames por paciente:", [(p.get("nome"), p.get("exames")) for p in pacientes])

    return pacientes


def _patch_pertence(row, pid, nome_norm):
    row_pid = _patch_get(row, "paciente_id", "id_paciente", "id")

    if row_pid.isdigit() and len(row_pid) < 4:
        row_pid = row_pid.zfill(4)

    if pid and row_pid and row_pid == pid:
        return True

    row_nome = _patch_get(row, "paciente_nome", "nome_paciente", "paciente", "nome")
    if nome_norm and row_nome and _patch_norm(row_nome) == nome_norm:
        return True

    return False


def excluir_paciente_e_vinculos(paciente):
    pid = _patch_get(paciente, "paciente_id", "id")
    if pid.isdigit() and len(pid) < 4:
        pid = pid.zfill(4)

    nome = _patch_get(paciente, "nome", "paciente_nome", "paciente")
    nome_norm = _patch_norm(nome)

    if not pid and not nome_norm:
        print("[PATCH DATA_FLET] Exclusão cancelada: paciente sem identificação.")
        return False

    cardapios = _patch_ler_csv("cardapios.csv")
    cardapio_ids = {
        _patch_get(c, "cardapio_id", "id")
        for c in cardapios
        if _patch_pertence(c, pid, nome_norm)
    }
    cardapio_ids = {c for c in cardapio_ids if c}

    arquivos = [
        "pacientes.csv",
        "exames.csv",
        "analise_exames.csv",
        "anamnese.csv",
        "recordatorio_habitual.csv",
        "recordatorio.csv",
        "antropometria.csv",
        "cardapios.csv",
        "cardapio_itens.csv",
        "evolucao_conduta.csv",
        "historico_edicoes.csv",
        "alimentos_recordatorio_personalizados.csv",
    ]

    total = 0

    for nome_csv in arquivos:
        caminho = _patch_data_dir() / nome_csv
        if not caminho.exists():
            continue

        rows = _patch_ler_csv(nome_csv)
        campos = _patch_campos_csv(nome_csv)
        novas = []
        removidos = 0

        for r in rows:
            remover = _patch_pertence(r, pid, nome_norm)

            if nome_csv == "cardapio_itens.csv":
                cid = _patch_get(r, "cardapio_id")
                if cid and cid in cardapio_ids:
                    remover = True

            if remover:
                removidos += 1
            else:
                novas.append(r)

        if removidos:
            _patch_salvar_csv(nome_csv, novas, campos)
            total += removidos
            print(f"[PATCH DATA_FLET] {nome_csv}: {removidos} removido(s).")

    if "RESULTADOS_EXAMES_MOCK" in globals():
        globals()["RESULTADOS_EXAMES_MOCK"] = [
            r for r in globals().get("RESULTADOS_EXAMES_MOCK", [])
            if not _patch_pertence(r, pid, nome_norm)
        ]

    # Recria o dicionário de exames cadastrados a partir do CSV após a exclusão.
    globals()["EXAMES_CADASTRADOS_MOCK"] = {}

    atualizar_pacientes_csv_real_definitivo()

    print(f"[PATCH DATA_FLET] Exclusão concluída para {nome or pid}. Total removido: {total}")
    return True

# ===== FIM PATCH SEGURO DATA_FLET: EXAMES ANALISE EXCLUSAO =====


# ===== PATCH AUTO-PERSISTENCIA EXAMES CSV =====

def _patch_raw_get(row, *chaves):
    if not isinstance(row, dict):
        return ""

    chaves_limpas = [_patch_limpar_chave(c) for c in chaves]

    for k, v in row.items():
        if _patch_limpar_chave(k) in chaves_limpas:
            if v is not None and str(v).strip() != "":
                return v

    return ""


def _patch_pid(row):
    pacientes, por_id, por_nome = _patch_pacientes()

    candidatos_id = []
    candidatos_nome = []

    if isinstance(row, dict):
        for campo in ["paciente_id", "id_paciente", "id"]:
            v = _patch_raw_get(row, campo)
            if v:
                candidatos_id.append(str(v).strip())

        for campo in ["paciente_nome", "nome_paciente", "paciente", "nome"]:
            v = _patch_raw_get(row, campo)
            if isinstance(v, dict):
                candidatos_id.append(str(v.get("id") or v.get("paciente_id") or "").strip())
                candidatos_nome.append(str(v.get("nome") or v.get("paciente") or "").strip())
            elif v:
                candidatos_nome.append(str(v).strip())

    selecionado = str(globals().get("PACIENTE_SELECIONADO_ID", "") or "").strip()
    if selecionado:
        candidatos_id.append(selecionado)

    for pid in candidatos_id:
        if pid.isdigit() and len(pid) < 4:
            pid = pid.zfill(4)

        if pid in por_id:
            return pid

    nomes_tratados = []

    for nome in candidatos_nome:
        nome = str(nome or "").strip()
        if not nome:
            continue

        nomes_tratados.append(nome)

        # Ex.: "Marizete Matos - 45 anos" -> "Marizete Matos"
        nome_sem_idade = _patch_re.sub(r"\s*-\s*\d+\s*anos?.*$", "", nome, flags=_patch_re.I).strip()
        if nome_sem_idade and nome_sem_idade != nome:
            nomes_tratados.append(nome_sem_idade)

    for nome in nomes_tratados:
        n = _patch_norm(nome)

        if n in por_nome:
            p = por_nome[n]
            pid = _patch_get(p, "paciente_id", "id")
            return pid.zfill(4) if pid.isdigit() and len(pid) < 4 else pid

        for nome_ref, p in por_nome.items():
            if n and (n.startswith(nome_ref) or nome_ref.startswith(n)):
                pid = _patch_get(p, "paciente_id", "id")
                return pid.zfill(4) if pid.isdigit() and len(pid) < 4 else pid

    return ""


def _patch_nome_exame(row):
    if isinstance(row, dict):
        for campo in ["nome_exame", "nome_padronizado", "exame", "exame_nome", "tipo_exame", "nome", "analito"]:
            v = _patch_raw_get(row, campo)

            if isinstance(v, dict):
                for sub in ["nome_exame", "nome", "descricao", "exame", "id"]:
                    sv = v.get(sub)
                    if sv:
                        texto = str(sv).strip()
                        ref = _patch_ref(texto)
                        return _patch_get(ref, "nome_exame", "nome") or texto

            elif isinstance(v, (list, tuple)) and v:
                texto = str(v[0]).strip()
                ref = _patch_ref(texto)
                return _patch_get(ref, "nome_exame", "nome") or texto

            elif v:
                texto = str(v).strip()
                ref = _patch_ref(texto)
                return _patch_get(ref, "nome_exame", "nome") or texto

        for campo in ["exame_id", "id_exame", "id"]:
            v = _patch_raw_get(row, campo)
            if v:
                texto = str(v).strip()
                ref = _patch_ref(texto)
                return _patch_get(ref, "nome_exame", "nome") or texto

    return ""


def _patch_resultado_valor(row):
    return (
        _patch_get(row, "resultado")
        or _patch_get(row, "valor")
        or _patch_get(row, "valor_resultado")
        or _patch_get(row, "resultado_exame")
    )


def _patch_persistir_resultado_item(item):
    if not isinstance(item, dict):
        return False

    pid = _patch_pid(item)
    nome_exame = _patch_nome_exame(item)
    resultado = _patch_resultado_valor(item)
    data_exame = _patch_data_exame(item)
    unidade = _patch_get(item, "unidade")

    if not pid or not nome_exame or not resultado:
        print(
            "[PATCH DATA_FLET] Ignorando exame sem dados mínimos:",
            {
                "pid": pid,
                "nome_exame": nome_exame,
                "resultado": resultado,
                "item": item,
            },
        )
        return False

    refs = _patch_refs()
    ref = _patch_ref(nome_exame, refs)

    if not unidade:
        unidade = _patch_get(ref, "unidade")

    exames = _patch_ler_csv("exames.csv")
    analises = _patch_ler_csv("analise_exames.csv")

    chave = (
        pid,
        _patch_norm(data_exame),
        _patch_norm(nome_exame),
        _patch_norm(resultado),
        _patch_norm(unidade),
    )

    chaves_exames = {_patch_chave(r) for r in exames}
    chaves_analises = {_patch_chave(r) for r in analises}

    mudou = False

    if chave not in chaves_exames:
        exames.append({
            "exame_id": _patch_proximo_id(exames, "exame_id", 4),
            "paciente_id": pid,
            "data_exame": data_exame,
            "nome_exame": nome_exame,
            "resultado": resultado,
            "unidade": unidade,
            "observacoes": _patch_get(item, "observacoes", "obs") or "Lançado pela interface NutriSoft",
        })

        _patch_salvar_csv(
            "exames.csv",
            exames,
            [
                "exame_id",
                "paciente_id",
                "data_exame",
                "nome_exame",
                "resultado",
                "unidade",
                "observacoes",
            ],
        )
        mudou = True

    if chave not in chaves_analises:
        analise = _patch_analisar(nome_exame, resultado, unidade, refs)

        analises.append({
            "analise_id": _patch_proximo_id(analises, "analise_id"),
            "paciente_id": pid,
            "data_exame": data_exame,
            "nome_exame": nome_exame,
            "nome_padronizado": analise["nome_padronizado"],
            "resultado": resultado,
            "unidade": unidade,
            "valor_min": analise["valor_min"],
            "valor_max": analise["valor_max"],
            "status": analise["status"],
            "mensagem": analise["mensagem"],
            "fonte_referencia": analise["fonte_referencia"],
        })

        _patch_salvar_csv(
            "analise_exames.csv",
            analises,
            [
                "analise_id",
                "paciente_id",
                "data_exame",
                "nome_exame",
                "nome_padronizado",
                "resultado",
                "unidade",
                "valor_min",
                "valor_max",
                "status",
                "mensagem",
                "fonte_referencia",
            ],
        )
        mudou = True

    if mudou:
        print(f"[PATCH DATA_FLET] Exame persistido em CSV: paciente={pid} | exame={nome_exame} | resultado={resultado} {unidade}")

    return mudou


class _PatchResultadosPersistentes(list):
    def append(self, item):
        super().append(item)

        try:
            persistiu = _patch_persistir_resultado_item(item)

            if persistiu:
                try:
                    sincronizar_resultados_exames_mock_data_flet()
                    print("[PATCH DATA_FLET] Interface/memória atualizada após salvar exame.")
                except Exception as exc:
                    print(f"[PATCH DATA_FLET] Exame salvo, mas falhou atualização da memória: {exc}")

        except Exception as exc:
            print(f"[PATCH DATA_FLET] Falha ao persistir exame no append: {exc}")


def sincronizar_resultados_exames_mock_data_flet():
    _patch_migrar_mock_para_csv()

    analises = _patch_ler_csv("analise_exames.csv")
    refs = _patch_refs()
    resultados = []

    for r in analises:
        pid = _patch_get(r, "paciente_id", "id_paciente")
        if pid.isdigit() and len(pid) < 4:
            pid = pid.zfill(4)

        nome_exame = _patch_nome_exame(r)
        unidade = _patch_get(r, "unidade")
        resultado = _patch_get(r, "resultado", "valor")
        data_exame = _patch_data_exame(r)

        ref = _patch_ref(nome_exame, refs)
        referencia = _patch_referencia_texto(ref, unidade)

        status = _patch_get(r, "status")
        if not status:
            status = _patch_analisar(nome_exame, resultado, unidade, refs)["status"]

        item = dict(r)
        item.update({
            "paciente_id": pid,
            "id_paciente": pid,
            "paciente": _patch_nome_paciente(pid),
            "paciente_nome": _patch_nome_paciente(pid),
            "data": data_exame,
            "data_exame": data_exame,
            "exame": nome_exame,
            "nome_exame": nome_exame,
            "nome_padronizado": _patch_get(r, "nome_padronizado") or nome_exame,
            "resultado": resultado,
            "unidade": unidade,
            "referencia": referencia,
            "referencia_texto": referencia,
            "status": status,
            "mensagem": _patch_get(r, "mensagem"),
            "fonte_referencia": _patch_get(r, "fonte_referencia"),
        })

        resultados.append(item)

    globals()["RESULTADOS_EXAMES_MOCK"] = _PatchResultadosPersistentes(resultados)

    cadastrados = {}

    for item in resultados:
        pid = _patch_get(item, "paciente_id", "id_paciente")
        if pid.isdigit() and len(pid) < 4:
            pid = pid.zfill(4)

        data = _patch_data_exame(item)
        nome_exame = _patch_nome_exame(item)
        ref = _patch_ref(nome_exame, refs)
        ref_id = _patch_get(ref, "id")

        if not pid or not data or not nome_exame:
            continue

        valores = [nome_exame]
        if ref_id:
            valores.append(ref_id)

        for chave in [(pid, data), (str(pid), data)]:
            cadastrados.setdefault(chave, [])
            for valor in valores:
                if valor and valor not in cadastrados[chave]:
                    cadastrados[chave].append(valor)

    globals()["EXAMES_CADASTRADOS_MOCK"] = cadastrados

    print(f"[PATCH DATA_FLET] Resultados sincronizados: {len(resultados)}")
    print(f"[PATCH DATA_FLET] Datas com exames cadastrados: {len(cadastrados)}")
    return resultados

# ===== FIM PATCH AUTO-PERSISTENCIA EXAMES CSV =====


# ===== PATCH TELA CADASTRO EXAMES: DATA E JA CADASTRADOS =====

def _patch_data_iso_cadastro(valor):
    texto = str(valor or "").strip()

    if not texto:
        return ""

    # dd/mm/aaaa -> aaaa-mm-dd
    m = _patch_re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", texto)
    if m:
        d, mth, y = m.groups()
        return f"{y}-{int(mth):02d}-{int(d):02d}"

    # aaaa-mm-dd
    m = _patch_re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", texto)
    if m:
        y, mth, d = m.groups()
        return f"{y}-{int(mth):02d}-{int(d):02d}"

    return texto


def _patch_data_br_cadastro(valor):
    iso = _patch_data_iso_cadastro(valor)

    m = _patch_re.match(r"^(\d{4})-(\d{2})-(\d{2})$", iso)
    if m:
        y, mth, d = m.groups()
        return f"{d}/{mth}/{y}"

    return str(valor or "").strip()


def chave_exames_paciente_data(paciente_id, data_exame):
    pid = str(paciente_id or "").strip()

    if pid.isdigit() and len(pid) < 4:
        pid = pid.zfill(4)

    return (pid, _patch_data_iso_cadastro(data_exame))


def _patch_token_exame_cadastrado(nome_exame):
    ref = _patch_ref(nome_exame)
    ref_id = _patch_get(ref, "id")

    if ref_id:
        return ref_id

    return str(nome_exame or "").strip()


def _patch_reconstruir_exames_cadastrados_por_data():
    global EXAMES_CADASTRADOS_MOCK

    cadastrados = {}

    for r in _patch_ler_csv("analise_exames.csv"):
        pid = _patch_get(r, "paciente_id", "id_paciente")

        if pid.isdigit() and len(pid) < 4:
            pid = pid.zfill(4)

        data_raw = _patch_data_exame(r)
        data_iso = _patch_data_iso_cadastro(data_raw)
        data_br = _patch_data_br_cadastro(data_raw)

        nome_exame = _patch_nome_exame(r)

        if not pid or not data_iso or not nome_exame:
            continue

        token = _patch_token_exame_cadastrado(nome_exame)

        if not token:
            continue

        # Mantém compatibilidade com telas que usam ISO e telas que usam DD/MM/AAAA.
        for data_key in {data_raw, data_iso, data_br}:
            if not data_key:
                continue

            chave = (pid, _patch_data_iso_cadastro(data_key))
            cadastrados.setdefault(chave, [])

            if token not in cadastrados[chave]:
                cadastrados[chave].append(token)

    EXAMES_CADASTRADOS_MOCK = cadastrados
    globals()["EXAMES_CADASTRADOS_MOCK"] = EXAMES_CADASTRADOS_MOCK

    print(f"[PATCH CADASTRO EXAMES] Índice paciente+data reconstruído: {len(cadastrados)} data(s).")
    return cadastrados


try:
    _patch_sync_original_cadastro_exames
except NameError:
    _patch_sync_original_cadastro_exames = sincronizar_resultados_exames_mock_data_flet


def sincronizar_resultados_exames_mock_data_flet():
    resultados = _patch_sync_original_cadastro_exames()
    _patch_reconstruir_exames_cadastrados_por_data()
    return resultados


try:
    _patch_exames_ja_original_cadastro
except NameError:
    _patch_exames_ja_original_cadastro = exames_ja_cadastrados_por_data


def exames_ja_cadastrados_por_data(paciente_id, data_exame):
    _patch_reconstruir_exames_cadastrados_por_data()
    return _patch_exames_ja_original_cadastro(paciente_id, data_exame)


try:
    _patch_exames_disponiveis_original_cadastro
except NameError:
    _patch_exames_disponiveis_original_cadastro = exames_disponiveis_por_data


def exames_disponiveis_por_data(paciente_id, data_exame):
    _patch_reconstruir_exames_cadastrados_por_data()
    return _patch_exames_disponiveis_original_cadastro(paciente_id, data_exame)

# ===== FIM PATCH TELA CADASTRO EXAMES: DATA E JA CADASTRADOS =====


# ===== PATCH CATALOGO EXAMES: DEDUP E GRUPOS =====

_EXAME_ALIASES_PADRAO = {
    "glucose": "Glicose",
    "glicemia": "Glicose",
    "glicose jejum": "Glicose",
    "glicose em jejum": "Glicose",
    "hemoglobina glicada hba1c": "Hemoglobina glicada",
    "hba1c": "Hemoglobina glicada",
    "colesterol": "Colesterol Total",
    "colesterol total": "Colesterol Total",
    "colesterol hdl": "HDL",
    "hdl colesterol": "HDL",
    "colesterol ldl": "LDL",
    "ldl colesterol": "LDL",
    "vldl colesterol": "VLDL",
    "colesterol vldl": "VLDL",
    "triglicerides": "Triglicerídeos",
    "triglicerideos": "Triglicerídeos",
    "tgo": "TGO / AST",
    "ast": "TGO / AST",
    "transaminase oxalacetica": "TGO / AST",
    "tgp": "TGP / ALT",
    "alt": "TGP / ALT",
    "transaminase piruvica": "TGP / ALT",
    "gama gt": "Gama GT",
    "ggt": "Gama GT",
    "gamma gt": "Gama GT",
    "fosfatase alcalina": "Fosfatase Alcalina",
    "creatinina sangue": "Creatinina",
    "creatinina serica": "Creatinina",
    "ureia sangue": "Ureia",
    "acido urico": "Ácido Úrico",
    "sodio": "Sódio",
    "potassio": "Potássio",
    "calcio": "Cálcio",
    "magnesio": "Magnésio",
    "ferritina serica": "Ferritina",
    "ferro serico": "Ferro",
    "vitamina d": "Vitamina D",
    "25 oh vitamina d": "Vitamina D",
    "vitamina b12": "Vitamina B12",
    "b12": "Vitamina B12",
    "tsh": "TSH",
    "t4 livre": "T4 Livre",
    "t3 livre": "T3 Livre",
    "hemograma": "Hemograma",
    "hemacias": "Hemácias",
    "leucocitos": "Leucócitos",
    "plaquetas": "Plaquetas",
    "insulina jejum": "Insulina",
    "insulina em jejum": "Insulina",
    "pcr": "Proteína C Reativa",
    "proteina c reativa": "Proteína C Reativa",
}

def _patch_nome_canonico_exame(nome):
    texto = str(nome or "").strip()
    n = _patch_norm(texto)

    if not n:
        return texto

    # Remove ruídos comuns vindos de laudos/listas
    n = n.replace("dosagem de ", "")
    n = n.replace("dosagem da ", "")
    n = n.replace("dosagem do ", "")
    n = n.replace("serico", "")
    n = n.replace("serica", "")
    n = " ".join(n.split())

    if n in _EXAME_ALIASES_PADRAO:
        return _EXAME_ALIASES_PADRAO[n]

    return texto


def _patch_grupo_exame_correto(nome, grupo_atual=""):
    n = _patch_norm(nome)

    regras = [
        ("Metabolismo glicídico", [
            "glicose", "glicemia", "hemoglobina glicada", "hba1c",
            "glicemia media", "insulina", "homa", "peptideo c"
        ]),
        ("Perfil Lipídico", [
            "colesterol", "hdl", "ldl", "vldl", "triglicer",
            "apolipoproteina", "lipoproteina"
        ]),
        ("Função Renal", [
            "creatinina", "ureia", "acido urico", "urina", "microalbuminuria",
            "clearance", "taxa de filtracao", "albumina creatinina"
        ]),
        ("Função Hepática", [
            "tgo", "ast", "tgp", "alt", "gama gt", "ggt",
            "fosfatase alcalina", "bilirrubina", "albumina", "proteinas totais"
        ]),
        ("Hemograma", [
            "hemograma", "hemacia", "hemoglobina", "hematocrito",
            "leucocito", "neutrofilo", "linfocito", "monocito",
            "eosinofilo", "basofilo", "plaqueta", "vcm", "hcm", "chcm", "rdw"
        ]),
        ("Vitaminas e Minerais", [
            "vitamina", "25 oh", "b12", "folato", "ferro", "ferritina",
            "transferrina", "calcio", "magnesio", "zinco", "selenio"
        ]),
        ("Eletrólitos", [
            "sodio", "potassio", "cloro", "fosforo", "bicarbonato"
        ]),
        ("Tireoide", [
            "tsh", "t4", "t3", "tireoglobulina", "anti tpo", "anti tg",
            "trab", "tireoide"
        ]),
        ("Inflamação e Imunologia", [
            "pcr", "proteina c reativa", "vhs", "fator reumatoide",
            "ana", "fan", "imunoglobulina"
        ]),
        ("Coagulação", [
            "tp", "ttpa", "inr", "protrombina", "fibrinogenio", "d dimero"
        ]),
        ("Hormônios", [
            "testosterona", "estradiol", "progesterona", "prolactina",
            "cortisol", "lh", "fsh", "dhea", "shbg"
        ]),
    ]

    for grupo, termos in regras:
        if any(t in n for t in termos):
            return grupo

    return str(grupo_atual or "Outros").strip() or "Outros"


def _patch_id_canonico_exame(nome):
    nome_can = _patch_nome_canonico_exame(nome)
    n = _patch_norm(nome_can)
    n = n.replace("%", "percentual")
    n = _patch_re.sub(r"[^a-z0-9]+", "_", n).strip("_")
    return n or _patch_re.sub(r"[^a-z0-9]+", "_", _patch_norm(nome)).strip("_")


def _patch_normalizar_item_exame(item):
    if not isinstance(item, dict):
        return item

    novo = dict(item)

    nome_original = (
        novo.get("nome_exame")
        or novo.get("nome")
        or novo.get("exame")
        or novo.get("descricao")
        or novo.get("id")
        or ""
    )

    nome_can = _patch_nome_canonico_exame(nome_original)
    grupo = _patch_grupo_exame_correto(nome_can, novo.get("grupo"))

    id_can = _patch_id_canonico_exame(nome_can)

    novo["id"] = novo.get("id") or id_can
    novo["id_canonico"] = id_can
    novo["nome"] = nome_can
    novo["nome_exame"] = nome_can
    novo["grupo"] = grupo

    return novo


def _patch_dedup_lista_exames(lista):
    vistos = {}
    ordem = []

    for item in list(lista or []):
        if not isinstance(item, dict):
            continue

        item = _patch_normalizar_item_exame(item)
        chave = item.get("id_canonico") or _patch_id_canonico_exame(
            item.get("nome_exame") or item.get("nome") or item.get("id")
        )

        if not chave:
            continue

        if chave not in vistos:
            vistos[chave] = item
            ordem.append(chave)
        else:
            atual = vistos[chave]

            # Mantém o item mais completo, preservando referência/fonte/unidade.
            for campo in [
                "referencia", "referencia_texto", "valor_min", "valor_max",
                "unidade", "fonte", "fonte_referencia", "status", "observacoes"
            ]:
                if not atual.get(campo) and item.get(campo):
                    atual[campo] = item.get(campo)

            if atual.get("grupo") in ["Outros", "", None] and item.get("grupo"):
                atual["grupo"] = item.get("grupo")

            vistos[chave] = atual

    return [vistos[k] for k in ordem]


def _patch_ordenar_exames_catalogo(lista):
    ordem_grupos = {
        "Metabolismo glicídico": 1,
        "Perfil Lipídico": 2,
        "Função Renal": 3,
        "Função Hepática": 4,
        "Hemograma": 5,
        "Vitaminas e Minerais": 6,
        "Eletrólitos": 7,
        "Tireoide": 8,
        "Inflamação e Imunologia": 9,
        "Coagulação": 10,
        "Hormônios": 11,
        "Outros": 99,
    }

    return sorted(
        lista or [],
        key=lambda x: (
            ordem_grupos.get(str(x.get("grupo") or "Outros"), 98),
            _patch_norm(x.get("nome_exame") or x.get("nome") or "")
        )
    )


try:
    _patch_criar_opcoes_grupos_original
except NameError:
    _patch_criar_opcoes_grupos_original = criar_opcoes_grupos_exames


def criar_opcoes_grupos_exames(lista_exames):
    lista = _patch_ordenar_exames_catalogo(_patch_dedup_lista_exames(lista_exames))
    return _patch_criar_opcoes_grupos_original(lista)


try:
    _patch_criar_opcoes_exames_original
except NameError:
    _patch_criar_opcoes_exames_original = criar_opcoes_exames_por_grupo


def criar_opcoes_exames_por_grupo(lista_exames, grupo=None, exames_ja_cadastrados=None):
    lista = _patch_ordenar_exames_catalogo(_patch_dedup_lista_exames(lista_exames))

    # Garante que bloqueio funcione tanto por id antigo quanto por id/nome canônico.
    ja = set(exames_ja_cadastrados or [])
    ja_expandido = set(ja)

    for v in list(ja):
        ja_expandido.add(_patch_id_canonico_exame(v))
        ja_expandido.add(_patch_nome_canonico_exame(v))

    filtrada = []
    for item in lista:
        item = _patch_normalizar_item_exame(item)
        tokens = {
            str(item.get("id") or ""),
            str(item.get("id_canonico") or ""),
            str(item.get("nome") or ""),
            str(item.get("nome_exame") or ""),
            _patch_id_canonico_exame(item.get("nome_exame") or item.get("nome")),
        }

        if tokens & ja_expandido:
            continue

        filtrada.append(item)

    return _patch_criar_opcoes_exames_original(filtrada, grupo, ja_expandido)


try:
    _patch_exames_disponiveis_grupo_original
except NameError:
    _patch_exames_disponiveis_grupo_original = exames_disponiveis_por_data


def exames_disponiveis_por_data(paciente_id, data_exame):
    lista = _patch_exames_disponiveis_grupo_original(paciente_id, data_exame)
    return _patch_ordenar_exames_catalogo(_patch_dedup_lista_exames(lista))


try:
    _patch_garantir_nome_original
except NameError:
    _patch_garantir_nome_original = garantir_nome_exame_item


def garantir_nome_exame_item(item):
    item = _patch_garantir_nome_original(item)
    return _patch_normalizar_item_exame(item)


try:
    _patch_nome_exibicao_original
except NameError:
    _patch_nome_exibicao_original = nome_exame_para_exibicao


def nome_exame_para_exibicao(item):
    if isinstance(item, dict):
        item = _patch_normalizar_item_exame(item)
        return item.get("nome_exame") or item.get("nome") or item.get("id") or "-"
    return _patch_nome_exibicao_original(item)

# ===== FIM PATCH CATALOGO EXAMES: DEDUP E GRUPOS =====














# ===== PATCH UX TABELAS NUTRICAO: LINHAS ALTAS E TEXTO WRAP =====

# Corrige tabelas com textos longos cortados verticalmente.
# A tela Nutrição usa DataTable em várias versões (_nutri, _ng, _nr),
# então o ajuste é aplicado de forma global e segura.

try:
    _patch_ft_datatable_original
except NameError:
    _patch_ft_datatable_original = ft.DataTable


def _patch_datatable_com_linhas_altas(*args, **kwargs):
    # Aplica linha alta SOMENTE em tabelas largas, como "Análise dos exames".
    # Tabelas compactas, como "Exames alterados", devem manter altura normal.
    colunas = kwargs.get("columns")

    if colunas is None and args:
        try:
            # Algumas versões recebem columns como primeiro argumento nomeado/posicional.
            possivel = args[0]
            if isinstance(possivel, list):
                colunas = possivel
        except Exception:
            colunas = None

    qtd_colunas = len(colunas or [])

    tabela_longa_nutricional = qtd_colunas >= 5

    if not tabela_longa_nutricional:
        # Não altera tabelas simples: Data, Exame, Resultado, Status etc.
        return _patch_ft_datatable_original(*args, **kwargs)

    # Remove altura fixa antiga, quando existir.
    kwargs.pop("data_row_height", None)

    # Altura confortável para textos longos de interpretação/conduta.
    kwargs.setdefault("data_row_min_height", 84)
    kwargs.setdefault("data_row_max_height", 180)
    kwargs.setdefault("heading_row_height", 58)
    kwargs.setdefault("column_spacing", 22)
    kwargs.setdefault("horizontal_margin", 12)

    try:
        return _patch_ft_datatable_original(*args, **kwargs)
    except TypeError:
        # Fallback para versões antigas do Flet.
        kwargs.pop("data_row_min_height", None)
        kwargs.pop("data_row_max_height", None)
        kwargs.setdefault("data_row_height", 120)
        return _patch_ft_datatable_original(*args, **kwargs)


ft.DataTable = _patch_datatable_com_linhas_altas


def _patch_texto_tabela_wrap(texto, largura=160, negrito=False, tamanho=11):
    return ft.Container(
        width=largura,
        padding=8,
        content=ft.Text(
            str(texto or "-"),
            size=tamanho,
            weight=ft.FontWeight.BOLD if negrito else ft.FontWeight.NORMAL,
            color="#111827" if negrito else "#374151",
            no_wrap=False,
            max_lines=None,
            overflow=ft.TextOverflow.VISIBLE,
        ),
    )


# Sobrescreve helpers usados nas versões da tela de Nutrição.
# Usa *args/**kwargs para não quebrar chamadas antigas com parâmetros diferentes.

def _patch_cell_generico(*args, **kwargs):
    texto = args[0] if len(args) >= 1 else kwargs.get("texto", "")
    largura = args[1] if len(args) >= 2 else kwargs.get("largura", kwargs.get("width", 160))
    negrito = kwargs.get("negrito", kwargs.get("bold", False))
    tamanho = kwargs.get("tamanho", kwargs.get("size", 11))
    return _patch_texto_tabela_wrap(texto, largura, negrito, tamanho)


def _nutri_cell_tabela(*args, **kwargs):
    return _patch_cell_generico(*args, **kwargs)


def _nutri_texto_tabela(*args, **kwargs):
    return _patch_cell_generico(*args, **kwargs)


def _ng_cell_tabela(*args, **kwargs):
    return _patch_cell_generico(*args, **kwargs)


def _ng_texto_tabela(*args, **kwargs):
    return _patch_cell_generico(*args, **kwargs)


def _nr_cell_tabela(*args, **kwargs):
    return _patch_cell_generico(*args, **kwargs)


def _nr_texto_tabela(*args, **kwargs):
    return _patch_cell_generico(*args, **kwargs)


def _ns_cell_tabela(*args, **kwargs):
    return _patch_cell_generico(*args, **kwargs)


def _ns_texto_tabela(*args, **kwargs):
    return _patch_cell_generico(*args, **kwargs)

# ===== FIM PATCH UX TABELAS NUTRICAO: LINHAS ALTAS E TEXTO WRAP =====


# ===== PATCH ANALISE INTELIGENTE: CONDUTAS ESPECIFICAS =====

def _ia_norm(valor):
    try:
        return _patch_norm(valor)
    except Exception:
        import unicodedata, re
        texto = str(valor or "").strip().lower()
        texto = unicodedata.normalize("NFKD", texto)
        texto = "".join(c for c in texto if not unicodedata.combining(c))
        texto = re.sub(r"[^a-z0-9%/., ]+", " ", texto)
        return " ".join(texto.split())


def _ia_exame_por_texto(texto):
    n = _ia_norm(texto)

    exames = [
        ("Hemoglobina glicada", ["hemoglobina glicada", "hba1c"]),
        ("Glicose", ["glicose", "glicemia"]),
        ("Insulina", ["insulina"]),
        ("Triglicerídeos", ["triglicerideos", "triglicerides"]),
        ("Ferritina", ["ferritina"]),
        ("Vitamina D", ["vitamina d", "25 oh"]),
        ("Vitamina B12", ["vitamina b12", "b12"]),
        ("Colesterol Total", ["colesterol total"]),
        ("LDL", ["ldl"]),
        ("HDL", ["hdl"]),
        ("VLDL", ["vldl"]),
        ("Creatinina", ["creatinina"]),
        ("Ureia", ["ureia"]),
        ("Ácido Úrico", ["acido urico"]),
        ("TGO / AST", ["tgo", "ast"]),
        ("TGP / ALT", ["tgp", "alt"]),
        ("Gama GT", ["gama gt", "ggt"]),
        ("Fosfatase Alcalina", ["fosfatase alcalina"]),
        ("Bilirrubinas", ["bilirrubina"]),
        ("Hemoglobina", ["hemoglobina"]),
        ("Hemácias", ["hemacias"]),
        ("Leucócitos", ["leucocitos"]),
        ("Plaquetas", ["plaquetas"]),
        ("Sódio", ["sodio"]),
        ("Potássio", ["potassio"]),
        ("Magnésio", ["magnesio"]),
        ("Cálcio", ["calcio"]),
        ("TSH", ["tsh"]),
        ("T4 Livre", ["t4 livre"]),
        ("T3 Livre", ["t3 livre"]),
        ("Proteína C Reativa", ["proteina c reativa", "pcr"]),
    ]

    for nome, termos in exames:
        if any(t in n for t in termos):
            return nome

    # fallback: pega o texto antes de "acima/abaixo"
    for sep in [" acima", " abaixo", " alterado", " fora"]:
        if sep in n:
            bruto = str(texto).split(sep.strip())[0].strip()
            return bruto[:40] if bruto else "Exame"

    return "Exame"


def _ia_direcao(texto):
    n = _ia_norm(texto)

    if any(t in n for t in ["abaixo", "baixo", "reduzido", "deficiencia"]):
        return "baixo"

    if any(t in n for t in ["acima", "alto", "elevado", "aumentado"]):
        return "alto"

    return "alterado"


def _ia_interpretacao(direcao):
    if direcao == "alto":
        return "Acima da referência"
    if direcao == "baixo":
        return "Abaixo da referência"
    return "Fora da referência"


def _ia_possivel_alteracao(exame, direcao):
    e = _ia_norm(exame)

    if "glicose" in e:
        return "Hiperglicemia no exame. Avaliar controle glicêmico, resistência insulínica e contexto de jejum."
    if "hemoglobina glicada" in e:
        return "Média glicêmica elevada nas últimas semanas, sugerindo pior controle glicêmico crônico."
    if "insulina" in e:
        return "Hiperinsulinemia, frequentemente associada à resistência insulínica e maior demanda pancreática."
    if "triglicer" in e:
        return "Triglicerídeos elevados, associados a excesso de carboidratos refinados, álcool, resistência insulínica ou esteatose."
    if "ferritina" in e and direcao == "alto":
        return "Ferritina elevada. Pode refletir inflamação, sobrecarga de ferro, alteração hepática/metabólica ou suplementação."
    if "ferritina" in e and direcao == "baixo":
        return "Ferritina reduzida, sugerindo baixa reserva de ferro e risco de deficiência."
    if "vitamina d" in e and direcao == "baixo":
        return "Vitamina D abaixo do ideal, com impacto potencial em saúde óssea, imunidade e função muscular."
    if "vitamina b12" in e and direcao == "baixo":
        return "Vitamina B12 baixa, podendo impactar energia, função neurológica e produção de células sanguíneas."
    if "colesterol total" in e:
        return "Colesterol total elevado. Interpretar junto com LDL, HDL, triglicerídeos e risco cardiovascular global."
    if e == "ldl":
        return "LDL elevado, marcador relevante para risco cardiovascular e aterosclerótico."
    if e == "hdl" and direcao == "baixo":
        return "HDL baixo, geralmente associado a sedentarismo, resistência insulínica, tabagismo ou pior qualidade alimentar."
    if "creatinina" in e or "ureia" in e:
        return "Alteração de marcador renal. Interpretar com hidratação, massa muscular, ingestão proteica e função renal."
    if "acido urico" in e:
        return "Ácido úrico alterado, associado a metabolismo de purinas, resistência insulínica, álcool, frutose e risco de gota."
    if any(t in e for t in ["tgo", "tgp", "gama gt", "fosfatase", "bilirrubina"]):
        return "Marcador hepático alterado. Avaliar álcool, gordura hepática, medicamentos, inflamação e padrão alimentar."
    if any(t in e for t in ["hemoglobina", "hemacias"]):
        return "Alteração hematológica. Avaliar ferro, B12, folato, hidratação e perdas sanguíneas."
    if "leucocitos" in e:
        return "Alteração de leucócitos, podendo refletir resposta inflamatória, infecciosa ou imunológica."
    if "plaquetas" in e:
        return "Plaquetas alteradas. Interpretar com hemograma completo, inflamação e avaliação médica."
    if any(t in e for t in ["sodio", "potassio", "magnesio", "calcio"]):
        return "Eletrólito/mineral alterado. Avaliar hidratação, função renal, medicamentos, ingestão alimentar e perdas."
    if any(t in e for t in ["tsh", "t4", "t3"]):
        return "Marcador tireoidiano alterado. Avaliar metabolismo, sintomas, medicamentos e acompanhamento endocrinológico."
    if "proteina c reativa" in e:
        return "Marcador inflamatório elevado. Avaliar infecção, inflamação crônica, composição corporal e padrão alimentar."

    return f"{exame} {('acima' if direcao == 'alto' else 'abaixo' if direcao == 'baixo' else 'fora')} da referência laboratorial."


def _ia_conduta_nutricional(exame, direcao):
    e = _ia_norm(exame)

    if "glicose" in e:
        return "Priorizar controle de carga glicêmica: reduzir açúcar, bebidas adoçadas, farinha branca e grandes porções de carboidrato isolado. Distribuir carboidratos ao longo do dia, associando proteína, fibras e gorduras boas nas refeições."
    if "hemoglobina glicada" in e:
        return "Estruturar plano alimentar para controle glicêmico contínuo: carboidratos de menor índice glicêmico, aumento de fibras, redução de ultraprocessados e ajuste de porções. Monitorar adesão e evolução em 8 a 12 semanas."
    if "insulina" in e:
        return "Focar em resistência insulínica: reduzir beliscos doces/refinados, evitar picos glicêmicos, aumentar proteína no café da manhã e refeições principais, incluir fibras e estimular rotina de atividade física conforme liberação clínica."
    if "triglicer" in e:
        return "Reduzir açúcar, sucos, refrigerantes, álcool, doces, pães/massas em excesso e ultraprocessados. Priorizar peixe, azeite, castanhas em porções controladas, legumes, verduras e carboidratos integrais conforme necessidade energética."
    if "ferritina" in e and direcao == "alto":
        return "Não indicar suplementação de ferro sem investigação. Reduzir álcool e ultraprocessados, avaliar excesso de carnes vermelhas/processadas e priorizar padrão anti-inflamatório com vegetais, leguminosas, fibras e gorduras de boa qualidade."
    if "ferritina" in e and direcao == "baixo":
        return "Aumentar fontes de ferro conforme tolerância: carnes magras, ovos, feijões e vegetais verde-escuros. Associar vitamina C nas refeições e evitar café/chá junto das principais fontes de ferro."
    if "vitamina d" in e and direcao == "baixo":
        return "Avaliar suplementação com profissional habilitado e exposição solar segura. Garantir ingestão adequada de gorduras boas e alimentos como ovos, peixes e laticínios fortificados quando compatíveis com o plano alimentar."
    if "vitamina b12" in e and direcao == "baixo":
        return "Avaliar ingestão de alimentos de origem animal e necessidade de suplementação. Investigar uso de metformina, antiácidos, restrições alimentares e sintomas neurológicos ou hematológicos."
    if "colesterol total" in e or e == "ldl":
        return "Adotar padrão cardioprotetor: reduzir gordura saturada, embutidos, frituras e ultraprocessados; aumentar fibras solúveis, aveia, leguminosas, frutas, vegetais, azeite e oleaginosas em porções planejadas."
    if e == "hdl" and direcao == "baixo":
        return "Melhorar qualidade da gordura alimentar e rotina de exercício: azeite, peixes, castanhas em porção controlada e redução de açúcar/refinados. Evitar tabagismo e sedentarismo."
    if "creatinina" in e or "ureia" in e:
        return "Revisar ingestão proteica, hidratação e uso de suplementos como creatina/proteína. Não restringir proteína sem avaliar função renal, massa muscular e orientação profissional."
    if "acido urico" in e:
        return "Reduzir álcool, especialmente cerveja, excesso de carnes/miúdos, embutidos, frutos do mar e bebidas adoçadas/frutose. Aumentar hidratação e priorizar padrão alimentar com vegetais e alimentos pouco processados."
    if any(t in e for t in ["tgo", "tgp", "gama gt", "fosfatase", "bilirrubina"]):
        return "Priorizar estratégia hepática: reduzir álcool, açúcar, frituras e ultraprocessados; favorecer perda de gordura corporal quando indicada, aumentar fibras, vegetais e padrão mediterrâneo."
    if any(t in e for t in ["hemoglobina", "hemacias"]):
        return "Avaliar ferro, B12, folato e ingestão proteica. Ajustar fontes alimentares conforme a deficiência provável e investigar perdas sanguíneas ou baixa absorção quando persistente."
    if "leucocitos" in e:
        return "Não há conduta nutricional isolada específica. Reforçar padrão anti-inflamatório, hidratação, sono adequado e investigar sinais infecciosos/inflamatórios com avaliação clínica."
    if "plaquetas" in e:
        return "Conduta nutricional deve ser cautelosa. Evitar suplementação sem indicação e correlacionar com hemograma, inflamação, medicamentos e avaliação médica."
    if any(t in e for t in ["sodio", "potassio", "magnesio", "calcio"]):
        return "Revisar hidratação, consumo de ultraprocessados, reposição de eletrólitos, medicamentos e perdas por suor, vômitos ou diarreia. Ajustar alimentos fonte conforme o mineral alterado."
    if any(t in e for t in ["tsh", "t4", "t3"]):
        return "Ajustar suporte nutricional da tireoide: proteína adequada, selênio, zinco, ferro e iodo conforme necessidade. Evitar suplementação isolada sem confirmar deficiência."
    if "proteina c reativa" in e:
        return "Focar em padrão anti-inflamatório: vegetais variados, frutas, leguminosas, peixes, azeite, fibras e redução de ultraprocessados, açúcar, álcool e excesso calórico."

    return "Individualizar conduta conforme anamnese, recordatório, medicamentos, sintomas e objetivo nutricional. Reavaliar o marcador após intervenção alimentar planejada."


def _ia_complementares(exame, direcao):
    e = _ia_norm(exame)

    if "glicose" in e:
        return "Hemoglobina glicada, insulina, HOMA-IR, triglicerídeos, HDL e circunferência abdominal."
    if "hemoglobina glicada" in e:
        return "Glicemia de jejum, insulina, HOMA-IR, perfil lipídico e avaliação clínica para diabetes."
    if "insulina" in e:
        return "Glicose, hemoglobina glicada, HOMA-IR, triglicerídeos, HDL, cintura e pressão arterial."
    if "triglicer" in e:
        return "Perfil lipídico completo, glicose, hemoglobina glicada, TGO, TGP, Gama GT e avaliação de álcool."
    if "ferritina" in e:
        return "Ferro sérico, transferrina, saturação de transferrina, PCR, TGO, TGP, Gama GT e hemograma."
    if "vitamina d" in e:
        return "Cálcio, fósforo, magnésio, PTH e nova dosagem após intervenção/suplementação."
    if "vitamina b12" in e:
        return "Hemograma, VCM, folato, homocisteína e investigação de absorção quando necessário."
    if "colesterol total" in e or e in ["ldl", "hdl", "vldl"]:
        return "Perfil lipídico completo, ApoB quando disponível, glicose, HbA1c, PCR e avaliação de risco cardiovascular."
    if "creatinina" in e or "ureia" in e:
        return "TFG estimada, urina tipo I, relação albumina/creatinina, hidratação e revisão de suplementos."
    if "acido urico" in e:
        return "Função renal, glicose, insulina, triglicerídeos, histórico de gota e consumo de álcool/frutose."
    if any(t in e for t in ["tgo", "tgp", "gama gt", "fosfatase", "bilirrubina"]):
        return "TGO, TGP, Gama GT, bilirrubinas, ferritina, triglicerídeos e avaliação de esteatose/álcool."
    if any(t in e for t in ["hemoglobina", "hemacias"]):
        return "Ferritina, ferro, transferrina, B12, folato, reticulócitos e investigação clínica."
    if "leucocitos" in e:
        return "Hemograma completo, PCR, sintomas recentes e avaliação médica se persistente."
    if "plaquetas" in e:
        return "Hemograma repetido, PCR, ferritina, função hepática e avaliação médica."
    if any(t in e for t in ["sodio", "potassio", "magnesio", "calcio"]):
        return "Função renal, hidratação, medicamentos, perdas gastrointestinais/suor e repetição do eletrólito."
    if any(t in e for t in ["tsh", "t4", "t3"]):
        return "T4 livre, T3 livre, anti-TPO, anti-TG, ferritina, zinco, selênio e avaliação endocrinológica."
    if "proteina c reativa" in e:
        return "Hemograma, ferritina, glicose, perfil lipídico, composição corporal e investigação de foco inflamatório."

    return "Repetir exame e avaliar marcadores relacionados conforme hipótese clínica."


def _ia_linha_from_item(item):
    texto = str(item or "").strip()

    if isinstance(item, dict):
        exame = item.get("exame") or item.get("nome_exame") or item.get("nome") or _ia_exame_por_texto(str(item))
        direcao = _ia_direcao(item.get("status") or item.get("interpretacao") or item.get("mensagem") or texto)
    else:
        exame = _ia_exame_por_texto(texto)
        direcao = _ia_direcao(texto)

    return {
        "exame": exame,
        "interpretacao": _ia_interpretacao(direcao),
        "possivel": _ia_possivel_alteracao(exame, direcao),
        "conduta": _ia_conduta_nutricional(exame, direcao),
        "complementares": _ia_complementares(exame, direcao),
    }


def _nutri_tabela_analise_a_partir_de_insights(itens):
    linhas = []

    for item in itens or []:
        texto = str(item or "").strip()
        n = _ia_norm(texto)

        # Evita transformar insights de hábitos gerais em exames laboratoriais.
        if any(t in n for t in ["recordatorio", "belisco", "agua", "sono", "atividade fisica", "fim de semana"]):
            continue

        linhas.append(_ia_linha_from_item(item))

    if not linhas:
        return ft.Container(
            padding=16,
            border_radius=12,
            bgcolor="#F8FAFC",
            content=ft.Text(
                "Nenhum exame alterado para análise nutricional específica.",
                size=12,
                color="#64748B",
            ),
        )

    return ft.Container(
        padding=8,
        border_radius=12,
        bgcolor="#F8FAFC",
        content=ft.DataTable(
            columns=[
                ft.DataColumn(_nutri_cell_tabela("Exame", 130, negrito=True)),
                ft.DataColumn(_nutri_cell_tabela("Interpretação", 150, negrito=True)),
                ft.DataColumn(_nutri_cell_tabela("Possível alteração", 250, negrito=True)),
                ft.DataColumn(_nutri_cell_tabela("Conduta / possível tratamento nutricional", 360, negrito=True)),
                ft.DataColumn(_nutri_cell_tabela("Complementares", 290, negrito=True)),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(_nutri_cell_tabela(linha["exame"], 130)),
                        ft.DataCell(_nutri_cell_tabela(linha["interpretacao"], 150)),
                        ft.DataCell(_nutri_cell_tabela(linha["possivel"], 250)),
                        ft.DataCell(_nutri_cell_tabela(linha["conduta"], 360)),
                        ft.DataCell(_nutri_cell_tabela(linha["complementares"], 290)),
                    ]
                )
                for linha in linhas
            ],
        ),
    )

# ===== FIM PATCH ANALISE INTELIGENTE: CONDUTAS ESPECIFICAS =====


# ===== PATCH UX ANALISE INTELIGENTE: TABELA COM SCROLL HORIZONTAL =====

def _ia_scroll_horizontal_value():
    try:
        return ft.ScrollMode.AUTO
    except Exception:
        return "auto"


def _ia_tabela_cell(texto, largura=160, negrito=False, tamanho=11):
    return ft.Container(
        width=largura,
        padding=6,
        content=ft.Text(
            str(texto or "-"),
            size=tamanho,
            weight=ft.FontWeight.BOLD if negrito else ft.FontWeight.NORMAL,
            color="#111827" if negrito else "#374151",
            no_wrap=False,
            max_lines=None,
            overflow=ft.TextOverflow.VISIBLE,
        ),
    )


def _nutri_tabela_analise_a_partir_de_insights(itens):
    linhas = []

    for item in itens or []:
        texto = str(item or "").strip()
        n = _ia_norm(texto)

        # Evita que resumos e hábitos gerais entrem como se fossem exames.
        if any(t in n for t in [
            "resumo",
            "recordatorio",
            "belisco",
            "agua",
            "sono",
            "atividade fisica",
            "fim de semana",
            "exame s analisado",
            "result fora",
        ]):
            continue

        linha = _ia_linha_from_item(item)

        exame_norm = _ia_norm(linha.get("exame"))
        if exame_norm in ["resumo", "exame", ""]:
            continue

        linhas.append(linha)

    if not linhas:
        return ft.Container(
            padding=16,
            border_radius=12,
            bgcolor="#F8FAFC",
            content=ft.Text(
                "Nenhum exame alterado para análise nutricional específica.",
                size=12,
                color="#64748B",
            ),
        )

    tabela = ft.DataTable(
        columns=[
            ft.DataColumn(_ia_tabela_cell("Exame", 120, negrito=True, tamanho=10)),
            ft.DataColumn(_ia_tabela_cell("Interpretação", 125, negrito=True, tamanho=10)),
            ft.DataColumn(_ia_tabela_cell("Possível alteração", 240, negrito=True, tamanho=10)),
            ft.DataColumn(_ia_tabela_cell("Conduta / possível tratamento nutricional", 330, negrito=True, tamanho=10)),
            ft.DataColumn(_ia_tabela_cell("Complementares", 260, negrito=True, tamanho=10)),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(_ia_tabela_cell(linha["exame"], 120)),
                    ft.DataCell(_ia_tabela_cell(linha["interpretacao"], 125)),
                    ft.DataCell(_ia_tabela_cell(linha["possivel"], 240)),
                    ft.DataCell(_ia_tabela_cell(linha["conduta"], 330)),
                    ft.DataCell(_ia_tabela_cell(linha["complementares"], 260)),
                ]
            )
            for linha in linhas
        ],
        column_spacing=12,
        horizontal_margin=8,
    )

    return ft.Container(
        padding=8,
        border_radius=12,
        bgcolor="#F8FAFC",
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Text(
                    "Análise inteligente por exame",
                    size=13,
                    weight=ft.FontWeight.BOLD,
                    color="#111827",
                ),
                ft.Text(
                    "Role horizontalmente para visualizar todas as colunas.",
                    size=11,
                    color="#64748B",
                ),
                ft.Row(
                    scroll=_ia_scroll_horizontal_value(),
                    controls=[tabela],
                ),
            ],
        ),
    )

# ===== FIM PATCH UX ANALISE INTELIGENTE: TABELA COM SCROLL HORIZONTAL =====























# ===== PATCH PERFORMANCE WINDOWS: CACHE CSV E LISTAS =====

# Objetivo:
# Reduzir lentidão no Windows evitando releitura excessiva dos CSVs,
# reconstrução repetida de índices e recálculo da lista de exames a cada atualização visual.

_PERF_CSV_CACHE = {}
_PERF_REFS_CACHE = {"key": None, "value": None}
_PERF_PACIENTES_CACHE = {"key": None, "value": None}
_PERF_CADASTRADOS_CACHE = {"key": None, "value": None}
_PERF_DISPONIVEIS_CACHE = {}
_PERF_BLOQUEADOS_CACHE = {}
_PERF_SYNC_CACHE = {"key": None, "value": None}
_PERF_PACIENTES_UI_CACHE = {"key": None, "value": None}


def _perf_mtime(nome_csv):
    try:
        caminho = _patch_data_dir() / nome_csv
        if caminho.exists():
            return caminho.stat().st_mtime_ns
    except Exception:
        pass
    return 0


def _perf_key_base():
    return (
        _perf_mtime("pacientes.csv"),
        _perf_mtime("exames.csv"),
        _perf_mtime("analise_exames.csv"),
        _perf_mtime("referencias_exames.csv"),
        _perf_mtime("alias_exames.csv"),
    )


def _perf_limpar_cache(nome_csv=None):
    global _PERF_CSV_CACHE

    if nome_csv:
        _PERF_CSV_CACHE.pop(nome_csv, None)
    else:
        _PERF_CSV_CACHE.clear()

    _PERF_REFS_CACHE["key"] = None
    _PERF_REFS_CACHE["value"] = None

    _PERF_PACIENTES_CACHE["key"] = None
    _PERF_PACIENTES_CACHE["value"] = None

    _PERF_CADASTRADOS_CACHE["key"] = None
    _PERF_CADASTRADOS_CACHE["value"] = None

    _PERF_SYNC_CACHE["key"] = None
    _PERF_SYNC_CACHE["value"] = None

    _PERF_PACIENTES_UI_CACHE["key"] = None
    _PERF_PACIENTES_UI_CACHE["value"] = None

    _PERF_DISPONIVEIS_CACHE.clear()
    _PERF_BLOQUEADOS_CACHE.clear()


def _perf_clone_rows(rows):
    saida = []
    for r in rows or []:
        if isinstance(r, dict):
            saida.append(dict(r))
        else:
            saida.append(r)
    return saida


try:
    _perf_ler_csv_original
except NameError:
    _perf_ler_csv_original = _patch_ler_csv


def _patch_ler_csv(nome):
    mtime = _perf_mtime(nome)
    cache = _PERF_CSV_CACHE.get(nome)

    if cache and cache.get("mtime") == mtime:
        return _perf_clone_rows(cache.get("rows", []))

    rows = _perf_ler_csv_original(nome)
    _PERF_CSV_CACHE[nome] = {
        "mtime": mtime,
        "rows": _perf_clone_rows(rows),
    }

    return _perf_clone_rows(rows)


try:
    _perf_salvar_csv_original
except NameError:
    _perf_salvar_csv_original = _patch_salvar_csv


def _patch_salvar_csv(nome, rows, campos=None):
    resultado = _perf_salvar_csv_original(nome, rows, campos)
    _perf_limpar_cache(nome)
    return resultado


try:
    _perf_refs_original
except NameError:
    _perf_refs_original = _patch_refs


def _patch_refs():
    key = (
        _perf_mtime("referencias_exames.csv"),
        _perf_mtime("alias_exames.csv"),
    )

    if _PERF_REFS_CACHE["key"] == key and _PERF_REFS_CACHE["value"] is not None:
        return dict(_PERF_REFS_CACHE["value"])

    refs = _perf_refs_original()
    _PERF_REFS_CACHE["key"] = key
    _PERF_REFS_CACHE["value"] = dict(refs)

    return dict(refs)


try:
    _perf_pacientes_original
except NameError:
    _perf_pacientes_original = _patch_pacientes


def _patch_pacientes():
    key = _perf_mtime("pacientes.csv")

    if _PERF_PACIENTES_CACHE["key"] == key and _PERF_PACIENTES_CACHE["value"] is not None:
        pacientes, por_id, por_nome = _PERF_PACIENTES_CACHE["value"]
        return (
            _perf_clone_rows(pacientes),
            {k: dict(v) for k, v in por_id.items()},
            {k: dict(v) for k, v in por_nome.items()},
        )

    pacientes, por_id, por_nome = _perf_pacientes_original()

    _PERF_PACIENTES_CACHE["key"] = key
    _PERF_PACIENTES_CACHE["value"] = (
        _perf_clone_rows(pacientes),
        {k: dict(v) for k, v in por_id.items()},
        {k: dict(v) for k, v in por_nome.items()},
    )

    return pacientes, por_id, por_nome


def _perf_data_key(data_exame):
    try:
        return _patch_data_iso_cadastro(data_exame)
    except Exception:
        return str(data_exame or "").strip()


try:
    _perf_reconstruir_cadastrados_original
except NameError:
    _perf_reconstruir_cadastrados_original = _patch_reconstruir_exames_cadastrados_por_data


def _patch_reconstruir_exames_cadastrados_por_data():
    key = (
        _perf_mtime("analise_exames.csv"),
        _perf_mtime("referencias_exames.csv"),
    )

    if _PERF_CADASTRADOS_CACHE["key"] == key and _PERF_CADASTRADOS_CACHE["value"] is not None:
        cadastrados = {
            k: list(v)
            for k, v in _PERF_CADASTRADOS_CACHE["value"].items()
        }
        globals()["EXAMES_CADASTRADOS_MOCK"] = cadastrados
        return cadastrados

    cadastrados = _perf_reconstruir_cadastrados_original()

    _PERF_CADASTRADOS_CACHE["key"] = key
    _PERF_CADASTRADOS_CACHE["value"] = {
        k: list(v)
        for k, v in (cadastrados or {}).items()
    }

    return cadastrados


try:
    _perf_sync_resultados_original
except NameError:
    _perf_sync_resultados_original = sincronizar_resultados_exames_mock_data_flet


def sincronizar_resultados_exames_mock_data_flet():
    key = (
        _perf_mtime("analise_exames.csv"),
        _perf_mtime("referencias_exames.csv"),
    )

    if _PERF_SYNC_CACHE["key"] == key and _PERF_SYNC_CACHE["value"] is not None:
        resultados = _PERF_SYNC_CACHE["value"]
        globals()["RESULTADOS_EXAMES_MOCK"] = resultados

        try:
            _patch_reconstruir_exames_cadastrados_por_data()
        except Exception:
            pass

        return resultados

    resultados = _perf_sync_resultados_original()

    _PERF_SYNC_CACHE["key"] = key
    _PERF_SYNC_CACHE["value"] = resultados

    return resultados


try:
    _perf_atualizar_pacientes_original
except NameError:
    _perf_atualizar_pacientes_original = atualizar_pacientes_csv_real_definitivo


def atualizar_pacientes_csv_real_definitivo():
    key = (
        _perf_mtime("pacientes.csv"),
        _perf_mtime("analise_exames.csv"),
        _perf_mtime("referencias_exames.csv"),
    )

    if _PERF_PACIENTES_UI_CACHE["key"] == key and _PERF_PACIENTES_UI_CACHE["value"] is not None:
        pacientes = _perf_clone_rows(_PERF_PACIENTES_UI_CACHE["value"])
        globals()["PACIENTES_MOCK"] = pacientes
        return pacientes

    pacientes = _perf_atualizar_pacientes_original()

    _PERF_PACIENTES_UI_CACHE["key"] = key
    _PERF_PACIENTES_UI_CACHE["value"] = _perf_clone_rows(pacientes)

    return pacientes


try:
    _perf_disponiveis_original
except NameError:
    _perf_disponiveis_original = exames_disponiveis_por_data


def exames_disponiveis_por_data(paciente_id, data_exame):
    pid = str(paciente_id or "").strip()
    if pid.isdigit() and len(pid) < 4:
        pid = pid.zfill(4)

    key = (
        pid,
        _perf_data_key(data_exame),
        _perf_mtime("analise_exames.csv"),
        _perf_mtime("referencias_exames.csv"),
    )

    if key in _PERF_DISPONIVEIS_CACHE:
        return _perf_clone_rows(_PERF_DISPONIVEIS_CACHE[key])

    lista = _perf_disponiveis_original(paciente_id, data_exame)
    _PERF_DISPONIVEIS_CACHE[key] = _perf_clone_rows(lista)

    return _perf_clone_rows(lista)


try:
    _perf_bloqueados_original
except NameError:
    _perf_bloqueados_original = exames_ja_cadastrados_por_data


def exames_ja_cadastrados_por_data(paciente_id, data_exame):
    pid = str(paciente_id or "").strip()
    if pid.isdigit() and len(pid) < 4:
        pid = pid.zfill(4)

    key = (
        pid,
        _perf_data_key(data_exame),
        _perf_mtime("analise_exames.csv"),
        _perf_mtime("referencias_exames.csv"),
    )

    if key in _PERF_BLOQUEADOS_CACHE:
        return _perf_clone_rows(_PERF_BLOQUEADOS_CACHE[key])

    lista = _perf_bloqueados_original(paciente_id, data_exame)
    _PERF_BLOQUEADOS_CACHE[key] = _perf_clone_rows(lista)

    return _perf_clone_rows(lista)

print("[PERFORMANCE WINDOWS] Cache de CSV/listas ativado.")

# ===== FIM PATCH PERFORMANCE WINDOWS: CACHE CSV E LISTAS =====






# Fallbacks de cores para patches adicionais
if "COR_SUCESSO" not in globals():
    COR_SUCESSO = "#16A34A"

if "COR_ALERTA" not in globals():
    COR_ALERTA = "#F59E0B"

if "COR_CRITICO" not in globals():
    COR_CRITICO = "#DC2626"

if "COR_TEXTO" not in globals():
    COR_TEXTO = "#111827"

if "COR_TEXTO_FRACO" not in globals():
    COR_TEXTO_FRACO = "#64748B"

# ===== PATCH EXCLUIR EXAME CADASTRADO ERRADO =====

def _del_exame_nome(item):
    if not isinstance(item, dict):
        return str(item or "").strip()

    try:
        nome = _patch_nome_exame(item)
        if nome:
            return nome
    except Exception:
        pass

    try:
        nome = nome_exame_para_exibicao(item)
        if nome:
            return nome
    except Exception:
        pass

    return str(
        item.get("nome_exame")
        or item.get("nome_padronizado")
        or item.get("nome")
        or item.get("exame")
        or item.get("exame_nome")
        or item.get("id")
        or ""
    ).strip()


def _del_exame_tokens(item):
    nome = _del_exame_nome(item)

    tokens = set()

    if nome:
        tokens.add(_patch_norm(nome))
        tokens.add(_patch_id_canonico_exame(nome) if "_patch_id_canonico_exame" in globals() else _patch_norm(nome))

    if isinstance(item, dict):
        for campo in ["id", "id_canonico", "exame_id", "nome_exame", "nome_padronizado", "nome", "exame", "exame_nome"]:
            valor = str(item.get(campo) or "").strip()
            if valor:
                tokens.add(_patch_norm(valor))
                if "_patch_id_canonico_exame" in globals():
                    tokens.add(_patch_id_canonico_exame(valor))

    try:
        ref = _patch_ref(nome)
        ref_id = _patch_get(ref, "id")
        ref_nome = _patch_get(ref, "nome_exame", "nome")

        if ref_id:
            tokens.add(_patch_norm(ref_id))
            if "_patch_id_canonico_exame" in globals():
                tokens.add(_patch_id_canonico_exame(ref_id))

        if ref_nome:
            tokens.add(_patch_norm(ref_nome))
            if "_patch_id_canonico_exame" in globals():
                tokens.add(_patch_id_canonico_exame(ref_nome))
    except Exception:
        pass

    return {t for t in tokens if t}


def _del_linha_exame_match(row, paciente_id, data_exame, tokens):
    pid = _patch_get(row, "paciente_id", "id_paciente")

    if pid.isdigit() and len(pid) < 4:
        pid = pid.zfill(4)

    paciente_id = str(paciente_id or "").strip()
    if paciente_id.isdigit() and len(paciente_id) < 4:
        paciente_id = paciente_id.zfill(4)

    if pid != paciente_id:
        return False

    data_row = _patch_data_iso_cadastro(_patch_data_exame(row))
    data_alvo = _patch_data_iso_cadastro(data_exame)

    if data_row != data_alvo:
        return False

    row_tokens = _del_exame_tokens(row)

    return bool(row_tokens & tokens)


def excluir_exame_cadastrado_errado(paciente_id, data_exame, exame):
    tokens = _del_exame_tokens(exame)
    nome = _del_exame_nome(exame)

    if not paciente_id or not data_exame or not tokens:
        print("[EXCLUIR EXAME] Exclusão cancelada: dados insuficientes.", paciente_id, data_exame, nome)
        return 0

    total_removido = 0

    for nome_csv in ["exames.csv", "analise_exames.csv"]:
        rows = _patch_ler_csv(nome_csv)
        campos = _patch_campos_csv(nome_csv)

        novas = []
        removidos = 0

        for row in rows:
            if _del_linha_exame_match(row, paciente_id, data_exame, tokens):
                removidos += 1
            else:
                novas.append(row)

        if removidos:
            _patch_salvar_csv(nome_csv, novas, campos)
            total_removido += removidos
            print(f"[EXCLUIR EXAME] {nome_csv}: {removidos} registro(s) removido(s).")

    try:
        if "_perf_limpar_cache" in globals():
            _perf_limpar_cache()
    except Exception as exc:
        print(f"[EXCLUIR EXAME] Falha ao limpar cache: {exc}")

    try:
        sincronizar_resultados_exames_mock_data_flet()
    except Exception as exc:
        print(f"[EXCLUIR EXAME] Falha ao sincronizar resultados: {exc}")

    try:
        atualizar_pacientes_csv_real_definitivo()
    except Exception as exc:
        print(f"[EXCLUIR EXAME] Falha ao atualizar pacientes: {exc}")

    print(f"[EXCLUIR EXAME] Exclusão concluída: paciente={paciente_id} | data={data_exame} | exame={nome} | total={total_removido}")
    return total_removido


def exame_bloqueado_card_com_exclusao(page, exame, paciente_id, data_exame, atualizar_callback=None):
    nome = _del_exame_nome(exame)

    try:
        detalhe_ref = montar_detalhe_referencia_exame(exame)
    except Exception:
        detalhe_ref = {
            "grupo": exame.get("grupo", "") if isinstance(exame, dict) else "",
            "referencia": exame.get("referencia", "") if isinstance(exame, dict) else "",
            "fonte": exame.get("fonte", "") if isinstance(exame, dict) else "",
        }

    grupo = detalhe_ref.get("grupo") or ""
    referencia = detalhe_ref.get("referencia") or ""
    fonte = detalhe_ref.get("fonte") or ""

    def abrir_confirmacao(e):
        dialog = None

        def fechar(ev=None):
            dialog.open = False
            page.update()

        def apagar(ev=None):
            total = excluir_exame_cadastrado_errado(paciente_id, data_exame, exame)

            dialog.open = False

            if total:
                try:
                    mostrar_snackbar(page, f'Exame "{nome}" apagado com sucesso.', COR_SUCESSO)
                except Exception:
                    pass
            else:
                try:
                    mostrar_snackbar(page, f'Não encontrei registros para apagar do exame "{nome}".', COR_ALERTA)
                except Exception:
                    pass

            if atualizar_callback:
                atualizar_callback()

            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Apagar exame cadastrado?"),
            content=ft.Text(
                f'Deseja apagar o exame "{nome}" cadastrado em {data_exame}?\n\n'
                "Esta ação remove o resultado do histórico e da análise nutricional."
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar),
                ft.ElevatedButton(
                    "Apagar exame",
                    icon=ft.Icons.DELETE_OUTLINE,
                    bgcolor=COR_CRITICO,
                    color="#FFFFFF",
                    on_click=apagar,
                ),
            ],
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    return ft.Container(
        padding=12,
        border_radius=16,
        bgcolor="#F8FAFC",
        content=ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=40,
                    height=40,
                    border_radius=12,
                    bgcolor="#DCFCE7",
                    content=ft.Icon(ft.Icons.CHECK_CIRCLE, color=COR_SUCESSO, size=22),
                ),
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        spacing=3,
                        controls=[
                            ft.Text(nome, size=14, weight=ft.FontWeight.BOLD, color=COR_TEXTO),
                            ft.Text(
                                f"{grupo} • Ref.: {referencia}",
                                size=11,
                                color=COR_TEXTO_FRACO,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                f"Fonte: {fonte}",
                                size=10,
                                color=COR_TEXTO_FRACO,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                    ),
                ),
                ft.Column(
                    spacing=6,
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                    controls=[
                        ft.Container(
                            padding=8,
                            border_radius=999,
                            bgcolor="#6B7280",
                            content=ft.Text(
                                "JÁ CADASTRADO",
                                size=10,
                                weight=ft.FontWeight.BOLD,
                                color="#FFFFFF",
                            ),
                        ),
                        ft.OutlinedButton(
                            content="Apagar",
                            icon=ft.Icons.DELETE_OUTLINE,
                            on_click=abrir_confirmacao,
                        ),
                    ],
                ),
            ],
        ),
    )

# ===== FIM PATCH EXCLUIR EXAME CADASTRADO ERRADO =====





# ===== PATCH FIX BOTAO APAGAR EXAME: DIALOG COMPATIVEL =====

def _del_abrir_dialog_compat(page, dialog):
    """
    Compatível com versões novas e antigas do Flet.
    Algumas versões não exibem AlertDialog via page.dialog = dialog.
    """
    try:
        print("[EXCLUIR EXAME] Abrindo diálogo de confirmação...")
    except Exception:
        pass

    try:
        page.open(dialog)
        return
    except Exception:
        pass

    try:
        if dialog not in page.overlay:
            page.overlay.append(dialog)
        dialog.open = True
        page.update()
        return
    except Exception:
        pass

    try:
        page.dialog = dialog
        dialog.open = True
        page.update()
    except Exception as exc:
        print(f"[EXCLUIR EXAME] Falha ao abrir diálogo: {exc}")


def _del_fechar_dialog_compat(page, dialog):
    try:
        page.close(dialog)
        return
    except Exception:
        pass

    try:
        dialog.open = False
        page.update()
    except Exception:
        pass


def _del_button_texto(label, on_click=None):
    try:
        return ft.TextButton(text=label, on_click=on_click)
    except TypeError:
        return ft.TextButton(label, on_click=on_click)


def _del_button_apagar(label, on_click=None):
    try:
        return ft.FilledButton(
            text=label,
            icon=ft.Icons.DELETE_OUTLINE,
            on_click=on_click,
        )
    except Exception:
        try:
            return ft.ElevatedButton(
                label,
                icon=ft.Icons.DELETE_OUTLINE,
                bgcolor=globals().get("COR_CRITICO", "#DC2626"),
                color="#FFFFFF",
                on_click=on_click,
            )
        except Exception:
            return ft.TextButton(label, on_click=on_click)


def exame_bloqueado_card_com_exclusao(page, exame, paciente_id, data_exame, atualizar_callback=None):
    nome = _del_exame_nome(exame)

    try:
        detalhe_ref = montar_detalhe_referencia_exame(exame)
    except Exception:
        detalhe_ref = {
            "grupo": exame.get("grupo", "") if isinstance(exame, dict) else "",
            "referencia": exame.get("referencia", "") if isinstance(exame, dict) else "",
            "fonte": exame.get("fonte", "") if isinstance(exame, dict) else "",
        }

    grupo = detalhe_ref.get("grupo") or ""
    referencia = detalhe_ref.get("referencia") or ""
    fonte = detalhe_ref.get("fonte") or ""

    def executar_exclusao(ev=None, dialog=None):
        print(f"[EXCLUIR EXAME] Confirmado apagar: paciente={paciente_id} | data={data_exame} | exame={nome}")

        total = excluir_exame_cadastrado_errado(paciente_id, data_exame, exame)

        if dialog is not None:
            _del_fechar_dialog_compat(page, dialog)

        if total:
            try:
                mostrar_snackbar(page, f'Exame "{nome}" apagado com sucesso.', globals().get("COR_SUCESSO", "#16A34A"))
            except Exception:
                pass
        else:
            try:
                mostrar_snackbar(page, f'Não encontrei registros para apagar do exame "{nome}".', globals().get("COR_ALERTA", "#F59E0B"))
            except Exception:
                pass

        try:
            if atualizar_callback:
                atualizar_callback()
            else:
                page.update()
        except Exception as exc:
            print(f"[EXCLUIR EXAME] Falha ao atualizar tela após apagar: {exc}")
            try:
                page.update()
            except Exception:
                pass

    def abrir_confirmacao(e=None):
        print(f"[EXCLUIR EXAME] Clique no botão Apagar: paciente={paciente_id} | data={data_exame} | exame={nome}")

        dialog = None

        def cancelar(ev=None):
            _del_fechar_dialog_compat(page, dialog)

        def confirmar(ev=None):
            executar_exclusao(ev, dialog)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Apagar exame cadastrado?"),
            content=ft.Text(
                f'Deseja apagar o exame "{nome}" cadastrado em {data_exame}?\n\n'
                "Esta ação remove o resultado do histórico e da análise nutricional."
            ),
            actions=[
                _del_button_texto("Cancelar", on_click=cancelar),
                _del_button_apagar("Apagar exame", on_click=confirmar),
            ],
        )

        _del_abrir_dialog_compat(page, dialog)

    return ft.Container(
        padding=12,
        border_radius=16,
        bgcolor="#F8FAFC",
        content=ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=40,
                    height=40,
                    border_radius=12,
                    bgcolor="#DCFCE7",
                    content=ft.Icon(ft.Icons.CHECK_CIRCLE, color=globals().get("COR_SUCESSO", "#16A34A"), size=22),
                ),
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        spacing=3,
                        controls=[
                            ft.Text(nome, size=14, weight=ft.FontWeight.BOLD, color=globals().get("COR_TEXTO", "#111827")),
                            ft.Text(
                                f"{grupo} • Ref.: {referencia}",
                                size=11,
                                color=globals().get("COR_TEXTO_FRACO", "#64748B"),
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                f"Fonte: {fonte}",
                                size=10,
                                color=globals().get("COR_TEXTO_FRACO", "#64748B"),
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                    ),
                ),
                ft.Column(
                    spacing=6,
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                    controls=[
                        ft.Container(
                            padding=8,
                            border_radius=999,
                            bgcolor="#6B7280",
                            content=ft.Text(
                                "JÁ CADASTRADO",
                                size=10,
                                weight=ft.FontWeight.BOLD,
                                color="#FFFFFF",
                            ),
                        ),
                        ft.OutlinedButton(
                            content="Apagar",
                            icon=ft.Icons.DELETE_OUTLINE,
                            on_click=abrir_confirmacao,
                        ),
                    ],
                ),
            ],
        ),
    )

# ===== FIM PATCH FIX BOTAO APAGAR EXAME: DIALOG COMPATIVEL =====





# ===== PATCH FIX EXCLUSAO EXAME: CSV MEMORIA VIEW =====

def _del_tokens_linha_robusto(row):
    tokens = set()

    if isinstance(row, dict):
        for campo in [
            "nome_exame", "nome_padronizado", "exame_nome",
            "exame", "nome", "id", "id_canonico", "exame_id"
        ]:
            valor = str(row.get(campo) or "").strip()
            if valor:
                tokens.add(_patch_norm(valor))
                try:
                    tokens.add(_patch_id_canonico_exame(valor))
                except Exception:
                    pass

        nome = (
            row.get("nome_exame")
            or row.get("nome_padronizado")
            or row.get("exame_nome")
            or row.get("exame")
            or row.get("nome")
            or ""
        )

        try:
            ref = _patch_ref(nome)
            for campo in ["id", "nome", "nome_exame"]:
                valor = _patch_get(ref, campo)
                if valor:
                    tokens.add(_patch_norm(valor))
                    try:
                        tokens.add(_patch_id_canonico_exame(valor))
                    except Exception:
                        pass
        except Exception:
            pass
    else:
        texto = str(row or "").strip()
        if texto:
            tokens.add(_patch_norm(texto))
            try:
                tokens.add(_patch_id_canonico_exame(texto))
            except Exception:
                pass

    return {t for t in tokens if t}


def _del_match_exame_robusto(row, paciente_id, data_exame, tokens_alvo):
    if not isinstance(row, dict):
        return False

    pid_row = _patch_get(row, "paciente_id", "id_paciente")

    if pid_row.isdigit() and len(pid_row) < 4:
        pid_row = pid_row.zfill(4)

    pid_alvo = str(paciente_id or "").strip()
    if pid_alvo.isdigit() and len(pid_alvo) < 4:
        pid_alvo = pid_alvo.zfill(4)

    if pid_row != pid_alvo:
        return False

    data_row = _patch_data_iso_cadastro(_patch_data_exame(row))
    data_alvo = _patch_data_iso_cadastro(data_exame)

    if data_row != data_alvo:
        return False

    tokens_row = _del_tokens_linha_robusto(row)

    if tokens_row & tokens_alvo:
        return True

    # Fallback para nomes parecidos.
    for a in tokens_alvo:
        for b in tokens_row:
            if a and b and (a in b or b in a):
                return True

    return False


def _del_limpar_memoria_e_cache_exame(paciente_id, data_exame, tokens_alvo):
    for nome_global in ["RESULTADOS_EXAMES_MOCK"]:
        lista = globals().get(nome_global)
        if isinstance(lista, list):
            antes = len(lista)
            lista[:] = [
                r for r in lista
                if not _del_match_exame_robusto(r, paciente_id, data_exame, tokens_alvo)
            ]
            depois = len(lista)
            if antes != depois:
                print(f"[EXCLUIR EXAME] Memória {nome_global}: {antes - depois} removido(s).")

    globals()["EXAMES_CADASTRADOS_MOCK"] = {}

    try:
        if "_perf_limpar_cache" in globals():
            _perf_limpar_cache()
    except Exception as exc:
        print(f"[EXCLUIR EXAME] Falha ao limpar cache de performance: {exc}")

    for nome_cache in [
        "_PERF_CSV_CACHE",
        "_PERF_DISPONIVEIS_CACHE",
        "_PERF_BLOQUEADOS_CACHE",
    ]:
        try:
            cache = globals().get(nome_cache)
            if hasattr(cache, "clear"):
                cache.clear()
        except Exception:
            pass

    for nome_cache in [
        "_PERF_REFS_CACHE",
        "_PERF_PACIENTES_CACHE",
        "_PERF_CADASTRADOS_CACHE",
        "_PERF_SYNC_CACHE",
        "_PERF_PACIENTES_UI_CACHE",
    ]:
        try:
            cache = globals().get(nome_cache)
            if isinstance(cache, dict):
                cache["key"] = None
                cache["value"] = None
        except Exception:
            pass


def excluir_exame_cadastrado_errado(paciente_id, data_exame, exame):
    tokens = _del_exame_tokens(exame)
    tokens.update(_del_tokens_linha_robusto(exame))

    nome = _del_exame_nome(exame)

    if not paciente_id or not data_exame or not tokens:
        print("[EXCLUIR EXAME] Exclusão cancelada: dados insuficientes.", paciente_id, data_exame, nome)
        return 0

    print(f"[EXCLUIR EXAME] Iniciando exclusão robusta: paciente={paciente_id} | data={data_exame} | exame={nome}")
    print(f"[EXCLUIR EXAME] Tokens usados: {sorted(tokens)}")

    total_removido = 0

    for nome_csv in ["exames.csv", "analise_exames.csv"]:
        rows = _patch_ler_csv(nome_csv)
        campos = _patch_campos_csv(nome_csv)

        novas = []
        removidos = 0

        for row in rows:
            if _del_match_exame_robusto(row, paciente_id, data_exame, tokens):
                removidos += 1
                print(f"[EXCLUIR EXAME] Removendo de {nome_csv}: {row}")
            else:
                novas.append(row)

        if removidos:
            _patch_salvar_csv(nome_csv, novas, campos)
            total_removido += removidos
            print(f"[EXCLUIR EXAME] {nome_csv}: {removidos} registro(s) removido(s).")
        else:
            print(f"[EXCLUIR EXAME] {nome_csv}: nenhum registro removido.")

    _del_limpar_memoria_e_cache_exame(paciente_id, data_exame, tokens)

    try:
        sincronizar_resultados_exames_mock_data_flet()
    except Exception as exc:
        print(f"[EXCLUIR EXAME] Falha ao sincronizar resultados: {exc}")

    try:
        atualizar_pacientes_csv_real_definitivo()
    except Exception as exc:
        print(f"[EXCLUIR EXAME] Falha ao atualizar pacientes: {exc}")

    print(f"[EXCLUIR EXAME] Exclusão finalizada: paciente={paciente_id} | data={data_exame} | exame={nome} | total={total_removido}")
    return total_removido

# ===== FIM PATCH FIX EXCLUSAO EXAME: CSV MEMORIA VIEW =====





# ===== PATCH FIX NOME EXAME: ALIASES DE EXIBICAO =====

try:
    _fix_nome_exame_para_exibicao_original
except NameError:
    _fix_nome_exame_para_exibicao_original = nome_exame_para_exibicao


def nome_exame_para_exibicao(item):
    if isinstance(item, dict):
        for campo in [
            "nome_exame",
            "exame_nome",
            "nome_padronizado",
            "nome",
            "exame",
            "analito",
            "descricao",
            "id",
        ]:
            valor = str(item.get(campo) or "").strip()
            if valor and valor not in ["-", "None", "null"]:
                return valor

    try:
        return _fix_nome_exame_para_exibicao_original(item)
    except Exception:
        return "-"


try:
    _fix_patch_nome_exame_original
except NameError:
    _fix_patch_nome_exame_original = _patch_nome_exame


def _patch_nome_exame(row):
    if isinstance(row, dict):
        for campo in [
            "nome_exame",
            "exame_nome",
            "nome_padronizado",
            "nome",
            "exame",
            "analito",
            "descricao",
            "id",
        ]:
            valor = str(row.get(campo) or "").strip()
            if valor and valor not in ["-", "None", "null"]:
                return valor

    try:
        return _fix_patch_nome_exame_original(row)
    except Exception:
        return ""

# ===== FIM PATCH FIX NOME EXAME: ALIASES DE EXIBICAO =====





# ===== PATCH FIX MIGRACAO DUPLICADA EXAMES =====

import csv as _dup_csv
import unicodedata as _dup_unicodedata
import re as _dup_re
from pathlib import Path as _dup_Path


def _dup_data_dir():
    return _dup_Path(__file__).resolve().parent / "data_flet"


def _dup_norm(valor):
    texto = str(valor or "").strip().lower()
    texto = _dup_unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not _dup_unicodedata.combining(c))
    texto = texto.replace("_", " ").replace("-", " ")
    texto = _dup_re.sub(r"[^a-z0-9%/., ]+", " ", texto)
    return " ".join(texto.split())


def _dup_get(row, *campos):
    if not isinstance(row, dict):
        return ""

    limpo = {
        str(k or "").replace("\ufeff", "").strip(): "" if v is None else str(v).strip()
        for k, v in row.items()
    }

    for c in campos:
        v = limpo.get(str(c or "").strip(), "")
        if v:
            return v

    return ""


def _dup_ler_csv(nome):
    caminho = _dup_data_dir() / nome

    if not caminho.exists():
        return [], []

    with open(caminho, newline="", encoding="utf-8-sig") as f:
        reader = _dup_csv.DictReader(f)
        campos = [
            str(c or "").replace("\ufeff", "").strip()
            for c in (reader.fieldnames or [])
        ]
        rows = []

        for r in reader:
            rows.append({
                str(k or "").replace("\ufeff", "").strip(): "" if v is None else str(v).strip()
                for k, v in r.items()
            })

    return campos, rows


def _dup_salvar_csv(nome, campos, rows):
    caminho = _dup_data_dir() / nome
    tmp = caminho.with_suffix(caminho.suffix + ".tmp")

    campos = list(campos or [])

    for obrigatorio in ["paciente_id", "data_exame", "nome_exame", "resultado", "unidade"]:
        if obrigatorio not in campos:
            campos.append(obrigatorio)

    for r in rows:
        for k in r.keys():
            if k not in campos:
                campos.append(k)

    with open(tmp, "w", newline="", encoding="utf-8-sig") as f:
        writer = _dup_csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({c: r.get(c, "") for c in campos})

    tmp.replace(caminho)


def _dup_nome_exame(row):
    nome = _dup_get(
        row,
        "nome_exame",
        "exame_nome",
        "nome_padronizado",
        "nome",
        "exame",
        "analito",
        "descricao",
    )

    if nome and nome not in ["-", "None", "null"]:
        return nome

    # fallback seguro para glicose, quando veio sem nome mas com referência 70-99 mg/dL
    unidade = _dup_norm(_dup_get(row, "unidade"))
    vmin = _dup_norm(_dup_get(row, "valor_min"))
    vmax = _dup_norm(_dup_get(row, "valor_max"))
    resultado = _dup_norm(_dup_get(row, "resultado"))

    if unidade == "mg/dl" and vmin == "70" and vmax == "99":
        return "Glicose"

    if unidade == "mg/dl" and resultado == "237":
        return "Glicose"

    return nome


def _dup_chave(row):
    pid = _dup_get(row, "paciente_id", "id_paciente")

    if pid.isdigit() and len(pid) < 4:
        pid = pid.zfill(4)

    data = _dup_get(row, "data_exame", "data")
    nome = _dup_nome_exame(row)
    resultado = _dup_get(row, "resultado", "valor")
    unidade = _dup_get(row, "unidade")

    return (
        pid,
        _dup_norm(data),
        _dup_norm(nome),
        _dup_norm(resultado),
        _dup_norm(unidade),
    )


def _dup_deduplicar_csv(nome_csv):
    campos, rows = _dup_ler_csv(nome_csv)

    if not rows:
        return 0

    vistos = set()
    novas = []
    removidos = 0

    for r in rows:
        nome = _dup_nome_exame(r)

        if nome:
            r["nome_exame"] = nome

            if nome_csv == "analise_exames.csv":
                if not _dup_get(r, "nome_padronizado") or _dup_get(r, "nome_padronizado") in ["-", "None", "null"]:
                    r["nome_padronizado"] = nome

        chave = _dup_chave(r)

        # Só remove duplicado quando a chave tem os dados mínimos.
        chave_valida = all([chave[0], chave[1], chave[2], chave[3]])

        if chave_valida and chave in vistos:
            removidos += 1
            print(f"[DEDUP EXAMES] Removendo duplicado em {nome_csv}: {r}")
            continue

        if chave_valida:
            vistos.add(chave)

        novas.append(r)

    if removidos:
        _dup_salvar_csv(nome_csv, campos, novas)
        print(f"[DEDUP EXAMES] {nome_csv}: {removidos} duplicado(s) removido(s).")

    return removidos


def deduplicar_exames_e_analises_csv():
    total = 0
    total += _dup_deduplicar_csv("exames.csv")
    total += _dup_deduplicar_csv("analise_exames.csv")

    try:
        if "_perf_limpar_cache" in globals():
            _perf_limpar_cache()
    except Exception:
        pass

    print(f"[DEDUP EXAMES] Total removido: {total}")
    return total


def _patch_migrar_mock_para_csv():
    # Desativado intencionalmente.
    # O salvamento real agora acontece no append via _patch_persistir_resultado_item().
    # Manter essa migração ativa estava duplicando exames após cada cadastro.
    return 0

# ===== FIM PATCH FIX MIGRACAO DUPLICADA EXAMES =====











# ===== PATCH REFERENCIAS POR SEXO E IDADE =====

import csv as _rsi_csv
import re as _rsi_re
import unicodedata as _rsi_unicodedata
from pathlib import Path as _rsi_Path


def _rsi_data_dir():
    try:
        return _patch_data_dir()
    except Exception:
        return _rsi_Path(__file__).resolve().parent / "data_flet"


def _rsi_norm(valor):
    texto = str(valor or "").strip().lower()
    texto = _rsi_unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not _rsi_unicodedata.combining(c))
    texto = texto.replace("_", " ").replace("-", " ")
    texto = _rsi_re.sub(r"[^a-z0-9%/., ]+", " ", texto)
    return " ".join(texto.split())


def _rsi_float(valor):
    texto = str(valor or "").strip()
    if not texto:
        return None

    texto = texto.replace(" ", "")

    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    else:
        texto = texto.replace(",", ".")

    m = _rsi_re.search(r"[-+]?\d+(?:\.\d+)?", texto)
    if not m:
        return None

    try:
        return float(m.group(0))
    except Exception:
        return None


def _rsi_get(row, *campos):
    if not isinstance(row, dict):
        return ""

    limpo = {
        str(k or "").replace("\ufeff", "").strip(): "" if v is None else str(v).strip()
        for k, v in row.items()
    }

    for c in campos:
        v = limpo.get(str(c or "").strip(), "")
        if v:
            return v

    return ""


def _rsi_ler_csv(nome):
    caminho = _rsi_data_dir() / nome
    if not caminho.exists():
        return [], []

    with open(caminho, newline="", encoding="utf-8-sig") as f:
        reader = _rsi_csv.DictReader(f)
        campos = [
            str(c or "").replace("\ufeff", "").strip()
            for c in (reader.fieldnames or [])
        ]
        rows = []
        for r in reader:
            rows.append({
                str(k or "").replace("\ufeff", "").strip(): "" if v is None else str(v).strip()
                for k, v in r.items()
            })

    return campos, rows


def _rsi_salvar_csv(nome, campos, rows):
    caminho = _rsi_data_dir() / nome
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_suffix(caminho.suffix + ".tmp")

    campos = list(campos or [])
    for r in rows:
        for k in r.keys():
            if k not in campos:
                campos.append(k)

    with open(tmp, "w", newline="", encoding="utf-8-sig") as f:
        writer = _rsi_csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({c: r.get(c, "") for c in campos})

    tmp.replace(caminho)


def _rsi_id(nome, sexo, idade_min, idade_max):
    base = _rsi_norm(f"{nome}_{sexo}_{idade_min}_{idade_max}")
    return _rsi_re.sub(r"[^a-z0-9]+", "_", base).strip("_")


def _rsi_row(nome, grupo, sexo, idade_min, idade_max, vmin, vmax, unidade, ref, fonte, fonte_url="", obs=""):
    return {
        "referencia_id": _rsi_id(nome, sexo, idade_min, idade_max),
        "nome_exame": nome,
        "nome_padronizado": nome,
        "grupo": grupo,
        "sexo": sexo,
        "idade_min": str(idade_min),
        "idade_max": str(idade_max),
        "valor_min": "" if vmin is None else str(vmin),
        "valor_max": "" if vmax is None else str(vmax),
        "unidade": unidade,
        "referencia": ref,
        "referencia_texto": ref,
        "fonte": fonte,
        "fonte_referencia": fonte,
        "fonte_url": fonte_url,
        "observacoes": obs,
        "status": "Completa",
    }


def gerar_referencias_exames_sexo_idade():
    _, base_rows = _rsi_ler_csv("referencias_exames.csv")

    saida = []

    # Exames que receberão linhas específicas, para não herdar valor masculino como "Todos".
    nomes_com_override = {
        "eritrocitos", "hemoglobina", "hematocrito", "hcm", "vcm", "chcm", "rdw",
        "leucocitos", "neutrofilos", "eosinofilos", "basofilos", "linfocitos",
        "monocitos", "plaquetas", "ferritina", "gama gt", "creatinina",
        "ferro", "saturacao da transferrina", "vhs", "tsh", "t4 livre",
        "glicose", "hemoglobina glicada",
    }

    # 1) Mantém a base atual para exames sem variação relevante por sexo/idade.
    for r in base_rows:
        nome = _rsi_get(r, "nome_exame", "nome")
        grupo = _rsi_get(r, "grupo")
        unidade = _rsi_get(r, "unidade")
        ref = _rsi_get(r, "referencia", "referencia_texto")
        fonte = _rsi_get(r, "fonte", "fonte_referencia") or "Base NutriSoft/Fleury importada"
        vmin = _rsi_get(r, "valor_min")
        vmax = _rsi_get(r, "valor_max")

        n = _rsi_norm(nome)

        if n in nomes_com_override:
            continue

        ref_norm = _rsi_norm(ref)

        # Se a própria referência diz "masculino", não transforma em "Todos".
        sexo = "Todos"
        if "masculino" in ref_norm and "feminino" not in ref_norm:
            sexo = "Masculino"
        elif "feminino" in ref_norm and "masculino" not in ref_norm:
            sexo = "Feminino"

        saida.append(_rsi_row(
            nome, grupo, sexo, 0, 120, vmin, vmax, unidade, ref, fonte,
            obs="Linha preservada da base original; aplicar por sexo/idade quando houver regra específica."
        ))

    # 2) Metabolismo glicídico — SBD.
    fonte_sbd = "Sociedade Brasileira de Diabetes - Diretriz 2025"
    url_sbd = "https://diretriz.diabetes.org.br/diagnostico-de-diabetes-mellitus/"
    saida += [
        _rsi_row("Glicose", "Metabolismo glicídico", "Todos", 18, 120, 70, 99, "mg/dL",
                 "Adultos não gestantes: 70 a 99 mg/dL; pré-diabetes 100 a 125; diabetes >=126",
                 fonte_sbd, url_sbd),
        _rsi_row("Hemoglobina glicada", "Metabolismo glicídico", "Todos", 18, 120, None, 5.69, "%",
                 "Adultos não gestantes: <5,7%; pré-diabetes 5,7 a 6,4%; diabetes >=6,5%",
                 fonte_sbd, url_sbd),
    ]

    # 3) Hemograma — Fleury 2022.
    fonte_hemo = "Fleury - Novos valores de referência para o hemograma"
    url_hemo = "https://www.fleury.com.br/artigos-medicos/novos-valores-de-referencia-para-o-hemograma-no-fleury"
    hemograma = [
        ("Eritrócitos", "milhões/mm3", 4.32, 5.67, 3.83, 4.99),
        ("Hemoglobina", "g/dL", 13.3, 16.5, 11.7, 14.9),
        ("Hematócrito", "%", 39.2, 49.0, 35.1, 44.1),
        ("HCM", "pg", 27.7, 32.7, 27.7, 32.7),
        ("VCM", "fL", 81.7, 95.3, 83.1, 96.8),
        ("CHCM", "g/dL", 32.4, 36.0, 32.0, 35.2),
        ("RDW", "%", 11.8, 14.1, 11.8, 14.2),
        ("Leucócitos", "/mm3", 3650, 8120, 3470, 8290),
        ("Neutrófilos", "/mm3", 1590, 4770, 1526, 5020),
        ("Eosinófilos", "/mm3", 34, 420, 20, 340),
        ("Basófilos", "/mm3", 10, 80, 10, 80),
        ("Linfócitos", "/mm3", 1120, 2950, 1097, 2980),
        ("Monócitos", "/mm3", 260, 730, 220, 650),
        ("Plaquetas", "/mm3", 151000, 304000, 163000, 343000),
    ]

    for nome, unidade, m_min, m_max, f_min, f_max in hemograma:
        saida.append(_rsi_row(nome, "Hemograma", "Masculino", 18, 120, m_min, m_max, unidade,
                              f"Masculino adulto: {m_min} a {m_max} {unidade}", fonte_hemo, url_hemo))
        saida.append(_rsi_row(nome, "Hemograma", "Feminino", 18, 120, f_min, f_max, unidade,
                              f"Feminino adulto: {f_min} a {f_max} {unidade}", fonte_hemo, url_hemo))

    # 4) Metabolismo do ferro — a+ / Grupo Fleury e MSD quando aplicável.
    fonte_ferritina = "a+ Medicina Diagnóstica / Grupo Fleury - Ferritina, soro"
    url_ferritina = "https://www.amaissaude.com.br/pe/exames/ferritina-soro"
    saida += [
        _rsi_row("Ferritina", "Metabolismo do ferro", "Masculino", 16, 120, 26, 446, "microg/L",
                 "Adulto masculino: 26 a 446 microg/L", fonte_ferritina, url_ferritina),
        _rsi_row("Ferritina", "Metabolismo do ferro", "Feminino", 16, 120, 15, 149, "microg/L",
                 "Adulto feminino: 15 a 149 microg/L", fonte_ferritina, url_ferritina),
        _rsi_row("Ferro", "Metabolismo do ferro", "Masculino", 12, 120, 65, 175, "mcg/dL",
                 "Masculino acima de 12 anos: 65 a 175 mcg/dL", "Minha Vida / consultoria Fleury - Ferro sérico",
                 "https://www.minhavida.com.br/saude/tratamento/4952-exame-de-ferro"),
        _rsi_row("Ferro", "Metabolismo do ferro", "Feminino", 12, 120, 50, 170, "mcg/dL",
                 "Feminino acima de 12 anos: 50 a 170 mcg/dL", "Minha Vida / consultoria Fleury - Ferro sérico",
                 "https://www.minhavida.com.br/saude/tratamento/4952-exame-de-ferro"),
        _rsi_row("Saturação da transferrina", "Metabolismo do ferro", "Masculino", 12, 120, 20, 50, "%",
                 "Masculino: 20 a 50%", "Minha Vida / consultoria Fleury - Saturação da transferrina",
                 "https://www.minhavida.com.br/saude/tratamento/4952-exame-de-ferro"),
        _rsi_row("Saturação da transferrina", "Metabolismo do ferro", "Feminino", 12, 120, 15, 50, "%",
                 "Feminino: 15 a 50%", "Minha Vida / consultoria Fleury - Saturação da transferrina",
                 "https://www.minhavida.com.br/saude/tratamento/4952-exame-de-ferro"),
    ]

    # 5) Função renal — Mayo Clinic.
    fonte_creat = "Mayo Clinic - Creatinine test"
    url_creat = "https://www.mayoclinic.org/tests-procedures/creatinine-test/about/pac-20384646"
    saida += [
        _rsi_row("Creatinina", "Função renal", "Masculino", 18, 120, 0.74, 1.35, "mg/dL",
                 "Adulto masculino: 0,74 a 1,35 mg/dL", fonte_creat, url_creat),
        _rsi_row("Creatinina", "Função renal", "Feminino", 18, 120, 0.59, 1.04, "mg/dL",
                 "Adulto feminino: 0,59 a 1,04 mg/dL", fonte_creat, url_creat),
    ]

    # 6) Gama GT — Mayo Clinic Laboratories.
    fonte_ggt = "Mayo Clinic Laboratories - Gamma-glutamyltransferase"
    url_ggt = "https://pediatric.testcatalog.org/show/GGT"
    saida += [
        _rsi_row("Gama GT", "Função hepática", "Masculino", 18, 120, 8, 61, "U/L",
                 "Masculino >=18 anos: 8 a 61 U/L", fonte_ggt, url_ggt),
        _rsi_row("Gama GT", "Função hepática", "Feminino", 18, 120, 5, 36, "U/L",
                 "Feminino >=18 anos: 5 a 36 U/L", fonte_ggt, url_ggt),
    ]

    # 7) VHS — referência por sexo/idade. Usada apenas como triagem, depende do método.
    fonte_vhs = "CBDL / ICSH - VHS por sexo e idade"
    url_vhs = "https://cbdl.org.br/entenda-o-que-e-o-exame-vhs-e-sua-finalidade/"
    saida += [
        _rsi_row("VHS", "Inflamação", "Masculino", 0, 49, None, 15, "mm",
                 "Masculino <50 anos: até 15 mm/h", fonte_vhs, url_vhs),
        _rsi_row("VHS", "Inflamação", "Feminino", 0, 49, None, 20, "mm",
                 "Feminino <50 anos: até 20 mm/h", fonte_vhs, url_vhs),
        _rsi_row("VHS", "Inflamação", "Masculino", 50, 84, None, 20, "mm",
                 "Masculino 50 a 84 anos: até 20 mm/h", fonte_vhs, url_vhs),
        _rsi_row("VHS", "Inflamação", "Feminino", 50, 84, None, 30, "mm",
                 "Feminino 50 a 84 anos: até 30 mm/h", fonte_vhs, url_vhs),
    ]

    # 8) Tireoide — Fleury, por idade.
    fonte_tsh = "Fleury - TSH por idade"
    url_tsh = "https://www.fleury.com.br/noticias/tsh-hormonio-tiroestimulante"
    saida += [
        _rsi_row("TSH", "Tireoide", "Todos", 12, 20, 0.51, 4.3, "mUI/L",
                 "12 a 20 anos: 0,51 a 4,3 mUI/L", fonte_tsh, url_tsh),
        _rsi_row("TSH", "Tireoide", "Todos", 20, 60, 0.45, 4.5, "mUI/L",
                 "20 a 60 anos: 0,45 a 4,5 mUI/L", fonte_tsh, url_tsh),
        _rsi_row("TSH", "Tireoide", "Todos", 60, 69, 0.44, 6.8, "mUI/L",
                 "60 a 69 anos: 0,44 a 6,8 mUI/L", fonte_tsh, url_tsh),
        _rsi_row("TSH", "Tireoide", "Todos", 70, 80, 0.44, 7.9, "mUI/L",
                 "70 a 80 anos: 0,44 a 7,9 mUI/L", fonte_tsh, url_tsh),
        _rsi_row("TSH", "Tireoide", "Todos", 81, 120, 0.48, 10.4, "mUI/L",
                 "Acima de 80 anos: 0,48 a 10,4 mUI/L", fonte_tsh, url_tsh),
    ]

    fonte_t4 = "Fleury - T4 livre por idade"
    url_t4 = "https://www.fleury.com.br/noticias/t4-livre-o-que-e"
    saida += [
        _rsi_row("T4 livre", "Tireoide", "Todos", 12, 20, 1.0, 1.7, "ng/dL",
                 "12 a 20 anos: 1,0 a 1,7 ng/dL", fonte_t4, url_t4),
        _rsi_row("T4 livre", "Tireoide", "Todos", 20, 120, 0.9, 1.8, "ng/dL",
                 "Acima de 20 anos: 0,9 a 1,8 ng/dL", fonte_t4, url_t4),
    ]

    campos = [
        "referencia_id", "nome_exame", "nome_padronizado", "grupo", "sexo",
        "idade_min", "idade_max", "valor_min", "valor_max", "unidade",
        "referencia", "referencia_texto", "fonte", "fonte_referencia",
        "fonte_url", "observacoes", "status",
    ]

    _rsi_salvar_csv("referencias_exames_sexo_idade.csv", campos, saida)
    print(f"[REF SEXO/IDADE] Base gerada: {len(saida)} linhas em referencias_exames_sexo_idade.csv")
    return saida


def _rsi_paciente_contexto(paciente_id):
    _, pacientes = _rsi_ler_csv("pacientes.csv")

    pid_alvo = str(paciente_id or "").strip()
    if pid_alvo.isdigit() and len(pid_alvo) < 4:
        pid_alvo = pid_alvo.zfill(4)

    for p in pacientes:
        pid = _rsi_get(p, "paciente_id", "id")
        if pid.isdigit() and len(pid) < 4:
            pid = pid.zfill(4)

        if pid == pid_alvo:
            sexo = _rsi_get(p, "sexo")
            idade = _rsi_float(_rsi_get(p, "idade"))
            return {
                "paciente_id": pid,
                "sexo": sexo,
                "idade": idade if idade is not None else 0,
            }

    return {"paciente_id": pid_alvo, "sexo": "", "idade": 0}


def _rsi_sexo_compativel(sexo_ref, sexo_paciente):
    sr = _rsi_norm(sexo_ref)
    sp = _rsi_norm(sexo_paciente)

    if sr in ["", "todos", "ambos", "ambos os sexos"]:
        return True

    if sp.startswith("masc") and sr.startswith("masc"):
        return True

    if sp.startswith("fem") and sr.startswith("fem"):
        return True

    return False


def _rsi_sexo_peso(sexo_ref, sexo_paciente):
    sr = _rsi_norm(sexo_ref)
    sp = _rsi_norm(sexo_paciente)

    if sp.startswith("masc") and sr.startswith("masc"):
        return 3

    if sp.startswith("fem") and sr.startswith("fem"):
        return 3

    if sr in ["", "todos", "ambos", "ambos os sexos"]:
        return 1

    return 0


def _rsi_idade_compativel(row, idade):
    imin = _rsi_float(_rsi_get(row, "idade_min"))
    imax = _rsi_float(_rsi_get(row, "idade_max"))

    if idade is None:
        idade = 0

    if imin is not None and idade < imin:
        return False

    if imax is not None and idade > imax:
        return False

    return True


def _rsi_nome_match(nome_a, nome_b):
    a = _rsi_norm(nome_a)
    b = _rsi_norm(nome_b)

    aliases = {
        "ast/tgo": ["ast tgo", "tgo", "ast"],
        "alt/tgp": ["alt tgp", "tgp", "alt"],
        "25-oh vitamina d": ["25 oh vitamina d", "vitamina d", "25oh d3", "25oh d3"],
        "hdl colesterol": ["hdl", "colesterol hdl"],
        "ldl colesterol": ["ldl", "colesterol ldl"],
        "vldl colesterol": ["vldl", "colesterol vldl"],
        "gama gt": ["ggt", "gama gt", "gamma gt"],
        "proteína c-reativa ultrassensível": ["pcr", "proteina c reativa", "proteina c reativa ultrassensivel"],
        "eritrocitos": ["hemacias", "eritrocitos"],
        "vhs": ["vhs", "hemossedimentacao", "velocidade de hemossedimentacao"],
    }

    if a == b:
        return True

    for canon, vals in aliases.items():
        vals_n = [_rsi_norm(canon)] + [_rsi_norm(v) for v in vals]
        if a in vals_n and b in vals_n:
            return True

    return a and b and (a == b or a in b or b in a)


def buscar_referencia_sexo_idade(nome_exame, paciente_id=None):
    caminho = _rsi_data_dir() / "referencias_exames_sexo_idade.csv"

    if not caminho.exists():
        gerar_referencias_exames_sexo_idade()

    _, refs = _rsi_ler_csv("referencias_exames_sexo_idade.csv")
    ctx = _rsi_paciente_contexto(paciente_id)
    sexo = ctx.get("sexo", "")
    idade = ctx.get("idade", 0)

    candidatas = [
        r for r in refs
        if _rsi_nome_match(_rsi_get(r, "nome_exame", "nome_padronizado"), nome_exame)
        and _rsi_sexo_compativel(_rsi_get(r, "sexo"), sexo)
        and _rsi_idade_compativel(r, idade)
    ]

    if not candidatas:
        return {}

    candidatas.sort(
        key=lambda r: (
            -_rsi_sexo_peso(_rsi_get(r, "sexo"), sexo),
            (_rsi_float(_rsi_get(r, "idade_max")) or 120) - (_rsi_float(_rsi_get(r, "idade_min")) or 0),
        )
    )

    return dict(candidatas[0])


def analisar_resultado_sexo_idade(nome_exame, resultado, unidade, paciente_id=None):
    ref = buscar_referencia_sexo_idade(nome_exame, paciente_id)

    if not ref:
        return {
            "nome_padronizado": nome_exame,
            "valor_min": "",
            "valor_max": "",
            "status": "Sem análise",
            "referencia": "",
            "fonte_referencia": "",
            "fonte_url": "",
            "mensagem": f"{nome_exame}: sem referência específica para sexo/idade do paciente.",
        }

    valor = _rsi_float(resultado)
    vmin = _rsi_float(_rsi_get(ref, "valor_min"))
    vmax = _rsi_float(_rsi_get(ref, "valor_max"))

    if valor is None:
        status = "Sem análise"
    elif vmin is not None and valor < vmin:
        status = "Baixo"
    elif vmax is not None and valor > vmax:
        status = "Alto"
    elif vmin is not None or vmax is not None:
        status = "Normal"
    else:
        status = "Sem análise"

    nome_pad = _rsi_get(ref, "nome_padronizado", "nome_exame") or nome_exame
    ref_txt = _rsi_get(ref, "referencia_texto", "referencia")
    unidade_ref = unidade or _rsi_get(ref, "unidade")

    msg = f"{nome_pad}: {resultado} {unidade_ref}".strip()
    msg += f" - {status}"
    if ref_txt:
        msg += f". Referência ({_rsi_get(ref, 'sexo')}, {_rsi_get(ref, 'idade_min')}-{_rsi_get(ref, 'idade_max')} anos): {ref_txt}"

    return {
        "nome_padronizado": nome_pad,
        "valor_min": _rsi_get(ref, "valor_min"),
        "valor_max": _rsi_get(ref, "valor_max"),
        "status": status,
        "referencia": ref_txt,
        "fonte_referencia": _rsi_get(ref, "fonte_referencia", "fonte"),
        "fonte_url": _rsi_get(ref, "fonte_url"),
        "sexo_referencia": _rsi_get(ref, "sexo"),
        "idade_min": _rsi_get(ref, "idade_min"),
        "idade_max": _rsi_get(ref, "idade_max"),
        "mensagem": msg,
    }


def recalcular_analises_por_sexo_idade():
    campos, rows = _rsi_ler_csv("analise_exames.csv")

    if not rows:
        return 0

    extras = ["referencia", "referencia_texto", "sexo_referencia", "idade_min", "idade_max", "fonte_url"]
    for c in extras:
        if c not in campos:
            campos.append(c)

    alterados = 0

    for r in rows:
        pid = _rsi_get(r, "paciente_id", "id_paciente")
        nome = _rsi_get(r, "nome_exame", "nome_padronizado", "exame_nome", "nome", "exame")
        resultado = _rsi_get(r, "resultado", "valor")
        unidade = _rsi_get(r, "unidade")

        if not pid or not nome or not resultado:
            continue

        analise = analisar_resultado_sexo_idade(nome, resultado, unidade, pid)

        r["nome_exame"] = analise["nome_padronizado"] or nome
        r["nome_padronizado"] = analise["nome_padronizado"] or nome
        r["valor_min"] = analise["valor_min"]
        r["valor_max"] = analise["valor_max"]
        r["status"] = analise["status"]
        r["mensagem"] = analise["mensagem"]
        r["referencia"] = analise["referencia"]
        r["referencia_texto"] = analise["referencia"]
        r["fonte_referencia"] = analise["fonte_referencia"]
        r["fonte_url"] = analise["fonte_url"]
        r["sexo_referencia"] = analise.get("sexo_referencia", "")
        r["idade_min"] = analise.get("idade_min", "")
        r["idade_max"] = analise.get("idade_max", "")

        alterados += 1

    _rsi_salvar_csv("analise_exames.csv", campos, rows)

    try:
        if "_perf_limpar_cache" in globals():
            _perf_limpar_cache()
    except Exception:
        pass

    print(f"[REF SEXO/IDADE] Análises recalculadas por sexo/idade: {alterados}")
    return alterados


try:
    _rsi_persistir_original
except NameError:
    _rsi_persistir_original = _patch_persistir_resultado_item


def _patch_persistir_resultado_item(item):
    if not isinstance(item, dict):
        return False

    pid = _patch_pid(item)
    nome_exame = _patch_nome_exame(item)
    resultado = _patch_resultado_valor(item)
    data_exame = _patch_data_exame(item)
    unidade = _patch_get(item, "unidade")

    if not pid or not nome_exame or not resultado:
        print("[REF SEXO/IDADE] Ignorando exame sem dados mínimos:", item)
        return False

    analise = analisar_resultado_sexo_idade(nome_exame, resultado, unidade, pid)

    if not unidade:
        ref = buscar_referencia_sexo_idade(nome_exame, pid)
        unidade = _rsi_get(ref, "unidade")

    exames = _patch_ler_csv("exames.csv")
    analises = _patch_ler_csv("analise_exames.csv")

    chave = (
        pid,
        _patch_norm(data_exame),
        _patch_norm(nome_exame),
        _patch_norm(resultado),
        _patch_norm(unidade),
    )

    chaves_exames = {_patch_chave(r) for r in exames}
    chaves_analises = {_patch_chave(r) for r in analises}

    mudou = False

    if chave not in chaves_exames:
        exames.append({
            "exame_id": _patch_proximo_id(exames, "exame_id", 4),
            "paciente_id": pid,
            "data_exame": data_exame,
            "nome_exame": nome_exame,
            "resultado": resultado,
            "unidade": unidade,
            "observacoes": _patch_get(item, "observacoes", "obs") or "Lançado pela interface NutriSoft",
        })

        _patch_salvar_csv(
            "exames.csv",
            exames,
            ["exame_id", "paciente_id", "data_exame", "nome_exame", "resultado", "unidade", "observacoes"],
        )
        mudou = True

    if chave not in chaves_analises:
        analises.append({
            "analise_id": _patch_proximo_id(analises, "analise_id"),
            "paciente_id": pid,
            "data_exame": data_exame,
            "nome_exame": nome_exame,
            "nome_padronizado": analise["nome_padronizado"],
            "resultado": resultado,
            "unidade": unidade,
            "valor_min": analise["valor_min"],
            "valor_max": analise["valor_max"],
            "status": analise["status"],
            "mensagem": analise["mensagem"],
            "referencia": analise["referencia"],
            "referencia_texto": analise["referencia"],
            "fonte_referencia": analise["fonte_referencia"],
            "fonte_url": analise["fonte_url"],
            "sexo_referencia": analise.get("sexo_referencia", ""),
            "idade_min": analise.get("idade_min", ""),
            "idade_max": analise.get("idade_max", ""),
        })

        _patch_salvar_csv(
            "analise_exames.csv",
            analises,
            [
                "analise_id", "paciente_id", "data_exame", "nome_exame", "nome_padronizado",
                "resultado", "unidade", "valor_min", "valor_max", "status", "mensagem",
                "referencia", "referencia_texto", "fonte_referencia", "fonte_url",
                "sexo_referencia", "idade_min", "idade_max",
            ],
        )
        mudou = True

    if mudou:
        print(
            f"[REF SEXO/IDADE] Exame persistido: paciente={pid} | exame={nome_exame} | "
            f"status={analise['status']} | ref={analise.get('sexo_referencia', '')} "
            f"{analise.get('idade_min', '')}-{analise.get('idade_max', '')}"
        )

    return mudou

# ===== FIM PATCH REFERENCIAS POR SEXO E IDADE =====

















# ===== PATCH DATATABLE EXAMES ALTERADOS: REFERENCIA APOS RESULTADO =====

import csv as _dtref_csv
import re as _dtref_re
import unicodedata as _dtref_unicodedata
from pathlib import Path as _dtref_Path


def _dtref_data_dir():
    try:
        return _patch_data_dir()
    except Exception:
        return _dtref_Path(__file__).resolve().parent / "data_flet"


def _dtref_norm(valor):
    texto = str(valor or "").strip().lower()
    texto = _dtref_unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not _dtref_unicodedata.combining(c))
    texto = texto.replace("_", " ").replace("-", " ")
    texto = _dtref_re.sub(r"[^a-z0-9%/., ]+", " ", texto)
    return " ".join(texto.split())


def _dtref_data_iso(valor):
    texto = str(valor or "").strip()

    m = _dtref_re.match(r"^(\d{2})/(\d{2})/(\d{4})$", texto)
    if m:
        dia, mes, ano = m.groups()
        return f"{ano}-{mes}-{dia}"

    return texto


def _dtref_texto_controle(ctrl):
    if ctrl is None:
        return ""

    for attr in ["value", "text"]:
        try:
            valor = getattr(ctrl, attr)
            if valor is not None and str(valor).strip():
                return str(valor).strip()
        except Exception:
            pass

    try:
        content = getattr(ctrl, "content", None)
        if content is not None:
            valor = _dtref_texto_controle(content)
            if valor:
                return valor
    except Exception:
        pass

    try:
        label = getattr(ctrl, "label", None)
        if label is not None:
            valor = _dtref_texto_controle(label)
            if valor:
                return valor
    except Exception:
        pass

    try:
        controls = getattr(ctrl, "controls", None)
        if controls:
            partes = []
            for c in controls:
                valor = _dtref_texto_controle(c)
                if valor:
                    partes.append(valor)
            return " ".join(partes).strip()
    except Exception:
        pass

    return ""


def _dtref_texto_coluna(col):
    try:
        return _dtref_texto_controle(col.label)
    except Exception:
        pass

    try:
        return _dtref_texto_controle(col.content)
    except Exception:
        pass

    return _dtref_texto_controle(col)


def _dtref_texto_celula(cell):
    try:
        return _dtref_texto_controle(cell.content)
    except Exception:
        return _dtref_texto_controle(cell)


def _dtref_ler_analises():
    caminho = _dtref_data_dir() / "analise_exames.csv"

    if not caminho.exists():
        return []

    with open(caminho, newline="", encoding="utf-8-sig") as f:
        reader = _dtref_csv.DictReader(f)
        return [
            {
                str(k or "").replace("\ufeff", "").strip(): "" if v is None else str(v).strip()
                for k, v in r.items()
            }
            for r in reader
        ]


def _dtref_referencia_por_linha(data_tabela, exame_tabela, resultado_tabela):
    data_iso = _dtref_data_iso(data_tabela)
    exame_n = _dtref_norm(exame_tabela)
    resultado_n = _dtref_norm(resultado_tabela)

    paciente_id = str(globals().get("PACIENTE_SELECIONADO_ID", "") or "").strip()
    if paciente_id.isdigit() and len(paciente_id) < 4:
        paciente_id = paciente_id.zfill(4)

    candidatos = []

    for r in _dtref_ler_analises():
        pid = str(r.get("paciente_id") or r.get("id_paciente") or "").strip()
        if pid.isdigit() and len(pid) < 4:
            pid = pid.zfill(4)

        if paciente_id and pid and pid != paciente_id:
            continue

        data = r.get("data_exame") or r.get("data") or ""

        nome = (
            r.get("nome_exame")
            or r.get("nome_padronizado")
            or r.get("exame_nome")
            or r.get("nome")
            or r.get("exame")
            or ""
        )

        resultado = f"{r.get('resultado', '')} {r.get('unidade', '')}".strip()

        data_match = not data_iso or not data or _dtref_data_iso(data) == data_iso

        exame_match = (
            exame_n
            and _dtref_norm(nome)
            and (
                exame_n == _dtref_norm(nome)
                or exame_n in _dtref_norm(nome)
                or _dtref_norm(nome) in exame_n
            )
        )

        resultado_match = True
        if resultado_n:
            resultado_match = (
                resultado_n == _dtref_norm(resultado)
                or resultado_n in _dtref_norm(resultado)
                or _dtref_norm(r.get("resultado")) in resultado_n
            )

        if data_match and exame_match and resultado_match:
            candidatos.append(r)

    if not candidatos:
        return "-"

    r = candidatos[0]
    ref = r.get("referencia") or r.get("referencia_texto") or ""

    if not ref:
        vmin = r.get("valor_min") or ""
        vmax = r.get("valor_max") or ""
        unidade = r.get("unidade") or ""

        if vmin and vmax:
            ref = f"{vmin} a {vmax} {unidade}".strip()
        elif vmin:
            ref = f">= {vmin} {unidade}".strip()
        elif vmax:
            ref = f"<= {vmax} {unidade}".strip()

    sexo = r.get("sexo_referencia") or ""
    idade_min = r.get("idade_min") or ""
    idade_max = r.get("idade_max") or ""

    if ref and (sexo or idade_min or idade_max):
        return f"{ref}\n{sexo or 'Todos'}, {idade_min or '0'}-{idade_max or '120'} anos"

    return ref or "-"


def _dtref_cell(texto, largura=170, negrito=False):
    return ft.Container(
        width=largura,
        padding=6,
        content=ft.Text(
            str(texto or "-"),
            size=10 if negrito else 11,
            weight=ft.FontWeight.BOLD if negrito else ft.FontWeight.NORMAL,
            color="#111827" if negrito else "#374151",
            no_wrap=False,
            max_lines=None,
            overflow=ft.TextOverflow.VISIBLE,
        ),
    )


def _dtref_scroll():
    try:
        return ft.ScrollMode.AUTO
    except Exception:
        return "auto"


def _dtref_linha_parece_exames_alterados(rows):
    if not rows:
        return False

    try:
        cells = list(rows[0].cells)
    except Exception:
        return False

    if len(cells) != 4:
        return False

    data_txt = _dtref_texto_celula(cells[0])
    status_txt = _dtref_norm(_dtref_texto_celula(cells[3]))

    data_ok = bool(
        _dtref_re.match(r"^\d{2}/\d{2}/\d{4}$", data_txt)
        or _dtref_re.match(r"^\d{4}-\d{2}-\d{2}$", data_txt)
    )

    status_ok = any(
        termo in status_txt
        for termo in ["alto", "baixo", "alterado", "critico", "sem analise", "normal"]
    )

    return data_ok and status_ok


try:
    _dtref_datatable_original
except NameError:
    _dtref_datatable_original = ft.DataTable


def _dtref_datatable_wrapper(*args, **kwargs):
    columns = kwargs.get("columns")
    rows = kwargs.get("rows")

    if columns is None and len(args) >= 1:
        try:
            if isinstance(args[0], list):
                columns = args[0]
        except Exception:
            pass

    if rows is None:
        rows = []

    labels = [_dtref_norm(_dtref_texto_coluna(c)) for c in (columns or [])]

    alvo_por_labels = (
        len(labels) == 4
        and labels[0] == "data"
        and labels[1] == "exame"
        and labels[2] == "resultado"
        and labels[3] == "status"
    )

    alvo_por_linha = (
        len(columns or []) == 4
        and _dtref_linha_parece_exames_alterados(rows)
    )

    if not (alvo_por_labels or alvo_por_linha):
        return _dtref_datatable_original(*args, **kwargs)

    novas_colunas = [
        columns[0],
        columns[1],
        columns[2],
        ft.DataColumn(_dtref_cell("Referência aplicada", 230, negrito=True)),
        columns[3],
    ]

    novas_linhas = []

    for row in rows or []:
        try:
            cells = list(row.cells)
        except Exception:
            novas_linhas.append(row)
            continue

        if len(cells) != 4:
            novas_linhas.append(row)
            continue

        data_txt = _dtref_texto_celula(cells[0])
        exame_txt = _dtref_texto_celula(cells[1])
        resultado_txt = _dtref_texto_celula(cells[2])

        ref_txt = _dtref_referencia_por_linha(
            data_txt,
            exame_txt,
            resultado_txt,
        )

        novas_cells = [
            cells[0],
            cells[1],
            cells[2],
            ft.DataCell(_dtref_cell(ref_txt, 230)),
            cells[3],
        ]

        try:
            novas_linhas.append(ft.DataRow(cells=novas_cells))
        except Exception:
            novas_linhas.append(row)

    base_dt = globals().get("_patch_ft_datatable_original", _dtref_datatable_original)

    tabela = base_dt(
        columns=novas_colunas,
        rows=novas_linhas,
        column_spacing=8,
        horizontal_margin=8,
    )

    return ft.Row(
        scroll=_dtref_scroll(),
        controls=[tabela],
    )


ft.DataTable = _dtref_datatable_wrapper

# ===== FIM PATCH DATATABLE EXAMES ALTERADOS: REFERENCIA APOS RESULTADO =====





# ===== PATCH SALVAMENTO DEFINITIVO EXAMES CSV =====

import csv as _sdef_csv
import re as _sdef_re
import unicodedata as _sdef_unicodedata
from pathlib import Path as _sdef_Path


def _sdef_data_dir():
    try:
        return _patch_data_dir()
    except Exception:
        return _sdef_Path(__file__).resolve().parent / "data_flet"


def _sdef_norm(valor):
    texto = str(valor or "").strip().lower()
    texto = _sdef_unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not _sdef_unicodedata.combining(c))
    texto = texto.replace("_", " ").replace("-", " ")
    texto = _sdef_re.sub(r"[^a-z0-9%/., ]+", " ", texto)
    return " ".join(texto.split())


def _sdef_get(row, *campos):
    if not isinstance(row, dict):
        return ""

    limpo = {
        str(k or "").replace("\ufeff", "").strip(): "" if v is None else str(v).strip()
        for k, v in row.items()
    }

    for campo in campos:
        valor = limpo.get(str(campo or "").strip(), "")
        if valor:
            return valor

    return ""


def _sdef_ler_csv(nome):
    caminho = _sdef_data_dir() / nome

    if not caminho.exists():
        return [], []

    with open(caminho, newline="", encoding="utf-8-sig") as f:
        reader = _sdef_csv.DictReader(f)
        campos = [
            str(c or "").replace("\ufeff", "").strip()
            for c in (reader.fieldnames or [])
        ]
        rows = []
        for r in reader:
            rows.append({
                str(k or "").replace("\ufeff", "").strip(): "" if v is None else str(v).strip()
                for k, v in r.items()
            })

    return campos, rows


def _sdef_salvar_csv(nome, campos, rows):
    caminho = _sdef_data_dir() / nome
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_suffix(caminho.suffix + ".tmp")

    campos = list(campos or [])

    for r in rows:
        for k in r.keys():
            if k not in campos:
                campos.append(k)

    with open(tmp, "w", newline="", encoding="utf-8-sig") as f:
        writer = _sdef_csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({c: r.get(c, "") for c in campos})

    tmp.replace(caminho)


def _sdef_data_iso(valor):
    texto = str(valor or "").strip()

    m = _sdef_re.match(r"^(\d{2})/(\d{2})/(\d{4})$", texto)
    if m:
        dia, mes, ano = m.groups()
        return f"{ano}-{mes}-{dia}"

    return texto


def _sdef_pid(item):
    pid = _sdef_get(item, "paciente_id", "id_paciente")

    if not pid:
        try:
            pid = _patch_pid(item)
        except Exception:
            pid = ""

    pid = str(pid or "").strip()

    if pid.isdigit() and len(pid) < 4:
        pid = pid.zfill(4)

    return pid


def _sdef_nome_exame(item):
    nome = _sdef_get(
        item,
        "nome_exame",
        "exame_nome",
        "nome_padronizado",
        "nome",
        "exame",
        "analito",
        "descricao",
    )

    if nome and nome not in ["-", "None", "null"]:
        return nome

    try:
        nome = _patch_nome_exame(item)
        if nome and nome not in ["-", "None", "null"]:
            return nome
    except Exception:
        pass

    return ""


def _sdef_resultado(item):
    return _sdef_get(item, "resultado", "valor", "valor_resultado", "resultado_exame")


def _sdef_unidade(item):
    return _sdef_get(item, "unidade")


def _sdef_chave(row):
    pid = _sdef_pid(row)
    data = _sdef_data_iso(_sdef_get(row, "data_exame", "data"))
    nome = _sdef_nome_exame(row)
    resultado = _sdef_resultado(row)
    unidade = _sdef_unidade(row)

    return (
        pid,
        _sdef_norm(data),
        _sdef_norm(nome),
        _sdef_norm(resultado),
        _sdef_norm(unidade),
    )


def _sdef_proximo_id(rows, campo, largura=0):
    maior = 0

    for r in rows:
        valor = _sdef_get(r, campo)
        m = _sdef_re.search(r"\d+", str(valor or ""))
        if m:
            try:
                maior = max(maior, int(m.group(0)))
            except Exception:
                pass

    novo = maior + 1
    return str(novo).zfill(largura) if largura else str(novo)


def _sdef_analise(item):
    pid = _sdef_pid(item)
    nome = _sdef_nome_exame(item)
    resultado = _sdef_resultado(item)
    unidade = _sdef_unidade(item)

    try:
        analise = analisar_resultado_sexo_idade(nome, resultado, unidade, pid)
        if isinstance(analise, dict):
            return analise
    except Exception as exc:
        print(f"[SALVAR EXAME DEFINITIVO] Falha análise sexo/idade, usando fallback: {exc}")

    try:
        analise = _patch_analisar(nome, resultado, unidade)
        if isinstance(analise, dict):
            return analise
    except Exception as exc:
        print(f"[SALVAR EXAME DEFINITIVO] Falha análise fallback: {exc}")

    return {
        "nome_padronizado": nome,
        "valor_min": "",
        "valor_max": "",
        "status": "Sem análise",
        "mensagem": f"{nome}: {resultado} {unidade}",
        "referencia": _sdef_get(item, "referencia", "referencia_texto"),
        "referencia_texto": _sdef_get(item, "referencia", "referencia_texto"),
        "fonte_referencia": _sdef_get(item, "fonte_referencia", "fonte"),
        "fonte_url": _sdef_get(item, "fonte_url"),
        "sexo_referencia": "",
        "idade_min": "",
        "idade_max": "",
    }


def _sdef_limpar_cache():
    try:
        if "_perf_limpar_cache" in globals():
            _perf_limpar_cache()
    except Exception as exc:
        print(f"[SALVAR EXAME DEFINITIVO] Falha ao limpar cache de performance: {exc}")

    globals()["EXAMES_CADASTRADOS_MOCK"] = {}

    for nome_cache in [
        "_PERF_CSV_CACHE",
        "_PERF_DISPONIVEIS_CACHE",
        "_PERF_BLOQUEADOS_CACHE",
    ]:
        try:
            cache = globals().get(nome_cache)
            if hasattr(cache, "clear"):
                cache.clear()
        except Exception:
            pass

    for nome_cache in [
        "_PERF_REFS_CACHE",
        "_PERF_PACIENTES_CACHE",
        "_PERF_CADASTRADOS_CACHE",
        "_PERF_SYNC_CACHE",
        "_PERF_PACIENTES_UI_CACHE",
    ]:
        try:
            cache = globals().get(nome_cache)
            if isinstance(cache, dict):
                cache["key"] = None
                cache["value"] = None
        except Exception:
            pass


def salvar_resultado_exame_csv_definitivo(item):
    if not isinstance(item, dict):
        print("[SALVAR EXAME DEFINITIVO] Item inválido:", item)
        return False

    pid = _sdef_pid(item)
    data_exame = _sdef_data_iso(_sdef_get(item, "data_exame", "data"))
    nome_exame = _sdef_nome_exame(item)
    resultado = _sdef_resultado(item)
    unidade = _sdef_unidade(item)

    if not pid or not data_exame or not nome_exame or not resultado:
        print(
            "[SALVAR EXAME DEFINITIVO] Dados mínimos ausentes:",
            {
                "paciente_id": pid,
                "data_exame": data_exame,
                "nome_exame": nome_exame,
                "resultado": resultado,
                "item": item,
            },
        )
        return False

    analise = _sdef_analise(item)

    if not unidade:
        unidade = _sdef_get(analise, "unidade")
        if not unidade:
            try:
                ref = buscar_referencia_sexo_idade(nome_exame, pid)
                unidade = _sdef_get(ref, "unidade")
            except Exception:
                unidade = ""

    item["paciente_id"] = pid
    item["data"] = data_exame
    item["data_exame"] = data_exame
    item["nome_exame"] = nome_exame
    item["exame_nome"] = nome_exame
    item["nome"] = nome_exame
    item["exame"] = nome_exame
    item["resultado"] = resultado
    item["unidade"] = unidade
    item["status"] = _sdef_get(analise, "status") or "Sem análise"
    item["referencia"] = _sdef_get(analise, "referencia", "referencia_texto")
    item["referencia_texto"] = item["referencia"]
    item["fonte_referencia"] = _sdef_get(analise, "fonte_referencia", "fonte")
    item["fonte_url"] = _sdef_get(analise, "fonte_url")
    item["sexo_referencia"] = _sdef_get(analise, "sexo_referencia")
    item["idade_min"] = _sdef_get(analise, "idade_min")
    item["idade_max"] = _sdef_get(analise, "idade_max")

    campos_exames, exames = _sdef_ler_csv("exames.csv")
    campos_analise, analises = _sdef_ler_csv("analise_exames.csv")

    chave = _sdef_chave(item)

    chaves_exames = {_sdef_chave(r) for r in exames}
    chaves_analises = {_sdef_chave(r) for r in analises}

    mudou = False

    if chave not in chaves_exames:
        exames.append({
            "exame_id": _sdef_proximo_id(exames, "exame_id", 4),
            "paciente_id": pid,
            "data_exame": data_exame,
            "nome_exame": nome_exame,
            "resultado": resultado,
            "unidade": unidade,
            "observacoes": _sdef_get(item, "observacoes", "observacao", "obs") or "Lançado pela interface NutriSoft",
        })

        for c in ["exame_id", "paciente_id", "data_exame", "nome_exame", "resultado", "unidade", "observacoes"]:
            if c not in campos_exames:
                campos_exames.append(c)

        _sdef_salvar_csv("exames.csv", campos_exames, exames)
        mudou = True

    if chave not in chaves_analises:
        analises.append({
            "analise_id": _sdef_proximo_id(analises, "analise_id"),
            "paciente_id": pid,
            "data_exame": data_exame,
            "nome_exame": nome_exame,
            "nome_padronizado": _sdef_get(analise, "nome_padronizado") or nome_exame,
            "resultado": resultado,
            "unidade": unidade,
            "valor_min": _sdef_get(analise, "valor_min"),
            "valor_max": _sdef_get(analise, "valor_max"),
            "status": _sdef_get(analise, "status") or "Sem análise",
            "mensagem": _sdef_get(analise, "mensagem"),
            "referencia": _sdef_get(analise, "referencia", "referencia_texto"),
            "referencia_texto": _sdef_get(analise, "referencia", "referencia_texto"),
            "fonte_referencia": _sdef_get(analise, "fonte_referencia", "fonte"),
            "fonte_url": _sdef_get(analise, "fonte_url"),
            "sexo_referencia": _sdef_get(analise, "sexo_referencia"),
            "idade_min": _sdef_get(analise, "idade_min"),
            "idade_max": _sdef_get(analise, "idade_max"),
        })

        for c in [
            "analise_id",
            "paciente_id",
            "data_exame",
            "nome_exame",
            "nome_padronizado",
            "resultado",
            "unidade",
            "valor_min",
            "valor_max",
            "status",
            "mensagem",
            "referencia",
            "referencia_texto",
            "fonte_referencia",
            "fonte_url",
            "sexo_referencia",
            "idade_min",
            "idade_max",
        ]:
            if c not in campos_analise:
                campos_analise.append(c)

        _sdef_salvar_csv("analise_exames.csv", campos_analise, analises)
        mudou = True

    _sdef_limpar_cache()

    if mudou:
        print(
            f"[SALVAR EXAME DEFINITIVO] Gravado em CSV: paciente={pid} | "
            f"data={data_exame} | exame={nome_exame} | resultado={resultado} {unidade} | "
            f"status={item['status']}"
        )
    else:
        print(
            f"[SALVAR EXAME DEFINITIVO] Registro já existia no CSV: paciente={pid} | "
            f"data={data_exame} | exame={nome_exame} | resultado={resultado} {unidade}"
        )

    return True

# ===== FIM PATCH SALVAMENTO DEFINITIVO EXAMES CSV =====





# ===== PATCH LISTA CADASTRADOS DEFINITIVA CSV =====

import csv as _lcd_csv
import re as _lcd_re
import unicodedata as _lcd_unicodedata
from pathlib import Path as _lcd_Path


def _lcd_data_dir():
    try:
        return _patch_data_dir()
    except Exception:
        return _lcd_Path(__file__).resolve().parent / "data_flet"


def _lcd_norm(valor):
    texto = str(valor or "").strip().lower()
    texto = _lcd_unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not _lcd_unicodedata.combining(c))
    texto = texto.replace("_", " ").replace("-", " ")
    texto = _lcd_re.sub(r"[^a-z0-9%/., ]+", " ", texto)
    return " ".join(texto.split())


def _lcd_id(valor):
    texto = _lcd_norm(valor)
    texto = _lcd_re.sub(r"[^a-z0-9]+", "_", texto).strip("_")
    return texto


def _lcd_get(row, *campos):
    if not isinstance(row, dict):
        return ""

    limpo = {
        str(k or "").replace("\ufeff", "").strip(): "" if v is None else str(v).strip()
        for k, v in row.items()
    }

    for campo in campos:
        valor = limpo.get(str(campo or "").strip(), "")
        if valor:
            return valor

    return ""


def _lcd_data_iso(valor):
    texto = str(valor or "").strip()

    m = _lcd_re.match(r"^(\d{2})/(\d{2})/(\d{4})$", texto)
    if m:
        dia, mes, ano = m.groups()
        return f"{ano}-{mes}-{dia}"

    m = _lcd_re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", texto)
    if m:
        ano, mes, dia = m.groups()
        return f"{ano}-{int(mes):02d}-{int(dia):02d}"

    return texto


def _lcd_pid(valor):
    pid = str(valor or "").strip()
    if pid.isdigit() and len(pid) < 4:
        pid = pid.zfill(4)
    return pid


def _lcd_ler_csv(nome):
    caminho = _lcd_data_dir() / nome

    if not caminho.exists():
        return []

    with open(caminho, newline="", encoding="utf-8-sig") as f:
        reader = _lcd_csv.DictReader(f)
        return [
            {
                str(k or "").replace("\ufeff", "").strip(): "" if v is None else str(v).strip()
                for k, v in r.items()
            }
            for r in reader
        ]


def _lcd_nome_exame(row):
    nome = _lcd_get(
        row,
        "nome_exame",
        "nome_padronizado",
        "exame_nome",
        "nome",
        "exame",
        "descricao",
        "analito",
        "id",
    )

    if nome and nome not in ["-", "None", "null"]:
        return nome

    return ""


def _lcd_tokens_nome(nome):
    tokens = set()

    nome = str(nome or "").strip()
    if not nome:
        return tokens

    tokens.add(_lcd_norm(nome))
    tokens.add(_lcd_id(nome))

    aliases = {
        "ferritina": ["ferritina", "ferr"],
        "ferro": ["ferro", "ferro_serico"],
        "saturacao_da_transferrina": [
            "saturacao_da_transferrina",
            "saturacao_transferrina",
            "transferrina_saturacao",
        ],
        "glicose": ["glicose", "glicemia", "glucose"],
        "hemoglobina_glicada": ["hemoglobina_glicada", "hba1c", "glicada"],
        "colesterol_total": ["colesterol_total", "colesterol"],
        "triglicerideos": ["triglicerideos", "triglicerides", "trig"],
        "creatinina": ["creatinina", "creat"],
    }

    base = _lcd_id(nome)

    for canon, vals in aliases.items():
        vals_norm = {_lcd_id(v) for v in vals}
        vals_norm.add(canon)

        if base in vals_norm:
            tokens.update(vals_norm)

    return {t for t in tokens if t}


def _lcd_tokens_item(item):
    tokens = set()

    if isinstance(item, dict):
        for campo in [
            "id",
            "id_canonico",
            "nome_exame",
            "nome_padronizado",
            "exame_nome",
            "nome",
            "exame",
            "descricao",
            "analito",
        ]:
            valor = _lcd_get(item, campo)
            tokens.update(_lcd_tokens_nome(valor))

        nome = _lcd_nome_exame(item)
        if nome:
            tokens.update(_lcd_tokens_nome(nome))
    else:
        tokens.update(_lcd_tokens_nome(item))

    return {t for t in tokens if t}


def _lcd_referencia_resumo(row):
    ref = _lcd_get(row, "referencia", "referencia_texto")

    if not ref:
        vmin = _lcd_get(row, "valor_min")
        vmax = _lcd_get(row, "valor_max")
        unidade = _lcd_get(row, "unidade")

        if vmin and vmax:
            ref = f"{vmin} - {vmax} {unidade}".strip()
        elif vmin:
            ref = f">= {vmin} {unidade}".strip()
        elif vmax:
            ref = f"<= {vmax} {unidade}".strip()

    return ref


def _lcd_item_cadastrado(row):
    nome = _lcd_nome_exame(row)
    grupo = _lcd_get(row, "grupo")

    if not grupo:
        try:
            ref = _patch_ref(nome)
            grupo = _patch_get(ref, "grupo")
        except Exception:
            grupo = ""

    if not grupo:
        try:
            grupo = _patch_grupo_exame_correto(nome, "")
        except Exception:
            grupo = ""

    referencia = _lcd_referencia_resumo(row)

    fonte = _lcd_get(row, "fonte_referencia", "fonte")
    if not fonte:
        try:
            ref = _patch_ref(nome)
            fonte = _patch_get(ref, "fonte_referencia", "fonte")
        except Exception:
            fonte = ""

    item = dict(row)
    item.update({
        "id": _lcd_id(nome),
        "id_canonico": _lcd_id(nome),
        "nome": nome,
        "nome_exame": nome,
        "exame_nome": nome,
        "exame": nome,
        "grupo": grupo,
        "referencia": referencia,
        "referencia_texto": referencia,
        "fonte": fonte,
        "fonte_referencia": fonte,
    })

    return item


def _lcd_linhas_cadastradas_csv(paciente_id, data_exame):
    pid_alvo = _lcd_pid(paciente_id)
    data_alvo = _lcd_data_iso(data_exame)

    linhas = []

    # analise_exames.csv é a fonte mais completa para exibir referência/status.
    for row in _lcd_ler_csv("analise_exames.csv"):
        pid = _lcd_pid(_lcd_get(row, "paciente_id", "id_paciente"))
        data = _lcd_data_iso(_lcd_get(row, "data_exame", "data"))

        if pid == pid_alvo and data == data_alvo:
            nome = _lcd_nome_exame(row)
            if nome:
                linhas.append(_lcd_item_cadastrado(row))

    # fallback: se o exame existe só em exames.csv por algum erro antigo.
    tokens_existentes = set()
    for item in linhas:
        tokens_existentes.update(_lcd_tokens_item(item))

    for row in _lcd_ler_csv("exames.csv"):
        pid = _lcd_pid(_lcd_get(row, "paciente_id", "id_paciente"))
        data = _lcd_data_iso(_lcd_get(row, "data_exame", "data"))

        if pid != pid_alvo or data != data_alvo:
            continue

        nome = _lcd_nome_exame(row)
        tokens = _lcd_tokens_nome(nome)

        if not nome or (tokens and tokens & tokens_existentes):
            continue

        linhas.append(_lcd_item_cadastrado(row))
        tokens_existentes.update(tokens)

    # Dedup final por token canônico.
    saida = []
    vistos = set()

    for item in linhas:
        tokens = _lcd_tokens_item(item)
        chave = sorted(tokens)[0] if tokens else _lcd_id(_lcd_nome_exame(item))

        if chave in vistos:
            continue

        vistos.add(chave)
        saida.append(item)

    saida.sort(key=lambda x: _lcd_norm(_lcd_nome_exame(x)))

    return saida


try:
    _lcd_exames_ja_original
except NameError:
    _lcd_exames_ja_original = exames_ja_cadastrados_por_data


def exames_ja_cadastrados_por_data(paciente_id, data_exame):
    linhas = _lcd_linhas_cadastradas_csv(paciente_id, data_exame)

    try:
        globals()["EXAMES_CADASTRADOS_MOCK"] = {
            (
                _lcd_pid(paciente_id),
                _lcd_data_iso(data_exame),
            ): [
                item.get("id") or item.get("id_canonico") or _lcd_id(_lcd_nome_exame(item))
                for item in linhas
            ]
        }
    except Exception:
        pass

    return linhas


try:
    _lcd_disponiveis_original
except NameError:
    _lcd_disponiveis_original = exames_disponiveis_por_data


def exames_disponiveis_por_data(paciente_id, data_exame):
    try:
        lista = _lcd_disponiveis_original(paciente_id, data_exame)
    except Exception:
        lista = []

    cadastrados = _lcd_linhas_cadastradas_csv(paciente_id, data_exame)

    tokens_bloqueados = set()
    for item in cadastrados:
        tokens_bloqueados.update(_lcd_tokens_item(item))

    disponiveis = []

    for exame in lista or []:
        tokens_exame = _lcd_tokens_item(exame)

        if tokens_exame and tokens_exame & tokens_bloqueados:
            continue

        disponiveis.append(exame)

    return disponiveis


def _lcd_refresh_pos_operacao_exame():
    try:
        if "_perf_limpar_cache" in globals():
            _perf_limpar_cache()
    except Exception:
        pass

    try:
        sincronizar_resultados_exames_mock_data_flet()
    except Exception as exc:
        print(f"[LISTA CADASTRADOS] Falha ao sincronizar resultados: {exc}")

    try:
        atualizar_pacientes_csv_real_definitivo()
    except Exception as exc:
        print(f"[LISTA CADASTRADOS] Falha ao atualizar pacientes: {exc}")


try:
    _lcd_salvar_definitivo_original
except NameError:
    _lcd_salvar_definitivo_original = salvar_resultado_exame_csv_definitivo


def salvar_resultado_exame_csv_definitivo(item):
    ok = _lcd_salvar_definitivo_original(item)

    if ok:
        _lcd_refresh_pos_operacao_exame()
        print("[LISTA CADASTRADOS] Índice atualizado após salvar exame.")

    return ok


try:
    _lcd_excluir_original
except NameError:
    _lcd_excluir_original = excluir_exame_cadastrado_errado


def excluir_exame_cadastrado_errado(paciente_id, data_exame, exame):
    total = _lcd_excluir_original(paciente_id, data_exame, exame)

    if total:
        _lcd_refresh_pos_operacao_exame()
        print("[LISTA CADASTRADOS] Índice atualizado após excluir exame.")

    return total

# ===== FIM PATCH LISTA CADASTRADOS DEFINITIVA CSV =====



if __name__ == "__main__":
    inicializar_base_flet()
    gerar_referencias_exames_sexo_idade()
    recalcular_analises_por_sexo_idade()
    gerar_referencias_exames_sexo_idade()
    recalcular_analises_por_sexo_idade()
    deduplicar_exames_e_analises_csv()
    atualizar_pacientes_csv_real_definitivo()
    aplicar_catalogo_fleury_nas_listas_do_app()
    sincronizar_data_flet_para_interface()
    ativar_persistencia_nutricional_data_flet()
    inicializar_base_taco_cardapio()
    ft.run(main)
