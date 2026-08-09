# Curriculum Recommender

A professional-grade curriculum planning platform with:
- constraint-based skill matching
- skills gap analysis against job postings
- career-track matching and course recommendation
- demo authentication and profile persistence hooks
- a modern dashboard experience

## Quick start

1. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. Start the API:
   ```bash
   python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000 --reload
   ```
3. Open the dashboard at http://127.0.0.1:8000/ui/dashboard.html
4. Open the legacy UI at http://127.0.0.1:8000/ui

## Expanded data generation

Run the dataset expansion utility to create a richer course catalog and synthetic job postings:

```bash
python backend/dataset_expander.py
```

## Deployment

- GitHub Actions workflow: [.github/workflows/ci.yml](.github/workflows/ci.yml)
- Vercel config: [vercel.json](vercel.json)
- Render/Heroku-style startup: [Procfile](Procfile)

## Environment variables

Copy `.env.example` to `.env` and update values as needed.

## Testing

Run the regression tests with:

```bash
python -m unittest discover -s tests -v
```
