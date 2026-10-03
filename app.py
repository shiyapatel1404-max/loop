import os
from functools import wraps
from datetime import datetime, timezone

from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import check_password_hash

from database import init_db, users_collection, feedback_collection, reports_collection
from ai_service import analyze_feedback

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-only-change-me")

# Initialize indexes/default admin. Safe to call on each serverless cold start.
init_db()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    try:
        return users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        session.clear()
        return None


def serialize_feedback(doc):
    if not doc:
        return None

    item = dict(doc)
    item["id"] = str(item.pop("_id"))
    if isinstance(item.get("created_at"), datetime):
        item["created_at"] = item["created_at"].astimezone(timezone.utc).strftime(
            "%Y-%m-%d %H:%M"
        )
    return item


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = users_collection.find_one({"email": email})

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = str(user["_id"])
            session["user_name"] = user.get("name", "User")
            session["role"] = user.get("role", "user")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        user=get_current_user(),
    )


@app.route("/feedback")
@login_required
def feedback():
    documents = feedback_collection.find().sort("created_at", -1).limit(200)
    feedback_items = [serialize_feedback(doc) for doc in documents]
    return render_template("feedback.html", feedback=feedback_items)


@app.route("/feedback/add", methods=["GET", "POST"])
@login_required
def add_feedback():
    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip()
        customer_email = request.form.get("customer_email", "").strip()
        source = request.form.get("source", "Website").strip()
        rating_raw = request.form.get("rating", "").strip()
        message = request.form.get("message", "").strip()

        if not message:
            flash("Feedback message is required.", "error")
            return render_template("add_feedback.html")

        try:
            rating = int(rating_raw) if rating_raw else None
            if rating is not None and not 1 <= rating <= 5:
                raise ValueError
        except ValueError:
            flash("Rating must be between 1 and 5.", "error")
            return render_template("add_feedback.html")

        analysis = analyze_feedback(message, rating)

        document = {
            "customer_name": customer_name,
            "customer_email": customer_email,
            "source": source,
            "rating": rating,
            "message": message,
            "sentiment": analysis["sentiment"],
            "sentiment_score": analysis["sentiment_score"],
            "category": analysis["category"],
            "theme": analysis["theme"],
            "priority": analysis["priority"],
            "keywords": analysis["keywords"],
            "created_at": datetime.now(timezone.utc),
            "created_by": session.get("user_id"),
        }

        feedback_collection.insert_one(document)
        flash("Feedback added successfully.", "success")
        return redirect(url_for("feedback"))

    return render_template("add_feedback.html")


@app.route("/api/dashboard")
@login_required
def dashboard_api():
    total = feedback_collection.count_documents({})

    positive = feedback_collection.count_documents({"sentiment": "Positive"})
    negative = feedback_collection.count_documents({"sentiment": "Negative"})
    neutral = feedback_collection.count_documents({"sentiment": "Neutral"})

    category_pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    categories = [
        {"name": item["_id"] or "General", "count": item["count"]}
        for item in feedback_collection.aggregate(category_pipeline)
    ]

    theme_pipeline = [
        {"$group": {"_id": "$theme", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 8},
    ]
    themes = [
        {"name": item["_id"] or "General", "count": item["count"]}
        for item in feedback_collection.aggregate(theme_pipeline)
    ]

    recent_cursor = feedback_collection.find().sort("created_at", -1).limit(8)
    recent = [serialize_feedback(doc) for doc in recent_cursor]

    return jsonify({
        "total": total,
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "categories": categories,
        "themes": themes,
        "recent": recent,
    })


@app.route("/api/feedback/<feedback_id>")
@login_required
def feedback_detail_api(feedback_id):
    try:
        document = feedback_collection.find_one({"_id": ObjectId(feedback_id)})
    except Exception:
        return jsonify({"error": "Invalid feedback ID"}), 400

    if not document:
        return jsonify({"error": "Feedback not found"}), 404

    return jsonify(serialize_feedback(document))


@app.route("/api/feedback/<feedback_id>", methods=["DELETE"])
@login_required
def delete_feedback(feedback_id):
    try:
        result = feedback_collection.delete_one({"_id": ObjectId(feedback_id)})
    except Exception:
        return jsonify({"error": "Invalid feedback ID"}), 400

    if result.deleted_count == 0:
        return jsonify({"error": "Feedback not found"}), 404

    return jsonify({"success": True})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
