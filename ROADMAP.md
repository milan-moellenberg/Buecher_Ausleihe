# Projekt-Roadmap: Schul-Ausleihsystem

## 1. Projekt-Setup & Infrastruktur (Lokal)
- [x] **Git & Repository Setup**
  - [x] Git-Repository lokal initialisieren und auf GitHub pushen
  - [x] `.gitignore` einrichten (Ausschluss von `venv/`, `node_modules/`, `.env`, DB-Anmeldedaten)
  - [x] Doku-Dateien anlegen (`README.md`, `ROADMAP.md`, `PROTOKOLL.md`)
- [x] **PostgreSQL Installation & Datenbank-Setup**
  - [x] PostgreSQL installieren (18.6)
  - [x] Datenbankzugriff über pgAdmin 4 testen
  - [x] DB-User `ausleihe_user` mit sicherem Passwort anlegen
  - [x] Datenbank `ausleihe_db` anlegen

---

## 2. Python Backend (FastAPI & SQLAlchemy)
- [x] **Umgebung & Grundkonfiguration**
  - [x] Python installieren & IDE (VS Code) einrichten
  - [x] Virtual Environment (`venv`) erstellen und aktivieren
  - [x] Paketverwaltung einrichten (`requirements.txt` )
  - [x] Umgebungs-Variablen via `.env` einbinden (DB-Credentials, Secret Keys)
  - [x] Simples Testskript für PostgreSQL-Verbindungsaufbau ausführen
- [x] **Datenbankmodellierung (SQLAlchemy ORM)**
  - [x] Entity `User` (Lehrer: ID, Name/Kürzel, Rolle)
  - [x] Entity `Kiste` (Bücherkiste: ID, QR-Code-Schlüssel, Name/Inhalt, Status)
  - [x] Entity `Ausleihe` (Historie: ID, Kiste_ID, User_ID, Klasse, Ausleihdatum, Rückgabedatum, Rückgeber_User_ID)
- [x] **Test-Driven Development (TDD) Setup**
  - [x] Test-Framework ( `unittest`) einrichten
  - [x] erste Unit-Tests für DB-Zugriffe und CRUD-Operationen (Create, Read, Update, Delete) schreiben
- [x] **QR-Code Generator Modul**
  - [x] Python-Skript/Utility zur automatischen Generierung von QR-Code-Grafiken (PNG) für Kisten-IDs erstellen
  - [x] Export der QR-Codes in lokalen Ordner / vorbereitung für Download-Funktion
- [x] **REST-API Entwicklung (FastAPI & Pydantic)**
  - [x] Pydantic Schemas für Request/Response-Validierung definieren
  - [x] Authentication- & Berechtigungskonzept umsetzen (Schul-Passwort für Ausleihe, Admin-Passwort für Admin-Bereich)
  - [x] REST-Endpunkte erstellen:
    - [x] `GET /kisten` / `GET /kisten/{id}` (Details & Status abfragen)
    - [x] `POST /ausleihe` (Kiste an Lehrer/Klasse ausleihen)
    - [x] `POST /rueckgabe` (Kiste zurückbringen inkl. Erfassung des Rückgebers)
    - [x] `GET /lehrer` & `POST /lehrer` (Lehrerliste & Registrierung neuer Lehrer)
    - [x] `GET /admin/historie` & Admin-Management (CRUD für Kisten)

---

## 3. Frontend-Entwicklung (Web App)
- [x] **Setup & Framework-Auswahl**
  - [x] Node.js installieren
  - [x] Frontend-Framework aufsetzen (z. B. Angular Material, React oder Vue.js) entschieden für Vue.js
  - [x] API-Client / Axios für Kommunikation mit dem FastAPI-Backend einrichten
- [x] **Benutzeroberfläche für Lehrer (QR-Code Zielseite)**
  - [x] Login / Passwortabfrage (Schul-Passwort)
  - [x] Dynamische Scan-Ansicht (`/scan/{kisten_id}`):
    - [x] **Fall A (Kiste verfügbar):** Ausleih-Formular (Lehrer-Dropdown + Schnell-Registrierung, Klasse-Eingabe, Ausleihen-Button)
    - [x] **Fall B (Kiste ausgeliehen):** Statusanzeige (Wer/Seit wann) + Rückgabe-Formular (Auswahl des Rückgebers, Zurückbringen-Button)
- [x] **Admin-Dashboard**
  - [x] Passwortgeschützter Admin-Bereich
  - [x] Kisten-Übersicht mit Live-Status und Such- & Filterfunktion
  - [x] Formular zum Hinzufügen/Bearbeiten neuer Kisten
  - [x] Ausleih-Historie & Protokoll-Einsicht

---

## 4. Deployment & Server-Infrastruktur (Linux)
- [x] **Virtuelle Maschine & OS Setup**
  - [x] VirtualBox 7.2.20 installieren
  - [x] Linux-Distribution (Ubuntu Server 26.04.1 LTS ) aufsetzen
  - [x] Systempakete aktualisieren & Basis-Tools installieren (`git`, `curl`, `build-essential`)
- [ ] **Server-Umgebung konfigurieren**
  - [x] PostgreSQL auf Linux installieren und Datenbank importieren/konfigurieren
  - [x] Python & Node.js auf dem Server installieren
  - [x] Repository via `git clone` auf den Server holen
- [ ] **Webserver & Process Management**
  - [x] Nginx als Reverse Proxy einrichten (Routing auf Backend & Frontend)
  - [x] Backend-Prozess als System-Dienst (Systemd) oder mit Uvicorn konfigurieren
  - [x] Anwendung lokal im Netzwerk / der VM aufrufen und durchtesten
- [ ] **Automatisierung (Optional / Krönung)**
  - [ ] Ansible Playbook schreiben, um das gesamte Deployment (Pakete, Nginx, App-Service, DB) per Skript zu automatisieren