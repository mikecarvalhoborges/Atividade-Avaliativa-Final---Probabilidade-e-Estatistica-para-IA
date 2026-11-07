# ==============================================================================
# PROJETO FINAL — PROBABILIDADE E ESTATÍSTICA PARA IA (UFRGS - IA003)
# Base de Dados: Brazilian E-Commerce Public Dataset by Olist (Kaggle)
# Objetivo: Consolidação da População, Dimensionamento Amostral e Sorteio da
#           Amostra Aleatória Simples (AAS) para análise no Power BI.
# ==============================================================================

import math
import os
import sys
import pandas as pd
import numpy as np

# Garante que o terminal do Windows exiba acentos e caracteres especiais em UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ==============================================================================
# BLOCO 1: CONSOLIDAÇÃO E LIMPEZA DA POPULAÇÃO (ETAPA 1)
# ==============================================================================
def consolidar_populacao_olist(caminho_saida_csv: str = "olist_pedidos_consolidado.csv") -> pd.DataFrame:
    """
    Carrega a base consolidada da população caso já exista na pasta, ou realiza
    os 5 passos de unificação e limpeza a partir dos arquivos originais da Olist.
    Cada linha do DataFrame retornado representa exatamente 1 pedido único (Unidade Amostral).
    """
    # Se o arquivo consolidado já foi gerado anteriormente, apenas o carregamos
    if os.path.exists(caminho_saida_csv):
        print(f"[ETAPA 1] Carregando base populacional já consolidada: '{caminho_saida_csv}'...")
        dados_populacao = pd.read_csv(caminho_saida_csv)
        print(f"          População carregada com sucesso: N = {len(dados_populacao)} pedidos únicos.\n")
        return dados_populacao

    print("[ETAPA 1] Iniciando unificação das tabelas originais da Olist...")

    # Leitura das 6 tabelas originais necessárias
    tabela_pedidos = pd.read_csv("olist_orders_dataset.csv")
    tabela_clientes = pd.read_csv("olist_customers_dataset.csv")
    tabela_itens = pd.read_csv("olist_order_items_dataset.csv")
    tabela_pagamentos = pd.read_csv("olist_order_payments_dataset.csv")
    tabela_avaliacoes = pd.read_csv("olist_order_reviews_dataset.csv")
    tabela_produtos = pd.read_csv("olist_products_dataset.csv")

    # PASSO 1: Filtrar apenas pedidos com ciclo concluído (status 'delivered')
    pedidos_entregues = tabela_pedidos[tabela_pedidos["order_status"] == "delivered"].copy()

    # Conversão das colunas de data e hora para o tipo datetime
    colunas_datas = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for coluna in colunas_datas:
        pedidos_entregues[coluna] = pd.to_datetime(pedidos_entregues[coluna], errors="coerce")

    # Cálculo de variáveis derivadas de tempo logístico (em dias)
    pedidos_entregues["tempo_entrega_dias"] = (
        (pedidos_entregues["order_delivered_customer_date"] - pedidos_entregues["order_purchase_timestamp"])
        .dt.total_seconds() / (24 * 3600)
    ).round(2)

    pedidos_entregues["dias_diferenca_estimativa"] = (
        (pedidos_entregues["order_estimated_delivery_date"] - pedidos_entregues["order_delivered_customer_date"])
        .dt.total_seconds() / (24 * 3600)
    ).round(2)

    # Variável qualitativa indicando se houve atraso na entrega
    pedidos_entregues["entregue_com_atraso"] = pd.Series(
        np.where(
            pedidos_entregues["order_delivered_customer_date"] > pedidos_entregues["order_estimated_delivery_date"],
            "Sim",
            "Não",
        ),
        index=pedidos_entregues.index,
        dtype="object",
    )
    mascara_datas_nulas = (
        pedidos_entregues["order_delivered_customer_date"].isna()
        | pedidos_entregues["order_estimated_delivery_date"].isna()
    )
    pedidos_entregues.loc[mascara_datas_nulas, "entregue_com_atraso"] = np.nan

    # PASSO 2: Juntar com a tabela de Clientes (Relação 1:1 via customer_id)
    base_unificada = pedidos_entregues.merge(
        tabela_clientes[["customer_id", "customer_unique_id", "customer_city", "customer_state"]],
        on="customer_id",
        how="left",
    )

    # PASSO 3: Agrupar Itens e Produtos por pedido (Relação 1:N -> 1:1 via order_id)
    itens_com_categoria = tabela_itens.merge(
        tabela_produtos[["product_id", "product_category_name"]],
        on="product_id",
        how="left",
    )
    itens_agrupados_por_pedido = itens_com_categoria.groupby("order_id", as_index=False).agg(
        quantidade_itens=("order_item_id", "count"),
        valor_total_produtos=("price", "sum"),
        valor_medio_item=("price", "mean"),
        valor_total_frete=("freight_value", "sum"),
        categoria_produto_principal=("product_category_name", "first"),
    )
    itens_agrupados_por_pedido["valor_total_produtos"] = itens_agrupados_por_pedido["valor_total_produtos"].round(2)
    itens_agrupados_por_pedido["valor_medio_item"] = itens_agrupados_por_pedido["valor_medio_item"].round(2)
    itens_agrupados_por_pedido["valor_total_frete"] = itens_agrupados_por_pedido["valor_total_frete"].round(2)

    base_unificada = base_unificada.merge(itens_agrupados_por_pedido, on="order_id", how="left")

    # PASSO 4: Agrupar Pagamentos por pedido (Relação 1:N -> 1:1 via order_id)
    # Ordenamos pelo maior valor pago para identificar o meio de pagamento principal do pedido
    pagamentos_ordenados = tabela_pagamentos.sort_values(
        by=["order_id", "payment_value"], ascending=[True, False]
    )
    pagamentos_agrupados_por_pedido = pagamentos_ordenados.groupby("order_id", as_index=False).agg(
        valor_total_pago=("payment_value", "sum"),
        numero_parcelas=("payment_installments", "max"),
        quantidade_pagamentos=("payment_sequential", "count"),
        meio_pagamento_principal=("payment_type", "first"),
    )
    pagamentos_agrupados_por_pedido["valor_total_pago"] = pagamentos_agrupados_por_pedido["valor_total_pago"].round(2)

    traducao_meio_pagamento = {
        "credit_card": "Cartão de Crédito",
        "boleto": "Boleto",
        "voucher": "Voucher",
        "debit_card": "Cartão de Débito",
        "not_defined": "Não Definido",
    }
    pagamentos_agrupados_por_pedido["meio_pagamento_principal"] = (
        pagamentos_agrupados_por_pedido["meio_pagamento_principal"].map(traducao_meio_pagamento)
    )

    base_unificada = base_unificada.merge(pagamentos_agrupados_por_pedido, on="order_id", how="left")

    # PASSO 5: Agrupar Avaliações por pedido (Relação 1:N -> 1:1 via order_id)
    avaliacoes_agrupadas_por_pedido = tabela_avaliacoes.groupby("order_id", as_index=False).agg(
        nota_avaliacao=("review_score", "mean"),
        quantidade_avaliacoes=("review_id", "count"),
    )
    avaliacoes_agrupadas_por_pedido["nota_avaliacao"] = avaliacoes_agrupadas_por_pedido["nota_avaliacao"].round(2)
    avaliacoes_agrupadas_por_pedido["avaliacao_positiva"] = pd.Series(
        np.where(avaliacoes_agrupadas_por_pedido["nota_avaliacao"] >= 4, "Sim", "Não"),
        index=avaliacoes_agrupadas_por_pedido.index,
        dtype="object",
    )
    avaliacoes_agrupadas_por_pedido.loc[
        avaliacoes_agrupadas_por_pedido["nota_avaliacao"].isna(), "avaliacao_positiva"
    ] = np.nan

    base_unificada = base_unificada.merge(avaliacoes_agrupadas_por_pedido, on="order_id", how="left")

    # Mapeamento das Unidades Federativas (UF) para as 5 Macrorregiões do Brasil
    mapa_uf_para_regiao = {
        "SP": "Sudeste", "RJ": "Sudeste", "MG": "Sudeste", "ES": "Sudeste",
        "PR": "Sul", "SC": "Sul", "RS": "Sul",
        "MS": "Centro-Oeste", "MT": "Centro-Oeste", "GO": "Centro-Oeste", "DF": "Centro-Oeste",
        "BA": "Nordeste", "PE": "Nordeste", "CE": "Nordeste", "RN": "Nordeste", "PB": "Nordeste",
        "AL": "Nordeste", "SE": "Nordeste", "MA": "Nordeste", "PI": "Nordeste",
        "PA": "Norte", "AM": "Norte", "RO": "Norte", "TO": "Norte", "AC": "Norte", "AP": "Norte", "RR": "Norte",
    }
    base_unificada["regiao_cliente"] = base_unificada["customer_state"].map(mapa_uf_para_regiao)

    # Tradução de todos os nomes de colunas para Português (PT-BR)
    dicionario_colunas_ptbr = {
        "order_id": "id_pedido",
        "customer_id": "id_cliente_pedido",
        "customer_unique_id": "id_cliente_unico",
        "order_status": "status_pedido",
        "order_purchase_timestamp": "data_compra",
        "order_approved_at": "data_aprovacao",
        "order_delivered_carrier_date": "data_envio_transportadora",
        "order_delivered_customer_date": "data_entrega_cliente",
        "order_estimated_delivery_date": "data_estimada_entrega",
        "customer_city": "cidade_cliente",
        "customer_state": "uf_cliente",
        "regiao_cliente": "regiao_cliente",
        "quantidade_itens": "quantidade_itens",
        "valor_total_produtos": "valor_total_produtos",
        "valor_medio_item": "valor_medio_item",
        "valor_total_frete": "valor_total_frete",
        "categoria_produto_principal": "categoria_produto_principal",
        "valor_total_pago": "valor_total_pago",
        "numero_parcelas": "numero_parcelas",
        "quantidade_pagamentos": "quantidade_pagamentos",
        "meio_pagamento_principal": "meio_pagamento_principal",
        "nota_avaliacao": "nota_avaliacao",
        "quantidade_avaliacoes": "quantidade_avaliacoes",
        "avaliacao_positiva": "avaliacao_positiva",
        "tempo_entrega_dias": "tempo_entrega_dias",
        "dias_diferenca_estimativa": "dias_diferenca_estimativa",
        "entregue_com_atraso": "entregue_com_atraso",
    }

    base_unificada = base_unificada.rename(columns=dicionario_colunas_ptbr)
    base_unificada = base_unificada[list(dicionario_colunas_ptbr.values())]
    base_unificada["status_pedido"] = "Entregue"

    # Tratamento de valores nulos: preencher categorias sem rótulo e remover registros incompletos
    base_unificada["categoria_produto_principal"] = (
        base_unificada["categoria_produto_principal"].fillna("nao_informada")
    )
    dados_populacao_limpos = base_unificada.dropna().copy()

    # Garantir tipagem inteira para colunas de contagem
    colunas_inteiras = ["quantidade_itens", "numero_parcelas", "quantidade_pagamentos", "quantidade_avaliacoes"]
    for coluna in colunas_inteiras:
        dados_populacao_limpos[coluna] = dados_populacao_limpos[coluna].astype(int)

    dados_populacao_limpos.to_csv(caminho_saida_csv, index=False, encoding="utf-8-sig")
    print(f"[ETAPA 1] Arquivo consolidado salvo: '{caminho_saida_csv}' (N = {len(dados_populacao_limpos)} pedidos).\n")
    return dados_populacao_limpos


