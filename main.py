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
