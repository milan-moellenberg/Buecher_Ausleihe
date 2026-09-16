# Projekt-Roadmap: Schul-Ausleihsystem

## 1. Projekt-Setup & Infrastruktur (Lokal)
- [ ] **Git & Repository Setup**
  - [ ] Git-Repository lokal initialisieren und auf GitHub pushen
  - [ ] `.gitignore` einrichten (Ausschluss von `venv/`, `node_modules/`, `.env`, DB-Anmeldedaten)
  - [ ] Doku-Dateien anlegen (`README.md`, `ROADMAP.md`, `PROTOKOLL.md`)
- [ ] **PostgreSQL Installation & Datenbank-Setup**
  - [ ] PostgreSQL installieren (EnterpriseDB)
  - [ ] Datenbankzugriff über pgAdmin testen
  - [ ] DB-User `ausleihe_user` mit sicherem Passwort anlegen
  - [ ] Datenbank `ausleihe_db` anlegen

---

## 2. Python Backend (FastAPI & SQLAlchemy)
- [ ] **Umgebung & Grundkonfiguration**
  - [ ] Python installieren & IDE (VS Code / PyCharm) einrichten
  - [ ] Virtual Environment (`venv`) erstellen und aktivieren
  - [ ] Paketverwaltung einrichten (`requirements.txt` oder Poetry)
  - [ ] Umgebungs-Variablen via `.env` einbinden (DB-Credentials, Secret Keys)
  - [ ] Simples Testskript für PostgreSQL-Verbindungsaufbau ausführen
- [ ] **Datenbankmodellierung (SQLAlchemy ORM)**
  - [ ] Entity `User` (Lehrer: ID, Name/Kürzel, Rolle)
  - [ ] Entity `Kiste` (Bücherkiste: ID, QR-Code-Schlüssel, Name/Inhalt, Status)
  - [ ] Entity `Ausleihe` (Historie: ID, Kiste_ID, User_ID, Klasse, Ausleihdatum, Rückgabedatum, Rückgeber_User_ID)
- [ ] **Test-Driven Development (TDD) Setup**
  - [ ] Test-Framework (z. B. `pytest` oder `unittest`) einrichten
  - [ ] Unit-Tests für DB-Zugriffe und CRUD-Operationen (Create, Read, Update, Delete) schreiben
- [ ] **QR-Code Generator Modul**
  - [ ] Python-Skript/Utility zur automatischen Generierung von QR-Code-Grafiken (PNG) für Kisten-IDs erstellen
  - [ ] Export der QR-Codes in lokalen Ordner / Download-Funktion
- [ ] **REST-API Entwicklung (FastAPI & Pydantic)**
  - [ ] Pydantic Schemas für Request/Response-Validierung definieren
  - [ ] Authentication- & Berechtigungskonzept umsetzen (Schul-Passwort für Ausleihe, Admin-Passwort für Admin-Bereich)
  - [ ] REST-Endpunkte erstellen:
    - [ ] `GET /kisten` / `GET /kisten/{id}` (Details & Status abfragen)
    - [ ] `POST /ausleihe` (Kiste an Lehrer/Klasse ausleihen)
    - [ ] `POST /rueckgabe` (Kiste zurückbringen inkl. Erfassung des Rückgebers)
    - [ ] `GET /lehrer` & `POST /lehrer` (Lehrerliste & Registrierung neuer Lehrer)
    - [ ] `GET /admin/historie` & Admin-Management (CRUD für Kisten)

---

## 3. Frontend-Entwicklung (Web App)
- [ ] **Setup & Framework-Auswahl**
  - [ ] Node.js installieren
  - [ ] Frontend-Framework aufsetzen (z. B. Angular Material, React oder Vue.js)
  - [ ] API-Client / Axios für Kommunikation mit dem FastAPI-Backend einrichten
- [ ] **Benutzeroberfläche für Lehrer (QR-Code Zielseite)**
  - [ ] Login / Passwortabfrage (Schul-Passwort)
  - [ ] Dynamische Scan-Ansicht (`/scan/{kisten_id}`):
    - [ ] **Fall A (Kiste verfügbar):** Ausleih-Formular (Lehrer-Dropdown + Schnell-Registrierung, Klasse-Eingabe, Ausleihen-Button)
    - [ ] **Fall B (Kiste ausgeliehen):** Statusanzeige (Wer/Seit wann) + Rückgabe-Formular (Auswahl des Rückgebers, Zurückbringen-Button)
- [ ] **Admin-Dashboard**
  - [ ] Passwortgeschützter Admin-Bereich
  - [ ] Kisten-Übersicht mit Live-Status und Such- & Filterfunktion
  - [ ] Formular zum Hinzufügen/Bearbeiten neuer Kisten
  - [ ] Ausleih-Historie & Protokoll-Einsicht

---

## 4. Deployment & Server-Infrastruktur (Linux)
- [ ] **Virtuelle Maschine & OS Setup**
  - [ ] VirtualBox installieren
  - [ ] Linux-Distribution (Ubuntu Server oder Rocky Linux) aufsetzen
  - [ ] Systempakete aktualisieren & Basis-Tools installieren (`git`, `curl`, `build-essential`)
- [ ] **Server-Umgebung konfigurieren**
  - [ ] PostgreSQL auf Linux installieren und Datenbank importieren/konfigurieren
  - [ ] Python & Node.js auf dem Server installieren
  - [ ] Repository via `git clone` auf den Server holen
- [ ] **Webserver & Process Management**
  - [ ] Nginx als Reverse Proxy einrichten (Routing auf Backend & Frontend)
  - [ ] Backend-Prozess als System-Dienst (Systemd) oder mit Gunicorn/Uvicorn konfigurieren
  - [ ] Anwendung lokal im Netzwerk / der VM aufrufen und durchtesten
- [ ] **Automatisierung (Optional / Krönung)**
  - [ ] Ansible Playbook schreiben, um das gesamte Deployment (Pakete, Nginx, App-Service, DB) per Skript zu automatisieren