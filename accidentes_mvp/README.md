# Sistema de Registro de Accidentes sin Lesionados

MVP web para registrar accidentes de tránsito donde solo hubo daños materiales. Incluye:

- Registro e inicio de sesión de usuarios
- Registro de conductores y vehículos involucrados
- Captura de geolocalización
- Carga de fotos de revisión del vehículo, licencias y daños
- Generación de código QR para consulta del caso
- Vista pública para tránsito y aseguradoras
- Base de datos SQL (SQLite para demo)

## Stack

- Python + Flask
- SQLite / SQL
- HTML + CSS + JavaScript

## Cómo ejecutarlo

```bash
python -m venv .venv
source .venv/bin/activate   # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask --app app init-db
python app.py
```

Abrir en el navegador:

```bash
http://127.0.0.1:5000
```

## Estructura

```text
accidentes_mvp/
├── app.py
├── schema.sql
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── new_accident.html
│   ├── case_detail.html
│   └── public_case.html
└── static/
    ├── style.css
    ├── app.js
    ├── uploads/
    └── qrcodes/
```

## Subir a GitHub

```bash
git init
git add .
git commit -m "Primer MVP sistema de accidentes"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/TU-REPOSITORIO.git
git push -u origin main
```

## Mejoras recomendadas para producción

- Cambiar SQLite por PostgreSQL o MySQL
- Guardar archivos en almacenamiento seguro (S3, Cloudinary, etc.)
- Autenticación robusta y variables de entorno
- Roles separados para tránsito y aseguradoras
- Firma digital del reporte
- Historial de cambios y auditoría
- Despliegue en Render, Railway o Heroku-like platform

## Nota

Este proyecto está diseñado como demostración funcional para mostrarlo en GitHub. Antes de usarlo en producción, conviene reforzar seguridad, validaciones legales y protección de datos personales.
