# FastAPI User Module Boilerplate

## Features
- User registration (with email activation)
- Login (JWT)
- Forgot/reset/change password (with email)
- User detail endpoints

## Quickstart

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Initialize the database**

```bash
python -c "from app.db.base import Base; from app.db.session import engine; import app.models.user; Base.metadata.create_all(bind=engine)"
```

3. **Run the server**

```bash
uvicorn app.main:app --reload
```

4. **Test the API**

- Register: `POST /api/register`
- Activate: Click link in simulated email (console)
- Login: `POST /api/login` (OAuth2 form)
- Forgot password: `POST /api/forgot-password`
- Reset password: Click link in simulated email (console)
- Change password: `POST /api/change-password` (auth required)
- Get/update profile: `/api/me` (auth required)

**All emails are simulated and printed to the console.**

---

## Notes
- Default DB is SQLite (`test.db`).
- You can swap out the email utility for real SMTP.
- For production, change the `SECRET_KEY` in `app/core/security.py`. 