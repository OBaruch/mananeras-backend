from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, crud, schemas
from database import SessionLocal, engine, Base
from utils.transcriber import download_audio, transcribe_audio
from utils.transcriber import get_latest_video_id_from_channel


app = FastAPI()

Base.metadata.create_all(bind=engine)

# Dependency para obtener la sesión de DB por request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "¡MVP Mañaneras conectado a PostgreSQL!"}

@app.post("/api/videos", response_model=schemas.Video)
def create_video(video: schemas.VideoCreate, db: Session = Depends(get_db)):
    return crud.create_video(db=db, video=video)

@app.get("/api/videos", response_model=list[schemas.Video])
def read_videos(db: Session = Depends(get_db)):
    return crud.get_videos(db)

@app.post("/api/videos/{video_id}/resumen", response_model=schemas.Resumen)
def create_resumen(video_id: int, resumen: schemas.ResumenCreate, db: Session = Depends(get_db)):
    # Validamos que el video exista
    db_video = db.query(models.Video).filter(models.Video.id == video_id).first()
    if not db_video:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    
    return crud.create_resumen(db=db, video_id=video_id, resumen_data=resumen)

@app.get("/api/videos/{video_id}/resumen", response_model=schemas.Resumen)
def read_resumen(video_id: int, db: Session = Depends(get_db)):
    resumen = crud.get_resumen_by_video(db, video_id)
    if not resumen:
        raise HTTPException(status_code=404, detail="Resumen no encontrado")
    return resumen


@app.post("/api/videos/{video_id}/auto-resumen", response_model=schemas.Resumen)
def generate_resumen_automatically(video_id: int, db: Session = Depends(get_db)):
    video = db.query(models.Video).filter(models.Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video no encontrado")

    try:
        # 1. Descarga el audio
        audio_path = download_audio(video.youtube_id)
        # 2. Transcribe el audio con Whisper
        texto = transcribe_audio(audio_path)
        # 3. Opcional: resumir con GPT aquí
        resumen = texto[:3000]  # Por ahora usaremos transcripción directa como resumen
        # 4. Guardar en la base de datos
        nuevo = crud.create_resumen(db=db, video_id=video_id, resumen_data=schemas.ResumenCreate(contenido=resumen))
        return nuevo
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar resumen: {str(e)}")
    
@app.post("/api/auto-resumen/latest", response_model=schemas.Resumen)
def auto_resumen_del_ultimo_video(db: Session = Depends(get_db)):
    try:
        canal_url = "https://www.youtube.com/@ClaudiaSheinbaumP/videos"
        youtube_id, title = get_latest_video_id_from_channel(canal_url)  # ✅ Desempaquetar correctamente

        # Revisa si el video ya existe
        video = db.query(models.Video).filter(models.Video.youtube_id == youtube_id).first()
        if not video:
            from datetime import datetime
            video = models.Video(
                youtube_id=youtube_id,
                title=title,  # ✅ Usar el título real del video
                date=datetime.utcnow()
            )
            db.add(video)
            db.commit()
            db.refresh(video)

        # Generar y guardar resumen
        audio_path = download_audio(video.youtube_id)
        texto = transcribe_audio(audio_path)
        resumen = texto[:3000]
        # Verifica si ya existe un resumen
        resumen_existente = crud.get_resumen_by_video(db, video.id)
        if resumen_existente:
            return resumen_existente  # evitar duplicados

        # Si no existe, lo crea
        nuevo = crud.create_resumen(
            db=db,
            video_id=video.id,
            resumen_data=schemas.ResumenCreate(contenido=resumen)
        )
        return nuevo

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en auto resumen: {str(e)}")
