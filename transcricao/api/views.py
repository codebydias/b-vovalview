# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# from faster_whisper import WhisperModel
# import tempfile

# @csrf_exempt
# def transcrever_audio(request):
#     if request.method == "POST" and request.FILES.get("audio"):
#         audio_file = request.FILES["audio"]
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
#             for chunk in audio_file.chunks():
#                 temp_file.write(chunk)
#             temp_file_path = temp_file.name

#         model = WhisperModel("base")  # ou 'medium', 'large', conforme sua infra
#         segments, _ = model.transcribe(temp_file_path)

#         transcricao = ""
#         for segment in segments:
#             transcricao += segment.text + " "

#         return JsonResponse({"transcricao": transcricao.strip()})
#     return JsonResponse({"error": "Requisição inválida"}, status=400)


# def teste(request):
#     return JsonResponse({"mensagem": "API funcionando!"})

import tempfile
import os
from django.http import JsonResponse
from faster_whisper import WhisperModel
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def transcrever_audio(request):
    if request.method == "GET":
        return JsonResponse({"response": "Hello world"}, status=200)

    if request.method == "POST" and request.FILES.get("audio"):
        audio_file = request.FILES["audio"]
       
        print("Nome do arquivo:", audio_file.name)
        print("Tipo MIME:", audio_file.content_type) 
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                for chunk in audio_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            # model = WhisperModel("base")
            model = WhisperModel("base", device="cpu")  # Força o uso da CPU
            segments, _ = model.transcribe(temp_file_path)

            transcricao = " ".join(segment.text for segment in segments)
            os.remove(temp_file_path)

            return JsonResponse({"transcricao": transcricao})
        except Exception as e:
            return JsonResponse({"error": f"Erro ao transcrever: {str(e)}"}, status=500)

    return JsonResponse({"error": "Requisição inválida"}, status=400)
