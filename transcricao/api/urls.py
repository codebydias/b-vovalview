from django.urls import path
from .views import transcrever_audio, gerar_pdf

urlpatterns = [
    path('teste/', transcrever_audio, name='transcrever_audio'),
    path("pdf/", gerar_pdf),
    
]