# ==============================================================================
# BLOCO 2: DIMENSIONAMENTO DO TAMANHO DA AMOSTRA (ETAPA 3 - PARTE A)
# ==============================================================================
def calcular_tamanho_amostral_proporcao(
    tamanho_populacao: int,
    nivel_confianca: float = 0.95,
    margem_erro: float = 0.05,
    proporcao_esperada: float = 0.50,
) -> int:
    """
    Calcula o tamanho necessário da amostra (n) para estimar uma proporção em uma
    população finita (mesma fórmula da Calculadora USP/Bauru):

        n = [ N * Z^2 * p * (1 - p) ] / [ (N - 1) * e^2 + Z^2 * p * (1 - p) ]

    Parâmetros:
        tamanho_populacao (N): Total de elementos da população (95.808 pedidos).
        nivel_confianca (1 - alpha): Grau de confiança desejado (padrão: 0.95 -> 95%).
        margem_erro (e): Erro máximo tolerado na estimativa (Opção B: 0.05 -> 5%).
        proporcao_esperada (p): Proporção conservadora que maximiza a variância (0.50 -> 50%).
    """
    # Mapeamento do Nível de Confiança para o valor crítico Z da Distribuição Normal Padrão
    tabela_valores_criticos_z = {
        0.90: 1.645,
        0.95: 1.960,
        0.99: 2.576,
    }
    valor_critico_z = tabela_valores_criticos_z.get(nivel_confianca, 1.960)

    # Numerador da fórmula: N * Z^2 * p * (1 - p)
    numerador = (
        tamanho_populacao
        * (valor_critico_z ** 2)
        * proporcao_esperada
        * (1.0 - proporcao_esperada)
    )

    # Denominador da fórmula: (N - 1) * e^2 + Z^2 * p * (1 - p)
    denominador = (
        (tamanho_populacao - 1) * (margem_erro ** 2)
        + (valor_critico_z ** 2) * proporcao_esperada * (1.0 - proporcao_esperada)
    )

    # Resultado exato em ponto flutuante e arredondamento para cima (math.ceil)
    # Em estatística, sempre arredondamos o tamanho amostral para o inteiro superior
    # para garantir que a margem de erro máxima nunca seja ultrapassada.
    tamanho_amostra_exato = numerador / denominador
    tamanho_amostra_final = math.ceil(tamanho_amostra_exato)

    print("=" * 78)
    print("[ETAPA 3 - A] DIMENSIONAMENTO AMOSTRAL (CALCULADORA USP/BAURU)")
    print("=" * 78)
    print(f"  • Tamanho da População (N)       : {tamanho_populacao:,} pedidos")
    print(f"  • Nível de Confiança (1 - α)     : {nivel_confianca * 100:.0f}% (Z = {valor_critico_z})")
    print(f"  • Proporção Conservadora (p)     : {proporcao_esperada * 100:.0f}% (maximiza p*(1-p) = 0.25)")
    print(f"  • Margem de Erro Máxima (e)      : {margem_erro * 100:.1f}% ({margem_erro})")
    print(f"  • Cálculo Exato da Fórmula       : n = {tamanho_amostra_exato:.4f}")
    print(f"  • Tamanho Amostral Adotado (n)   : {tamanho_amostra_final} pedidos")
    print("=" * 78 + "\n")

    return tamanho_amostra_final


