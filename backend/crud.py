from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models

# CRUD operations for the User model

def create_user(db: Session, short_name: str, rolle: str):
    try:
        new_user = models.User(short_name=short_name, rolle=rolle)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError:
        db.rollback()
        return None  # Handle the case where the short name is not unique

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_short_name(db: Session, short_name: str):
    return db.query(models.User).filter(models.User.short_name == short_name).first()

def get_all_users(db: Session):
    return db.query(models.User).all()



# CRUD operations for the Kiste model

def create_kiste(db: Session, qr_code_id: str, titel: str, kategorie: str = None, beschreibung: str = None):
    try:
        new_kiste = models.Kiste(
            qr_code_id=qr_code_id, 
            titel=titel, 
            kategorie=kategorie, 
            beschreibung=beschreibung
        )
        db.add(new_kiste)
        db.commit()
        db.refresh(new_kiste)
        return new_kiste
    except IntegrityError:
        db.rollback()
        return None  # Handle the case where the QR code ID is not unique
    
def get_kiste_by_qr_code(db: Session, qr_code_id: str):
    return db.query(models.Kiste).filter(models.Kiste.qr_code_id == qr_code_id).first()

def get_all_kisten(db: Session):
    return db.query(models.Kiste).all()


# Crud operations for the Ausleihe model
def get_all_ausleihen(db: Session):
    return db.query(models.Ausleihe).all() 


def ausleihen_kiste(db: Session, user_id: int, kiste_id: int):
    new_ausleihe = models.Ausleihe(
        ausleih_user_id=user_id,
        kiste_id=kiste_id,
        status=models.AusleihStatus.AUSGELIEHEN
    )
    db.add(new_ausleihe)
    db.commit()
    db.refresh(new_ausleihe)
    return new_ausleihe

def get_active_ausleihe_by_qr_code(db: Session, kiste_qr_code_id: str):
    kiste = get_kiste_by_qr_code(db, kiste_qr_code_id)
    if not kiste:
        return None  # Kiste not found

    return db.query(models.Ausleihe).filter(
        models.Ausleihe.kiste_id == kiste.id,
        models.Ausleihe.status == models.AusleihStatus.AUSGELIEHEN
    ).first()

def mark_as_returned(db: Session, ausleihe:models.Ausleihe, rueckgabe_user_id: int):
    ausleihe.status = models.AusleihStatus.ZURUECKGEGEBEN
    ausleihe.rueckgabe_datum = func.now()
    ausleihe.rueckgabe_user_id = rueckgabe_user_id

    db.commit()
    db.refresh(ausleihe)
    return ausleihe



    

