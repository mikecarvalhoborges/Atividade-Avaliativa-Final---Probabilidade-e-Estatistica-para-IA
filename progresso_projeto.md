# Roadmap e Diário de Progresso — Trabalho Final de Probabilidade e Estatística

> **Ferramentas do Projeto:**
> * **Engenharia de Dados, Amostragem, TCL, QQ-Plot e Inferência:** Python (`pandas`, `numpy`, `math`) no arquivo [`dashboard.py`](./dashboard.py)
> * **Visualização e Painéis Interativos (Painéis 1, 2 e 3):** Power BI Desktop
> * **Entrega Final:** Links públicos dos 3 painéis + Vídeo de até 5 minutos no YouTube + Link da base original (Kaggle Olist)

---

## Visão Geral do Roadmap (8 Etapas Passo a Passo)

```
[Etapa 1] Consolidação e Limpeza da Base Populacional (Python)          --> [CONCLUÍDA]
    │
    ▼
[Etapa 2] Seleção das Variáveis e Definição da População/Unidade        --> [CONCLUÍDA]
    │
    ▼
[Etapa 3] Dimensionamento Amostral (Calculadora USP) e Sorteio da AAS   --> [CONCLUÍDA]
    │
    ▼
[Etapa 4] Estatística Descritiva: População vs. Amostra (Python -> CSV) --> [CONCLUÍDA]
    │
    ▼
[Etapa 5] Inferência Estatística + TCL + QQ-Plot (Python -> CSV)        --> [CONCLUÍDA]
    │
    ▼
[Etapa 6] Bateria de Testes e Validação do Código Python + Relatório    --> [CONCLUÍDA]
    │
    ▼
[Etapa 7] Tutorial Clique a Clique de Power BI (Do Zero aos 3 Painéis)  --> [CONCLUÍDA]
    │
    ▼
[Etapa 8] Roteiro de 5 Minutos para Gravação do Vídeo e Checklist Final --> [CONCLUÍDA]
```

---

## Resumo das Etapas 1 a 6 (Concluídas no Python)

* **Etapa 1 (População Limpa):** [`olist_pedidos_consolidado.csv`](./olist_pedidos_consolidado.csv) ($N = 95.808$ pedidos únicos, 27 colunas em PT-BR, zero nulos).
* **Etapa 2 (Variáveis do Estudo):**
  * **Q1 (`meio_pagamento_principal`):** Cartão de Crédito ($p_1 = 75,49\%$).
  * **Q4 (`regiao_cliente`):** Região Sudeste ($p_2 = 68,59\%$).
  * **M1 (`valor_total_pago`):** Ticket Médio ($\mu_1 = \text{R\$ } 159,60$).
  * **M3 (`valor_total_frete`):** Frete Médio ($\mu_2 = \text{R\$ } 22,76$).
* **Etapa 3 (Amostra AAS $n = 383$):** [`olist_amostra_aas.csv`](./olist_amostra_aas.csv) (Confiança 95%, Margem de Erro 5%, $p = 50\%$, Semente = 42).
* **Etapa 4 (Tabelas Descritivas):** [`resumo_qualitativas_pop_vs_amostra.csv`](./resumo_qualitativas_pop_vs_amostra.csv) e [`resumo_quantitativas_pop_vs_amostra.csv`](./resumo_quantitativas_pop_vs_amostra.csv).
* **Etapa 5 (Inferência, TCL e QQ-Plot):** [`resultados_inferencia_painel3.csv`](./resultados_inferencia_painel3.csv), [`distribuicao_amostral_tcl.csv`](./distribuicao_amostral_tcl.csv) e [`dados_qqplot_powerbi.csv`](./dados_qqplot_powerbi.csv).
* **Etapa 6 (Validação):** 8 testes unitários aprovados (`1.227s — OK`), documentados em [`relatorio_consolidacao_dados.md`](./relatorio_consolidacao_dados.md).

---

## Etapa 7: Guia Didático Clique a Clique para se Localizar no Power BI Desktop

### PARTE 1: O Mapa da Tela do Power BI Desktop (Onde fica cada coisa)

Quando você abre o **Power BI Desktop**, a tela é dividida em **5 lugares principais**:

```
+-----------------------------------------------------------------------------------+
| [1. FAIXA SUPERIOR / MENU]  Página Inicial | Inserir | Modelagem | Exibição       |
+----+---------------------------------------------------------+----------+---------+
| 2. |                                                         | 4.       | 5.      |
| B  |                                                         | PAINEL   | PAINEL  |
| A  |                                                         | DE       | DE      |
| R  |                 3. TELA EM BRANCO (CANVAS)              | VISUALI- | DADOS   |
| R  |            (Onde você monta e arrasta os gráficos)      | ZAÇÕES   | (Suas   |
| A  |                                                         | (Ícones  | tabelas |
|    |                                                         |  dos     | e       |
| E  |                                                         | gráficos)| colunas)|
| S  |                                                         |          |         |
| Q. |                                                         |          |         |
+----+---------------------------------------------------------+----------+---------+
| [6. ABAS NO RODAPÉ]  [Página 1]  [+] (Clique no + para criar Página 2 e Página 3) |
+-----------------------------------------------------------------------------------+
```

