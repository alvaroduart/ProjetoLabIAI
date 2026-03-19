import markdown
from django.shortcuts import render
from django.utils.safestring import mark_safe
from .ai_service import gerar_recomendacao_investimento, descobrir_perfil_investidor


def index(request):
    """Renderiza a página inicial com o formulário de perfil."""
    return render(request, "investidor/index.html")

def questionario_perfil(request):
    """Renderiza a página com o questionário da IA"""
    return render(request, "investidor/questionario.html")

def processar_questionario(request):
    """Processa as perguntas, deduz o perfil e gera o relatório"""
    if request.method == 'POST':
        ativos = request.POST.get('ativos', '').strip()
        valor = request.POST.get('valor', '')
        
        # Respostas comportamentais
        q_queda = request.POST.get('q_queda', '')
        q_tempo = request.POST.get('q_tempo', '')
        q_objetivo = request.POST.get('q_objetivo', '')
        
        if not ativos:
            return render(request, "investidor/questionario.html", {"erro": "Insira pelo menos um ativo."})

        # 1. A IA descobre o perfil do usuário
        perfil_inferido = descobrir_perfil_investidor(q_queda, q_tempo, q_objetivo)
        risco = perfil_inferido.get('risco', 'Moderado')
        objetivo = perfil_inferido.get('objetivo', 'Médio')
        
        # 2. A IA gera o relatório com os dados descobertos
        resultado_markdown = gerar_recomendacao_investimento(ativos, objetivo, risco, valor)
        
        # 3. Criamos uma mensagem para avisar o usuário qual foi o perfil identificado
        mensagem_perfil = f"Com base nas suas respostas, a IA identificou seu perfil como {risco.upper()} com foco no {objetivo.upper()} prazo."
        
        return render(request, "investidor/resultado.html", {
            "resultado": resultado_markdown,
            "ativos": ativos,
            "mensagem_perfil": mensagem_perfil # Enviamos isso para a tela final
        })
        
    return render(request, "investidor/index.html")

def processar_analise(request):
    """Lógica para processar o formulário POST e retornar o resultado da IA."""
    if request.method == 'POST':
        # Captura os campos e define strings vazias como fallback
        ativos = request.POST.get('ativos', '').strip()
        objetivo = request.POST.get('objetivo', '')
        risco = request.POST.get('risco', '')
        valor = request.POST.get('valor', '')
        
        # Validação de segurança simples
        if not ativos:
            return render(request, "investidor/index.html", {
                "erro": "Por favor, insira pelo menos um ativo (ex: PETR4, VALE3)."
            })

        # Chama a função de IA
        resultado_markdown = gerar_recomendacao_investimento(ativos, objetivo, risco, valor)
        
        # Converte o Markdown da IA para HTML, habilitando a renderização de tabelas
        resultado_html = markdown.markdown(
            resultado_markdown,
            extensions=['tables', 'fenced_code']
        )
        
        # Renderiza a página de resposta com o texto convertido e seguro para o Django
        return render(request, "investidor/resultado.html", {
            "resultado": mark_safe(resultado_html),
            "ativos": ativos
        })
    
    # Se alguém tentar acessar a URL diretamente via GET, volta pro index
    return render(request, "investidor/index.html")