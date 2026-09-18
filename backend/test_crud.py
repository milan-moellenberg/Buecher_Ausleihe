import unittest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from database import Base, DATABASE_URL
import models
import crud

class TestCRUDFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create an in-memory SQLite database for testing
        cls.engine = create_engine(DATABASE_URL)
        Base.metadata.drop_all(bind = cls.engine)  # Drop all tables to ensure a clean slate
        Base.metadata.create_all(bind = cls.engine)
        cls.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)

    def setUp(self):
        self.db = self.SessionLocal()

    def tearDown(self):
        self.db.close()

        with self.engine.connect() as connection:
            trans = connection.begin()
            connection.execute(text("TRUNCATE users, kisten, ausleihen RESTART IDENTITY CASCADE;"))
            trans.commit()

    def test_create_and_get_user(self):
        user = crud.create_user(
            self.db, 
            short_name="testuser", 
            rolle="Lehrkraft"
        )
        self.assertIsNotNone(user.id)
        self.assertEqual(user.short_name, "testuser")
        self.assertEqual(user.rolle, "Lehrkraft")

        fetched_user_by_id = crud.get_user_by_id(self.db, user.id)
        self.assertIsNotNone(fetched_user_by_id)
        self.assertEqual(fetched_user_by_id.id, user.id)

        fetched_user_by_short_name = crud.get_user_by_short_name(self.db, "testuser")
        self.assertIsNotNone(fetched_user_by_short_name)
        self.assertEqual(fetched_user_by_short_name.short_name, "testuser")

    def test_create_and_get_kiste(self):
        kiste = crud.create_kiste(
            self.db, 
            qr_code_id="QR123", 
            titel="Test Kiste", 
            kategorie="Test Kategorie", 
            beschreibung="Test Beschreibung"
        )
        self.assertIsNotNone(kiste.id)
        self.assertEqual(kiste.qr_code_id, "QR123")

        fetched_kiste = crud.get_kiste_by_qr_code(self.db, "QR123")
        self.assertIsNotNone(fetched_kiste)
        self.assertEqual(fetched_kiste.qr_code_id, "QR123")

    # desired workflow: user borrows the kiste, same user returns the kiste
    def test_ausleihen_and_rueckgabe_kiste(self):
        user = crud.create_user(self.db, short_name="testuser2", rolle="Lehrkraft")
        kiste = crud.create_kiste(self.db, qr_code_id="QR456", titel="Test Kiste 2")

        ausleihe = crud.ausleihen_kiste(self.db, user.short_name, kiste.qr_code_id)
        self.assertIsNotNone(ausleihe)
        self.assertEqual(ausleihe.ausleih_user_id, user.id)
        self.assertEqual(ausleihe.status, models.AusleihStatus.AUSGELIEHEN)

        rueckgabe = crud.rueckgabe_kiste_by_qr_code(self.db, user.short_name, kiste.qr_code_id)
        self.assertIsNotNone(rueckgabe)
        self.assertEqual(rueckgabe.status, models.AusleihStatus.ZURUECKGEGEBEN)
        self.assertIsNotNone(rueckgabe.rueckgabe_datum)

    # if the user who returns the kiste is different from the user who borrowed it, the rueckgabe_user_id should be set correctly
    def test_ausleihen_and_foreign_rueckgabe_kiste(self):
        user1 = crud.create_user(self.db, short_name="testuser1", rolle="Lehrkraft")
        user2 = crud.create_user(self.db, short_name="testuser2", rolle="Lehrkraft")
        kiste = crud.create_kiste(self.db, qr_code_id="QR789", titel="Test Kiste 3")

        ausleihe = crud.ausleihen_kiste(self.db, user1.short_name, kiste.qr_code_id)
        self.assertIsNotNone(ausleihe)

        rueckgabe = crud.rueckgabe_kiste_by_qr_code(self.db, user2.short_name, kiste.qr_code_id)
        self.assertIsNotNone(rueckgabe)
        self.assertEqual(rueckgabe.status, models.AusleihStatus.ZURUECKGEGEBEN)
        self.assertEqual(rueckgabe.ausleih_user_id, user1.id)
        self.assertEqual(rueckgabe.rueckgabe_user_id, user2.id)


if __name__ == "__main__":
    unittest.main()