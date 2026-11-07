# Relatório de Consolidação, Agrupamento e Limpeza de Dados — Olist E-Commerce

Este documento descreve todo o processo de engenharia e preparação de dados realizado para unificar as tabelas relacionais do **Brazilian E-Commerce Public Dataset by Olist** (`olistbr/brazilian-ecommerce`) em uma única base analítica consolidada ao nível de pedido: **[`olist_pedidos_consolidado.csv`](./olist_pedidos_consolidado.csv)**.

---

## 1. Visão Geral das Tabelas Originais

O dataset original da Olist é distribuído em 9 arquivos CSV. Para construir a base populacional onde a **unidade amostral é 1 pedido (`id_pedido`)**, foram utilizadas as 6 tabelas abaixo:

| Arquivo Original | Total de Linhas | `order_id` Únicos | Papel na Consolidação |
| :--- | :---: | :---: | :--- |
| `olist_orders_dataset.csv` | 99.441 | 99.441 | Tabela base central (1 linha por pedido) |
| `olist_customers_dataset.csv` | 99.441 | — | Localização do cliente (`customer_id` 1:1 com pedido) |
| `olist_order_items_dataset.csv` | 112.650 | 98.666 | Itens comprados, preços e fretes (relação $1:N$) |
| `olist_order_payments_dataset.csv` | 103.886 | 99.440 | Transações e meios de pagamento (relação $1:N$) |
| `olist_order_reviews_dataset.csv` | 99.224 | 98.673 | Avaliações de satisfação dos clientes (relação $1:N$) |
| `olist_products_dataset.csv` | 32.951 | — | Cadastro de produtos para obter a categoria principal |

---

## 2. Os 5 Passos de Unificação e Agrupamento

Para evitar a duplicação de pedidos (o que violaria a equiprobabilidade exigida na **Amostragem Aleatória Simples - AAS**), todas as tabelas com relação $1:N$ foram previamente agregadas por `order_id` antes da junção (*Left Join*).

### Passo 1: Preparação e Filtro da Tabela Base (`orders`)
* **Filtro de Status:** A base original continha **99.441 pedidos** distribuídos em 8 status:
  * `delivered` (entregue): **96.478** (97,02%)
  * `shipped` (enviado): 1.107 (1,11%)
  * `canceled` (cancelado): 625 (0,63%)
  * `unavailable` (indisponível): 609 (0,61%)
  * `invoiced` (faturado): 314 (0,32%)
  * `processing` (em processamento): 301 (0,30%)
  * `created` (criado): 5 (0,01%)
  * `approved` (aprovado): 2 (< 0,01%)
* **Decisão metodológica:** Foram mantidos exclusivamente os **96.478 pedidos com status `delivered` (`Entregue`)**, removendo **2.963 pedidos** não concluídos. Isso garante que a população de interesse represente transações completas com ciclo logístico encerrado.
* **Criação de variáveis derivadas de tempo:**
  * `tempo_entrega_dias`: diferença exata (em dias decimais) entre `data_entrega_cliente` e `data_compra`.
  * `dias_diferenca_estimativa`: diferença (em dias decimais) entre `data_estimada_entrega` e `data_entrega_cliente` (valores positivos indicam entrega antes do prazo; negativos indicam atraso).
  * `entregue_com_atraso`: variável qualitativa (`Sim` se `data_entrega_cliente > data_estimada_entrega`, e `Não` caso contrário).

### Passo 2: Junção com Clientes (`customers` — Relação $1:1$)
* Junção direta via chave `customer_id`, incorporando o identificador único do cliente (`id_cliente_unico`), a cidade (`cidade_cliente`) e o estado (`uf_cliente`).
* Foi criada também a variável qualitativa derivada `regiao_cliente` (*Sudeste, Sul, Nordeste, Centro-Oeste, Norte*) a partir da UF.

### Passo 3: Agrupamento e Junção de Itens e Produtos (`order_items` + `products` — Relação $1:N \rightarrow 1:1$)
* Os 112.650 registros de itens foram enriquecidos com a categoria do produto (`olist_products_dataset.csv` via `product_id`) e agrupados por `order_id` usando as seguintes regras:
  * `quantidade_itens`: contagem (`count`) de itens no pedido.
  * `valor_total_produtos`: soma (`sum`) da coluna `price` de todos os itens do pedido.
  * `valor_medio_item`: média (`mean`) da coluna `price` dos itens do pedido.
  * `valor_total_frete`: soma (`sum`) da coluna `freight_value` de todos os itens do pedido.
  * `categoria_produto_principal`: primeira categoria válida (`first`) associada aos itens do pedido.

