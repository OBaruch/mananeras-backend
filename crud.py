from sqlalchemy.orm import Session
from models import Video
from schemas import VideoCreate
from models import Resumen
from schemas import ResumenCreate

def get_videos(db: Session):
    return db.query(Video).all()

def create_video(db: Session, video: VideoCreate):
    db_video = Video(**video.dict())
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

def create_resumen(db: Session, video_id: int, resumen_data: ResumenCreate):
    resumen = Resumen(**resumen_data.dict(), video_id=video_id)
    db.add(resumen)
    db.commit()
    db.refresh(resumen)
    return resumen

def get_resumen_by_video(db: Session, video_id: int):
    return db.query(Resumen).filter(Resumen.video_id == video_id).first()