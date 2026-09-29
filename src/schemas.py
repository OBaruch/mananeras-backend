from pydantic import BaseModel
from datetime import datetime

# ========== VIDEO SCHEMAS ==========

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

# ========== RESUMEN SCHEMAS ==========

class ResumenBase(BaseModel):
    contenido: str
    transcripcion_completa: str | None = None
    bullet_points: str | None = None
    clasificacion_discurso: str | None = None
    temas_principales: str | None = None
    categoria_politica: str | None = None
    sentimiento: str | None = None

class ResumenCreate(ResumenBase):
    pass

class Resumen(ResumenBase):
    id: int
    video_id: int

    class Config:
        orm_mode = True
