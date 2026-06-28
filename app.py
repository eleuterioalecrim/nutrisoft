"""NutriSoft - Aplicação inicial em modo terminal.

Versão 0.6:
- Cadastro de pacientes, anamnese, antropometria e exames.
- Análise comparativa de exames.
- Dashboard geral e por paciente.
- Geração de gráficos em PNG com matplotlib.
"""

from src.database import inicializar_banco_csv
from src.pacientes import (
    cadastrar_paciente, listar_pacientes, buscar_paciente_por_id,
    buscar_pacientes_por_nome, formatar_paciente_resumo
)
from src.anamnese import (
    cadastrar_anamnese, cadastrar_recordatorio, listar_anamneses_por_paciente,
    listar_recordatorios_por_paciente, gerar_resumo_nutricional_paciente,
    formatar_anamnese_resumo
)
from src.antropometria import (
    cadastrar_antropometria, listar_antropometrias_por_paciente,
    calcular_evolucao_antropometrica, preparar_series_graficos_antropometria,
    formatar_antropometria_resumo
)
from src.exames import (
    cadastrar_exame, listar_exames_por_paciente, listar_exames_por_nome,
    cadastrar_referencia_exame, listar_referencias_exames, cadastrar_alias_exame,
    listar_alias_exames, listar_analises_por_paciente, listar_exames_alterados_por_paciente,
    gerar_resumo_exames_paciente, formatar_exame_resumo, formatar_referencia_resumo,
    formatar_analise_resumo
)
from src.analises import executar_analise_exames
from src.graficos import gerar_todos_graficos_paciente
from src.dashboard import formatar_dashboard_paciente_texto, formatar_indicadores_gerais_texto


def pausar():
    input("\nPressione ENTER para continuar...")


def perguntar(campo: str) -> str:
    return input(f"{campo}: ").strip()


def menu():
    print("\n" + "=" * 88)
    print("NutriSoft v0.6 - Gestão Nutricional")
    print("=" * 88)
    print("1  - Cadastrar paciente")
    print("2  - Listar pacientes")
    print("3  - Buscar paciente por nome")
    print("4  - Buscar paciente por ID")
    print("5  - Cadastrar anamnese nutricional")
    print("6  - Cadastrar recordatório habitual")
    print("7  - Listar anamneses por paciente")
    print("8  - Ver resumo nutricional do paciente")
    print("9  - Cadastrar avaliação antropométrica")
    print("10 - Listar histórico antropométrico")
    print("11 - Ver evolução antropométrica")
    print("12 - Preparar séries para gráficos antropométricos")
    print("13 - Cadastrar exame laboratorial")
    print("14 - Listar exames por paciente")
    print("15 - Buscar exames por nome")
    print("16 - Cadastrar referência de exame")
    print("17 - Listar referências de exames")
    print("18 - Cadastrar alias de exame")
    print("19 - Listar aliases de exames")
    print("20 - Executar análise comparativa de exames")
    print("21 - Ver análise de exames por paciente")
    print("22 - Ver apenas exames alterados por paciente")
    print("23 - Ver resumo de exames do paciente")
    print("24 - Dashboard geral")
    print("25 - Dashboard do paciente")
    print("26 - Gerar gráficos do paciente")
    print("0  - Sair")
    return input("\nEscolha uma opção: ").strip()


def tela_cadastrar_paciente():
    print("\nCadastro de Paciente")
    print("-" * 88)
    dados = {
        "nome": perguntar("Nome"),
        "data_nascimento": perguntar("Data de nascimento (AAAA-MM-DD ou DD/MM/AAAA)"),
        "sexo": perguntar("Sexo (M/F/Outro/Não informado)") or "Não informado",
        "telefone": perguntar("Telefone"),
        "email": perguntar("E-mail"),
        "profissao": perguntar("Profissão/Estudo"),
        "horario_trabalho": perguntar("Horário de trabalho/estudo"),
        "observacoes": perguntar("Observações"),
    }
    resultado = cadastrar_paciente(dados)
    if resultado["sucesso"]:
        print("\nPaciente cadastrado com sucesso!")
        print(formatar_paciente_resumo(resultado["paciente"]))
    else:
        print("\nNão foi possível cadastrar o paciente:")
        for erro in resultado["erros"]:
            print(f"- {erro}")
    pausar()