### Passo 4: Agrupamento e Junção de Pagamentos (`order_payments` — Relação $1:N \rightarrow 1:1$)
* Como um mesmo pedido pode ser pago com mais de um método (ex.: cartão + voucher), os 103.886 registros foram ordenados por `order_id` e pelo valor pago (`payment_value` decrescente) e agrupados por `order_id`:
  * `valor_total_pago`: soma (`sum`) de todos os valores pagos no pedido.
  * `numero_parcelas`: valor máximo (`max`) de parcelas (`payment_installments`) utilizado no pedido.
  * `quantidade_pagamentos`: contagem (`count`) de transações de pagamento usadas no pedido.
  * `meio_pagamento_principal`: método de pagamento de maior valor no pedido, traduzido para português (`Cartão de Crédito`, `Boleto`, `Voucher`, `Cartão de Débito`).

### Passo 5: Agrupamento e Junção de Avaliações (`order_reviews` — Relação $1:N \rightarrow 1:1$)
* Os 99.224 registros de avaliações foram agrupados por `order_id`:
  * `nota_avaliacao`: média (`mean`) das notas atribuídas ao pedido (escala de 1 a 5).
  * `quantidade_avaliacoes`: contagem (`count`) de avaliações registradas para o pedido.
  * `avaliacao_positiva`: variável qualitativa derivada (`Sim` quando `nota_avaliacao >= 4`, e `Não` quando `< 4`).

---

## 3. Valores Nulos Encontrados e Tratamento Realizado

### 3.1. Valores Nulos nas Tabelas Brutas Originais
Antes da unificação, as tabelas apresentavam os seguintes valores ausentes:
* **`olist_orders_dataset.csv` (99.441 linhas):**
  * `order_approved_at`: 160 nulos (0,16%)
  * `order_delivered_carrier_date`: 1.783 nulos (1,79%)
  * `order_delivered_customer_date`: 2.965 nulos (2,98% — concentrados quase totalmente nos pedidos não entregues/cancelados)
* **`olist_order_reviews_dataset.csv` (99.224 linhas):**
  * `review_comment_title`: 87.656 nulos (88,34%) — coluna de texto livre descartada.
  * `review_comment_message`: 58.247 nulos (58,70%) — coluna de texto livre descartada.
* **`olist_products_dataset.csv` (32.951 linhas):**
  * `product_category_name`: 610 produtos sem categoria cadastrada (1,85%).
* **`customers`, `items` e `payments`:** 0 valores nulos em suas colunas originais.

### 3.2. Valores Nulos Após a Unificação dos 96.478 Pedidos Entregues
Após filtrar os 96.478 pedidos entregues e realizar o *Left Join* com as tabelas agrupadas, foram identificados os seguintes valores ausentes:

| Coluna (PT-BR) | Qtd. de Nulos | % sobre 96.478 | Origem do Valor Nulo | Tratamento Aplicado |
| :--- | :---: | :---: | :--- | :--- |
| `categoria_produto_principal` | 1.332 | 1,3806% | Produtos sem categoria cadastrada na tabela `products` | Preenchido com `'nao_informada'` para preservar pedidos válidos |
| `nota_avaliacao` / `avaliacao_positiva` | 646 | 0,6696% | Pedidos entregues que não tiveram avaliação registrada em `reviews` | Linhas removidas (`dropna`) |
| `data_aprovacao` | 14 | 0,0145% | Falha de registro do timestamp de aprovação | Linhas removidas (`dropna`) |
| `data_entrega_cliente` / `tempo_entrega_dias` / `entregue_com_atraso` | 8 | 0,0083% | Pedidos marcados como entregues mas sem data final registrada | Linhas removidas (`dropna`) |
| `data_envio_transportadora` | 2 | 0,0021% | Falha de registro do timestamp de despacho | Linhas removidas (`dropna`) |
| `valor_total_pago` / `numero_parcelas` / `meio_pagamento_principal` | 1 | 0,0010% | 1 único pedido (`bfbd0f9bdef84302105ad712db648a6c`) ausente na tabela `payments` | Linha removida (`dropna`) |

