# Deployment Notes

This project now supports a hosted PostgreSQL database through environment variables.

## Required environment variables

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-app-domain.com
CSRF_TRUSTED_ORIGINS=https://your-app-domain.com
CORS_ALLOW_ALL_ORIGINS=False
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DBNAME
DB_SSLMODE=require
DB_CONN_MAX_AGE=60
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-app-password
DEFAULT_FROM_EMAIL=your-email@example.com
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Run migrations in production

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

## Create an admin user

```bash
python manage.py createsuperuser
```

## Local development

If `DATABASE_URL` is not set, Django uses the local PostgreSQL settings from `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`.

## Render

This repo includes [render.yaml](C:/Users/NEW%20USER/Documents/python%20projects/LOST%20AND%20FOUND/render.yaml:1) for Render.

On Render:

1. Push this project to GitHub.
2. In Render, create a new Blueprint and point it to the repo.
3. After the service is created, set:
   - `ALLOWED_HOSTS` to your Render domain, for example `your-app.onrender.com`
   - `CSRF_TRUSTED_ORIGINS` to `https://your-app.onrender.com`
   - `EMAIL_HOST_USER` to your real sender email
   - `EMAIL_HOST_PASSWORD` to your email app password
   - `DEFAULT_FROM_EMAIL` to the same sender email
4. Render will provide `DATABASE_URL` automatically from the managed PostgreSQL database in the blueprint.

The web service uses:

- Build command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
- Start command: `gunicorn foundIt.wsgi:application`
