import tempfile
import os
import io
from django.http import JsonResponse, FileResponse
from faster_whisper import WhisperModel
from django.views.decorators.csrf import csrf_exempt
from transformers import pipeline
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
import textwrap

# Summarizer com modelo mais robusto
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Função para dividir texto em chunks
def dividir_em_chunks(texto, max_tokens=1024):
    palavras = texto.split()
    for i in range(0, len(palavras), max_tokens):
        yield " ".join(palavras[i:i + max_tokens])

@csrf_exempt
def transcrever_audio(request):
    if request.method == "GET":
        return JsonResponse({"response": "Hello world"}, status=200)

    if request.method == "POST" and request.FILES.get("audio"):
        audio_file = request.FILES["audio"]
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                for chunk in audio_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            model = WhisperModel("medium", device="cpu", compute_type="int8")
            segments, _ = model.transcribe(temp_file_path, language="pt", vad_filter=True)
            transcricao = " ".join(segment.text for segment in segments)
            os.remove(temp_file_path)

            resumos = []
            for chunk in dividir_em_chunks(transcricao, max_tokens=1024):
                resumo_parcial = summarizer(
                    chunk,
                    max_length=500,
                    min_length=300,
                    do_sample=False
                )[0]['summary_text']
                resumos.append(resumo_parcial)

            resumo = " ".join(resumos)

            return JsonResponse({
                "transcricao": transcricao,
                "resumo": resumo
            })
        except Exception as e:
            return JsonResponse({"error": f"Erro ao transcrever: {str(e)}"}, status=500)

    return JsonResponse({"error": "Requisição inválida"}, status=400)

# Geração do PDF com formatação
def gerar_pdf(request):
    transcricao = request.GET.get("transcricao", "")
    resumo = request.GET.get("resumo", "")
    nome_audio = request.GET.get("nome_audio", "transcricao")  # padrão caso não venha nada

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    left_margin = 2 * cm
    right_margin = width - 2 * cm
    top_margin = height - 2 * cm
    bottom_margin = 2 * cm
    max_line_width = right_margin - left_margin
    y = top_margin

    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, y, "Relatório de Transcrição")
    y -= 2 * cm

    def draw_text_block(label, content, y):
        p.setFont("Helvetica-Bold", 14)
        p.drawString(left_margin, y, label)
        y -= 0.7 * cm
        p.setFont("Helvetica", 11)

        import textwrap
        max_chars = int((max_line_width / (0.18 * cm)))

        for linha in content.splitlines():
            wrapped_lines = textwrap.wrap(
                linha,
                width=max_chars,
                break_long_words=False,
                break_on_hyphens=False
            )
            for sub in wrapped_lines:
                p.drawString(left_margin, y, sub)
                y -= 0.5 * cm
                if y <= bottom_margin:
                    p.showPage()
                    y = top_margin
                    p.setFont("Helvetica", 11)

        return y - 1 * cm

    y = draw_text_block("Transcrição:", transcricao, y)
    y = draw_text_block("Resumo:", resumo, y)

    p.save()
    buffer.seek(0)
    filename = f"{nome_audio.rsplit('.', 1)[0]}_transcricao.pdf"  # remove extensão
    return FileResponse(buffer, as_attachment=True, filename=filename)