---

## 4. Resumo Quantitativo: Total de Pedidos Antes e Após a Limpeza

| Etapa do Processamento | Total de Pedidos (Linhas) | Linhas Removidas na Etapa | % Retido da Base Inicial |
| :--- | :---: | :---: | :---: |
| **1. Base Bruta Original (`olist_orders_dataset.csv`)** | **99.441** | — | 100,00% |
| **2. Após Filtro de Pedidos Entregues (`order_status == 'delivered'`)** | **96.478** | -2.963 | 97,02% |
| **3. Após Remoção de Registros Incompletos (`dropna` em datas, pagamento e avaliação)** | **95.808** | -670 | **96,35%** |

* **População Final Consolidada ($N$):** **95.808 pedidos únicos** e **27 colunas** (com **zero valores nulos** em toda a tabela).
* *(Nota: Caso deseje filtrar também os pedidos cuja categoria do produto foi preenchida como `'nao_informada'`, restam exatos 94.485 pedidos).*

---

## 5. Dicionário de Colunas (Traduzidas para PT-BR) e Parâmetros Populacionais

A tabela final `olist_pedidos_consolidado.csv` possui as seguintes 27 colunas traduzidas para o português, acompanhadas dos verdadeiros **parâmetros populacionais ($N = 95.808$)** para referência direta no **Painel 1** e comparação no **Painel 3**:

### 5.1. Identificadores e Datas
1. `id_pedido`: Código único do pedido (Unidade Amostral).
2. `id_cliente_pedido`: Código do cliente associado àquele pedido.
3. `id_cliente_unico`: Identificador único do cliente (permite identificar recompras).
4. `status_pedido`: Status do pedido (todos `'Entregue'`).
5. `data_compra`: Data e hora da realização do pedido.
6. `data_aprovacao`: Data e hora da aprovação do pagamento.
7. `data_envio_transportadora`: Data e hora em que o pacote foi entregue à transportadora.
8. `data_entrega_cliente`: Data e hora em que o cliente recebeu o pedido.
9. `data_estimada_entrega`: Prazo estimado de entrega informado no momento da compra.

### 5.2. Variáveis Qualitativas (Para Análise de Proporção Populacional $p$)
10. `cidade_cliente`: Nome do município do comprador.
11. `uf_cliente`: Sigla do estado do comprador (ex.: SP = 41,74%, RJ = 12,83%, MG = 11,70%).
12. `regiao_cliente`: Macrorregião brasileira do comprador:
    * **Sudeste:** 65.719 pedidos (**68,59%**)
    * **Sul:** 13.743 pedidos (**14,34%**)
    * **Nordeste:** 8.973 pedidos (**9,37%**)
    * **Centro-Oeste:** 5.594 pedidos (**5,84%**)
    * **Norte:** 1.779 pedidos (**1,86%**)
13. `categoria_produto_principal`: Categoria principal do produto adquirido.
14. `meio_pagamento_principal`: Método de pagamento principal do pedido:
    * **Cartão de Crédito:** 72.330 pedidos (**75,49%**)
    * **Boleto:** 19.048 pedidos (**19,88%**)
    * **Voucher:** 2.953 pedidos (**3,08%**)
    * **Cartão de Débito:** 1.477 pedidos (**1,54%**)
15. `avaliacao_positiva`: Indica se a nota de avaliação do pedido foi $\ge 4$:
    * **Sim:** 75.606 pedidos (**78,91%**)
    * **Não:** 20.202 pedidos (**21,09%**)
16. `entregue_com_atraso`: Indica se o pedido foi entregue após a data estimada:
    * **Não (No prazo):** 88.149 pedidos (**92,01%**)
    * **Sim (Com atraso):** 7.659 pedidos (**7,99%**)

### 5.3. Variáveis Quantitativas (Para Análise de Média Populacional $\mu$)

