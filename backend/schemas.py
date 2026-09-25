from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from models import AusleihStatus

# User schemata
class UserBase(BaseModel):
    short_name: str
    rolle: str = "Lehrkraft"

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Kiste schemata
class KisteBase(BaseModel):
    qr_code_id: str
    titel: str
    kategorie: Optional[str] = None
    beschreibung: Optional[str] = None

class KisteCreate(KisteBase):
    pass

class KisteResponse(KisteBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Ausleihe schemata
class AusleiheCreate(BaseModel):
    qr_code_id: str
    ausleih_user_id: int
    passwort: str

class RueckgabeCreate(BaseModel):
    qr_code_id: str
    rueckgabe_user_id: int
    passwort: str

class AusleiheResponse(BaseModel):
    id: int
    ausleih_user_id: int
    kiste_id: int
    ausleih_datum: datetime
    rueckgabe_datum: Optional[datetime] = None
    rueckgabe_user_id: Optional[int] = None
    status: AusleihStatus

    model_config = ConfigDict(from_attributes=True)

