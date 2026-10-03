# Project LOOP

Project LOOP is a simple Flask + MongoDB customer feedback intelligence MVP.

## Stack

- Python
- Flask
- MongoDB Atlas
- PyMongo
- HTML/CSS/JavaScript
- Chart.js
- Vercel

## Features

- Login/logout
- Feedback collection
- Keyword-based sentiment analysis
- Sentiment score
- Category detection
- Theme detection
- Priority detection
- Dashboard analytics
- Sentiment chart
- Category chart
- Top themes
- Recent feedback
- Delete feedback
- MongoDB persistence
- Vercel-ready environment configuration

## 1. Create MongoDB Atlas

Create a MongoDB Atlas deployment and a database user.

In Atlas, use:

Connect → Drivers → Python

Copy the connection string and replace its password placeholder.

MongoDB's official PyMongo documentation recommends using `MongoClient` with the Atlas connection URI. Keep the URI out of source control and provide it through an environment variable.

## 2. Local setup

Create a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in:

```env
MONGODB_URI=your_mongodb_atlas_connection_string
MONGODB_DB_NAME=project_loop
SECRET_KEY=your-secret-key
ADMIN_EMAIL=admin@loop.com
ADMIN_PASSWORD=admin123
```

Run:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

Default demo login:

```text
Email: admin@loop.com
Password: admin123
```

Change the admin password before using the app publicly.

## 3. Deploy to Vercel

Push this project to GitHub.

Then:

1. Open Vercel.
2. Add New Project.
3. Import your GitHub repository.
4. Vercel should detect the Flask application automatically.
5. Add these Environment Variables:

```text
MONGODB_URI
MONGODB_DB_NAME
SECRET_KEY
ADMIN_EMAIL
ADMIN_PASSWORD
ADMIN_NAME
```

6. Deploy.

No SQLite database file is required.

No `/api/index.py` or custom routing file is required for current Vercel Flask deployments.

## Important MongoDB Atlas setting

Your Atlas cluster must allow connections from your Vercel deployment.

For a portfolio/demo deployment, you can configure the Atlas network access according to your security requirements. Avoid exposing database credentials in the repository.

## Production notes

The application uses hashed passwords with Werkzeug instead of storing plain-text passwords.

MongoDB indexes are created for email, creation time, sentiment, category, and theme.

The current AI analysis is intentionally simple and local. The next step can replace `ai_service.py` with an actual LLM-powered analysis service.

For a larger SaaS version, add organizations/tenants and enforce `tenant_id` filtering on every feedback/report query.
