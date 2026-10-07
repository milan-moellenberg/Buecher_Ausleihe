# Hier fließen FastAPI (Webserver & Router), SQLAlchemy (Datenbank) und Pydantic (Validierung) zusammen

import os
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db
from qr_generator import generate_qr_code

import crud
import models
import schemas




app = FastAPI(
    title= "Bücher Ausleihe API",
    description= "API für das QR-basierte Ausleihsystem von Kisten mit Büchersätzen an Schulen",
    root_path= "/api",  # Alle Endpunkte werden unter /api/ verfügbar sein
    version= "1.0.0"
)

# allow requests from Vue.js Frontend; allow origin for local development and production
origins = [
    "http://localhost:5173",  # Standard Vite Dev-Server
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pfad zum QR-Code Ordner definieren
QR_CODE_DIR = "static/qrcodes"

# static folder for QR codes
os.makedirs("static/qrcodes", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# password checking functions
SCHOOL_PASSWORD = os.getenv("SCHOOL_PASSWORD")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

if not SCHOOL_PASSWORD or not ADMIN_PASSWORD:
    raise RuntimeError("SCHOOL_PASSWORD or ADMIN_PASSWORD did not get set in the .env file!")

def verify_school_password(password: str):
    if password != SCHOOL_PASSWORD and password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid school password"
        )

def verify_admin_password(password: str):
    if password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )


# --- Kisten endpoints ---

@app.get("/kisten", response_model=List[schemas.KisteResponse], tags=["Kisten"])
def read_kisten(db: Session = Depends(get_db)):
    """Get all Kisten"""
    return crud.get_all_kisten(db)

@app.get("/kisten/{qr_code_id}", response_model=schemas.KisteResponse, tags=["Kisten"])
def read_kiste(qr_code_id: str, db: Session = Depends(get_db)):
    """Get a Kiste by its QR code ID"""
    kiste = crud.get_kiste_by_qr_code(db, qr_code_id=qr_code_id)
    if not kiste:
        raise HTTPException(status_code=404, detail="Box not found")

    #check for an active Ausleihe:
    aktive_ausleihe = crud.get_active_ausleihe_by_qr_code(db, qr_code_id=qr_code_id)
    kiste.aktive_ausleihe = aktive_ausleihe
    
    return kiste

@app.get("/kisten/{kiste_id}/qrcode", tags=["Kisten"])
def get_or_create_kiste_qrcode(kiste_id: int, db: Session = Depends(get_db)):
    kiste = db.query(models.Kiste).filter(models.Kiste.id == kiste_id).first()
    if not kiste or not kiste.qr_code_id:
        raise HTTPException(status_code=404, detail="Kiste oder QR-Code-ID nicht gefunden")

    file_path = os.path.join(QR_CODE_DIR, f"{kiste.qr_code_id}.png")

    # Falls die Datei gelöscht wurde oder nie existierte: On-the-fly generieren!
    if not os.path.exists(file_path):
        generate_qr_code(data=kiste.qr_code_id)

    return FileResponse(file_path, media_type="image/png")

@app.post("/admin/kisten", response_model=schemas.KisteResponse, tags=["Admin"])
def create_kiste(kiste: schemas.KisteCreate, password: str, db: Session = Depends(get_db)):
    """Create a new Kiste and its QR code image (Admin only)"""
    verify_admin_password(password)
    new_kiste = crud.create_kiste(
        db, 
        titel=kiste.titel, 
        kategorie=kiste.kategorie, 
        beschreibung=kiste.beschreibung
    )
    if not new_kiste:
        raise HTTPException(status_code=400, detail="Box with this QR code ID already exists")

    # create QR-Code png
    generate_qr_code(data=new_kiste.qr_code_id)

    return new_kiste

@app.put("/admin/kisten/{kiste_id}", response_model=schemas.KisteResponse, tags=["Admin"])
def edit_kiste(kiste_id: int, kiste_data: schemas.KisteUpdate, password: str, db: Session = Depends(get_db)):
    verify_admin_password(password)
    try:
        updated = crud.update_kiste(db, kiste_id, kiste_data)
        if not updated:
            raise HTTPException(status_code=404, detail="Kiste nicht gefunden")
        
        # Falls QR-ID geändert wurde, neues QR-Code Bild generieren
        if kiste_data.qr_code_id:
            generate_qr_code(data=updated.qr_code_id)
            
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/admin/kisten/regenerate-qrcodes", tags=["Admin"])
def regenerate_all_qrcodes(password: str, db: Session = Depends(get_db)):
    verify_admin_password(password)
    
    kisten = db.query(models.Kiste).all()
    generated_count = 0
    
    for kiste in kisten:
        if kiste.qr_code_id:
            # Erzeugt das Bild unter /static/qrcodes/{qr_code_id}.png
            generate_qr_code(data=kiste.qr_code_id)
            generated_count += 1
            
    return {
        "message": f"QR-Codes wurden für {generated_count} Kisten erfolgreich neu generiert.",
        "count": generated_count
    }

    