# ==============================================================================
# BLOCO 3: SELEÇÃO DA AMOSTRA ALEATÓRIA SIMPLES - AAS (ETAPA 3 - PARTE B)
# ==============================================================================
def selecionar_amostra_aleatoria_simples(
    dados_populacao: pd.DataFrame,
    tamanho_amostra: int,
    semente_aleatoria: int = 42,
    caminho_saida_amostra_csv: str = "olist_amostra_aas.csv",
) -> pd.DataFrame:
    """
    Realiza o sorteio de uma Amostra Aleatória Simples (AAS) sem reposição a partir
    da população consolidada, garantindo que cada pedido tenha exatamente a mesma
    probabilidade de ser selecionado (1 / N).

    Parâmetros:
        dados_populacao: DataFrame completo com os 95.808 pedidos da população.
        tamanho_amostra (n): Quantidade de pedidos a serem sorteados (1.056).
        semente_aleatoria (seed): Valor fixo para garantir reprodutibilidade científica.
        caminho_saida_amostra_csv: Nome do arquivo CSV onde a amostra será salva.
    """
    tamanho_populacao = len(dados_populacao)
    probabilidade_individual = (1.0 / tamanho_populacao) * 100
    probabilidade_inclusao_amostra = (tamanho_amostra / tamanho_populacao) * 100

    # O método .sample(n=..., replace=False, random_state=...) realiza o sorteio
    # pseudoaleatório uniforme sem reposição (Amostragem Aleatória Simples - AAS)
    dados_amostra = dados_populacao.sample(
        n=tamanho_amostra,
        replace=False,
        random_state=semente_aleatoria,
    ).copy()

    # Salvamos a amostra em um arquivo CSV na pasta do projeto para uso no Power BI (Painel 2 e 3)
    dados_amostra.to_csv(caminho_saida_amostra_csv, index=False, encoding="utf-8-sig")

    print("=" * 78)
    print("[ETAPA 3 - B] SORTEIO DA AMOSTRA ALEATÓRIA SIMPLES (AAS)")
    print("=" * 78)
    print(f"  • Método de Seleção              : Sorteio Aleatório Simples sem reposição")
    print(f"  • Semente Aleatória (Seed)       : {semente_aleatoria} (garante reprodutibilidade)")
    print(f"  • Probabilidade de cada pedido   : 1/{tamanho_populacao} ({probabilidade_individual:.6f}% por sorteio)")
    print(f"  • Fração de Amostragem (n / N)   : {probabilidade_inclusao_amostra:.2f}% da população")
    print(f"  • Pedidos Únicos na Amostra      : {dados_amostra['id_pedido'].nunique()} (sem duplicatas)")
    print(f"  • Arquivo salvo para o Power BI  : '{caminho_saida_amostra_csv}'")
    print("=" * 78 + "\n")

    return dados_amostra


# ==============================================================================
# BLOCO 4: ESTATÍSTICA DESCRITIVA — POPULAÇÃO VS. AMOSTRA (ETAPA 4)
# ==============================================================================
def gerar_resumo_qualitativo_populacao_vs_amostra(
    dados_populacao: pd.DataFrame,
    dados_amostra: pd.DataFrame,
    lista_variaveis_qualitativas: list,
    caminho_saida_csv: str = "resumo_qualitativas_pop_vs_amostra.csv",
) -> pd.DataFrame:
    """
    Calcula as frequências absolutas (contagem de pedidos) e as frequências relativas
    (proporções em %) para todas as categorias das variáveis qualitativas escolhidas
    (Q1: meio_pagamento_principal e Q4: regiao_cliente), comparando lado a lado
    os parâmetros da População (N) e as estimativas da Amostra (n).
    """
    linhas_resumo = []

    for nome_variavel in lista_variaveis_qualitativas:
        # Frequência absoluta e proporção (%) na População
        contagem_populacao = dados_populacao[nome_variavel].value_counts()
        proporcao_populacao = dados_populacao[nome_variavel].value_counts(normalize=True) * 100

        # Frequência absoluta e proporção (%) na Amostra
        contagem_amostra = dados_amostra[nome_variavel].value_counts()
        proporcao_amostra = dados_amostra[nome_variavel].value_counts(normalize=True) * 100

        # Percorre cada categoria da variável qualitativa
        for categoria in contagem_populacao.index:
            freq_abs_pop = int(contagem_populacao.get(categoria, 0))
            prop_pop = float(proporcao_populacao.get(categoria, 0.0))

            freq_abs_amo = int(contagem_amostra.get(categoria, 0))
            prop_amo = float(proporcao_amostra.get(categoria, 0.0))

            diferenca_pontos_percentuais = prop_amo - prop_pop

            linhas_resumo.append({
                "variavel_qualitativa": nome_variavel,
                "categoria": categoria,
                "frequencia_populacao_N": freq_abs_pop,
                "proporcao_populacao_pct": round(prop_pop, 2),
                "frequencia_amostra_n": freq_abs_amo,
                "proporcao_amostra_pct": round(prop_amo, 2),
                "diferenca_amostra_vs_pop_pp": round(diferenca_pontos_percentuais, 2),
            })

    tabela_resumo_qualitativo = pd.DataFrame(linhas_resumo)
    tabela_resumo_qualitativo.to_csv(caminho_saida_csv, index=False, encoding="utf-8-sig")

    print("=" * 78)
    print("[ETAPA 4 - A] DISTRIBUIÇÃO DE FREQUÊNCIAS (VARIÁVEIS QUALITATIVAS: Q1 e Q4)")
    print("=" * 78)
    print(tabela_resumo_qualitativo.to_string(index=False))
    print(f"\n  • Arquivo salvo para o Power BI: '{caminho_saida_csv}'")
    print("=" * 78 + "\n")

    return tabela_resumo_qualitativo