1. **Faixa Superior (Menu **`Página Inicial`**):** É onde fica o botão **`Obter dados`** (ou **`Texto/CSV`**) para carregar seus arquivos `.csv`.
2. **Barra Fina na Esquerda (3 Ícones empilhados):**
   * **Ícone 1 (Gráfico de barras — `Exibição de Relatório`):** É a tela onde desenhamos os painéis.
   * **Ícone 2 (Tabela — `Exibição de Tabela`):** Serve para você espiar as linhas e colunas das suas tabelas carregadas.
   * **Ícone 3 (3 caixinhas ligadas — `Exibição de Modelo`):** Mostra se o Power BI tentou ligar uma tabela na outra com setinhas.
3. **Tela Central em Branco (Canvas):** Onde seus gráficos aparecem. **Regra de ouro:** Sempre clique num espaço em branco da tela antes de criar um gráfico novo (se você estiver com um gráfico selecionado e clicar noutro ícone, ele troca o gráfico antigo em vez de criar um novo!).
4. **Coluna da Direita — `Visualizações`:** Tem vários quadradinhos com ícones de gráficos (Barras, Colunas, Pizza, Cartão `123`, Tabela, Script Python `Py`). Logo abaixo dos ícones, aparecem as **Caixinhas para arrastar colunas** (`Eixo X`, `Eixo Y`, `Legenda`, `Valores`).
5. **Última Coluna da Direita — `Dados` (ou `Campos`):** Lista todas as tabelas `.csv` que você importou. Clicando na setinha `>` ao lado do nome da tabela, ela abre todas as colunas para você arrastar!
6. **Abas no Rodapé (embaixo da tela):** Onde está escrito `Página 1`. É ali que você terá as 3 abas do trabalho: **Painel 1 (População)**, **Painel 2 (Amostra)** e **Painel 3 (Inferência)**.

---

### PARTE 2: Como Importar os CSVs sem Erro de Ponto/Vírgula (Passo Inicial)

1. No menu superior **`Página Inicial`**, clique no botão **`Texto/CSV`** (ou **`Obter dados` $\rightarrow$ `Texto/CSV`**).
2. Vá até a pasta do nosso projeto e selecione o primeiro arquivo: **`olist_pedidos_consolidado.csv`**.
3. Uma janela de pré-visualização vai abrir:
   * Olhe para a coluna `valor_total_pago`: nossos números têm ponto decimal (ex.: `159.60`).
   * Na parte de baixo dessa janela, clique no botão **`Transformar Dados`** (fica ao lado de "Carregar"). Isso abre a janela do **Power Query**.
   * Lá no canto superior esquerdo do Power Query, clique em **`Arquivo` $\rightarrow$ `Opções e configurações` $\rightarrow$ `Opções da consulta`**.
   * No menu esquerdo da janelinha, clique em **`Regional`** (embaixo de " Consulta Atual") e mude a **Localidade** para **`Inglês (Estados Unidos)`** e dê **OK**!
   * *(Pronto! Fazendo isso, o Power BI entende automaticamente que o ponto `.` é casa decimal e não milhar!)*
   * Clique no botão **`Fechar e Aplicar`** (no canto superior esquerdo).
4. Repita esse processo em **`Página Inicial` $\rightarrow$ `Texto/CSV`** para importar os outros arquivos da pasta:
   * `olist_amostra_aas.csv`
   * `resumo_qualitativas_pop_vs_amostra.csv`
   * `resumo_quantitativas_pop_vs_amostra.csv`
   * `resultados_inferencia_painel3.csv`
   * `distribuicao_amostral_tcl.csv`
   * `dados_qqplot_powerbi.csv`
5. **Conferência rápida (30 segundos):**
   * Clique no **3º ícone da barra esquerda (`Exibição de Modelo`)**.
   * Se houver qualquer linha ligando uma tabela na outra, clique com o botão direito em cima da linha e clique em **`Excluir`**. Deixe todas as tabelas soltas!
   * Volte para o **1º ícone da barra esquerda (`Exibição de Relatório`)**.

---

### PARTE 3: Montando o PAINEL 1 (População — $N = 95.808$) Passo a Passo

No rodapé da tela, dê dois cliques em `Página 1` e renomeie para: **`Painel 1 - População`**.

#### Passo 1.1: Criar os Cartões de Indicadores (KPIs) no Topo
1. Clique em um espaço vazio da tela branca.
2. No painel **`Visualizações`** (à direita), procure o ícone chamado **`Cartão`** (é um retângulo com o número **`123`** dentro, geralmente na 4ª fileira de ícones). Clique nele!
3. Agora vá no painel **`Dados`** (extrema direita), abra a tabela **`olist_pedidos_consolidado`** e arraste a coluna **`id_pedido`** para dentro da caixinha **`Campos`** (abaixo dos ícones de Visualizações).
4. Clique na setinha para baixo `v` ao lado de `id_pedido` (dentro da caixinha `Campos`) e escolha **`Contagem`**. O cartão vai mostrar **`95,81 Mil`** (ou `95.808` — para mostrar o número exato `95.808`, clique no ícone do **Pincel `Formatar seu visual`** no topo do painel Visualizações $\rightarrow$ `Valor do balão` $\rightarrow$ `Exibir unidades`: mude de *Automático* para **`Nenhum`**!).
5. **Mais 2 Cartões rápidos (Média e Mediana do Valor Pago):**
   * Clique no fundo branco $\rightarrow$ clique no ícone **`Cartão (123)`** $\rightarrow$ arraste **`valor_total_pago`** (da tabela `olist_pedidos_consolidado`). Clique na setinha `v` do campo e escolha **`Média`** (vai aparecer **`159,60`**!).
   * Clique no fundo branco $\rightarrow$ clique no ícone **`Cartão (123)`** $\rightarrow$ arraste **`valor_total_pago`** novamente, clique na setinha `v` do campo e escolha **`Mediana`** (vai aparecer **`105,28`**!).
   * Faça o mesmo para **`valor_total_frete`** (Média = **`22,76`** e Mediana = **`17,16`**).

