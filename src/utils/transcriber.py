import yt_dlp
import whisper
import os
import uuid
from transformers import pipeline

AUDIO_DIR = "/tmp/audio_files"

class YtdlLogger:
    def __init__(self):
        self.messages = []

    def debug(self, msg):
        # For yt-dlp, debug messages are often about the download process itself
        if msg.startswith('[debug] '):
            self.messages.append(msg)
        elif msg.startswith('[info] '):
            self.messages.append(msg)
        elif 'ffmpeg' in msg.lower() or 'postprocessor' in msg.lower(): # Capture ffmpeg/postprocessor messages
            self.messages.append(msg)
        print(msg) # Also print to stdout for live logging if possible

    def warning(self, msg):
        self.messages.append(f"WARNING: {msg}")
        print(f"WARNING: {msg}")

    def error(self, msg):
        self.messages.append(f"ERROR: {msg}")
        print(f"ERROR: {msg}")

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
        'quiet': False # Changed to False to enable logging
    }

    ytdl_logger = YtdlLogger()
    ydl_opts['logger'] = ytdl_logger

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        if not os.path.exists(absolute_audio_path):
            error_message = f"Audio file not found after download: {absolute_audio_path}"
            if hasattr(ytdl_logger, 'messages') and ytdl_logger.messages:
                error_message += "\nCollected yt-dlp logs:\n" + "\n".join(ytdl_logger.messages)
            raise RuntimeError(error_message)
    except Exception as e:
        # Include logs in this exception as well, in case the error happens during ydl.download()
        error_message = f"No se pudo descargar el audio de YouTube: {str(e)}"
        if hasattr(ytdl_logger, 'messages') and ytdl_logger.messages:
            error_message += "\nCollected yt-dlp logs:\n" + "\n".join(ytdl_logger.messages)
        raise RuntimeError(error_message)


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