# Obrify

Gestión económica de obras de reforma. Web para uso interno con potencial futuro de SaaS.

**Stack**: Django 5 + Bootstrap 5 + HTMX. SQLite en desarrollo, Postgres en producción. Sin Docker.

## Arrancar en local

Requisitos: Python 3.12+ instalado.

```bash
# 1. Clonar y entrar
git clone <url>
cd Obrify

# 2. Crear entorno virtual e instalar
python -m venv .venv
source .venv/bin/activate      # Linux / Mac
# .venv\Scripts\activate       # Windows

pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# (edita .env si quieres cambiar SECRET_KEY o usar Postgres)

# 4. Crear tablas
python manage.py migrate

# 5. Crear tu primera organización y usuario admin
python manage.py createsuperuser
# email: tu@email.com
# password: (elige uno)

# 6. Arrancar
python manage.py runserver
```

Abre <http://localhost:8000> → te lleva a login.

## Primera configuración

1. Entra con el superusuario que creaste.
2. Ve a <http://localhost:8000/admin/core/organizacion/add/> y crea la empresa (por ejemplo, la empresa de tu tío).
3. Vuelve a <http://localhost:8000/admin/core/usuario/> y asigna esa organización a tu usuario.
4. Ya puedes crear clientes y obras desde el admin: <http://localhost:8000/admin/>.

## Estructura del proyecto

```
obrify/
├── config/               # Configuración Django
├── apps/
│   ├── core/             # Organización + Usuario (login por email)
│   └── projects/         # Cliente + Obra
├── templates/            # Plantillas HTML (Bootstrap 5)
├── static/               # CSS propio
├── requirements.txt
├── .env.example
└── manage.py
```

## Próximos pasos (roadmap MVP)

- [x] Semana 1 — Base, auth, cliente, obra
- [ ] Semana 2 — Catálogo de partidas, proveedores
- [ ] Semana 3 — Presupuestos con editor y PDF
- [ ] Semana 4 — Facturas con extracción híbrida (pdfplumber + Tesseract)
- [ ] Semana 5 — Empleados, horas, dashboard obra, informe semanal PDF

## Despliegue en VPS

Pendiente de definir cuando el MVP esté listo (semana 5-6). Plan: gunicorn + nginx + Let's Encrypt.
