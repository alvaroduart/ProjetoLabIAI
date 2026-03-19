import os
from django.core.wsgi import get_wsgi_application

# Aponta para o seu ficheiro de configurações 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()