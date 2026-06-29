# NutriSoft v1.5 - Edição guiada e catálogo laboratorial ampliado

## 1. Edição guiada

A view `Edição` foi reformulada para respeitar o mesmo tipo de campo usado no cadastro:

- `selectbox` para campos de escolha única;
- `multiselect` para campos de múltipla escolha;
- campos livres apenas quando o dado original também é livre;
- opção de complemento em campos de múltipla seleção;
- manutenção do histórico de alterações.

## 2. Catálogo laboratorial ampliado

O arquivo `src/catalogo_exames.py` foi ampliado com exames dos seguintes painéis:

- glicêmico/metabólico;
- lipídico/cardiovascular;
- vitaminas/minerais/ferro;
- hemograma;
- hepático;
- renal/eletrólitos;
- tireoidiano;
- inflamatório/muscular;
- hormonal/nutricional complementar;
- urina/metabólico complementar.

## 3. Observação sobre referências

Não existe uma lista universal única de “todos os valores de referência possíveis”.
Cada laboratório pode variar por método, equipamento, unidade, idade, sexo,
gestação, altitude, medicamentos e contexto clínico.

Por isso, o NutriSoft carrega uma base inicial ampla e editável.
O profissional deve revisar e ajustar conforme o laudo utilizado.