# --- Lehrkräfte endpoints ---

@app.get("/lehrer", response_model=list[schemas.UserResponse])
def get_lehrer(db: Session = Depends(get_db)):
    return crud.get_active_lehrer(db)

# Endpunkt für Admin-Ansicht (Liefert alle inkl. Ehemalige)
@app.get("/admin/users", response_model=list[schemas.UserResponse], tags=["Admin"])
def get_all_users(password: str, db: Session = Depends(get_db)):
    verify_admin_password(password)
    return db.query(models.User).all()

@app.post("/lehrer", response_model=schemas.UserResponse, tags=["Lehrkräfte"])
def create_user(user: schemas.UserCreate, password: str, db: Session = Depends(get_db)):
    """Create a new Lehrkraft (Admin only)"""
    verify_admin_password(password)
    new_user = crud.create_user(db, short_name=user.short_name, rolle=user.rolle)
    if not new_user:
        raise HTTPException(status_code=400, detail="User with this short name already exists")
    return new_user

@app.put("/admin/users/{user_id}", response_model=schemas.UserResponse, tags=["Admin"])
def edit_user(user_id: int, user_data: schemas.UserUpdate, password: str, db: Session = Depends(get_db)):
    verify_admin_password(password)
    updated = crud.update_user(db, user_id, user_data)
    if not updated:
        raise HTTPException(status_code=404, detail="User nicht gefunden")
    return updated


# --- Ausleihe endpoints ---

@app.post("/ausleihe", response_model=schemas.AusleiheResponse, tags=["Ausleihe"])
def ausleihen(payload: schemas.AusleiheCreate, force_reborrow: bool = False, db: Session = Depends(get_db)):
    """
    Kiste Ausleihen
    force_reborrow: If True, allows a user to borrow a Kiste even if it had an active loan for it.
    """
    verify_school_password(payload.passwort)

    #does the chest exist?
    kiste = crud.get_kiste_by_qr_code(db, qr_code_id=payload.qr_code_id)
    if not kiste:
        raise HTTPException(status_code=404, detail="Box not found")

    #does the user exist?
    user = crud.get_user_by_id(db, user_id=payload.ausleih_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User with this short name not found")

    #is the box already borrowed/not returned yet?
    aktive_ausleihe = crud.get_active_ausleihe_by_qr_code(db, qr_code_id=kiste.qr_code_id)
    if aktive_ausleihe:
        if not force_reborrow:
            # send http 409 Conflict so the Frontend can ask the user if they want to force the reborrow
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=f"Box is currently borrowed by user ID {aktive_ausleihe.ausleih_user_id}. Confirmation required to auto-return."
            )
        else:
            # Autoreturn the box before borrowing it again
            crud.mark_as_returned(
                db,
                ausleihe= aktive_ausleihe,
                rueckgabe_user_id= user.id
            )

    
    return crud.ausleihen_kiste(
        db, 
        user_id=user.id, 
        kiste_id=kiste.id
    )

@app.post("/rueckgabe", response_model=schemas.AusleiheResponse, tags=["Ausleihe"])
def rueckgabe(payload: schemas.RueckgabeCreate, db: Session = Depends(get_db)):
    """Return a borrowed Kiste."""
    verify_school_password(payload.passwort)

    #does the chest exist?
    kiste = crud.get_kiste_by_qr_code(
        db, 
        qr_code_id=payload.qr_code_id)
    if not kiste:
        raise HTTPException(status_code=404, detail="Box not found")

    #does the user exist?
    user = crud.get_user_by_id(db, user_id= payload.rueckgabe_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    #is the box currently borrowed?
    aktive_ausleihe = crud.get_active_ausleihe_by_qr_code(db, qr_code_id=kiste.qr_code_id)
    if not aktive_ausleihe:
        raise HTTPException(
            status_code=400, 
            detail="Box is not currently borrowed"
        )

    return_ausleihe = crud.mark_as_returned(
        db,
        ausleihe=aktive_ausleihe,
        rueckgabe_user_id=user.id
    )

    return return_ausleihe


# --- admin endpoints and history---

@app.get("/admin/ausleihe", response_model=List[schemas.AusleiheResponse], tags=["Admin"])
def read_history(admin_password: str, db: Session = Depends(get_db)):
    """Get the history Admin only)"""
    verify_admin_password(admin_password)
    return crud.get_all_ausleihen(db)
