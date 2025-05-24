import yt_dlp
import whisper
import os
import uuid
from transformers import pipeline

AUDIO_DIR = "/tmp/audio_files"

def download_audio(youtube_id: str) -> str:
    url = f"https://www.youtube.com/watch?v={youtube_id}"
    os.makedirs(AUDIO_DIR, exist_ok=True)
    audio_filename = f"audio_{uuid.uuid4().hex}.mp3"
    absolute_audio_path = os.path.join(AUDIO_DIR, audio_filename)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': absolute_audio_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        if not os.path.exists(absolute_audio_path):
            raise RuntimeError(f"Audio file not found after download: {absolute_audio_path}")
    except Exception as e:
        raise RuntimeError(f"No se pudo descargar el audio de YouTube: {str(e)}")


    return absolute_audio_path

def transcribe_audio(path: str, model_size="base") -> str:
    model = whisper.load_model(model_size)
    result = model.transcribe(path, language="es")
    os.remove(path)
    return result['text']

def get_latest_video_id_from_channel(channel_url: str) -> tuple[str, str]:
    ydl_opts = {
        'quiet': True,
        'extract_flat': 'in_playlist',
        'force_generic_extractor': True,
        'dump_single_json': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        entries = info.get('entries', [])
        if not entries:
            raise Exception("No se encontraron videos en el canal.")
        
        video_id = entries[0].get('id')
        title = entries[0].get('title', 'Sin título')
        return video_id, title
    


# Modelo multitarea en español
nlp = pipeline("text2text-generation", model="google/flan-t5-base")

def analizar_texto(texto: str) -> dict:
    resumen = nlp(f"Resume en español el siguiente texto: {texto[:4000]}", max_length=300)[0]['generated_text']
    bullets = nlp(f"Extrae los puntos principales en formato bullet en español: {texto[:4000]}", max_length=300)[0]['generated_text']
    clasificacion = nlp(f"¿Qué tipo de discurso es este texto? Responde con una sola palabra: {texto[:1000]}", max_length=10)[0]['generated_text']
    temas = nlp(f"Lista los temas o palabras clave mencionadas: {texto[:3000]}", max_length=200)[0]['generated_text']
    categoria = nlp(f"¿A qué categoría política pertenece este contenido? (social, salud, economía, educación, etc): {texto[:1000]}", max_length=20)[0]['generated_text']
    sentimiento = nlp(f"Analiza el sentimiento del texto (positivo, negativo, neutral): {texto[:1000]}", max_length=10)[0]['generated_text']

    return {
        "resumen": resumen,
        "bullet_points": bullets,
        "clasificacion_discurso": clasificacion,
        "temas_principales": temas,
        "categoria_politica": categoria,
        "sentimiento": sentimiento
    }