#### Passo 1.2: Gráfico 1 — Proporção por Meio de Pagamento (Variável Qualitativa Q1)
1. Clique num espaço em branco da tela.
2. No painel **`Visualizações`**, clique no **1º ícone da 1ª fileira**: **`Gráfico de barras empilhadas`** (ou **`Gráfico de barras clusterizado`** — barras deitadas).
3. No painel **`Dados`**, abra a tabela **`resumo_qualitativas_pop_vs_amostra`**:
   * Arraste a coluna **`categoria`** para a caixinha **`Eixo Y`**.
   * Arraste a coluna **`proporcao_populacao_pct`** para a caixinha **`Eixo X`**.
   * Arraste a coluna **`frequencia_populacao_N`** para a caixinha **`Dicas de ferramentas`** (assim, ao passar o mouse na barra, mostra os `72.330` pedidos!).
4. **Como filtrar só Meio de Pagamento nesse gráfico:**
   * Com o gráfico selecionado, olhe a coluna **`Filtros`** (fica logo à esquerda do painel Visualizações).
   * Arraste a coluna **`variavel_qualitativa`** para dentro de *"Filtros neste visual"* e marque a caixinha **`meio_pagamento_principal`**.
   * Pronto! Você verá: **Cartão de Crédito (75,49%)**, Boleto (19,88%), Voucher (3,08%) e Cartão de Débito (1,54%)!

#### Passo 1.3: Gráfico 2 — Proporção de Pedidos por Região (Variável Qualitativa Q4)
1. Clique no Gráfico 1 que você acabou de fazer, aperte **`Ctrl + C`** e **`Ctrl + V`** (copiar e colar!).
2. Arraste a cópia para o lado.
3. No painel **`Filtros`** desse novo gráfico, desmarque `meio_pagamento_principal` e marque **`regiao_cliente`**!
4. Pronto! Em 5 segundos você já tem o gráfico da Região Sudeste (**68,59%**), Sul (14,34%), Nordeste (9,37%), Centro-Oeste (5,84%) e Norte (1,86%)!

#### Passo 1.4: O Trio `ggplot` (Distribuição + Boxplot + QQ-Plot da População) DENTRO do Power BI
1. Clique num espaço vazio na metade de baixo da tela.
2. No painel **`Visualizações`**, procure o ícone **`Py`** (tem as letras **Py** — fica na 5ª ou 6ª fileira de ícones). Clique nele! (Se aparecer um aviso perguntando se deseja habilitar visuais de script, clique em **`Habilitar`**).
3. No painel **`Dados`**, abra a tabela **`olist_pedidos_consolidado`** e arraste **duas colunas** para dentro da caixinha **`Valores`** do visual `Py`:
   * Arraste **`id_pedido`** (IMPORTANTE: clique na setinha `v` ao lado de `id_pedido` na caixinha Valores e marque **`Não resumir`** — se não marcar "Não resumir", o Power BI junta todas as linhas numa só!).
   * Arraste **`valor_total_pago`** (clique na setinha `v` ao lado dele e marque **`Não resumir`** também!).
4. Olhe para a parte de baixo da tela do Power BI: abriu uma janela chamada **`Editor de script do Python`**.
5. Apague qualquer linha em branco que estiver lá, cole o código do **Bloco `ggplot` dos Painéis 1 e 2** (que está logo abaixo na Seção de Códigos Prontos) e clique no botãozinho **`Play` (triângulo de executar)** no canto direito da barra do Editor de script do Python!
6. O Power BI vai rodar o Python e desenhar **os 3 gráficos `ggplot` (Histograma com Média/Mediana + Boxplot + QQ-Plot)** lado a lado dentro do seu painel!

#### Passo 1.5: Tabela de Medidas Descritivas no Rodapé
1. Clique num espaço vazio no rodapé da tela.
2. No painel **`Visualizações`**, clique no ícone **`Tabela`** (uma gradezinha na 5ª fileira).
3. Da tabela **`resumo_quantitativas_pop_vs_amostra`**, arraste para **`Colunas`**: `variavel_quantitativa`, `media`, `mediana`, `desvio_padrao`, `variancia`, `coeficiente_variacao_pct`, `quartil_1_25pct`, `quartil_3_75pct`, `amplitude_interquartil_iqr`, `minimo`, `maximo`, `assimetria_skewness`.
4. No painel **`Filtros`** dessa tabela, arraste **`conjunto_dados`** e marque **`População (N = 95.808)`**.

---

### PARTE 4: Montando o PAINEL 2 (Amostra AAS — $n = 383$) em 2 Minutos!

