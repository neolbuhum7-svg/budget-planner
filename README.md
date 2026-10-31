# Budget Planner

A simple budget planner web app built with Flask and SQLite.

## Run locally

```
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

## Deploy on Render

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
