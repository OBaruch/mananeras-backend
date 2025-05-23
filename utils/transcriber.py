import yt_dlp
import whisper
import os
import uuid


def download_audio(youtube_id: str) -> str:
    url = f"https://www.youtube.com/watch?v={youtube_id}"
    filename = f"audio_{uuid.uuid4().hex}.mp3"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filename,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        raise RuntimeError(f"No se pudo descargar el audio de YouTube: {str(e)}")


    return filename

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