def tela_listar_pacientes():
    print("\nPacientes cadastrados")
    print("-" * 88)
    pacientes = listar_pacientes()
    if not pacientes:
        print("Nenhum paciente cadastrado.")
    else:
        for paciente in pacientes:
            print(formatar_paciente_resumo(paciente))
    pausar()


def tela_buscar_por_nome():
    termo = perguntar("\nDigite parte do nome do paciente")
    encontrados = buscar_pacientes_por_nome(termo)
    print("\nResultado da busca")
    print("-" * 88)
    if not encontrados:
        print("Nenhum paciente encontrado.")
    else:
        for paciente in encontrados:
            print(formatar_paciente_resumo(paciente))
    pausar()


def tela_buscar_por_id():
    paciente_id = perguntar("\nDigite o ID do paciente")
    paciente = buscar_paciente_por_id(paciente_id)
    print("\nResultado da busca")
    print("-" * 88)
    if not paciente:
        print("Nenhum paciente encontrado.")
    else:
        print(formatar_paciente_resumo(paciente))
        print(f"Data cadastro: {paciente.get('data_cadastro', '')}")
        print(f"Data nascimento: {paciente.get('data_nascimento', '')}")
        print(f"E-mail: {paciente.get('email', '')}")
        print(f"Profissão/Estudo: {paciente.get('profissao', '')}")
        print(f"Horário: {paciente.get('horario_trabalho', '')}")
        print(f"Observações: {paciente.get('observacoes', '')}")
    pausar()


def tela_cadastrar_anamnese():
    print("\nCadastro de Anamnese Nutricional")
    print("-" * 88)
    paciente_id = perguntar("ID do paciente")
    paciente = buscar_paciente_por_id(paciente_id)
    if not paciente:
        print("Paciente não encontrado. Cadastre o paciente antes da anamnese.")
        pausar()
        return

    print(f"Paciente: {paciente.get('nome', '')}")
    dados = {
        "paciente_id": paciente_id,
        "data_anamnese": perguntar("Data da anamnese (AAAA-MM-DD) [vazio = hoje]"),
        "queixa_principal": perguntar("Queixa principal"),
        "historia_doenca_atual": perguntar("História da doença atual"),
        "sintomas": perguntar("Sintomas observados/relatados"),
        "historia_patologica_pregressa": perguntar("História patológica pregressa"),
        "historia_familiar": perguntar("História familiar"),
        "numero_filhos_idades": perguntar("Nº de filhos e idades"),
        "amamentou": perguntar("Amamentou? (Sim/Não)"),
        "atividade_fisica": perguntar("Atividade física (tipo/frequência)"),
        "horario_atividade_fisica": perguntar("Horário da atividade física"),
        "consumo_alcool": perguntar("Consumo de álcool (tipo/frequência)"),
        "tabagismo": perguntar("Tabagismo"),
        "qualidade_sono": perguntar("Qualidade do sono"),
        "hora_acordar": perguntar("Hora de acordar"),
        "hora_dormir": perguntar("Hora de dormir"),
        "comportamento_peso": perguntar("Comportamento do peso"),
        "disposicao_fisica": perguntar("Disposição física/energia"),
        "funcionamento_intestinal": perguntar("Funcionamento intestinal"),
        "funcionamento_urinario": perguntar("Funcionamento urinário"),
        "internacoes_cirurgias": perguntar("Internações/Cirurgias"),
        "medicamentos_suplementos": perguntar("Medicamentos/Suplementos em uso"),
        "intolerancia_alergia_alimentar": perguntar("Intolerância/Alergia alimentar"),
        "denticao": perguntar("Dentição (Completa/Incompleta)"),
        "mastigacao": perguntar("Mastigação"),
        "quem_cozinha": perguntar("Quem cozinha"),
        "apetite": perguntar("Apetite"),
        "horario_mais_fome": perguntar("Horário de mais fome"),
        "ingestao_agua_dia": perguntar("Ingestão de água/dia"),
        "tratamento_nutricional_anterior": perguntar("Tratamento nutricional anterior? (Sim/Não)"),
        "qual_tratamento": perguntar("Qual tratamento"),
        "alimentos_preferidos": perguntar("Alimentos preferidos"),
        "habito_beliscar": perguntar("Hábito de beliscar? (Sim/Não)"),
        "alimentos_que_nao_gosta": perguntar("Alimentos que não gosta"),
        "habitos_fim_de_semana": perguntar("Hábitos de fim de semana"),
    }
    resultado = cadastrar_anamnese(dados)
    if resultado["sucesso"]:
        print("\nAnamnese cadastrada com sucesso!")
        print(formatar_anamnese_resumo(resultado["anamnese"]))
    else:
        print("\nNão foi possível cadastrar a anamnese:")
        for erro in resultado["erros"]:
            print(f"- {erro}")
    pausar()