| Coluna (PT-BR) | Descrição | Média Populacional ($\mu$) | Mediana | Desvio-Padrão ($\sigma$) | Mínimo | Máximo |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `valor_total_pago` | Valor total pago no pedido (R\$) | **R\$ 159,60** | R\$ 105,28 | R\$ 217,53 | R\$ 9,59 | R\$ 13.664,08 |
| `valor_total_produtos` | Soma dos preços dos itens (R\$) | **R\$ 136,80** | R\$ 86,25 | R\$ 207,80 | R\$ 0,85 | R\$ 13.440,00 |
| `valor_total_frete` | Valor total do frete (R\$) | **R\$ 22,76** | R\$ 17,16 | R\$ 21,52 | R\$ 0,00 | R\$ 1.794,96 |
| `valor_medio_item` | Preço médio por item no pedido (R\$) | **R\$ 125,08** | R\$ 79,00 | R\$ 190,63 | R\$ 0,85 | R\$ 6.735,00 |
| `tempo_entrega_dias` | Tempo entre compra e entrega (dias) | **12,52 dias** | 10,20 dias | 9,46 dias | 0,53 dias | 208,35 dias |
| `dias_diferenca_estimativa` | Folga entre prazo estimado e entrega (dias) | **11,36 dias** | 12,05 dias | 10,16 dias | -188,98 dias | 146,02 dias |
| `numero_parcelas` | Quantidade máxima de parcelas | **2,93 parcelas** | 2,00 | 2,71 | 0 | 24 |
| `nota_avaliacao` | Nota de satisfação (1 a 5 estrelas) | **4,16 estrelas** | 5,00 | 1,28 | 1,00 | 5,00 |
| `quantidade_itens` | Número de itens no pedido | **1,14 itens** | 1,00 | 0,53 | 1 | 21 |
| `quantidade_pagamentos` | Nº de transações de pagamento | **1,04** | 1,00 | 0,35 | 1 | 26 |
| `quantidade_avaliacoes` | Nº de avaliações registradas | **1,01** | 1,00 | 0,08 | 1 | 3 |

---

## 6. Relatório de Validação, Testes Automatizados e Ajustes de Código (`dashboard.py`)

Ao final do desenvolvimento da etapa de processamento e inferência estatística em Python ([`dashboard.py`](./dashboard.py)), foi executada uma bateria automatizada de **8 testes unitários (`unittest`)** para auditar a integridade dos dados, a reprodutibilidade da amostragem, a simulação do Teorema Central do Limite (TCL), os quantis do QQ-Plot e a precisão matemática das funções estatísticas.

### 6.1. Bateria de Testes Executada (`Ran 8 tests in 1.227s — OK`)

| ID do Teste | Escopo Auditado | Critério de Sucesso Verificado | Status |
| :--- | :--- | :--- | :---: |
| **`test_01_integridade_populacao`** | Base Consolidada (`olist_pedidos_consolidado.csv`) | Confirma exatamente `95.808` linhas, `27` colunas traduzidas em PT-BR, `95.808` `id_pedido` únicos (sem duplicatas), `0` valores nulos e 100% dos registros com `status_pedido == 'Entregue'`. | **APROVADO** |
| **`test_02_calculo_tamanho_amostral`** | Dimensionamento Amostral (`calcular_tamanho_amostral_proporcao`) | Valida a fórmula de população finita da Calculadora USP/Bauru para $N = 95.808$, $Z = 1,96$ e $p = 0,50$: confirma $n = 383$ para margem de erro de $5\%$ e $n = 1.056$ para margem de erro de $3\%$. | **APROVADO** |
| **`test_03_integridade_e_reprodutibilidade_amostra_aas`** | Sorteio da Amostra (`olist_amostra_aas.csv`) | Confirma `383` pedidos sorteados sem reposição (`id_pedido` 100% únicos), todos subconjunto estrito da população, e reprodutibilidade idêntica ao reexecutar com `semente_aleatoria=42`. | **APROVADO** |
| **`test_04_consistencia_resumo_qualitativo`** | Tabela Descritiva Qualitativa (`resumo_qualitativas_pop_vs_amostra.csv`) | Confirma que a soma das frequências absolutas de Q1 (`meio_pagamento_principal`) e Q4 (`regiao_cliente`) fecha exatamente em $N = 95.808$ e $n = 383$, e que a soma dos percentuais fecha em $100,0\%$. | **APROVADO** |
| **`test_05_consistencia_resumo_quantitativo`** | Tabela Descritiva Quantitativa (`resumo_quantitativas_pop_vs_amostra.csv`) | Confirma o uso correto de `ddof=0` ($\sigma$ populacional) e `ddof=1` ($s$ amostral), além da exatidão das fórmulas $\text{IQR} = Q_3 - Q_1$ e $\text{CV}\% = (s / \bar{x}) \times 100$. | **APROVADO** |
| **`test_06_precisao_funcoes_probabilidade_e_inferencia`** | Inferência Estatística (`resultados_inferencia_painel3.csv`) | Audita a CDF Normal Padrão (`_cdf_normal_padrao(1.96) == 0.9750021`), o valor crítico $t$ de Student via bisseção e integração de Simpson (`_valor_critico_t_bicaudal(0.95, 382) == 1.96619`, erro $< 10^{-6}$), captura dos 4 parâmetros populacionais pelos respectivos ICs de 95% e decisões dos 4 testes de hipóteses. | **APROVADO** |
| **`test_07_distribuicao_amostral_tcl_e_qqplot`** | Simulação do TCL e Quantis do QQ-Plot (`distribuicao_amostral_tcl.csv` e `dados_qqplot_powerbi.csv`) | Confirma as `1.000` amostras simuladas de $n = 383$, convergência da média das médias amostrais ($\text{R\$ } 159,43 \approx \mu = \text{R\$ } 159,60$), queda drástica da assimetria de `9,24` para `0,14` (normalidade pelo TCL) e integridade dos `2.298` pontos calculados para os gráficos QQ-Plot. | **APROVADO** |
| **`test_08_existencia_arquivos_csv_para_power_bi`** | Exportação de Arquivos para Power BI | Confirma a existência física, codificação `utf-8-sig` (compatível com acentuação no Power BI e Excel) e preenchimento dos 7 arquivos CSV gerados na pasta do projeto. | **APROVADO** |

