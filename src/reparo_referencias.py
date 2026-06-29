from src.referencias_padrao import carregar_catalogo_padrao
from src.catalogo_exames import cobertura_catalogo
from src.analises import executar_analise_exames
from src.database import ler_csv


def reparar_referencias_e_analises() -> dict:
    """
    Força a carga das referências/aliases e reprocessa todas as análises.
    Deve ser usado após atualização de versão ou quando exames aparecem sem referência.
    """
    resultado_catalogo = carregar_catalogo_padrao()
    total_analises = executar_analise_exames()

    analises = ler_csv("analise_exames")
    sem_referencia = [
        a for a in analises
        if str(a.get("status", "")).strip() == "Sem referência"
    ]

    exames_sem_referencia = sorted({
        a.get("nome_exame_padronizado", "") or a.get("nome_exame_original", "")
        for a in sem_referencia
        if a.get("nome_exame_padronizado", "") or a.get("nome_exame_original", "")
    })

    return {
        "catalogo": resultado_catalogo,
        "cobertura": cobertura_catalogo(),
        "total_analises": total_analises,
        "total_sem_referencia": len(sem_referencia),
        "exames_sem_referencia": exames_sem_referencia,
    }
