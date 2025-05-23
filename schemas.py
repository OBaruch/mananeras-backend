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