Você **não precisa montar tudo do zero** no Painel 2:
1. Lá no rodapé do Power BI, clique com o **botão direito** em cima da aba **`Painel 1 - População`** e clique em **`Duplicar página`**.
2. Dê dois cliques na aba nova e renomeie para: **`Painel 2 - Amostra AAS (n = 383)`**.
3. Agora só troque os dados de População para Amostra em cada visual da tela:
   * **Nos Cartões do topo:** Clique em cada cartão, tire a coluna da tabela `olist_pedidos_consolidado` (clicando no `X` ao lado do campo) e arraste a mesma coluna da tabela **`olist_amostra_aas`**! (A contagem de `id_pedido` vai mostrar **`383`**, a média de `valor_total_pago` vai mostrar **`166,11`** e a mediana **`106,21`**!).
   * **Nos 2 Gráficos de Barras (Q1 e Q4):** Clique em cada um, tire `proporcao_populacao_pct` do Eixo X e arraste **`proporcao_amostra_pct`** (e coloque `frequencia_amostra_n` na Dica de ferramentas).
   * **No Visual `Py` (`ggplot` do Histograma + Boxplot + QQ-Plot):** Clique nele, tire `id_pedido` e `valor_total_pago` da população e arraste **`id_pedido`** (*"Não resumir"*) e **`valor_total_pago`** (*"Não resumir"*) da tabela **`olist_amostra_aas`**! O código Python é exatamente o mesmo e já vai redesenhar automaticamente os 3 gráficos para os `383` pedidos da amostra!
   * **Na Tabela do Rodapé:** No painel **`Filtros`**, desmarque `"População (N = 95.808)"` e marque **`"Amostra AAS (n = 383)"`**.

---

### PARTE 5: Montando o PAINEL 3 (Inferência Estatística + Distribuição Amostral do TCL)

1. Lá no rodapé do Power BI, clique no botão **`+`** para criar uma aba em branco e renomeie para: **`Painel 3 - Inferência e Comparação`**.

#### Passo 3.1: Visual `Py` (`ggplot`) da Distribuição Amostral do TCL + QQ-Plot das Médias
1. Clique no fundo em branco $\rightarrow$ clique no ícone **`Py` (Visual do Python)** em `Visualizações`.
2. No painel **`Dados`**, abra a tabela **`distribuicao_amostral_tcl`** e arraste para **`Valores`**:
   * **`id_simulacao`** (clique na setinha `v` $\rightarrow$ marque **`Não resumir`**).
   * **`media_amostral_valor_pago`** (clique na setinha `v` $\rightarrow$ marque **`Não resumir`**).
3. Cole no **Editor de script do Python** o código do **Bloco `ggplot` do Painel 3 (TCL)** abaixo e clique no botão **`Play`**. Ele vai desenhar o **Sino da Distribuição Amostral com a curva Normal vermelha** e o **QQ-Plot das médias amostrais alinhado na reta**!

#### Passo 3.2: Gráfico Comparativo População vs. Amostra (Colunas Lado a Lado)
1. Clique num espaço vazio $\rightarrow$ clique no ícone **`Gráfico de colunas clusterizado`** (4º ícone da 1ª fileira em `Visualizações`).
2. Da tabela **`resumo_qualitativas_pop_vs_amostra`**, arraste:
   * **`categoria`** para o **`Eixo X`**.
   * **`proporcao_populacao_pct`** E **`proporcao_amostra_pct`** (os dois juntos!) para o **`Eixo Y`**.
   * Você verá duas colunas coladas lado a lado para cada categoria (População vs. Amostra), mostrando visualmente que as proporções são quase idênticas!

#### Passo 3.3: Tabela Completa dos Intervalos de Confiança e Testes de Hipóteses
1. Clique num espaço vazio na metade inferior do Painel 3 $\rightarrow$ clique no ícone **`Tabela`**.
2. Da tabela **`resultados_inferencia_painel3`**, arraste para **`Colunas`** (nessa ordem):
   * `codigo_analise`
   * `evento_ou_unidade`
   * `hipotese_nula_H0`
   * `hipotese_alternativa_H1`
   * `parametro_populacional_real`
   * `estimativa_pontual_amostra`
   * `ic_95_limite_inferior`
   * `ic_95_limite_superior`
   * `parametro_pop_dentro_do_ic`
   * `distribuicao_teste`
   * `estatistica_teste_calculada`
   * `valor_p`
   * `decisao_teste_hipotese`
   * `condicoes_aplicacao`
   * `conclusao_interpretacao`
   * *(IMPORTANTE: Para as colunas numéricas dessa tabela de 4 linhas, se o Power BI colocar "Soma de..." no título da coluna, clique na setinha `v` de cada uma delas na caixinha `Colunas` e marque **`Não resumir`**).*

---

### ANEXO: Os 3 Códigos Python Prontos para Colar no Visual `Py` do Power BI (Com Legendas Completas e Filtro Interativo!)

> **Como deixar TUDO interativo (Cartão + Gráficos de Barras + Visual `Py`):**
> Na caixinha **`Valores`** do visual `Py` (no Painel 1), coloque as duas colunas **`meio_pagamento_principal`** e **`regiao_cliente`** da tabela **`olist_pedidos_consolidado`** (como só existem 4 meios de pagamento e 5 regiões, $4 \times 5 = 20$ linhas, o Power BI nunca trava e avisa o Python toda vez que você clicar em "Boleto" ou "Sudeste"!).

