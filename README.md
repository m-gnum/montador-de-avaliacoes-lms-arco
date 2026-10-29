# Montador de avaliações — SAS (Arco Educação)

Automação em Python + Selenium que monta, de forma automática, avaliações do tipo **simulado de vestibulares regionais de São Paulo** para escolas da marca **SAS**, da Arco Educação.

O script abre o Google Chrome, acessa a plataforma e executa os mesmos cliques que uma pessoa da operação faria: filtra o banco de questões, seleciona as questões, configura a aplicação e baixa os materiais. O ganho é duplo:

- **Rapidez:** uma prova com dezenas de questões é montada sem trabalho manual repetitivo.
- **Liberdade para a operação:** o navegador roda sozinho, e a pessoa pode fazer outras atividades enquanto a montagem acontece.

> **Aviso:** o projeto automatiza plataformas internas da SAS/Arco, que exigem credenciais próprias. Este repositório é um **portfólio**: o código está aqui para leitura e referência, e não é executável sem acesso a essas plataformas. Nenhum dado real (credenciais, banco de questões ou histórico de aplicações) faz parte do repositório.

## Conteúdo

| Arquivo | Para que serve |
|---|---|
| `montador_avaliacoes_lms.py` | Monta a prova **dentro do LMS da escola** (visão do usuário da escola): cria a prova, escolhe as questões por filtros, define turma, data e horário da aplicação impressa e baixa os materiais (prova e cartões). |
| `montador_simulados_versao_backoffice (v2 - apenas montar questões).py` | Monta as questões de uma prova já criada no **backoffice** (bastidores do LMS, usado pelo time do SAS). Na v2, consulta a planilha de apoio para evitar repetir questões e manter questões agrupadas juntas. |
| `classificar_questoes_por_similaridade_de_cossenos.py` | Script de preparação, usado uma única vez: identifica questões de Linguagens com o mesmo texto-base (similaridade de cosseno sobre TF-IDF de bigramas) e as agrupa. O resultado alimenta a aba `questoes_agrupadas`. |
| `planilha_de_apoio_da_operacao.xlsx` | **Template** da planilha de apoio, com cabeçalhos e linhas fictícias de exemplo (veja abaixo). |

## Como funciona

### Montador do LMS (`montador_avaliacoes_lms.py`)

1. Faz login e clica em *Criar prova*, informando o nome.
2. Para cada linha da lista de filtros, aplica **nível, disciplina, banca e assunto** no banco de questões e seleciona a quantidade pedida de questões, sorteadas entre as encontradas.
3. Adiciona as questões, escolhe *Aplicação Impressa*, a turma, a data e os horários de início e fim.
4. Conclui a prova e baixa os materiais (prova e cartões-resposta).

### Montador do backoffice (v2)

1. Carrega a planilha de apoio e faz login no backoffice, selecionando a marca SAS.
2. Abre diretamente a composição do simulado pelo ID.
3. Para cada linha de filtros (**nível, tipo, disciplina, assunto, banca**), busca as questões e escolhe as que passam nas regras da planilha:
   - **descarta** questões já usadas na 1ª aplicação (`questoes_1a_aplicacao`);
   - **mantém juntas** as questões que compartilham o mesmo texto-base (`questoes_agrupadas`), valendo para Português, Inglês e Espanhol — por isso, nessas disciplinas a quantidade final pode ser maior que a pedida;
   - **só aceita** questões que existem no catálogo (`todas_as_questoes`).
4. Salva o rascunho (*Continuar depois*) e imprime o ID e o nome do simulado para conferência.

## Planilha de apoio

O arquivo versionado é apenas um **template**. Para uso real, substitua as linhas de exemplo pelos dados da operação, mantendo os nomes das abas e das colunas:

| Aba | Colunas | Conteúdo |
|---|---|---|
| `todas_as_questoes` | `id`, `reference`, `tipo_questao`, `disc`, `dim`, `ass`, `banca`, `ano` | Catálogo de questões elegíveis. |
| `questoes_agrupadas` | `grupo`, `text_purified`, `reference`, `banca`, `tamanho_grupo`, `planilha_origem`, `label_reference` | Questões que compartilham texto-base (saída do script de similaridade). |
| `questoes_1a_aplicacao` | `reference`, `question_id`, `activity_id`, `activity_name` | Questões já aplicadas, que não devem se repetir. |

Se a planilha não for encontrada, o script avisa e segue sem as verificações.

## Configuração

### Credenciais e endereços

Credenciais e endereços das plataformas **não ficam no código**. Defina-os como variáveis de ambiente antes de executar:

```bash
export MONTADOR_LOGIN="seu_login"
export MONTADOR_SENHA="sua_senha"
export MONTADOR_URL_LMS="https://lms.exemplo.com"                # script do LMS
export MONTADOR_URL_BACKOFFICE="https://backoffice.exemplo.com"  # script do backoffice
```

No Windows (PowerShell):

```powershell
$env:MONTADOR_LOGIN = "seu_login"
$env:MONTADOR_SENHA = "sua_senha"
$env:MONTADOR_URL_LMS = "https://lms.exemplo.com"
$env:MONTADOR_URL_BACKOFFICE = "https://backoffice.exemplo.com"
```

### Parâmetros da prova

Os parâmetros ficam no fim de cada script.

**LMS** — `nome_da_prova`, `nome_da_turma`, `data_aplicacao` (`ddmmaaaa`), `hora_inicio` / `hora_fim` (`hhmm`) e `texto_input`, com uma linha por filtro:

```
id,nível,disciplina,assunto,banca,quantidade
1,Ensino Médio,Português,Interpretação textual,BANCA EXEMPLO,2
```

**Backoffice** — `id_simulado`, `caderno_1` e `filtros_caderno_1`, com uma linha por filtro:

```
id,nível,tipo,disciplina,assunto,banca,quantidade
1,Ensino Médio,Múltipla Escolha,Matemática,Números Inteiros,BANCA EXEMPLO,1
```

Os valores de disciplina, assunto e banca devem ser escritos exatamente como aparecem na plataforma, e não podem conter vírgula nem ponto e vírgula.

## Execução

Requisitos: Python 3 e Google Chrome. O driver do Chrome é baixado automaticamente pelo Selenium (versão 4.6 ou superior).

```bash
pip install -r requirements.txt
python montador_avaliacoes_lms.py
# ou
python "montador_simulados_versao_backoffice (v2 - apenas montar questões).py"
```

O script do backoffice precisa ser executado a partir da pasta do projeto, pois procura a planilha de apoio no diretório atual.

## Limitações

- A automação depende da estrutura das páginas (seletores XPath). Mudanças na interface das plataformas podem quebrar o script e exigir ajustes.
- Em cada filtro, as questões são sorteadas entre as primeiras listadas na tela (até 10), e não entre todo o resultado da busca.
- Os scripts não têm testes automatizados: a validação é feita observando a execução e conferindo a prova montada.

## Tecnologias

Python · Selenium · pandas · scikit-learn (apenas no script de similaridade)
