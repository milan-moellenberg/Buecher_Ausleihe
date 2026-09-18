# Schul-Ausleihsystem für Bücherkisten

Ein digitales Verwaltungssystem zur einfachen Ausleihe und Rückgabe von Bücherkisten an Schulen via QR-Code. Entwickelt als Fullstack-Webanwendung mit Fokus auf minimalen Aufwand für Lehrkräfte, Datensicherheit und nachvollziehbare Historie.

---

## Inhaltsverzeichnis
- [Schul-Ausleihsystem für Bücherkisten](#schul-ausleihsystem-für-bücherkisten)
  - [Inhaltsverzeichnis](#inhaltsverzeichnis)
  - [Über das Projekt](#über-das-projekt)
  - [Tech-Stack](#tech-stack)
    - [**Backend**](#backend)
    - [**Frontend**](#frontend)
    - [**Infrastruktur \& DevOps**](#infrastruktur--devops)
  - [Kernfunktionen](#kernfunktionen)
  - [Ausleih-Workflow](#ausleih-workflow)

---

## Über das Projekt

In Schulen werden Klassensätze von Büchern in physischen Kisten aufbewahrt. Dieses System vereinfacht die Verwaltung:
* Jede Kiste erhält einen **unveränderlichen QR-Code**.
* Beim Scannen mit dem Smartphone öffnet sich direkt die passende Ausleih- bzw. Rückgabemaske.
* Lehrer müssen sich nicht kompliziert registrieren; ein einfaches **Schul-Passwort** und ein ohnehin bestehendes **Namenskürzel** genügen.
* Falls eine Kiste nicht ordnungsgemäß ausgeloggt wurde, kann der nachfolgende Lehrer die Kiste übernehmen – der Rückgeber wird dennoch namentlich protokolliert, um Verlusten vorzubeugen und bei wem man bei Verlust nachfragen kann.

---

## Tech-Stack

### **Backend**
* **Programmiersprache:** Python 3.14+
* **Framework:** FastAPI (REST-API)
* **ORM & Datenbank:** SQLAlchemy mit PostgreSQL
* **Validierung & Datenmodelle:** Pydantic
* **Testing:** Pytest / Unittest (TDD-Ansatz)

### **Frontend**
* **Framework:** Single Page Application (Angular / React / Vue.js)
* **UI-Bibliothek:** Component Library (z.B. Angular Material / Tailwind)

### **Infrastruktur & DevOps**
* **Version Control:** Git & GitHub
* **Server-Umgebung:** Linux (Ubuntu Server / Rocky Linux in VirtualBox)
* **Webserver / Reverse Proxy:** Nginx
* **Automation:** Ansible (Playbook-basiertes Deployment)

---

## Kernfunktionen

* **📱 Dynamischer QR-Code Scan:** Direktes Aufrufen der Kisten-Statusseite ohne Suchen.
* **🔄 Smarte Ausleihe & Rückgabe:**
  * Kiste frei → Ausleihformular (Lehrer-Dropdown + Klasse).
  * Kiste belegt → Anzeige des aktuellen Ausleihers + Rückgabeformular (inkl. Eintragen des Rückgebers).
* **➕ Schnell-Registrierung:** Fehlende Lehrkräfte können direkt in der Ausleihmaske hinzugefügt werden.
* **🛡️ Passwort-Schutz:** Schul-Passwort für die Ausleihe, Admin-Passwort für die Verwaltung.
* **📊 Admin-Dashboard:** 
  * Kisten-Übersicht mit Live-Status und Suchfunktion.
  * Anlegen neuer Kisten und automatischer QR-Code-Export.
  * Vollständige Ausleih-Historie.

---

## Ausleih-Workflow

```text
[ QR-Code Scannen ] 
       │
       ▼
[ /scan/{kisten_id} ]
       │
       ├─► Status: VERFÜGBAR ──► [ Lehrer & Klasse wählen ] ──► [ Ausleihen ]
       │
       └─► Status: BELEGT    ──► [ Rückgeber wählen ]       ──► [ Zurückbringen ]