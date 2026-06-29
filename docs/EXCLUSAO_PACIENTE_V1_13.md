# NutriSoft v1.13 - Exclusão de paciente dentro da sessão Pacientes

## Mudança de UX

A exclusão de paciente deixou de ser uma tela separada no menu Gestão.

Agora fica dentro de:

```text
Pacientes → Ações
```

## Fluxo

1. Acessar `Pacientes`.
2. Abrir a aba `Ações`.
3. Selecionar o paciente.
4. Clicar em `Excluir paciente e todos os dados vinculados`.
5. Confirmar no pop-up/modal.
6. Digitar a confirmação textual:

```text
EXCLUIR <paciente_id>
```

## Segurança

Antes da exclusão, o sistema cria backup automático em:

```text
backups/pacientes_excluidos/
```

## Dados excluídos

- cadastro do paciente;
- anamnese;
- recordatório habitual;
- antropometria;
- exames;
- análises de exames;
- evolução/conduta;
- arquivos gerados em `reports/` vinculados ao ID do paciente.

## Observação técnica

O sistema usa `st.dialog` quando disponível.
Em versões antigas do Streamlit, usa fallback em tela.
