# Pydantic-Klassen (schemas.py) beschreiben, wie Daten über das Internet (HTTP / JSON) gesendet und empfangen werden

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

class UserUpdate(BaseModel):
    short_name: Optional[str] = None
    rolle: Optional[str] = None  # "Lehrkraft" oder "Ehemalig"
    
class UserResponse(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Ausleihe schemata

class AusleiheBase(BaseModel):
    
    ausleih_user_id: int
    
class AusleiheCreate(AusleiheBase):
    passwort: str
    qr_code_id: str
    
class AusleiheResponse(AusleiheBase):
    id: int
    kiste_id: int
    ausleih_datum: datetime
    rueckgabe_datum: Optional[datetime] = None
    rueckgabe_user_id: Optional[int] = None
    status: AusleihStatus

    model_config = ConfigDict(from_attributes=True)

class RueckgabeCreate(BaseModel):
    qr_code_id: str
    rueckgabe_user_id: int
    passwort: str
    
# Kiste schemata
class KisteBase(BaseModel):
    titel: str
    kategorie: Optional[str] = None
    beschreibung: Optional[str] = None

class KisteCreate(KisteBase):
    pass

class KisteUpdate(KisteBase):
    titel: Optional[str] = None
    qr_code_id: Optional[str] = None

class KisteResponse(KisteBase):
    id: int
    qr_code_id: str
    aktive_ausleihe: Optional[AusleiheResponse] = None
    
    model_config = ConfigDict(from_attributes=True)

class RegenerateQRCodesPayload(BaseModel):
    kisten_ids: List[int] = []