def gerar_resumo_quantitativo_populacao_vs_amostra(
    dados_populacao: pd.DataFrame,
    dados_amostra: pd.DataFrame,
    lista_variaveis_quantitativas: list,
    caminho_saida_csv: str = "resumo_quantitativas_pop_vs_amostra.csv",
) -> pd.DataFrame:
    """
    Calcula todas as medidas descritivas de posição, tendência central, dispersão
    e forma para as variáveis quantitativas escolhidas (M1: valor_total_pago e
    M3: valor_total_frete), tanto para a População (N) quanto para a Amostra (n).

    Medidas calculadas:
        • Média (tendência central sensível a valores extremos)
        • Mediana / 2º Quartil (tendência central robusta a outliers)
        • Desvio-Padrão e Variância (dispersão absoluta)
        • Coeficiente de Variação - CV% (dispersão relativa = Desvio-Padrão / Média)
        • 1º Quartil (Q1 - 25%) e 3º Quartil (Q3 - 75%)
        • Amplitude Interquartil (IQR = Q3 - Q1, dispersão dos 50% centrais)
        • Mínimo e Máximo
        • Assimetria / Skewness (> 0 indica cauda longa à direita, comum em preços)
    """
    linhas_resumo = []

    for nome_variavel in lista_variaveis_quantitativas:
        for nome_grupo, dataframe_atual, grau_liberdade_ddof in [
            ("População (N = 95.808)", dados_populacao, 0),
            ("Amostra AAS (n = 383)", dados_amostra, 1),
        ]:
            serie = dataframe_atual[nome_variavel].dropna()

            media = float(serie.mean())
            mediana = float(serie.median())
            # Na população usamos ddof=0 (divisão por N); na amostra usamos ddof=1 (divisão por n-1)
            desvio_padrao = float(serie.std(ddof=grau_liberdade_ddof))
            variancia = float(serie.var(ddof=grau_liberdade_ddof))
            coeficiente_variacao_pct = (desvio_padrao / media) * 100 if media != 0 else 0.0

            quartil_1 = float(serie.quantile(0.25))
            quartil_3 = float(serie.quantile(0.75))
            amplitude_interquartil_iqr = quartil_3 - quartil_1

            valor_minimo = float(serie.min())
            valor_maximo = float(serie.max())
            assimetria_skewness = float(serie.skew())

            linhas_resumo.append({
                "variavel_quantitativa": nome_variavel,
                "conjunto_dados": nome_grupo,
                "quantidade_observacoes": int(len(serie)),
                "media": round(media, 2),
                "mediana": round(mediana, 2),
                "desvio_padrao": round(desvio_padrao, 2),
                "variancia": round(variancia, 2),
                "coeficiente_variacao_pct": round(coeficiente_variacao_pct, 2),
                "quartil_1_25pct": round(quartil_1, 2),
                "quartil_3_75pct": round(quartil_3, 2),
                "amplitude_interquartil_iqr": round(amplitude_interquartil_iqr, 2),
                "minimo": round(valor_minimo, 2),
                "maximo": round(valor_maximo, 2),
                "assimetria_skewness": round(assimetria_skewness, 2),
            })

    tabela_resumo_quantitativo = pd.DataFrame(linhas_resumo)
    tabela_resumo_quantitativo.to_csv(caminho_saida_csv, index=False, encoding="utf-8-sig")

    print("=" * 78)
    print("[ETAPA 4 - B] MEDIDAS DESCRITIVAS (VARIÁVEIS QUANTITATIVAS: M1 e M3)")
    print("=" * 78)
    print(tabela_resumo_quantitativo.to_string(index=False))
    print(f"\n  • Arquivo salvo para o Power BI: '{caminho_saida_csv}'")
    print("=" * 78 + "\n")

    return tabela_resumo_quantitativo


# ==============================================================================
# BLOCO 5: INFERÊNCIA ESTATÍSTICA — INTERVALOS DE CONFIANÇA E TESTES DE HIPÓTESES
#          (ETAPA 5 — DADOS PARA O PAINEL 3 DO POWER BI)
# ==============================================================================
def _cdf_normal_padrao(valor_z: float) -> float:
    """
    Calcula a probabilidade acumulada P(Z <= valor_z) da Distribuição Normal Padrão N(0, 1)
    utilizando a função erro matemática exata (math.erf).
    """
    return 0.5 * (1.0 + math.erf(valor_z / math.sqrt(2.0)))


def _cdf_t_student(valor_t: float, graus_liberdade: int) -> float:
    """
    Calcula a probabilidade acumulada P(T <= valor_t) da Distribuição t de Student
    com 'graus_liberdade' (gl = n - 1), utilizando integração numérica de Simpson
    de alta precisão sobre a função densidade de probabilidade exata de Student.
    """
    if valor_t == 0.0:
        return 0.5

    # Constante de normalização da densidade t de Student usando log-gamma (evita overflow)
    gl = float(graus_liberdade)
    log_constante = (
        math.lgamma((gl + 1.0) / 2.0)
        - 0.5 * math.log(gl * math.pi)
        - math.lgamma(gl / 2.0)
    )

    def densidade_t(x: float) -> float:
        return math.exp(log_constante - ((gl + 1.0) / 2.0) * math.log(1.0 + (x * x) / gl))

    # Integração de 0 até |valor_t| pela Regra de Simpson Composta (2.000 subintervalos)
    limite_superior = min(abs(valor_t), 25.0)
    numero_passos = 2000
    passo_h = limite_superior / numero_passos
    soma_simpson = densidade_t(0.0) + densidade_t(limite_superior)

    for indice in range(1, numero_passos):
        ponto_x = indice * passo_h
        peso = 4.0 if indice % 2 == 1 else 2.0
        soma_simpson += peso * densidade_t(ponto_x)

    area_central_metade = (passo_h / 3.0) * soma_simpson
    probabilidade_acumulada = 0.5 + area_central_metade if valor_t > 0 else 0.5 - area_central_metade
    return max(0.0, min(1.0, probabilidade_acumulada))


def _valor_critico_t_bicaudal(nivel_confianca: float, graus_liberdade: int) -> float:
    """
    Encontra o valor crítico t_(alpha/2, gl) tal que P(-t <= T <= +t) = nivel_confianca
    utilizando busca binária (bisseção) de alta precisão.
    """
    probabilidade_alvo_cauda_superior = 1.0 - (1.0 - nivel_confianca) / 2.0
    limite_inferior, limite_superior = 0.0, 10.0

    for _ in range(80):
        ponto_medio = (limite_inferior + limite_superior) / 2.0
        if _cdf_t_student(ponto_medio, graus_liberdade) < probabilidade_alvo_cauda_superior:
            limite_inferior = ponto_medio
        else:
            limite_superior = ponto_medio

    return (limite_inferior + limite_superior) / 2.0


def _calcular_valor_p(estatistica_teste: float, tipo_teste: str, distribuicao: str, graus_liberdade: int = 0) -> float:
    """
    Calcula o valor-p (p-value) de acordo com a direção da Hipótese Alternativa (H1):
        • 'unicaudal_direita' (H1: parametro > valor_ref) -> P(Estatistica >= valor_observado)
        • 'unicaudal_esquerda'(H1: parametro < valor_ref) -> P(Estatistica <= valor_observado)
        • 'bicaudal'          (H1: parametro != valor_ref)-> 2 * P(Estatistica >= |valor_observado|)
    """
    if distribuicao == "z":
        prob_acumulada = _cdf_normal_padrao(estatistica_teste)
        prob_cauda_direita = 1.0 - _cdf_normal_padrao(abs(estatistica_teste))
    else:
        prob_acumulada = _cdf_t_student(estatistica_teste, graus_liberdade)
        prob_cauda_direita = 1.0 - _cdf_t_student(abs(estatistica_teste), graus_liberdade)

    if tipo_teste == "unicaudal_direita":
        return 1.0 - prob_acumulada
    elif tipo_teste == "unicaudal_esquerda":
        return prob_acumulada
    else:  # bicaudal
        return 2.0 * prob_cauda_direita


