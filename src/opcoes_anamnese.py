"""
Opções padronizadas para reduzir escrita livre na anamnese.

A ideia é manter a ficha mais rápida, padronizada e analisável,
preservando campos abertos apenas para observações clínicas relevantes.
"""

SEXO = ["Não informado", "F", "M", "Outro"]

SIM_NAO = ["", "Sim", "Não"]
SIM_NAO_EVENTUAL = ["", "Sim", "Não", "Eventualmente"]

SINTOMAS = [
    "Flatulência",
    "Náuseas",
    "Azia",
    "Tonturas",
    "Cãibras",
    "Dores articulares",
    "Ansiedade",
    "Edema",
    "Constipação",
    "Diarreia",
    "Cefaleia",
    "Fadiga",
    "Compulsão alimentar",
    "Sonolência após refeições",
    "Sem sintomas relevantes",
]

HISTORIA_PATOLOGICA = [
    "Diabetes",
    "Colesterol elevado",
    "Triglicerídeos elevados",
    "Hipertensão arterial",
    "Hepatite",
    "Anemia",
    "Gastrite/Úlcera",
    "Osteoporose",
    "Disfunção tireoidiana",
    "Doença hepática",
    "Doença dermatológica",
    "Alergia",
    "Doença renal",
    "Doença cardiovascular",
    "Resistência à insulina",
    "Esteatose hepática",
    "Nenhuma informada",
]

HISTORIA_FAMILIAR_OPCOES = [
    "Diabetes",
    "Hipertensão arterial",
    "Obesidade",
    "Dislipidemia",
    "Doença cardiovascular",
    "Câncer",
    "Doença tireoidiana",
    "Doença renal",
    "Nenhuma informada",
]

ATIVIDADE_FISICA_TIPO = [
    "",
    "Sedentário",
    "Academia/Musculação",
    "Caminhada",
    "Corrida de rua",
    "Ciclismo",
    "Mountain bike",
    "Spinning",
    "Natação",
    "Hidroginástica",
    "Triathlon",
    "Futebol",
    "Futsal",
    "Vôlei",
    "Basquete",
    "Handebol",
    "Tênis",
    "Beach tennis",
    "Tênis de mesa",
    "Judô",
    "Jiu-jitsu",
    "Karatê",
    "Kempo",
    "Taekwondo",
    "Muay Thai",
    "Boxe",
    "MMA",
    "Capoeira",
    "Funcional",
    "Cross training/Crossfit",
    "Pilates",
    "Yoga",
    "Dança",
    "Balé",
    "Ginástica",
    "Calistenia",
    "Remo",
    "Surf",
    "Skate",
    "Patinação",
    "Escalada",
    "Trilha/Trekking",
    "Outro",
]

FREQUENCIA_SEMANAL = [
    "",
    "Não pratica",
    "1x por semana",
    "2x por semana",
    "3x por semana",
    "4x por semana",
    "5x por semana",
    "6x por semana",
    "Todos os dias",
]

PERIODO_DIA = [
    "",
    "Manhã",
    "Tarde",
    "Noite",
    "Madrugada",
    "Variável",
]

CONSUMO_ALCOOL = [
    "",
    "Não consome",
    "Socialmente",
    "1x por semana",
    "2-3x por semana",
    "4x ou mais por semana",
    "Diariamente",
]

TABAGISMO = [
    "",
    "Não fuma",
    "Ex-tabagista",
    "Fumante eventual",
    "Fumante diário",
]

QUALIDADE_SONO = [
    "",
    "Muito boa",
    "Boa",
    "Regular",
    "Ruim",
    "Muito ruim",
]

COMPORTAMENTO_PESO = [
    "",
    "Estável",
    "Ganho recente",
    "Perda recente",
    "Oscilante",
    "Dificuldade para ganhar peso",
    "Dificuldade para perder peso",
]

DISPOSICAO = [
    "",
    "Muito boa",
    "Boa",
    "Regular",
    "Baixa",
    "Muito baixa",
]

FUNCIONAMENTO_INTESTINAL = [
    "",
    "Diário",
    "A cada 2 dias",
    "A cada 3 dias ou mais",
    "Constipação",
    "Diarreia",
    "Alterna constipação e diarreia",
    "Uso de laxante",
]

FUNCIONAMENTO_URINARIO = [
    "",
    "Normal",
    "Aumentado",
    "Reduzido",
    "Ardência/desconforto",
    "Acorda à noite para urinar",
]

DENTICAO = ["", "Completa", "Incompleta", "Prótese", "Aparelho ortodôntico"]

MASTIGACAO = [
    "",
    "Normal",
    "Rápida",
    "Lenta",
    "Dificuldade para mastigar",
    "Dor/desconforto",
]

QUEM_COZINHA = [
    "",
    "Paciente",
    "Cônjuge/Família",
    "Empregada/cuidador",
    "Compra comida pronta",
    "Restaurante",
    "Variável",
]

APETITE = [
    "",
    "Normal",
    "Aumentado",
    "Reduzido",
    "Oscilante",
    "Compulsivo em alguns períodos",
]

INGESTAO_AGUA = [
    "",
    "Menos de 500 ml/dia",
    "500 ml a 1 L/dia",
    "1 a 1,5 L/dia",
    "1,5 a 2 L/dia",
    "2 a 3 L/dia",
    "Mais de 3 L/dia",
]

REFEICOES = [
    "Café da manhã",
    "Lanche da manhã",
    "Almoço",
    "Lanche da tarde",
    "Jantar",
    "Ceia",
    "Beliscos entre refeições",
]

GRUPOS_ALIMENTARES = [
    "Arroz/massas/pães",
    "Feijão/leguminosas",
    "Carnes/ovos",
    "Leite e derivados",
    "Frutas",
    "Verduras/legumes",
    "Doces",
    "Frituras",
    "Ultraprocessados",
    "Refrigerantes/sucos artificiais",
    "Café",
    "Água",
]

HABITOS_FIM_SEMANA = [
    "Mantém rotina semelhante",
    "Aumenta consumo de álcool",
    "Aumenta doces",
    "Aumenta frituras",
    "Aumenta delivery/restaurante",
    "Pula refeições",
    "Come em horários irregulares",
    "Reduz consumo de água",
]