def tela_cadastrar_recordatorio():
    print("\nCadastro de Recordatório Habitual")
    print("-" * 88)
    paciente_id = perguntar("ID do paciente")
    paciente = buscar_paciente_por_id(paciente_id)
    if not paciente:
        print("Paciente não encontrado. Cadastre o paciente antes do recordatório.")
        pausar()
        return

    print(f"Paciente: {paciente.get('nome', '')}")
    dados = {
        "paciente_id": paciente_id,
        "data_registro": perguntar("Data do registro (AAAA-MM-DD) [vazio = hoje]"),
        "desjejum": perguntar("Desjejum"),
        "lanche_manha": perguntar("Lanche da manhã"),
        "almoco": perguntar("Almoço"),
        "lanche_tarde": perguntar("Lanche da tarde"),
        "jantar": perguntar("Jantar"),
        "ceia": perguntar("Ceia"),
        "observacoes": perguntar("Observações do recordatório"),
    }
    resultado = cadastrar_recordatorio(dados)
    if resultado["sucesso"]:
        rec = resultado["recordatorio"]
        print("\nRecordatório cadastrado com sucesso!")
        print(f"Recordatório {rec.get('recordatorio_id')} | Paciente {rec.get('paciente_id')} | Data {rec.get('data_registro')}")
    else:
        print("\nNão foi possível cadastrar o recordatório:")
        for erro in resultado["erros"]:
            print(f"- {erro}")
    pausar()


def tela_listar_anamneses():
    paciente_id = perguntar("\nDigite o ID do paciente")
    paciente = buscar_paciente_por_id(paciente_id)
    if not paciente:
        print("Paciente não encontrado.")
        pausar()
        return

    print(f"\nAnamneses de {paciente.get('nome', '')}")
    print("-" * 88)
    anamneses = listar_anamneses_por_paciente(paciente_id)
    recordatorios = listar_recordatorios_por_paciente(paciente_id)

    if not anamneses:
        print("Nenhuma anamnese cadastrada.")
    else:
        for item in anamneses:
            print(formatar_anamnese_resumo(item))

    print("\nRecordatórios habituais")
    print("-" * 88)
    if not recordatorios:
        print("Nenhum recordatório cadastrado.")
    else:
        for rec in recordatorios:
            print(f"Recordatório {rec.get('recordatorio_id', '')} | Data {rec.get('data_registro', '')} | Almoço: {rec.get('almoco', '')[:50]}")
    pausar()


def tela_resumo_nutricional():
    paciente_id = perguntar("\nDigite o ID do paciente")
    paciente = buscar_paciente_por_id(paciente_id)
    if not paciente:
        print("Paciente não encontrado.")
        pausar()
        return

    resumo = gerar_resumo_nutricional_paciente(paciente_id)
    print(f"\nResumo nutricional - {paciente.get('nome', '')}")
    print("-" * 88)
    if not resumo.get("possui_anamnese"):
        print(resumo.get("resumo"))
    else:
        print(f"Data da anamnese: {resumo.get('data_anamnese', '')}")
        print(f"Queixa principal: {resumo.get('queixa_principal', '')}")
        print("\nPontos de atenção:")
        for ponto in resumo.get("pontos_atencao", []):
            print(f"- {ponto}")
    pausar()


