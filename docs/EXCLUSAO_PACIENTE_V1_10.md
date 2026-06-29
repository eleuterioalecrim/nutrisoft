# NutriSoft v1.10 - Exclusão segura de paciente

## Nova funcionalidade

Caminho:

```text
Gestão → Exclusão de paciente
```

A tela permite excluir todos os dados vinculados a um paciente.

## Bases afetadas

- pacientes;
- anamnese;
- recordatorio_habitual;
- antropometria;
- exames;
- analise_exames;
- evolucao_conduta.

## Bases preservadas

- referencias_exames;
- alias_exames;
- historico_edicoes.

As referências e aliases são bases globais do sistema e não pertencem a um paciente específico.

## Arquivos removidos

Também podem ser removidos arquivos gerados em:

```text
reports/
```

desde que o nome do arquivo contenha o ID do paciente.

## Segurança

Antes da exclusão, o sistema pode gerar backup em:

```text
backups/pacientes_excluidos/
```

A exclusão exige confirmação digitada:

```text
EXCLUIR <paciente_id>
```

Exemplo:

```text
EXCLUIR 0002
```

## Via terminal

```bash
python3 scripts/excluir_paciente.py 0002
```