#### Código 1: Para o Visual `Py` do Painel 1 (População — $N = 95.808$)
```python
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
from statistics import NormalDist

plt.style.use('ggplot')
caminho = r"G:\Meu Drive\UFRGS\IA003\Trabalhos\Atividade Avaliativa Final — Probabilidade e Estatística para IA\olist_pedidos_consolidado.csv"
df = pd.read_csv(caminho)

# Filtra interativamente caso o usuário clique em Boleto, Cartão ou em uma Região no Power BI!
if 'meio_pagamento_principal' in dataset.columns:
    df = df[df['meio_pagamento_principal'].isin(dataset['meio_pagamento_principal'].dropna().unique())]
if 'regiao_cliente' in dataset.columns:
    df = df[df['regiao_cliente'].isin(dataset['regiao_cliente'].dropna().unique())]

dados = df['valor_total_pago'].dropna().to_numpy()
media, mediana = np.mean(dados), np.median(dados)
q1, q3 = np.percentile(dados, [25, 75])
iqr = q3 - q1

fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))

# 1. Distribuição (Histograma com Média e Mediana)
axes[0].hist(dados[dados <= np.percentile(dados, 98)], bins=35, edgecolor='black', color='#E24A33', alpha=0.85, label='Frequência de Pedidos')
axes[0].axvline(media, color='#348ABD', linestyle='--', linewidth=2.2, label=f'Média (µ): R$ {media:.2f}')
axes[0].axvline(mediana, color='#2CA02C', linestyle='-', linewidth=2.2, label=f'Mediana (50%): R$ {mediana:.2f}')
axes[0].set_title(f'1. Distribuição População (N = {len(dados):,})', fontsize=10, fontweight='bold')
axes[0].set_xlabel('Valor Total Pago (R$)')
axes[0].set_ylabel('Qtd. de Pedidos')
axes[0].legend(loc='upper right', fontsize=8, frameon=True, facecolor='white')

# 2. Boxplot com Legenda Didática (Q1, Mediana, Média, Q3, Limites e Outliers)
axes[1].boxplot(
    dados, vert=False, patch_artist=True, showmeans=True,
    boxprops=dict(facecolor='#348ABD', alpha=0.75, edgecolor='black'),
    medianprops=dict(color='#2CA02C', linewidth=2.5),
    meanprops=dict(marker='D', markeredgecolor='black', markerfacecolor='#E24A33', markersize=6),
    flierprops=dict(marker='o', markerfacecolor='black', markersize=3, alpha=0.4)
)
axes[1].set_xlim(0, np.percentile(dados, 96))
axes[1].set_title('2. Boxplot (Posição, Dispersão e Outliers)', fontsize=10, fontweight='bold')
axes[1].set_xlabel('Valor Total Pago (R$)')
axes[1].set_yticks([])

legenda_boxplot = [
    Patch(facecolor='#348ABD', edgecolor='black', alpha=0.75, label=f'Caixa (IQR = Q3-Q1): R$ {q1:.2f} a R$ {q3:.2f}'),
    Line2D([0], [0], color='#2CA02C', lw=2.5, label=f'Linha Verde (Mediana): R$ {mediana:.2f}'),
    Line2D([0], [0], marker='D', color='w', markerfacecolor='#E24A33', markeredgecolor='black', markersize=6, label=f'Losango (Média µ): R$ {media:.2f}'),
    Line2D([0], [0], color='black', lw=1.2, label=f'Hastes: Limite 1,5x IQR (até R$ {q3 + 1.5*iqr:.2f})'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='black', markersize=5, label='Pontos Pretos: Outliers (Valores Extremos)')
]
axes[1].legend(handles=legenda_boxplot, loc='upper right', fontsize=7.5, frameon=True, facecolor='white')

# 3. QQ-Plot Normal com Legenda Didática
n = min(len(dados), 500)
p = (np.arange(1, n + 1) - 0.5) / n
z_teorico = np.array([NormalDist().inv_cdf(prob) for prob in p])
q_obs = np.quantile(dados, p)
incl = (q3 - q1) / (0.6745 - (-0.6745))
inter = q1 - incl * (-0.6745)

axes[2].scatter(z_teorico, q_obs, color='#348ABD', s=14, alpha=0.75, label='Pontos Azuis: Quantis Reais dos Pedidos')
axes[2].plot(z_teorico, inter + incl * z_teorico, color='#E24A33', linewidth=2.2, label='Reta Vermelha: Distribuição Normal Ideal')
axes[2].plot([], [], ' ', label='Curva fora da reta = Assimétrica (Não-Normal)')
axes[2].set_title('3. QQ-Plot Normal (Teste Visual de Normalidade)', fontsize=10, fontweight='bold')
axes[2].set_xlabel('Quantis Teóricos da Normal Padrão (Z)')
axes[2].set_ylabel('Quantis Observados (R$)')
axes[2].legend(loc='upper left', fontsize=7.5, frameon=True, facecolor='white')

plt.tight_layout()
plt.show()
```

