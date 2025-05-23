from sqlalchemy.orm import Session
from models import Video
from schemas import VideoCreate

def get_videos(db: Session):
    return db.query(Video).all()

def create_video(db: Session, video: VideoCreate):
    db_video = Video(**video.dict())
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video
