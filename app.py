from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change in production

# MongoDB Atlas connection
client = MongoClient("mongodb+srv://hello:Gnana123@voting.8vt5bip.mongodb.net/?retryWrites=true&w=majority&appName=voting")
db = client["flask_auth"]
users_collection = db["users"]

@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users_collection.find_one({"username": username})
        if user and check_password_hash(user["password"], password):
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password!", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = users_collection.find_one({"username": username})
        if existing_user:
            flash("Username already exists!", "warning")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(password)
        users_collection.insert_one({"username": username, "password": hashed_pw})
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    
    users = list(users_collection.find({}, {"_id": 0, "username": 1}))
    return render_template("dashboard.html", username=session["username"], users=users)

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
