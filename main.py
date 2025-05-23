from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, crud, schemas
from database import SessionLocal, engine, Base

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