# Peak Power — Django with Profiles & Image Uploads

Features:
- CRUD workouts with image
- User signup/login
- User profile with avatar & bio
- REST API

Run locally:
```bash
python -m venv .venv
source .venv/bin/activate  # or .\\.venv\\Scripts\\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```