def realizar_inferencia_proporcao_e_media(
    dados_populacao: pd.DataFrame,
    dados_amostra: pd.DataFrame,
    nivel_confianca: float = 0.95,
    nivel_significancia: float = 0.05,
    caminho_saida_csv: str = "resultados_inferencia_painel3.csv",
) -> pd.DataFrame:
    """
    Executa toda a Inferência Estatística exigida no Painel 3 do projeto:
        a) Duas análises inferenciais para parâmetros de PROPORÇÃO (Q1 e Q4) via distribuição Z:
           - Intervalo de Confiança de 95% para a proporção populacional (p)
           - Teste de Hipóteses para a proporção (estatística Z_calc e valor-p)
           - Verificação das condições de aplicação (n * p_hat >= 10 e n * (1 - p_hat) >= 10)
        b) Duas análises inferenciais para parâmetros de MÉDIA (M1 e M3) via distribuição t de Student:
           - Intervalo de Confiança de 95% para a média populacional (mu)
           - Teste de Hipóteses para a média (estatística t_calc e valor-p)
           - Verificação das condições de aplicação (Teorema Central do Limite: n >= 30)
        c) Comparação direta com os verdadeiros parâmetros da População (N = 95.808).
    """
    tamanho_amostra = len(dados_amostra)
    graus_liberdade = tamanho_amostra - 1
    valor_critico_z = 1.960  # Para 95% de confiança na distribuição Normal Padrão
    valor_critico_t = _valor_critico_t_bicaudal(nivel_confianca, graus_liberdade)

    resultados_inferencia = []

    # --------------------------------------------------------------------------
    # PARTE A: INFERÊNCIA PARA OS 2 PARÂMETROS DE PROPORÇÃO (Q1 e Q4)
    # --------------------------------------------------------------------------
    configuracoes_proporcao = [
        {
            "codigo_analise": "Proporção 1 (Q1)",
            "variavel": "meio_pagamento_principal",
            "evento_interesse": "Pagamento via Cartão de Crédito",
            "categoria_sucesso": "Cartão de Crédito",
            "hipotese_nula_H0": "p = 0,70 (70,00%)",
            "hipotese_alternativa_H1": "p > 0,70 (Unicaudal à Direita)",
            "valor_referencia_H0": 0.70,
            "tipo_teste": "unicaudal_direita",
            "pergunta_negocio": "Mais de 70% dos pedidos do e-commerce são pagos com Cartão de Crédito?",
        },
        {
            "codigo_analise": "Proporção 2 (Q4)",
            "variavel": "regiao_cliente",
            "evento_interesse": "Comprador da Região Sudeste",
            "categoria_sucesso": "Sudeste",
            "hipotese_nula_H0": "p = 0,6667 (66,67% / dois terços)",
            "hipotese_alternativa_H1": "p != 0,6667 (Bicaudal)",
            "valor_referencia_H0": 2.0 / 3.0,
            "tipo_teste": "bicaudal",
            "pergunta_negocio": "A proporção de pedidos da região Sudeste difere de dois terços (66,67%)?",
        },
    ]

    for config in configuracoes_proporcao:
        variavel = config["variavel"]
        categoria = config["categoria_sucesso"]
        p0 = config["valor_referencia_H0"]

        # Parâmetro real na População (p) e Estimativa Pontual na Amostra (p_hat)
        parametro_populacional_p = float((dados_populacao[variavel] == categoria).mean())
        estimativa_amostral_p_hat = float((dados_amostra[variavel] == categoria).mean())

        # Condições de aplicação para proporção: n * p_hat >= 10 e n * (1 - p_hat) >= 10
        sucessos_amostra = int((dados_amostra[variavel] == categoria).sum())
        fracassos_amostra = tamanho_amostra - sucessos_amostra
        condicao_aplicacao = (
            f"AAS atendida; n*p̂ = {sucessos_amostra} >= 10 e n*(1-p̂) = {fracassos_amostra} >= 10 (Aproximação Normal válida)"
        )

        # Intervalo de Confiança para a Proporção: p_hat +- Z_(alpha/2) * sqrt(p_hat * (1 - p_hat) / n)
        erro_padrao_ic = math.sqrt((estimativa_amostral_p_hat * (1.0 - estimativa_amostral_p_hat)) / tamanho_amostra)
        margem_erro_ic = valor_critico_z * erro_padrao_ic
        limite_inferior_ic = estimativa_amostral_p_hat - margem_erro_ic
        limite_superior_ic = estimativa_amostral_p_hat + margem_erro_ic

        # Teste de Hipótese para a Proporção: Z_calc = (p_hat - p0) / sqrt(p0 * (1 - p0) / n)
        erro_padrao_hipotese_nula = math.sqrt((p0 * (1.0 - p0)) / tamanho_amostra)
        estatistica_z_calculada = (estimativa_amostral_p_hat - p0) / erro_padrao_hipotese_nula
        valor_p = _calcular_valor_p(estatistica_z_calculada, config["tipo_teste"], distribuicao="z")

        decisao_teste = "Rejeita H0" if valor_p <= nivel_significancia else "Não Rejeita H0"
        parametro_dentro_ic = "Sim" if (limite_inferior_ic <= parametro_populacional_p <= limite_superior_ic) else "Não"

        if decisao_teste == "Rejeita H0":
            conclusao_interpretacao = (
                f"Como valor-p ({valor_p:.4f}) <= α ({nivel_significancia}), rejeita-se H0. "
                f"Há evidência estatística significativa de que {config['hipotese_alternativa_H1']}. "
                f"O parâmetro populacional real ({parametro_populacional_p*100:.2f}%) confirma a conclusão e está dentro do IC 95%."
            )
        else:
            conclusao_interpretacao = (
                f"Como valor-p ({valor_p:.4f}) > α ({nivel_significancia}), não se rejeita H0. "
                f"A diferença amostral observada é compatível com a flutuação aleatória do sorteio. "
                f"O parâmetro populacional real ({parametro_populacional_p*100:.2f}%) foi capturado pelo IC 95%."
            )

        resultados_inferencia.append({
            "codigo_analise": config["codigo_analise"],
            "tipo_parametro": "Proporção (p - %)",
            "variavel": variavel,
            "evento_ou_unidade": config["evento_interesse"],
            "pergunta_negocio": config["pergunta_negocio"],
            "hipotese_nula_H0": config["hipotese_nula_H0"],
            "hipotese_alternativa_H1": config["hipotese_alternativa_H1"],
            "tipo_teste": config["tipo_teste"],
            "tamanho_amostra_n": tamanho_amostra,
            "parametro_populacional_real": round(parametro_populacional_p * 100, 2),
            "estimativa_pontual_amostra": round(estimativa_amostral_p_hat * 100, 2),
            "erro_amostral_absoluto": round((estimativa_amostral_p_hat - parametro_populacional_p) * 100, 2),
            "erro_padrao_amostral": round(erro_padrao_ic * 100, 2),
            "nivel_confianca_pct": round(nivel_confianca * 100, 0),
            "valor_critico_ic": round(valor_critico_z, 4),
            "margem_erro_ic": round(margem_erro_ic * 100, 2),
            "ic_95_limite_inferior": round(limite_inferior_ic * 100, 2),
            "ic_95_limite_superior": round(limite_superior_ic * 100, 2),
            "parametro_pop_dentro_do_ic": parametro_dentro_ic,
            "distribuicao_teste": "Normal Padrão (Z)",
            "estatistica_teste_calculada": round(estatistica_z_calculada, 4),
            "nivel_significancia_alpha": nivel_significancia,
            "valor_p": round(valor_p, 4),
            "decisao_teste_hipotese": decisao_teste,
            "condicoes_aplicacao": condicao_aplicacao,
            "conclusao_interpretacao": conclusao_interpretacao,
        })

    # --------------------------------------------------------------------------
    # PARTE B: INFERÊNCIA PARA OS 2 PARÂMETROS DE MÉDIA (M1 e M3)
    # --------------------------------------------------------------------------
    configuracoes_media = [
        {
            "codigo_analise": "Média 1 (M1)",
            "variavel": "valor_total_pago",
            "evento_interesse": "Ticket Médio por Pedido (R$)",
            "hipotese_nula_H0": "µ = R$ 150,00",
            "hipotese_alternativa_H1": "µ != R$ 150,00 (Bicaudal)",
            "valor_referencia_H0": 150.00,
            "tipo_teste": "bicaudal",
            "pergunta_negocio": "O ticket médio dos pedidos difere estatisticamente da referência comercial de R$ 150,00?",
        },
        {
            "codigo_analise": "Média 2 (M3)",
            "variavel": "valor_total_frete",
            "evento_interesse": "Valor Médio de Frete por Pedido (R$)",
            "hipotese_nula_H0": "µ = R$ 20,00",
            "hipotese_alternativa_H1": "µ > R$ 20,00 (Unicaudal à Direita)",
            "valor_referencia_H0": 20.00,
            "tipo_teste": "unicaudal_direita",
            "pergunta_negocio": "O custo médio do frete por pedido ultrapassa significativamente o valor de R$ 20,00?",
        },
    ]

    for config in configuracoes_media:
        variavel = config["variavel"]
        mu0 = config["valor_referencia_H0"]

        # Parâmetro real na População (mu) e Estimativa Pontual na Amostra (x_barra)
        parametro_populacional_mu = float(dados_populacao[variavel].mean())
        estimativa_amostral_x_barra = float(dados_amostra[variavel].mean())
        desvio_padrao_amostral_s = float(dados_amostra[variavel].std(ddof=1))

        # Condições de aplicação para média: Amostra Aleatória Simples e n = 383 >= 30 (TCL)
        condicao_aplicacao = (
            f"AAS atendida; n = {tamanho_amostra} >= 30 (Teorema Central do Limite garante normalidade de x̄; gl = {graus_liberdade})"
        )

        # Intervalo de Confiança t de Student para a Média: x_barra +- t_(alpha/2, n-1) * (s / sqrt(n))
        erro_padrao_media = desvio_padrao_amostral_s / math.sqrt(tamanho_amostra)
        margem_erro_ic = valor_critico_t * erro_padrao_media
        limite_inferior_ic = estimativa_amostral_x_barra - margem_erro_ic
        limite_superior_ic = estimativa_amostral_x_barra + margem_erro_ic

        # Teste de Hipótese t de Student para a Média: t_calc = (x_barra - mu0) / (s / sqrt(n))
        estatistica_t_calculada = (estimativa_amostral_x_barra - mu0) / erro_padrao_media
        valor_p = _calcular_valor_p(
            estatistica_t_calculada,
            config["tipo_teste"],
            distribuicao="t",
            graus_liberdade=graus_liberdade,
        )

        decisao_teste = "Rejeita H0" if valor_p <= nivel_significancia else "Não Rejeita H0"
        parametro_dentro_ic = "Sim" if (limite_inferior_ic <= parametro_populacional_mu <= limite_superior_ic) else "Não"

        if decisao_teste == "Rejeita H0":
            conclusao_interpretacao = (
                f"Como valor-p ({valor_p:.4f}) <= α ({nivel_significancia}), rejeita-se H0. "
                f"Há forte evidência amostral de que {config['hipotese_alternativa_H1']}. "
                f"A média real da população (R$ {parametro_populacional_mu:.2f}) confirma o teste e está dentro do IC 95%."
            )
        else:
            conclusao_interpretacao = (
                f"Como valor-p ({valor_p:.4f}) > α ({nivel_significancia}), não se rejeita H0. "
                f"Devido à alta dispersão dos preços (s = R$ {desvio_padrao_amostral_s:.2f}), o IC 95% (R$ {limite_inferior_ic:.2f} a R$ {limite_superior_ic:.2f}) "
                f"inclui tanto R$ {mu0:.2f} quanto a média real da população (R$ {parametro_populacional_mu:.2f})."
            )

        resultados_inferencia.append({
            "codigo_analise": config["codigo_analise"],
            "tipo_parametro": "Média (µ - R$)",
            "variavel": variavel,
            "evento_ou_unidade": config["evento_interesse"],
            "pergunta_negocio": config["pergunta_negocio"],
            "hipotese_nula_H0": config["hipotese_nula_H0"],
            "hipotese_alternativa_H1": config["hipotese_alternativa_H1"],
            "tipo_teste": config["tipo_teste"],
            "tamanho_amostra_n": tamanho_amostra,
            "parametro_populacional_real": round(parametro_populacional_mu, 2),
            "estimativa_pontual_amostra": round(estimativa_amostral_x_barra, 2),
            "erro_amostral_absoluto": round(estimativa_amostral_x_barra - parametro_populacional_mu, 2),
            "erro_padrao_amostral": round(erro_padrao_media, 2),
            "nivel_confianca_pct": round(nivel_confianca * 100, 0),
            "valor_critico_ic": round(valor_critico_t, 4),
            "margem_erro_ic": round(margem_erro_ic, 2),
            "ic_95_limite_inferior": round(limite_inferior_ic, 2),
            "ic_95_limite_superior": round(limite_superior_ic, 2),
            "parametro_pop_dentro_do_ic": parametro_dentro_ic,
            "distribuicao_teste": f"t de Student (gl = {graus_liberdade})",
            "estatistica_teste_calculada": round(estatistica_t_calculada, 4),
            "nivel_significancia_alpha": nivel_significancia,
            "valor_p": round(valor_p, 4),
            "decisao_teste_hipotese": decisao_teste,
            "condicoes_aplicacao": condicao_aplicacao,
            "conclusao_interpretacao": conclusao_interpretacao,
        })

    tabela_inferencia = pd.DataFrame(resultados_inferencia)
    tabela_inferencia.to_csv(caminho_saida_csv, index=False, encoding="utf-8-sig")

    print("=" * 78)
    print("[ETAPA 5] INFERÊNCIA ESTATÍSTICA: INTERVALOS DE CONFIANÇA E TESTES DE HIPÓTESES")
    print("=" * 78)
    for linha in resultados_inferencia:
        unidade_simbolo = "%" if "Proporção" in linha["tipo_parametro"] else "R$"
        print(f"► {linha['codigo_analise']} — {linha['evento_ou_unidade']} ('{linha['variavel']}')")
        print(f"  • Pergunta       : {linha['pergunta_negocio']}")
        print(f"  • Hipóteses      : H0: {linha['hipotese_nula_H0']}  vs.  H1: {linha['hipotese_alternativa_H1']}")
        print(f"  • População Real : {linha['parametro_populacional_real']:.2f} ({unidade_simbolo}) | Estimativa Amostral: {linha['estimativa_pontual_amostra']:.2f} ({unidade_simbolo})")
        print(f"  • IC 95%         : [{linha['ic_95_limite_inferior']:.2f} ; {linha['ic_95_limite_superior']:.2f}] (Margem de Erro: ±{linha['margem_erro_ic']:.2f} | Capturou População? {linha['parametro_pop_dentro_do_ic']})")
        print(f"  • Teste (α=0.05) : {linha['distribuicao_teste']} | Estatística = {linha['estatistica_teste_calculada']:+.4f} | valor-p = {linha['valor_p']:.4f} -> [{linha['decisao_teste_hipotese']}]")
        print(f"  • Pressupostos   : {linha['condicoes_aplicacao']}")
        print(f"  • Conclusão      : {linha['conclusao_interpretacao']}\n")

    print(f"  • Arquivo salvo para o Power BI (Painel 3): '{caminho_saida_csv}'")
    print("=" * 78 + "\n")

    return tabela_inferencia