#### Código 2: Para o Visual `Py` do Painel 2 (Amostra AAS — $n = 383$)
*(Na caixinha `Valores` do visual `Py` do Painel 2, arraste `meio_pagamento_principal` e `regiao_cliente` da tabela `olist_amostra_aas`)*
```python
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
from statistics import NormalDist

plt.style.use('ggplot')
caminho = r"G:\Meu Drive\UFRGS\IA003\Trabalhos\Atividade Avaliativa Final — Probabilidade e Estatística para IA\olist_amostra_aas.csv"
df = pd.read_csv(caminho)

if 'meio_pagamento_principal' in dataset.columns:
    df = df[df['meio_pagamento_principal'].isin(dataset['meio_pagamento_principal'].dropna().unique())]
if 'regiao_cliente' in dataset.columns:
    df = df[df['regiao_cliente'].isin(dataset['regiao_cliente'].dropna().unique())]

dados = df['valor_total_pago'].dropna().to_numpy()
media, mediana = np.mean(dados), np.median(dados)
q1, q3 = np.percentile(dados, [25, 75])
iqr = q3 - q1

fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))

# 1. Distribuição da Amostra
axes[0].hist(dados[dados <= np.percentile(dados, 98)], bins=25, edgecolor='black', color='#E24A33', alpha=0.85, label='Frequência na Amostra')
axes[0].axvline(media, color='#348ABD', linestyle='--', linewidth=2.2, label=f'Média (x̄): R$ {media:.2f}')
axes[0].axvline(mediana, color='#2CA02C', linestyle='-', linewidth=2.2, label=f'Mediana: R$ {mediana:.2f}')
axes[0].set_title(f'1. Distribuição da Amostra (n = {len(dados)})', fontsize=10, fontweight='bold')
axes[0].set_xlabel('Valor Total Pago (R$)')
axes[0].set_ylabel('Qtd. de Pedidos')
axes[0].legend(loc='upper right', fontsize=8, frameon=True, facecolor='white')

# 2. Boxplot da Amostra com Legenda
axes[1].boxplot(
    dados, vert=False, patch_artist=True, showmeans=True,
    boxprops=dict(facecolor='#348ABD', alpha=0.75, edgecolor='black'),
    medianprops=dict(color='#2CA02C', linewidth=2.5),
    meanprops=dict(marker='D', markeredgecolor='black', markerfacecolor='#E24A33', markersize=6),
    flierprops=dict(marker='o', markerfacecolor='black', markersize=4, alpha=0.5)
)
axes[1].set_xlim(0, np.percentile(dados, 96))
axes[1].set_title('2. Boxplot da Amostra (Posição e Outliers)', fontsize=10, fontweight='bold')
axes[1].set_xlabel('Valor Total Pago (R$)')
axes[1].set_yticks([])

legenda_boxplot = [
    Patch(facecolor='#348ABD', edgecolor='black', alpha=0.75, label=f'Caixa (IQR = Q3-Q1): R$ {q1:.2f} a R$ {q3:.2f}'),
    Line2D([0], [0], color='#2CA02C', lw=2.5, label=f'Linha Verde (Mediana): R$ {mediana:.2f}'),
    Line2D([0], [0], marker='D', color='w', markerfacecolor='#E24A33', markeredgecolor='black', markersize=6, label=f'Losango (Média x̄): R$ {media:.2f}'),
    Line2D([0], [0], color='black', lw=1.2, label=f'Hastes: Limite 1,5x IQR (até R$ {q3 + 1.5*iqr:.2f})'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='black', markersize=5, label='Pontos Pretos: Outliers na Amostra')
]
axes[1].legend(handles=legenda_boxplot, loc='upper right', fontsize=7.5, frameon=True, facecolor='white')

# 3. QQ-Plot Normal da Amostra com Legenda
n = len(dados)
p = (np.arange(1, n + 1) - 0.5) / n
z_teorico = np.array([NormalDist().inv_cdf(prob) for prob in p])
q_obs = np.sort(dados)
incl = (q3 - q1) / (0.6745 - (-0.6745))
inter = q1 - incl * (-0.6745)

axes[2].scatter(z_teorico, q_obs, color='#348ABD', s=16, alpha=0.75, label='Pontos Azuis: Pedidos da Amostra (n=383)')
axes[2].plot(z_teorico, inter + incl * z_teorico, color='#E24A33', linewidth=2.2, label='Reta Vermelha: Distribuição Normal Ideal')
axes[2].plot([], [], ' ', label='Curva fora da reta = Assimétrica (Não-Normal)')
axes[2].set_title('3. QQ-Plot Normal (Amostra AAS)', fontsize=10, fontweight='bold')
axes[2].set_xlabel('Quantis Teóricos da Normal Padrão (Z)')
axes[2].set_ylabel('Quantis Observados na Amostra (R$)')
axes[2].legend(loc='upper left', fontsize=7.5, frameon=True, facecolor='white')

plt.tight_layout()
plt.show()
```

#### Código 3: Para o Visual `Py` do Painel 3 (Distribuição Amostral TCL + QQ-Plot das Médias)
```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from statistics import NormalDist

plt.style.use('ggplot')
caminho = r"G:\Meu Drive\UFRGS\IA003\Trabalhos\Atividade Avaliativa Final — Probabilidade e Estatística para IA\distribuicao_amostral_tcl.csv"
df = pd.read_csv(caminho)
medias = df['media_amostral_valor_pago'].dropna().to_numpy()
media_tcl, dp_tcl = np.mean(medias), np.std(medias, ddof=1)
q1, q3 = np.percentile(medias, [25, 75])

fig, axes = plt.subplots(1, 2, figsize=(13, 4.2))

# 1. Distribuição Amostral das Médias (Sino do TCL) + Curva Normal Teórica
axes[0].hist(medias, bins=30, density=True, edgecolor='black', color='#348ABD', alpha=0.8, label='1.000 Médias Amostrais (x̄ de n=383)')
x_eixo = np.linspace(min(medias), max(medias), 200)
y_normal = [NormalDist(media_tcl, dp_tcl).pdf(x) for x in x_eixo]
axes[0].plot(x_eixo, y_normal, color='#E24A33', linewidth=2.5, label=f'Curva Normal Teórica (Erro Padrão = R$ {dp_tcl:.2f})')
axes[0].axvline(159.60, color='black', linestyle='--', linewidth=2.2, label='Média Real População (µ = R$ 159,60)')
axes[0].axvline(166.11, color='#2CA02C', linestyle='-', linewidth=2.2, label='Nossa Amostra Sorteada (x̄ = R$ 166,11)')
axes[0].set_title('1. Distribuição Amostral da Média (Teorema Central do Limite)', fontsize=10, fontweight='bold')
axes[0].set_xlabel('Média Amostral do Valor Pago x̄ (R$)')
axes[0].set_ylabel('Densidade')
axes[0].legend(loc='upper right', fontsize=8, frameon=True, facecolor='white')

# 2. QQ-Plot da Distribuição Amostral com Legenda
n = len(medias)
p = (np.arange(1, n + 1) - 0.5) / n
z_teorico = np.array([NormalDist().inv_cdf(prob) for prob in p])
q_obs = np.sort(medias)
incl = (q3 - q1) / (0.6745 - (-0.6745))
inter = q1 - incl * (-0.6745)

axes[1].scatter(z_teorico, q_obs, color='#348ABD', s=14, alpha=0.75, label='Pontos Azuis: 1.000 Médias Amostrais (x̄)')
axes[1].plot(z_teorico, inter + incl * z_teorico, color='#E24A33', linewidth=2.2, label='Reta Vermelha: Distribuição Normal Ideal')
axes[1].plot([], [], ' ', label='Pontos sobre a reta = Normalidade Confirmada pelo TCL!')
axes[1].set_title('2. QQ-Plot das Médias Amostrais (Comprovação do TCL)', fontsize=10, fontweight='bold')
axes[1].set_xlabel('Quantis Teóricos da Normal Padrão (Z)')
axes[1].set_ylabel('Médias Amostrais x̄ (R$)')
axes[1].legend(loc='upper left', fontsize=8, frameon=True, facecolor='white')

plt.tight_layout()
plt.show()
```