---

### 6.2. Problemas Identificados Durante o Desenvolvimento e Mudanças Realizadas no Código

Durante a construção e os testes de execução do script [`dashboard.py`](./dashboard.py), foram identificados e corrigidos **3 pontos técnicos importantes**:

1. **Incompatibilidade de Tipos no NumPy 2.x / Pandas 3.1 (`DTypePromotionError`):**
   * **O que ocorreu:** Ao criar as colunas categóricas `entregue_com_atraso` e `avaliacao_positiva` combinando strings (`"Sim"` / `"Não"`) e `np.nan` dentro de `np.where` aninhados, o NumPy 2.x lançou a exceção `DTypePromotionError` por não promover automaticamente `FloatDType` (`np.nan`) com `StrDType`.
   * **Mudança realizada:** Substituímos o `np.where` aninhado pela criação explícita de uma `pd.Series(..., dtype="object")` seguida da atribuição de `np.nan` via máscara booleana (`.loc[mascara_nulos] = np.nan`), garantindo compatibilidade total com Pandas 3.1+.
2. **Codificação de Caracteres Matemáticos no Terminal Windows (`UnicodeEncodeError` em `cp1252`):**
   * **O que ocorreu:** Ao exibir no console do Windows símbolos estatísticos como $\alpha$, $\mu$, $\hat{p}$ e $\bar{x}$, o terminal padrão (`cp1252`) gerou erro de codificação.
   * **Mudança realizada:** Adicionamos no cabeçalho de [`dashboard.py`](./dashboard.py) a instrução `sys.stdout.reconfigure(encoding="utf-8")` e exportamos todos os arquivos CSV com `encoding="utf-8-sig"` (UTF-8 com BOM), garantindo que tanto o terminal quanto o Power BI reconheçam todos os acentos e símbolos do português automaticamente.
3. **Independência de Bibliotecas Externas para a Distribuição $t$ de Student:**
   * **O que ocorreu:** Para evitar que o script dependesse da instalação manual do pacote `scipy` no ambiente local, era necessário calcular os valores críticos $t_{(\alpha/2, n-1)}$ e os valores-$p$ exatos da distribuição $t$ de Student usando apenas a biblioteca padrão `math`.
   * **Mudança realizada:** Implementamos em [`dashboard.py`](./dashboard.py) as funções `_cdf_t_student` (utilizando `math.lgamma` e a Regra de Simpson Composta com 2.000 subintervalos) e `_valor_critico_t_bicaudal` (via método da bisseção com 80 iterações), atingindo precisão de 6 casas decimais ($t_{0,025; 382} = 1,966194$).