# ==============================================================================
# BLOCO 6: DISTRIBUIÇÃO AMOSTRAL (TCL) E COORDENADAS DO QQ-PLOT PARA O POWER BI
# ==============================================================================
def _inversa_normal_padrao(probabilidade_p: float) -> float:
    """
    Calcula o quantil teórico z tal que P(Z <= z) = probabilidade_p na Distribuição
    Normal Padrão N(0, 1), utilizando busca binária sobre _cdf_normal_padrao.
    Usado para construir os quantis teóricos exatos do gráfico QQ-Plot.
    """
    limite_inferior, limite_superior = -5.0, 5.0
    for _ in range(60):
        ponto_medio = (limite_inferior + limite_superior) / 2.0
        if _cdf_normal_padrao(ponto_medio) < probabilidade_p:
            limite_inferior = ponto_medio
        else:
            limite_superior = ponto_medio
    return (limite_inferior + limite_superior) / 2.0


def simular_distribuicao_amostral_tcl(
    dados_populacao: pd.DataFrame,
    tamanho_amostra: int = 383,
    numero_simulacoes: int = 1000,
    semente_aleatoria: int = 2026,
    caminho_saida_csv: str = "distribuicao_amostral_tcl.csv",
) -> pd.DataFrame:
    """
    Simula a Distribuição Amostral das Médias (x̄) e das Proporções (p̂) sorteando
    'numero_simulacoes' (1.000) amostras aleatórias simples de tamanho 'tamanho_amostra' (n = 383)
    a partir da População (N = 95.808), demonstrando empiricamente o Teorema Central do Limite (TCL).

    Como os dados brutos de 'valor_total_pago' e 'valor_total_frete' são fortemente
    assimétricos à direita na População e na Amostra, esta tabela permite plotar
    dentro do Power BI a distribuição das médias amostrais (que assume formato de
    Sino Normal simétrico centrado na verdadeira média populacional µ).
    """
    gerador_aleatorio = np.random.default_rng(semente_aleatoria)

    vetor_valor_pago = dados_populacao["valor_total_pago"].to_numpy()
    vetor_valor_frete = dados_populacao["valor_total_frete"].to_numpy()
    vetor_cartao = (dados_populacao["meio_pagamento_principal"] == "Cartão de Crédito").to_numpy(dtype=float)
    vetor_sudeste = (dados_populacao["regiao_cliente"] == "Sudeste").to_numpy(dtype=float)

    total_populacao = len(dados_populacao)
    registros_simulacao = []

    for indice_sim in range(1, numero_simulacoes + 1):
        # Sorteia n = 383 índices sem reposição de forma vetorizada e ultrarrápida
        indices_sorteados = gerador_aleatorio.choice(total_populacao, size=tamanho_amostra, replace=False)

        media_pago = float(vetor_valor_pago[indices_sorteados].mean())
        media_frete = float(vetor_valor_frete[indices_sorteados].mean())
        prop_cartao_pct = float(vetor_cartao[indices_sorteados].mean() * 100.0)
        prop_sudeste_pct = float(vetor_sudeste[indices_sorteados].mean() * 100.0)

        registros_simulacao.append({
            "id_simulacao": indice_sim,
            "media_amostral_valor_pago": round(media_pago, 2),
            "media_amostral_valor_frete": round(media_frete, 2),
            "proporcao_amostral_cartao_pct": round(prop_cartao_pct, 2),
            "proporcao_amostral_sudeste_pct": round(prop_sudeste_pct, 2),
        })

    tabela_dist_amostral = pd.DataFrame(registros_simulacao)
    tabela_dist_amostral.to_csv(caminho_saida_csv, index=False, encoding="utf-8-sig")

    print("=" * 78)
    print(f"[ETAPA 5 - EXTRA 1] DISTRIBUIÇÃO AMOSTRAL DO TCL ({numero_simulacoes} AMOSTRAS DE n = {tamanho_amostra})")
    print("=" * 78)
    print(
        f"  • Ticket Pago (x̄) : Média das 1.000 médias = R$ {tabela_dist_amostral['media_amostral_valor_pago'].mean():.2f} "
        f"(µ Pop = R$ {vetor_valor_pago.mean():.2f}) | Assimetria caiu de {dados_populacao['valor_total_pago'].skew():.2f} para {tabela_dist_amostral['media_amostral_valor_pago'].skew():.2f}!"
    )
    print(
        f"  • Valor Frete (x̄) : Média das 1.000 médias = R$ {tabela_dist_amostral['media_amostral_valor_frete'].mean():.2f} "
        f"(µ Pop = R$ {vetor_valor_frete.mean():.2f}) | Assimetria caiu de {dados_populacao['valor_total_frete'].skew():.2f} para {tabela_dist_amostral['media_amostral_valor_frete'].skew():.2f}!"
    )
    print(f"  • Arquivo salvo para o Power BI: '{caminho_saida_csv}'")
    print("=" * 78 + "\n")

    return tabela_dist_amostral


