server {
    listen 80;
    server_name _;

    # 1. Frontend: Statische Vue.js-Dateien aus dem dist-Ordner ausliefern
    location / {
        root /home/milan/Buecher_Ausleihe/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 2. Backend: API-Anfragen an FastAPI/Uvicorn weiterleiten
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /api;
    }

    # 3. Backend: QR-Code Bild-Downloads/Anzeigen direkt routen (falls nötig)
    location /static/ {
        alias /home/milan/Buecher_Ausleihe/backend/static/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}




[Unit]
Description=FastAPI Backend for Book Crate Rental System
After=network.target postgresql.service

[Service]
User=milan
WorkingDirectory=/home/milan/Buecher_Ausleihe/backend/
ExecStart=/home/milan/Buecher_Ausleihe/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
Environment="PATH=/home/milan/Buecher_Ausleihe/backend/venv/bin"

[Install]
WantedBy=multi-user.target