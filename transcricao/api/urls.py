from django.urls import path
from .views import transcrever_audio

urlpatterns = [
    path('teste/', transcrever_audio, name='transcrever_audio'),
]