def gerar_dados_qqplot_powerbi(
    dados_populacao: pd.DataFrame,
    dados_amostra: pd.DataFrame,
    tabela_dist_amostral: pd.DataFrame,
    numero_quantis: int = 383,
    caminho_saida_csv: str = "dados_qqplot_powerbi.csv",
) -> pd.DataFrame:
    """
    Calcula os pares de coordenadas (quantil_teorico_z, quantil_observado, reta_teorica_normal)
    para construir o gráfico QQ-Plot (Quantil-Quantil Normal) diretamente dentro do Power BI
    para:
        1. População (N = 95.808, avaliada em 383 quantis representativos)
        2. Amostra Aleatória Simples (n = 383 pedidos)
        3. Distribuição Amostral das Médias (1.000 amostras do TCL)
    """
    # Pré-calcula os quantis teóricos z de Filliben/Blom: p_i = (i - 0.5) / m
    quantis_z = [
        _inversa_normal_padrao((i - 0.5) / numero_quantis)
        for i in range(1, numero_quantis + 1)
    ]
    probabilidades_p = [(i - 0.5) / numero_quantis for i in range(1, numero_quantis + 1)]

    conjuntos_para_qqplot = [
        ("População (N = 95.808)", "valor_total_pago", dados_populacao["valor_total_pago"]),
        ("População (N = 95.808)", "valor_total_frete", dados_populacao["valor_total_frete"]),
        ("Amostra AAS (n = 383)", "valor_total_pago", dados_amostra["valor_total_pago"]),
        ("Amostra AAS (n = 383)", "valor_total_frete", dados_amostra["valor_total_frete"]),
        ("Distribuição Amostral da Média (TCL)", "valor_total_pago", tabela_dist_amostral["media_amostral_valor_pago"]),
        ("Distribuição Amostral da Média (TCL)", "valor_total_frete", tabela_dist_amostral["media_amostral_valor_frete"]),
    ]

    linhas_qqplot = []
    for nome_conjunto, nome_variavel, serie_dados in conjuntos_para_qqplot:
        if len(serie_dados) == numero_quantis:
            valores_ordenados = np.sort(serie_dados.to_numpy())
        else:
            valores_ordenados = np.quantile(serie_dados.to_numpy(), probabilidades_p)

        # Reta teórica da Normal passando pelo 1º e 3º quartis (padrão scipy.stats.probplot / R qqline)
        q1_obs, q3_obs = np.percentile(serie_dados.to_numpy(), [25, 75])
        z_q1, z_q3 = -0.67448975, 0.67448975
        inclinacao_reta = (q3_obs - q1_obs) / (z_q3 - z_q1)
        intercepto_reta = q1_obs - inclinacao_reta * z_q1

        for idx in range(numero_quantis):
            z_val = quantis_z[idx]
            obs_val = float(valores_ordenados[idx])
            reta_val = float(intercepto_reta + inclinacao_reta * z_val)

            linhas_qqplot.append({
                "conjunto_dados": nome_conjunto,
                "variavel": nome_variavel,
                "ordem_quantil": idx + 1,
                "quantil_teorico_z": round(z_val, 4),
                "quantil_observado": round(obs_val, 2),
                "reta_teorica_normal": round(reta_val, 2),
            })

    tabela_qqplot = pd.DataFrame(linhas_qqplot)
    tabela_qqplot.to_csv(caminho_saida_csv, index=False, encoding="utf-8-sig")

    print("=" * 78)
    print("[ETAPA 5 - EXTRA 2] COORDENADAS DO QQ-PLOT GERADAS PARA O POWER BI")
    print("=" * 78)
    print(f"  • Total de pontos gerados : {len(tabela_qqplot)} (População, Amostra e Distribuição Amostral)")
    print(f"  • Arquivo salvo           : '{caminho_saida_csv}'")
    print("=" * 78 + "\n")

    return tabela_qqplot


