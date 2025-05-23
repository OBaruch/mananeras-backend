from pydantic import BaseModel
from datetime import datetime

class VideoBase(BaseModel):
    youtube_id: str
    title: str
    date: datetime

class VideoCreate(VideoBase):
    pass

class Video(VideoBase):
    id: int

    class Config:
        orm_mode = True

# ============ RESUMEN SCHEMAS ============

class ResumenBase(BaseModel):
    contenido: str

class ResumenCreate(ResumenBase):
    pass

class Resumen(ResumenBase):
    id: int
    video_id: int

    class Config:
        orm_mode = True