import os
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db


import crud
import models
import schemas

app = FastAPI(
    title= "Bücher Ausleihe API",
    description= "API für das QR-basierte Ausleihsystem von Kisten mit Büchersätzen an Schulen",
    version= "1.0.0"
)

# allow requests from Vue.js Frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# static folder for QR codes
os.makedirs("static/qr_codes", exist_ok=True)
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
    return kiste

@app.post("/admin/kisten", response_model=schemas.KisteResponse, tags=["Admin"])
def create_kiste(kiste: schemas.KisteCreate, password: str, db: Session = Depends(get_db)):
    """Create a new Kiste (Admin only)"""
    verify_admin_password(password)
    new_kiste = crud.create_kiste(
        db, 
        qr_code_id=kiste.qr_code_id, 
        titel=kiste.titel, 
        kategorie=kiste.kategorie, 
        beschreibung=kiste.beschreibung
    )
    if not new_kiste:
        raise HTTPException(status_code=400, detail="Box with this QR code ID already exists")
    return new_kiste


# --- Lehrkräfte endpoints ---

@app.get("/lehrer", response_model=List[schemas.UserResponse], tags=["Lehrkräfte"])
def read_users(db: Session = Depends(get_db)):
    """Get all Lehrkräfte"""
    return crud.get_all_users(db)

@app.post("/lehrer", response_model=schemas.UserResponse, tags=["Lehrkräfte"])
def create_user(user: schemas.UserCreate, password: str, db: Session = Depends(get_db)):
    """Create a new Lehrkraft (Admin only)"""
    verify_admin_password(password)
    new_user = crud.create_user(db, short_name=user.short_name, rolle=user.rolle)
    if not new_user:
        raise HTTPException(status_code=400, detail="User with this short name already exists")
    return new_user


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
    aktive_ausleihe = crud.get_active_ausleihe_by_qr_code(db, kiste_qr_code_id=kiste.qr_code_id)
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
    aktive_ausleihe = crud.get_active_ausleihe_by_qr_code(db, kiste_qr_code_id=kiste.qr_code_id)
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
