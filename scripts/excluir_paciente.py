import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.database import inicializar_banco_csv
from src.exclusao_paciente import contar_dados_paciente, excluir_dados_paciente


def main():
    inicializar_banco_csv()

    if len(sys.argv) < 2:
        print("Uso:")
        print("python3 scripts/excluir_paciente.py <PACIENTE_ID>")
        sys.exit(1)

    paciente_id = sys.argv[1]
    info = contar_dados_paciente(paciente_id)
    paciente = info.get("paciente")

    if not paciente:
        print("Paciente não encontrado.")
        sys.exit(1)

    print("Paciente:")
    print(f"ID: {paciente.get('paciente_id')}")
    print(f"Nome: {paciente.get('nome')}")
    print("")
    print("Registros encontrados:")
    for base, qtd in info["contagens"].items():
        print(f"- {base}: {qtd}")
    print(f"Arquivos gerados: {info['total_arquivos']}")
    print("")
    esperado = f"EXCLUIR {paciente_id}"
    print(f"Para confirmar, digite exatamente: {esperado}")
    confirmacao = input("> ").strip()

    resultado = excluir_dados_paciente(
        paciente_id=paciente_id,
        confirmar_texto=confirmacao,
        excluir_arquivos_gerados=True,
        criar_backup=True,
    )

    if not resultado["sucesso"]:
        print("Erro:", resultado["erro"])
        sys.exit(1)

    print("Exclusão concluída.")
    if resultado.get("backup"):
        print("Backup:", resultado["backup"]["backup_zip"])

    print("Registros removidos:")
    for base, qtd in resultado["removidos"].items():
        print(f"- {base}: {qtd}")

    print(f"Arquivos removidos: {len(resultado['arquivos_removidos'])}")


if __name__ == "__main__":
    main()
