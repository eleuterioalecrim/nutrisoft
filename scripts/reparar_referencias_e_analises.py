import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.database import inicializar_banco_csv
from src.reparo_referencias import reparar_referencias_e_analises


def main():
    inicializar_banco_csv()
    resultado = reparar_referencias_e_analises()

    print("=== NutriSoft - Reparo de Referências e Análises ===")
    print(f"Referências criadas: {resultado['catalogo']['referencias']['criadas']}")
    print(f"Referências já existentes: {resultado['catalogo']['referencias']['ignoradas']}")
    print(f"Aliases criados: {resultado['catalogo']['aliases']['criados']}")
    print(f"Aliases já existentes: {resultado['catalogo']['aliases']['ignorados']}")
    print(f"Tipos de exames no catálogo: {resultado['cobertura']['total_exames']}")
    print(f"Referências cadastráveis: {resultado['cobertura']['total_referencias']}")
    print(f"Cobertura do catálogo: {resultado['cobertura']['cobertura_percentual']}%")
    print(f"Análises reprocessadas: {resultado['total_analises']}")
    print(f"Análises ainda sem referência: {resultado['total_sem_referencia']}")

    if resultado["exames_sem_referencia"]:
        print("")
        print("Exames ainda sem referência após reparo:")
        for exame in resultado["exames_sem_referencia"]:
            print(f"- {exame}")
        print("")
        print("Atenção: estes nomes provavelmente não correspondem ao catálogo/aliases ou foram cadastrados como 'Outro'.")
    else:
        print("OK: nenhum exame ficou sem referência.")


if __name__ == "__main__":
    main()
