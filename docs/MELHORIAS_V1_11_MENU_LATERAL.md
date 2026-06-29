# NutriSoft v1.11 - Menu lateral profissional

## Problema

A navegação em lista suspensa não era adequada para uso contínuo no atendimento.

## Solução

A navegação foi alterada para um menu lateral com cards/botões agrupados:

- Operação;
- Análise;
- Gestão.

Cada item possui:

- ícone;
- nome da página;
- descrição curta;
- destaque visual quando ativo.

## Próxima etapa do fluxo

Quando o usuário está em uma etapa do fluxo de atendimento, o menu lateral mostra a próxima etapa.

Fluxo:

```text
Pacientes → Anamnese → Antropometria → Exames → Dashboard
```

## Arquivos alterados

```text
src/web/navigation.py
src/web/styles.py
```