def tela_cadastrar_antropometria():
    print("\nCadastro de Avaliação Antropométrica")
    print("-" * 88)
    paciente_id = perguntar("ID do paciente")
    paciente = buscar_paciente_por_id(paciente_id)
    if not paciente:
        print("Paciente não encontrado. Cadastre o paciente antes da avaliação.")
        pausar()
        return

    print(f"Paciente: {paciente.get('nome', '')}")
    dados = {
        "paciente_id": paciente_id,
        "data_avaliacao": perguntar("Data da avaliação (AAAA-MM-DD) [vazio = hoje]"),
        "peso": perguntar("Peso em kg"),
        "altura": perguntar("Altura em metros ou cm (ex.: 1,70 ou 170)"),
        "circunferencia_cintura": perguntar("Circunferência da cintura em cm"),
        "observacoes": perguntar("Observações"),
    }
    resultado = cadastrar_antropometria(dados)
    if resultado["sucesso"]:
        print("\nAvaliação antropométrica cadastrada com sucesso!")
        print(formatar_antropometria_resumo(resultado["antropometria"]))
        print(f"Risco cintura: {resultado['antropometria'].get('risco_cintura', '')}")
    else:
        print("\nNão foi possível cadastrar a avaliação:")
        for erro in resultado["erros"]:
            print(f"- {erro}")
    pausar()


def tela_listar_antropometria():
    paciente_id = perguntar("\nDigite o ID do paciente")
    paciente = buscar_paciente_por_id(paciente_id)
    if not paciente:
        print("Paciente não encontrado.")
        pausar()
        return

    print(f"\nHistórico antropométrico - {paciente.get('nome', '')}")
    print("-" * 88)
    registros = listar_antropometrias_por_paciente(paciente_id)
    if not registros:
        print("Nenhuma avaliação antropométrica cadastrada.")
    else:
        for registro in registros:
            print(formatar_antropometria_resumo(registro))
            if registro.get("risco_cintura"):
                print(f"  Risco cintura: {registro.get('risco_cintura')}")
    pausar()


def tela_evolucao_antropometrica():
    paciente_id = perguntar("\nDigite o ID do paciente")
    paciente = buscar_paciente_por_id(paciente_id)
    if not paciente:
        print("Paciente não encontrado.")
        pausar()
        return

    evolucao = calcular_evolucao_antropometrica(paciente_id)
    print(f"\nEvolução antropométrica - {paciente.get('nome', '')}")
    print("-" * 88)
    if not evolucao.get("possui_dados"):
        print(evolucao.get("resumo"))
    else:
        for chave in ["primeira_data", "ultima_data", "peso_inicial", "peso_atual", "delta_peso", "imc_inicial", "imc_atual", "delta_imc", "cintura_inicial", "cintura_atual", "delta_cintura", "classificacao_atual", "risco_cintura_atual"]:
            print(f"{chave}: {evolucao.get(chave, '')}")
    pausar()


def tela_series_graficos_antropometria():
    paciente_id = perguntar("\nDigite o ID do paciente")
    paciente = buscar_paciente_por_id(paciente_id)
    if not paciente:
        print("Paciente não encontrado.")
        pausar()
        return

    series = preparar_series_graficos_antropometria(paciente_id)
    print(f"\nSéries para gráficos - {paciente.get('nome', '')}")
    print("-" * 88)
    print(f"Datas: {series.get('datas')}")
    print(f"Pesos: {series.get('pesos')}")
    print(f"IMCs: {series.get('imcs')}")
    print(f"Cinturas: {series.get('cinturas')}")
    pausar()


def tela_cadastrar_exame():
    print("\nCadastro de Exame Laboratorial")
    print("-" * 88)
    paciente_id = perguntar("ID do paciente")
    paciente = buscar_paciente_por_id(paciente_id)
    if not paciente:
        print("Paciente não encontrado. Cadastre o paciente antes do exame.")
        pausar()
        return

    print(f"Paciente: {paciente.get('nome', '')}")
    dados = {
        "paciente_id": paciente_id,
        "data_exame": perguntar("Data do exame (AAAA-MM-DD) [vazio = hoje]"),
        "nome_exame": perguntar("Nome do exame"),
        "resultado": perguntar("Resultado numérico"),
        "unidade": perguntar("Unidade (ex.: mg/dL, ng/mL, g/dL)"),
        "observacoes": perguntar("Observações"),
    }
    resultado = cadastrar_exame(dados)
    if resultado["sucesso"]:
        print("\nExame cadastrado com sucesso!")
        print(formatar_exame_resumo(resultado["exame"]))
        print("Análise comparativa atualizada em data/analise_exames.csv")
    else:
        print("\nNão foi possível cadastrar o exame:")
        for erro in resultado["erros"]:
            print(f"- {erro}")
    pausar()


