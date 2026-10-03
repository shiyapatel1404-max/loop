import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise RuntimeError(
        "MONGODB_URI is not configured. "
        "Create a .env file locally or add MONGODB_URI in Vercel Environment Variables."
    )

client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=10000,
    connectTimeoutMS=10000,
    maxPoolSize=10,
)

db = client[os.getenv("MONGODB_DB_NAME", "project_loop")]

users_collection = db["users"]
feedback_collection = db["feedback"]
reports_collection = db["reports"]


def init_db():
    # Indexes make common lookups faster and prevent duplicate user emails.
    users_collection.create_index("email", unique=True)
    feedback_collection.create_index("created_at")
    feedback_collection.create_index("sentiment")
    feedback_collection.create_index("category")
    feedback_collection.create_index("theme")

    # Create the demo/admin account only when it doesn't already exist.
    admin_email = os.getenv("ADMIN_EMAIL", "admin@loop.com").strip().lower()
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    admin_name = os.getenv("ADMIN_NAME", "LOOP Admin")

    if not users_collection.find_one({"email": admin_email}):
        users_collection.insert_one({
            "name": admin_name,
            "email": admin_email,
            "password": generate_password_hash(admin_password),
            "role": "admin",
            "created_at": datetime.now(timezone.utc),
        })