# ==============================================================================
# EXECUÇÃO PRINCIPAL DO SCRIPT
# ==============================================================================
if __name__ == "__main__":
    # 1. Carrega (ou gera) a tabela consolidada da População (N = 95.808 pedidos)
    populacao_pedidos = consolidar_populacao_olist("olist_pedidos_consolidado.csv")

    # 2. Calcula o tamanho da amostra usando os parâmetros da Opção B (padrão clássico):
    #    Confiança = 95%, Margem de Erro = 5% (0.05), Proporção = 50% (0.50) -> n = 383
    tamanho_amostra_calculado = calcular_tamanho_amostral_proporcao(
        tamanho_populacao=len(populacao_pedidos),
        nivel_confianca=0.95,
        margem_erro=0.05,
        proporcao_esperada=0.50,
    )

    # 3. Seleciona a Amostra Aleatória Simples (AAS) e salva em 'olist_amostra_aas.csv'
    amostra_pedidos = selecionar_amostra_aleatoria_simples(
        dados_populacao=populacao_pedidos,
        tamanho_amostra=tamanho_amostra_calculado,
        semente_aleatoria=42,
        caminho_saida_amostra_csv="olist_amostra_aas.csv",
    )

    # 4. Gera as tabelas de Análise Descritiva Comparativa (População vs. Amostra)
    variaveis_qualitativas_estudo = ["meio_pagamento_principal", "regiao_cliente"]
    resumo_qualitativo = gerar_resumo_qualitativo_populacao_vs_amostra(
        dados_populacao=populacao_pedidos,
        dados_amostra=amostra_pedidos,
        lista_variaveis_qualitativas=variaveis_qualitativas_estudo,
        caminho_saida_csv="resumo_qualitativas_pop_vs_amostra.csv",
    )

    variaveis_quantitativas_estudo = ["valor_total_pago", "valor_total_frete"]
    resumo_quantitativo = gerar_resumo_quantitativo_populacao_vs_amostra(
        dados_populacao=populacao_pedidos,
        dados_amostra=amostra_pedidos,
        lista_variaveis_quantitativas=variaveis_quantitativas_estudo,
        caminho_saida_csv="resumo_quantitativas_pop_vs_amostra.csv",
    )

    # 5. Executa a Inferência Estatística (ICs e Testes de Hipóteses) para o Painel 3
    resultados_inferencia = realizar_inferencia_proporcao_e_media(
        dados_populacao=populacao_pedidos,
        dados_amostra=amostra_pedidos,
        nivel_confianca=0.95,
        nivel_significancia=0.05,
        caminho_saida_csv="resultados_inferencia_painel3.csv",
    )

    # 6. Gera a Distribuição Amostral (TCL - 1.000 amostras) e os dados do QQ-Plot para o Power BI
    distribuicao_amostral_tcl = simular_distribuicao_amostral_tcl(
        dados_populacao=populacao_pedidos,
        tamanho_amostra=tamanho_amostra_calculado,
        numero_simulacoes=1000,
        semente_aleatoria=2026,
        caminho_saida_csv="distribuicao_amostral_tcl.csv",
    )

    dados_qqplot = gerar_dados_qqplot_powerbi(
        dados_populacao=populacao_pedidos,
        dados_amostra=amostra_pedidos,
        tabela_dist_amostral=distribuicao_amostral_tcl,
        numero_quantis=tamanho_amostra_calculado,
        caminho_saida_csv="dados_qqplot_powerbi.csv",
    )