def tela_listar_exames_paciente():
    paciente_id = perguntar("\nDigite o ID do paciente")
    paciente = buscar_paciente_por_id(paciente_id)
    if not paciente:
        print("Paciente não encontrado.")
        pausar()
        return

    exames = listar_exames_por_paciente(paciente_id)
    print(f"\nExames laboratoriais - {paciente.get('nome', '')}")
    print("-" * 88)
    if not exames:
        print("Nenhum exame cadastrado.")
    else:
        for exame in exames:
            print(formatar_exame_resumo(exame))
    pausar()


def tela_buscar_exames_nome():
    nome = perguntar("\nDigite parte do nome do exame")
    exames = listar_exames_por_nome(nome)
    print("\nResultado da busca de exames")
    print("-" * 88)
    if not exames:
        print("Nenhum exame encontrado.")
    else:
        for exame in exames:
            paciente = buscar_paciente_por_id(exame.get("paciente_id", ""))
            nome_paciente = paciente.get("nome", "") if paciente else "Paciente não localizado"
            print(f"{formatar_exame_resumo(exame)} | Paciente: {nome_paciente}")
    pausar()


def tela_cadastrar_referencia():
    print("\nCadastro de Referência de Exame")
    print("-" * 88)
    dados = {
        "nome_exame": perguntar("Nome padronizado do exame"),
        "sexo": perguntar("Sexo de aplicação (Todos/M/F/Outro/Não informado)") or "Todos",
        "idade_min": perguntar("Idade mínima"),
        "idade_max": perguntar("Idade máxima"),
        "valor_min": perguntar("Valor mínimo de referência"),
        "valor_max": perguntar("Valor máximo de referência"),
        "unidade": perguntar("Unidade"),
        "fonte_referencia": perguntar("Fonte da referência"),
        "observacoes": perguntar("Observações"),
    }
    resultado = cadastrar_referencia_exame(dados)
    if resultado["sucesso"]:
        print("\nReferência cadastrada com sucesso!")
        print(formatar_referencia_resumo(resultado["referencia"]))
    else:
        print("\nNão foi possível cadastrar a referência:")
        for erro in resultado["erros"]:
            print(f"- {erro}")
    pausar()


def tela_listar_referencias():
    referencias = listar_referencias_exames()
    print("\nReferências cadastradas")
    print("-" * 88)
    if not referencias:
        print("Nenhuma referência cadastrada.")
    else:
        for ref in referencias:
            print(formatar_referencia_resumo(ref))
    pausar()


def tela_cadastrar_alias():
    print("\nCadastro de Alias de Exame")
    print("-" * 88)
    alias = perguntar("Alias/forma alternativa")
    nome_padronizado = perguntar("Nome padronizado")
    resultado = cadastrar_alias_exame(alias, nome_padronizado)
    if resultado["sucesso"]:
        print("\nAlias cadastrado com sucesso!")
        print(f"{resultado['alias'].get('alias')} -> {resultado['alias'].get('nome_padronizado')}")
    else:
        print("\nNão foi possível cadastrar o alias:")
        for erro in resultado["erros"]:
            print(f"- {erro}")
    pausar()


def tela_listar_alias():
    aliases = listar_alias_exames()
    print("\nAliases cadastrados")
    print("-" * 88)
    if not aliases:
        print("Nenhum alias cadastrado.")
    else:
        for item in aliases:
            print(f"{item.get('alias', '')} -> {item.get('nome_padronizado', '')}")
    pausar()


def tela_executar_analise():
    total = executar_analise_exames()
    print(f"\nAnálise concluída. Registros analisados: {total}")
    print("Resultado salvo em data/analise_exames.csv")
    pausar()


def tela_analise_paciente():
    paciente_id = perguntar("\nDigite o ID do paciente")
    paciente = buscar_paciente_por_id(paciente_id)
    if not paciente:
        print("Paciente não encontrado.")
        pausar()
        return

    executar_analise_exames()
    analises = listar_analises_por_paciente(paciente_id)
    print(f"\nAnálise de exames - {paciente.get('nome', '')}")
    print("-" * 88)
    if not analises:
        print("Nenhuma análise encontrada. Cadastre exames para este paciente.")
    else:
        for analise in analises:
            print(formatar_analise_resumo(analise))
    pausar()


