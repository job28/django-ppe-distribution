# PPE-Project

A Django-based PPE surplus donation and distribution platform (Irish Rail PPE initiative) that lists available items (tops, trousers, steel-toe boots), allows users to reserve/purchase with a nominal donation, and schedules pickup via local hubs.

## ✨ Features
- Item catalog (list & detail views)
- Simple cart / reservation flow
- Pickup hub scheduling (date, time, location)
- Email notifications (optional) and ICS calendar invite (placeholder)
- Admin interface for items, orders, and hubs
- Guest checkout supported; login optional (configurable)

## 🧰 Tech Stack
- Python 3.10+
- Django 4.x (Admin, ORM, Templates)
- SQLite (dev) / PostgreSQL (prod recommended)
- HTML/CSS/Bootstrap (or Tailwind) for UI
- Gunicorn/uvicorn + nginx (prod), or Django dev server (local)

## 🚀 Quickstart (Local)
```bash
# 1) Create & activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Environment variables
# Create a .env file in the repo root and set values as needed (see below).

# 4) Run migrations & create a superuser
python manage.py migrate
python manage.py createsuperuser

# 5) (Optional) load sample data
# python manage.py loaddata sample_data.json

# 6) Start the dev server
python manage.py runserver
```

Then open http://127.0.0.1:8000/ in your browser.

## 🔑 Environment variables (.env)
Create a `.env` file in the project root. Common keys:

```
# Django
DEBUG=True
SECRET_KEY=change-me
ALLOWED_HOSTS=127.0.0.1,localhost

# Database (SQLite by default). Example for Postgres:
# DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/DBNAME

# Email (optional)
# EMAIL_HOST=smtp.example.com
# EMAIL_HOST_USER=your_user
# EMAIL_HOST_PASSWORD=your_password
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
```

Use `django-environ` or similar to load these safely in `settings.py` (see `INSTALLED_APPS` and env handling).

## 🗂️ Project layout
- `manage.py` – Django entrypoint
- Core project settings: `PPE-Project/ppeproject/ppeproject`
- Apps: `apps/` or inside project folder (e.g., `items`, `orders`, `pickup`)
- Templates: `templates/`
- Static files: `static/`
- Media uploads: `media/`

## 🧪 Tests
```bash
pytest         # or: python manage.py test
```

## 🛫 Deployment notes
- Use environment variables for secrets and DB
- Collect static files: `python manage.py collectstatic`
- Configure a production server (Gunicorn + nginx or a PaaS)
- Set `DEBUG=False` and configure `ALLOWED_HOSTS`
- Use Postgres in production

## 📄 License
MIT — see [LICENSE](LICENSE).

## 🤝 Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📫 Security
See [SECURITY.md](SECURITY.md).
