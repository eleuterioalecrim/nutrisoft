# NutriSoft v1.7 - Fluxo assistido e bloqueio de exames duplicados

## 1. Bloqueio visual de exame já cadastrado na mesma data

No cadastro de exames:

- o usuário seleciona/informa a data do exame;
- o sistema consulta os exames já cadastrados para o paciente naquela data;
- exames já cadastrados deixam de aparecer na lista;
- caso o usuário tente repetir manualmente, o sistema bloqueia o salvamento.

Isso evita duplicidade e reduz confusão durante o atendimento.

## 2. Navegação assistida

Ao concluir uma sessão, o sistema avança automaticamente para a próxima etapa:

```text
Pacientes → Anamnese → Antropometria → Exames → Dashboard
```

## 3. Exceção para exames

A sessão de exames não avança automaticamente após cada exame, porque normalmente
o profissional cadastra vários exames na mesma data.

Ao terminar todos os exames, o usuário clica em:

```text
Concluir sessão de exames e ir para Dashboard
```

## 4. Arquivos principais

```text
src/exames_fluxo.py
src/web/navigation.py
src/web/page_exames.py
src/web/page_pacientes.py
src/web/page_anamnese.py
src/web/page_antropometria.py
```