def tela_exames_alterados():
    paciente_id = perguntar("\nDigite o ID do paciente")
    paciente = buscar_paciente_por_id(paciente_id)
    if not paciente:
        print("Paciente não encontrado.")
        pausar()
        return

    executar_analise_exames()
    alterados = listar_exames_alterados_por_paciente(paciente_id)
    print(f"\nExames alterados ou pendentes - {paciente.get('nome', '')}")
    print("-" * 88)
    if not alterados:
        print("Nenhum exame alterado ou pendente encontrado.")
    else:
        for analise in alterados:
            print(formatar_analise_resumo(analise))
    pausar()


def tela_resumo_exames():
    paciente_id = perguntar("\nDigite o ID do paciente")
    paciente = buscar_paciente_por_id(paciente_id)
    if not paciente:
        print("Paciente não encontrado.")
        pausar()
        return

    resumo = gerar_resumo_exames_paciente(paciente_id)
    print(f"\nResumo de exames - {paciente.get('nome', '')}")
    print("-" * 88)
    print(resumo.get("resumo"))
    if resumo.get("possui_exames"):
        print("\nPrincipais alertas:")
        alertas = resumo.get("principais_alertas", [])
        if not alertas:
            print("- Nenhum alerta de exame acima ou abaixo da referência cadastrada.")
        else:
            for alerta in alertas:
                print(f"- {alerta}")
    pausar()


def tela_dashboard_geral():
    print()
    print(formatar_indicadores_gerais_texto())
    pausar()


def tela_dashboard_paciente():
    paciente_id = perguntar("\nDigite o ID do paciente")
    print()
    print(formatar_dashboard_paciente_texto(paciente_id))
    pausar()


def tela_gerar_graficos_paciente():
    paciente_id = perguntar("\nDigite o ID do paciente")
    paciente = buscar_paciente_por_id(paciente_id)
    if not paciente:
        print("Paciente não encontrado.")
        pausar()
        return

    print(f"\nGerando gráficos para {paciente.get('nome', '')}...")
    resultados = gerar_todos_graficos_paciente(paciente_id)
    print("-" * 88)
    for nome, info in resultados.items():
        if info["sucesso"]:
            print(f"{nome}: gerado em {info['arquivo']}")
        else:
            print(f"{nome}: não gerado - {info['erro']}")
    pausar()


def main():
    inicializar_banco_csv()
    while True:
        opcao = menu()
        if opcao == "1":
            tela_cadastrar_paciente()
        elif opcao == "2":
            tela_listar_pacientes()
        elif opcao == "3":
            tela_buscar_por_nome()
        elif opcao == "4":
            tela_buscar_por_id()
        elif opcao == "5":
            tela_cadastrar_anamnese()
        elif opcao == "6":
            tela_cadastrar_recordatorio()
        elif opcao == "7":
            tela_listar_anamneses()
        elif opcao == "8":
            tela_resumo_nutricional()
        elif opcao == "9":
            tela_cadastrar_antropometria()
        elif opcao == "10":
            tela_listar_antropometria()
        elif opcao == "11":
            tela_evolucao_antropometrica()
        elif opcao == "12":
            tela_series_graficos_antropometria()
        elif opcao == "13":
            tela_cadastrar_exame()
        elif opcao == "14":
            tela_listar_exames_paciente()
        elif opcao == "15":
            tela_buscar_exames_nome()
        elif opcao == "16":
            tela_cadastrar_referencia()
        elif opcao == "17":
            tela_listar_referencias()
        elif opcao == "18":
            tela_cadastrar_alias()
        elif opcao == "19":
            tela_listar_alias()
        elif opcao == "20":
            tela_executar_analise()
        elif opcao == "21":
            tela_analise_paciente()
        elif opcao == "22":
            tela_exames_alterados()
        elif opcao == "23":
            tela_resumo_exames()
        elif opcao == "24":
            tela_dashboard_geral()
        elif opcao == "25":
            tela_dashboard_paciente()
        elif opcao == "26":
            tela_gerar_graficos_paciente()
        elif opcao == "0":
            print("\nEncerrando NutriSoft.")
            break
        else:
            print("\nOpção inválida.")
            pausar()


if __name__ == "__main__":
    main()
