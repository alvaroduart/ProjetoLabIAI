import os
import json
import re
import certifi
import yfinance as yf

from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.yfinance import YFinanceTools
from agno.tools.tavily import TavilyTools
from dotenv import load_dotenv

# ==============================
# CONFIGURAÇÃO INICIAL
# ==============================

load_dotenv()

# Corrige erro de certificado SSL
os.environ["SSL_CERT_FILE"] = certifi.where()

# Evita erro de timezone do yfinance
yf.set_tz_cache_location("cache")


# ==============================
# PERFIL DO INVESTIDOR
# ==============================

def descobrir_perfil_investidor(q_queda, q_tempo, q_objetivo):
    agente_perfil = Agent(
        model=Groq(id="llama-3.3-70b-versatile"),
        description="Especialista em Suitability financeiro.",
        instructions=[
            "Analise as respostas do investidor.",
            "Classifique o risco: Conservador, Moderado ou Arrojado.",
            "Classifique o objetivo: Curto, Médio ou Longo prazo.",
            "Responda apenas com JSON válido.",
            'Exemplo: {"risco": "Moderado", "objetivo": "Longo"}'
        ]
    )

    prompt = f"""
Respostas do investidor:
1. Reação a uma queda de 20%: {q_queda}
2. Tempo que pretende investir: {q_tempo}
3. Objetivo principal: {q_objetivo}
"""

    try:
        resposta = agente_perfil.run(prompt).content
        # limpa markdown
        texto_limpo = re.sub(r"```json|```", "", resposta).strip()
        dados = json.loads(texto_limpo)
        return dados
    except Exception as e:
        print("Erro suitability:", e)
        return {"risco": "Moderado", "objetivo": "Médio"}


# ==============================
# FORMATAR ATIVOS
# ==============================

def formatar_ativos(ativos):
    ativos_lista = [a.strip().upper() for a in ativos.split(",")]
    # Garante que as ações brasileiras tenham o .SA no final
    ativos_formatados = [
        f"{a}.SA" if not a.endswith(".SA") else a for a in ativos_lista
    ]
    return ativos_formatados


# ==============================
# RECOMENDAÇÃO DE INVESTIMENTO
# ==============================

def gerar_recomendacao_investimento(ativos, objetivo, risco, valor):
    if not ativos:
        return "⚠️ Informe pelo menos um ativo."

    ativos_formatados = formatar_ativos(ativos)
    ativos_query = ", ".join(ativos_formatados)

    agente = Agent(
        model=Groq(id="llama-3.3-70b-versatile"),
        tools=[
            YFinanceTools(), # Otimizando a tool
            TavilyTools()
        ],
        markdown=True,
        description="Analista Financeiro Sênior especializado no mercado de ações brasileiro (B3).",
        instructions=[
            "Você deve usar o YFinanceTools para obter a cotação exata do dia de HOJE e a variação diária.",
            "Você deve usar o TavilyTools para buscar notícias recentes.",
            "REGRA TAVILY OBRIGATÓRIA: Direcione a busca de notícias EXCLUSIVAMENTE para o portal Bora Investir da B3. "
            "Na sua query do Tavily, adicione SEMPRE o prefixo: 'site:borainvestir.b3.com.br/noticias/mercado/' antes do ticker.",
            "Sempre execute as ferramentas antes de responder. Não invente dados.",
            "Nunca escreva chamadas de função no texto final.",
            f"Perfil do investidor a ser respeitado: risco {risco}, objetivo {objetivo}, capital R$ {valor}.",
            "Retorne apenas o relatório final preenchido."
        ]
    )

    prompt = f"""
Analise os seguintes ativos da bolsa brasileira: {ativos_query}

PASSO 1: Obter Dados Reais
- Use o YFinanceTools para buscar o preço atualizado de hoje e a variação diária de cada ativo.
- Use o TavilyTools para buscar as últimas notícias de cada ativo usando estritamente o operador site:borainvestir.b3.com.br/noticias/mercado/

PASSO 2: Gerar o Relatório
Com base nos dados coletados, preencha EXATAMENTE o formato abaixo:

### 📊 Análise Comparativa

| Ativo | Preço Atual (Hoje) | Variação (24h) | Sentimento do Mercado |
|---|---|---|---|

### 💡 Destaques (Bora Investir B3)
[Escreva um breve resumo cruzado das notícias encontradas no portal da B3 para estes ativos.]

### 🏆 Melhor Ativo
[Nome do melhor ativo para o perfil **{risco}**]
[Explique a escolha em até 3 linhas com base nos dados e notícias.]

### 💰 Sugestão de Alocação
Distribua o capital de **R$ {valor}** entre os ativos analisados, justificando brevemente a divisão baseada no perfil **{risco}** e objetivo de **{objetivo}** prazo.
"""

    try:
        resposta = agente.run(prompt)
        return resposta.content
    except Exception as e:
        return f"Erro na análise da IA: {str(e)}"

# ==============================
# TESTE RÁPIDO (Opcional)
# ==============================
if __name__ == "__main__":
    print("Iniciando teste de análise...")
    resultado = gerar_recomendacao_investimento(
        ativos="PETR4, VALE3, ITUB4", 
        objetivo="Longo", 
        risco="Moderado", 
        valor="10000"
    )
    print("\n" + resultado)