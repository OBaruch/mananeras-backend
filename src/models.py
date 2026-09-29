from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    youtube_id = Column(String, unique=True, index=True)
    title = Column(String)
    date = Column(DateTime, default=datetime.utcnow)

    resumen = relationship("Resumen", back_populates="video", uselist=False)

class Resumen(Base):
    __tablename__ = "resumenes"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    contenido = Column(Text)

    # Nuevos campos
    transcripcion_completa = Column(Text, nullable=True)
    bullet_points = Column(Text, nullable=True)
    clasificacion_discurso = Column(String, nullable=True)
    temas_principales = Column(Text, nullable=True)
    categoria_politica = Column(String, nullable=True)
    sentimiento = Column(String, nullable=True)

    video = relationship("Video", back_populates="resumen")