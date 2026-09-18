import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
from database import Base

# state enum for the Ausleihe model
class AusleihStatus(str, enum.Enum):
    AUSGELIEHEN = "ausgeliehen"
    ZURUECKGEGEBEN = "zurueckgegeben"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    short_name = Column(String(50), nullable=False)
    rolle = Column(String(50), default="Lehrkraft")

    ausleihen = relationship("Ausleihe", back_populates="user", foreign_keys="[Ausleihe.ausleih_user_id]")

class Kiste(Base):
    __tablename__ = "kisten"

    id = Column(Integer, primary_key=True, index=True)

    qr_code_id = Column(String(100), unique=True, nullable=False, index=True)
    titel = Column(String(150), nullable=False)
    kategorie = Column(String(100), nullable=True)
    beschreibung = Column(String(200), nullable=True)

    ausleihen = relationship("Ausleihe", back_populates="kiste")

class Ausleihe(Base):
    __tablename__ = "ausleihen"

    id = Column(Integer, primary_key=True, index=True)
    ausleih_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    kiste_id = Column(Integer, ForeignKey("kisten.id"), nullable=False)

    ausleih_datum = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    rueckgabe_datum = Column(DateTime(timezone=True), nullable=True)
    rueckgabe_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(AusleihStatus), default=AusleihStatus.AUSGELIEHEN, nullable=False)

    user = relationship("User", back_populates="ausleihen", foreign_keys=[ausleih_user_id])
    rueckgabe_user = relationship("User", foreign_keys=[rueckgabe_user_id])
    kiste = relationship("Kiste", back_populates="ausleihen", foreign_keys=[kiste_id])