---

## Etapa 8: Roteiro Cronometrado de 5 Minutos para o Vídeo + Checklist Final de Entrega

> **Dica de Gravação:** Grave a tela com o **Power BI Desktop** aberto em tela cheia (ou OBS Studio / gravador nativo do Windows `Win + G`) e o arquivo [`dashboard.py`](./dashboard.py) aberto em uma segunda janela caso queira mostrar rapidamente de onde vieram a semente aleatória (`semente_aleatoria = 42`) e a fórmula da Calculadora USP/Bauru.

### Bloco 1 (0:00 – 0:50) — Contexto da Base, População e Unidade Experimental
* **Tela:** `Painel 1 - População` no Power BI Desktop.
* **O que falar:**
  > *"Olá! Neste trabalho de Probabilidade e Estatística para IA, analisamos o ecossistema brasileiro de e-commerce utilizando a base pública da Olist no Kaggle. Originalmente, a base é dividida em 9 tabelas relacionais com 99.441 pedidos brutos. Em nosso pipeline em Python (`dashboard.py`), consolidamos os dados no grão de pedido único e aplicamos filtros de integridade — mantendo apenas pedidos efetivamente entregues e sem dados faltantes. Nossa **População de Estudo ($N$)** ficou definida em **95.808 pedidos entregues** entre 2016 e 2018, onde cada **unidade experimental** é um pedido único."*

### Bloco 2 (0:50 – 2:00) — Estatística Descritiva da População (Painel 1)
* **Tela:** `Painel 1 - População` (demonstrando o clique interativo em uma barra, ex.: `"Boleto"` ou `"Sudeste"`, e depois desmarcando).
* **O que falar:**
  > *"No **Painel 1**, analisamos os parâmetros reais da população ($N = 95.808$). Nas variáveis qualitativas, vemos que o **Cartão de Crédito** domina com **75,49%** dos pedidos, seguido pelo Boleto com 19,93%, e que a **Região Sudeste** concentra **68,59%** das compras. O painel é totalmente dinâmico: ao clicarmos em uma região ou meio de pagamento, a contagem e os gráficos abaixo filtram instantaneamente.*
  > *Nas variáveis quantitativas, o **Ticket Médio populacional ($\mu_1$)** é de **R$ 159,60**, enquanto a **Mediana** é de **R$ 105,28** (com desvio padrão $\sigma = \text{R\$ } 217,53$). No **Frete ($\mu_2$)**, a média é **R$ 22,76** e a mediana **R$ 17,16**. No trio de gráficos `ggplot`, o **Histograma** e o **Boxplot** mostram por que a média é maior que a mediana: há forte assimetria positiva à direita (assimetria de $9,24$), com muitos outliers acima do limite superior de $1,5 \times \text{IQR}$ (R$ 352,25). O **QQ-Plot Normal** confirma que a população original não segue distribuição Normal, pois os pontos azuis curvam fortemente para cima da reta vermelha."*

### Bloco 3 (2:00 – 3:05) — Dimensionamento Amostral e Amostra AAS (Painel 2)
* **Tela:** `Painel 2 - Amostra AAS (n = 383)`.
* **O que falar:**
  > *"Passando ao **Painel 2**, realizamos uma **Amostragem Aleatória Simples (AAS) sem reposição**. Para dimensionar o tamanho da amostra a partir de uma população finita de $N = 95.808$, aplicamos a fórmula da Calculadora de Tamanho Amostral da USP/Bauru com **95% de confiança ($Z = 1,96$)**, proporção conservadora máxima ($p = 50\%$) e **margem de erro de 5%**, resultando em **$n = 383$ pedidos**, sorteados no Python com semente fixa (`random_state = 42`) para total reprodutibilidade.*
  > *Mesmo analisando apenas 0,4% da base total, a amostra preservou fielmente a estrutura da população: a proporção de Cartão de Crédito na amostra ficou em **75,98%** (erro de apenas $+0,48$ ponto percentual) e a Região Sudeste ficou em **67,62%** (diferença de $-0,97$ p.p.). O ticket médio amostral ($\bar{x}_1$) foi de **R$ 166,11** (mediana R$ 106,21) e o frete médio ($\bar{x}_2$) foi de **R$ 23,12**, mantendo o mesmo perfil assimétrico no Histograma, Boxplot e QQ-Plot."*

