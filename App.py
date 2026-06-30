
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 19:21:39 2023

@author: hp
"""

from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from models import db, User, Patient
import os
import numpy as np
import pickle
from datetime import datetime, timedelta
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import func, distinct

model = pickle.load(open("model.pkl", "rb"))
app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-here"  # Change this to a secure secret key
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Flask extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

SYMPTOMS = [
    "itching",
    "continuous_sneezing",
    "shivering",
    "joint_pain",
    "stomach_pain",
    "vomiting",
    "fatigue",
    "weight_loss",
    "restlessness",
    "lethargy",
    "high_fever",
    "headache",
    "dark_urine",
    "nausea",
    "pain_behind_the_eyes",
    "constipation",
    "abdominal_pain",
    "diarrhoea",
    "mild_fever",
    "yellowing_of_eyes",
    "malaise",
    "phlegm",
    "congestion",
    "chest_pain",
    "fast_heart_rate",
    "neck_pain",
    "dizziness",
    "puffy_face_and_eyes",
    "knee_pain",
    "muscle_weakness",
    "passage_of_gases",
    "irritability",
    "muscle_pain",
    "belly_pain",
    "abnormal_menstruation",
    "increased_appetite",
    "lack_of_concentration",
    "visual_disturbances",
    "receiving_blood_transfusion",
    "coma",
    "history_of_alcohol_consumption",
    "blood_in_sputum",
    "palpitations",
    "inflammatory_nails",
    "yellow_crust_ooze",
]


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


# Create database tables
with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("researcher_dashboard"))
        else:
            flash("Invalid email or password")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(email=email).first():
            flash("Email already registered")
            return redirect(url_for("signup"))

        user = User(email=email, is_researcher=True)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for("researcher_dashboard"))

    return render_template("signup.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/researcher_dashboard")
@login_required
def researcher_dashboard():
    if not current_user.is_researcher:
        flash("Access denied. Researcher privileges required.", "danger")
        return redirect(url_for("home"))

    # Get page number from query parameters
    page = request.args.get("page", 1, type=int)
    per_page = 10  # Number of records per page

    # Get all patients for dropdowns
    all_patients = Patient.query.all()

    # Get paginated patient records for table
    paginated_patients = Patient.query.order_by(Patient.date_added.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Calculate statistics
    stats = {
        "total_patients": len(set(p.patient_id for p in all_patients)),
        "total_diagnoses": len(set(p.diagnosis for p in all_patients)),
        "recent_cases": len(
            [p for p in all_patients if (datetime.utcnow() - p.date_added).days <= 7]
        ),
    }

    return render_template(
        "researcher_dashboard.html",
        patients=paginated_patients,
        all_patients=all_patients,
        stats=stats,
    )


@app.route("/visualization")
@login_required
def visualization():
    if not current_user.is_researcher:
        flash("Access denied. Researcher privileges required.", "danger")
        return redirect(url_for("home"))

    # Get all patient records
    patients = Patient.query.all()

    # Prepare data for charts
    # 1. Disease Distribution
    disease_counts = {}
    for p in patients:
        disease_counts[p.diagnosis] = disease_counts.get(p.diagnosis, 0) + 1

    # 2. Age Distribution
    age_groups = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "80+": 0}
    for p in patients:
        age = p.patient_user.age
        if age <= 20:
            age_groups["0-20"] += 1
        elif age <= 40:
            age_groups["21-40"] += 1
        elif age <= 60:
            age_groups["41-60"] += 1
        elif age <= 80:
            age_groups["61-80"] += 1
        else:
            age_groups["80+"] += 1

    # 3. Gender Distribution
    gender_counts = {"Male": 0, "Female": 0}
    for p in patients:
        gender_counts[p.patient_user.gender] += 1

    # 4. Symptoms Frequency
    symptom_counts = {}
    for p in patients:
        for symptom in p.symptoms:
            symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1

    # 5. Timeline of Cases
    timeline_data = {}
    for p in patients:
        date_str = p.date_added.strftime("%Y-%m-%d")
        timeline_data[date_str] = timeline_data.get(date_str, 0) + 1

    # Sort the data
    disease_data = dict(
        sorted(disease_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    )
    symptom_data = dict(
        sorted(symptom_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    )
    timeline_data = dict(sorted(timeline_data.items()))

    return render_template(
        "visualization.html",
        disease_data=disease_data,
        age_data=age_groups,
        gender_data=gender_counts,
        symptom_data=symptom_data,
        timeline_data=timeline_data,
    )


@app.route("/details")
def pred():
    return render_template("details.html")


def get_available_researcher():
    """Get a researcher with the least number of assigned patients"""
    researchers = User.query.filter_by(is_researcher=True).all()
    if not researchers:
        return None

    # Get researcher with least assigned patients
    researcher_loads = [
        (r, Patient.query.filter_by(researcher_id=r.id).count()) for r in researchers
    ]
    return min(researcher_loads, key=lambda x: x[1])[0]


@app.route("/predict", methods=["POST", "GET"])
def predict():
    if request.method == "POST":
        # Get patient details
        patient_data = {
            "name": request.form.get("name"),
            "age": request.form.get("age"),
            "gender": request.form.get("gender"),
            "blood_group": request.form.get("blood_group"),
            "contact": request.form.get("contact"),
        }

        # Get symptoms (skip the patient details fields)
        symptoms = [request.form.get(f"symptom{i}") for i in range(1, 10)]
        symptoms = [s for s in symptoms if s]  # Remove empty values

        b = [0] * 45
        for x in range(0, 45):
            for y in symptoms:
                if SYMPTOMS[x] == y:
                    b[x] = 1
        b = np.array(b)
        b = b.reshape(1, 45)
        prediction = model.predict(b)
        prediction = prediction[0]

        # Get an available researcher
        researcher = get_available_researcher()

        # Create a new user for the patient
        patient_user = User(
            name=patient_data["name"],
            age=patient_data["age"],
            gender=patient_data["gender"],
            blood_group=patient_data["blood_group"],
            contact=patient_data["contact"],
            email=f"patient_{datetime.utcnow().timestamp()}@temp.com",  # Temporary email
            is_researcher=False,
        )
        db.session.add(patient_user)
        db.session.flush()  # Get the ID without committing

        # Save diagnosis
        patient = Patient(
            symptoms=symptoms,
            diagnosis=prediction,
            patient_id=patient_user.id,
            researcher_id=researcher.id if researcher else None,
        )
        db.session.add(patient)
        db.session.commit()

        return render_template(
            "results.html",
            prediction_text=f"The probable diagnosis for {patient_data['name']} is {prediction}",
        )
    return render_template("details.html")


@app.route("/calculate-similarity", methods=["POST"])
@login_required
def calculate_similarity():
    patient1_id = request.form.get("patient1")
    patient2_id = request.form.get("patient2")

    patient1 = Patient.query.get(patient1_id)
    patient2 = Patient.query.get(patient2_id)

    # Convert symptoms to vectors
    all_symptoms = set(SYMPTOMS)  # Changed from col to SYMPTOMS

    def symptoms_to_vector(symptoms):
        return [1 if symptom in symptoms else 0 for symptom in all_symptoms]

    vector1 = symptoms_to_vector(patient1.symptoms)
    vector2 = symptoms_to_vector(patient2.symptoms)

    # Calculate cosine similarity
    similarity = cosine_similarity([vector1], [vector2])[0][0]
    similarity_percentage = round(similarity * 100, 2)

    # Find common symptoms
    common_symptoms = set(patient1.symptoms) & set(patient2.symptoms)

    return jsonify(
        {
            "similarity_score": similarity_percentage,
            "common_symptoms": list(common_symptoms),
        }
    )


@app.route("/patient-login", methods=["GET", "POST"])
def patient_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email, is_researcher=False).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("pred"))
        else:
            flash("Invalid email or password")

    return render_template("patient_login.html")


@app.route("/patient-signup", methods=["GET", "POST"])
def patient_signup():
    if request.method == "POST":
        email = request.form.get("email")
        if User.query.filter_by(email=email).first():
            flash("Email already registered")
            return redirect(url_for("patient_signup"))

        user = User(
            email=email,
            name=request.form.get("name"),
            age=request.form.get("age"),
            gender=request.form.get("gender"),
            blood_group=request.form.get("blood_group"),
            contact=request.form.get("contact"),
            is_researcher=False,
        )
        user.set_password(request.form.get("password"))

        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for("pred"))

    return render_template("patient_signup.html")


@app.route("/patient-similarity", methods=["GET"])
@login_required
def get_patient_similarity():
    # Get patient IDs from query parameters
    patient1_id = request.args.get("patient1")
    patient2_id = request.args.get("patient2")

    if not patient1_id or not patient2_id:
        return (
            jsonify(
                {"error": "Both patient1 and patient2 query parameters are required"}
            ),
            400,
        )

    try:
        patient1 = Patient.query.get(patient1_id)
        patient2 = Patient.query.get(patient2_id)

        if not patient1 or not patient2:
            return jsonify({"error": "One or both patients not found"}), 404

        # Convert symptoms to vectors
        all_symptoms = set(SYMPTOMS)

        def symptoms_to_vector(symptoms):
            return [1 if symptom in symptoms else 0 for symptom in all_symptoms]

        vector1 = symptoms_to_vector(patient1.symptoms)
        vector2 = symptoms_to_vector(patient2.symptoms)

        # Calculate cosine similarity
        similarity = cosine_similarity([vector1], [vector2])[0][0]
        similarity_percentage = round(similarity * 100, 2)

        # Find common symptoms
        common_symptoms = set(patient1.symptoms) & set(patient2.symptoms)

        return jsonify(
            {
                "similarity_score": similarity_percentage,
                "common_symptoms": list(common_symptoms),
                "patient1": {
                    "id": patient1.id,
                    "name": patient1.patient_user.name,
                    "diagnosis": patient1.diagnosis,
                },
                "patient2": {
                    "id": patient2.id,
                    "name": patient2.patient_user.name,
                    "diagnosis": patient2.diagnosis,
                },
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "error": "An error occurred while calculating similarity",
                    "details": str(e),
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(debug=True)
