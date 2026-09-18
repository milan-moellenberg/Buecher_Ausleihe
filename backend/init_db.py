from database import Base, engine, SessionLocal
import models
from models import User, Kiste, Ausleihe, AusleihStatus

def init_and_seed():
    print ("Initializing database in PostgreSQL...")
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized and seeded successfully.")

    db = SessionLocal()
    try: 
        # Check if data already exists to avoid duplicate seeding
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("Data already exists. Skipping seeding.")
            return

        print (" \n Seeding database with initial data...")

        # Test user
        user1 = User(short_name="MAMU", rolle="Lehrkraft")
        user2 = User(short_name="KASC", rolle="Lehrkraft")

        # Test kisten
        kiste1 = Kiste(qr_code_id="QR001", titel="Kiste 1", kategorie="Kategorie A", beschreibung="Beschreibung der Kiste 1")
        kiste2 = Kiste(qr_code_id="QR002", titel="Kiste 2", kategorie="Kategorie B", beschreibung="Beschreibung der Kiste 2")
        kiste3 = Kiste(qr_code_id="QR003", titel="Kiste 3", kategorie="Kategorie C", beschreibung="Beschreibung der Kiste 3")  

        # Add users and kisten to the session
        db.add_all([user1, user2, kiste1, kiste2, kiste3])
        db.commit() 

        print("Database seeded successfully.")
        print("   - 2 users added: MAMU, KASC")
        print("   - 3 kisten added: QR001, QR002, QR003")
        
    except Exception as e:
        db.rollback()  # Rollback the session in case of an error
        print(f"Error occurred during seeding: {e}")
    finally:
        db.close()  # Close the session

if __name__ == "__main__":
    init_and_seed()