### Bloco 4 (3:05 – 4:15) — Teorema Central do Limite (TCL) e Intervalos de Confiança (Painel 3)
* **Tela:** `Painel 3 - Inferência e Comparação` (apontando para o gráfico da Distribuição Amostral + QQ-Plot e para a Tabela de Inferência).
* **O que falar:**
  > *"No **Painel 3**, respondemos a uma pergunta fundamental: se os dados originais de e-commerce não são normais, por que podemos aplicar testes paramétricos Z e t? O gráfico superior demonstra o **Teorema Central do Limite (TCL)** na prática: sorteamos 1.000 amostras independentes de tamanho $n = 383$ e plotei a distribuição das médias amostrais ($\bar{x}$). A assimetria despenca de $9,24$ para $0,14$, formando um sino gaussiano perfeito centrado em R$ 159,43, e os pontos azuis no **QQ-Plot das Médias** colam exatamente sobre a reta vermelha!*
  > *Construímos então os **Intervalos de Confiança de 95%** a partir da nossa amostra de 383 pedidos, e nos 4 casos o parâmetro populacional verdadeiro caiu exatamente dentro da margem estimada: Cartão de Crédito entre **[71,70%; 80,26%]** (real: 75,49%), Região Sudeste entre **[62,94%; 72,31%]** (real: 68,59%), Valor Pago entre **[R$ 146,18; R$ 186,04]** (real: R$ 159,60) e Frete entre **[R$ 21,26; R$ 24,98]** (real: R$ 22,76)."*

### Bloco 5 (4:15 – 5:00) — Testes de Hipóteses ($\alpha = 5\%$) e Conclusão
* **Tela:** Tabela Mestra de Inferência no `Painel 3`.
* **O que falar:**
  > *"Por fim, executamos 4 **Testes de Hipóteses** com nível de significância $\alpha = 5\%$:*
  > *1. No **Teste Z unilateral para Cartão de Crédito** ($H_0: p = 0,70$ vs. $H_1: p > 0,70$), obtivemos $Z = +2,55$ e $p\text{-valor} = 0,0053 < 0,05$: **rejeitamos $H_0$**, comprovando que o cartão supera 70% das vendas.*
  > *2. No **Teste Z bilateral para Região Sudeste** ($H_0: p = 2/3$), obtivemos $Z = +0,40$ e $p\text{-valor} = 0,6910$: **não rejeitamos $H_0$**, logo a amostra é estatisticamente compatível com a concentração de dois terços no Sudeste.*
  > *3. No **Teste t bilateral para o Ticket Médio** ($H_0: \mu = \text{R\$ } 150$), obtivemos $t = +1,59$ e $p\text{-valor} = 0,1128$: **não rejeitamos $H_0$** ao nível de 5%.*
  > *4. E no **Teste t unilateral para o Frete Médio** ($H_0: \mu = \text{R\$ } 20$ vs. $H_1: \mu > \text{R\$ } 20$), obtivemos $t = +3,29$ e $p\text{-valor} = 0,0005$: **rejeitamos $H_0$**, confirmando que o custo médio de frete no Brasil supera R$ 20,00. Muito obrigado!"*

---

## Checklist Final de Entrega da Atividade Avaliativa

- [x] **Guia dos 20 Conceitos Teóricos (máx. 5 linhas cada):** [`conceitos_estatistica_probabilidade.txt`](./conceitos_estatistica_probabilidade.txt)
- [x] **Base Populacional Consolidada ($N = 95.808$):** [`olist_pedidos_consolidado.csv`](./olist_pedidos_consolidado.csv)
- [x] **Relatório Técnico de Consolidação e Validação:** [`relatorio_consolidacao_dados.md`](./relatorio_consolidacao_dados.md)
- [x] **Script Python Completo e Comentado em PT-BR:** [`dashboard.py`](./dashboard.py)
- [x] **Tabelas Auxiliares para Power BI:**
  - [`olist_amostra_aas.csv`](./olist_amostra_aas.csv) ($n = 383$)
  - [`resumo_qualitativas_pop_vs_amostra.csv`](./resumo_qualitativas_pop_vs_amostra.csv)
  - [`resumo_quantitativas_pop_vs_amostra.csv`](./resumo_quantitativas_pop_vs_amostra.csv)
  - [`resultados_inferencia_painel3.csv`](./resultados_inferencia_painel3.csv)
  - [`distribuicao_amostral_tcl.csv`](./distribuicao_amostral_tcl.csv)
  - [`dados_qqplot_powerbi.csv`](./dados_qqplot_powerbi.csv)
- [ ] **Painéis no Power BI Desktop (`.pbix`):**
  - [x] `Painel 1 - População` (Cartão + Gráficos de Barras Interativos + Trio `ggplot` com Legendas)
  - [ ] Tabela Descritiva no rodapé do `Painel 1 - População`
  - [ ] `Painel 2 - Amostra AAS (n = 383)`
  - [ ] `Painel 3 - Inferência e Comparação`
- [ ] **Gravação do Vídeo de 5 Minutos e Upload no YouTube (Não listado ou Público)**
