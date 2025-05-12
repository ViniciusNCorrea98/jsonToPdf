from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from database import Base

class AgendaDisparos(Base):
    __tablename__ = "agenda_disparos"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer)
    name = Column(String)
    telefone = Column(String)
    inbox_id = Column(Integer)
    imagem = Column(Boolean)
    audio = Column(Boolean)
    video = Column(Boolean)
    texto = Column(Text)
    status = Column(String)
    campanha = Column(String)
    captacao = Column(String)
    anuncio = Column(String)
    nome_colaborador = Column(String)
    send_at = Column(DateTime)
