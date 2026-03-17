# SL Theory Website

Small Flask app for exploring the drop-impact scaling theory described in the paper linked below. The browser collects Weber number `We` and Ohnesorge number `Oh`, then calls two JSON endpoints to compute Reynolds number and classify the impact regime.

- Paper: https://arxiv.org/abs/2408.12714
- Live site: https://unifying-theory-website.vercel.app/

## What's in the repo

```text
SLtheoryWebsite/
  app.py
  calculateReynoldsNumber.py
  regimeDecide.py
  templates/index.html
  requirements.txt
  runtime.txt
  vercel.json
```

`app.py` creates the Flask app, registers the blueprints, and runs the server locally. `calculateReynoldsNumber.py` serves the homepage and computes Reynolds number. `regimeDecide.py` classifies the regime from `We` and `Oh`.

## Local run

```bash
pip install -r requirements.txt
python app.py
```

The app is configured for Python 3.9 in `runtime.txt`.

## Endpoints

- `GET /` renders the single-page UI from `templates/index.html`.
- `POST /add` expects JSON like `{"weberNumber": 10, "ohnesorgeNumber": 0.1}` and returns `{"result": <Re>}`.
- `POST /regime` expects the same JSON and returns `{"regime": "I" | "II" | "III" | "IV"}`.

The frontend calls `/add` and `/regime` separately after the user submits the input form.

## Deployment

`vercel.json` routes all traffic to `app.py` using `@vercel/python`, so Vercel is the intended deployment target.

## Notes

- The code validates that inputs are present and numeric, but it does not enforce physical bounds. Use positive values for `We` and `Oh`; `Oh = 0` will break the Reynolds calculation.
- `Flask-SocketIO` is installed, but there are no socket handlers in the current app.
- The page loads MathJax and a polyfill from external CDNs and embeds a YouTube iframe, so full rendering depends on external network access.
