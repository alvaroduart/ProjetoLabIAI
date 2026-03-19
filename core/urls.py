from django.contrib import admin
from django.urls import path
# Importamos TODAS as funções de visualização da sua aplicação, incluindo as novas
from investidor.views import index, processar_analise, questionario_perfil, processar_questionario

urlpatterns = [
    # Rota para a interface administrativa do Django 
    path('admin/', admin.site.urls),
    
    # Rota principal: exibe o formulário de perfil do investidor 
    path('', index, name='index'),
    
    # Rota para processar os dados e invocar a IA (Formulário Direto)
    path('analisar/', processar_analise, name='processar_analise'),

    # --- NOVAS ROTAS DO QUESTIONÁRIO (SUITABILITY) ---
    # Rota para exibir a nova tela de perguntas
    path('descobrir-perfil/', questionario_perfil, name='questionario_perfil'),
    
    # Rota para a IA processar as respostas e deduzir o perfil
    path('processar-questionario/', processar_questionario, name='processar_questionario'),
]