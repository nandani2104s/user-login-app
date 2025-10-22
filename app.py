from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User
import os

app = Flask(__name__)
app.secret_key = 'secret_key'  # Replace with a real secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/images'

db.init_app(app)

# Home → redirect to login
@app.route('/')
def home():
    return redirect(url_for('login'))

# SIGNUP
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form
        profile_picture = request.files['profile_picture']

        if data['password'] != data['confirm_password']:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('signup'))

        # Save image
        picture_name = profile_picture.filename
        picture_path = os.path.join(app.config['UPLOAD_FOLDER'], picture_name)
        profile_picture.save(picture_path)

        new_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            profile_picture=picture_name,
            username=data['username'],
            email=data['email'],
            password=data['password'],  # No hashing for now
            address=f"{data['address_line1']}, {data['city']}, {data['state']} - {data['pincode']}",
            user_type=data['user_type']
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Signup successful. Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(username=data['username']).first()
        if user and user.password == data['password']:
            session['user_id'] = user.id
            if user.user_type == 'Doctor':
                return redirect(url_for('doctor_dashboard'))
            else:
                return redirect(url_for('patient_dashboard'))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

# PATIENT DASHBOARD
@app.route('/patient_dashboard')
def patient_dashboard():
    user = get_logged_in_user()
    return render_template('dashboard.html', user=user)

# DOCTOR DASHBOARD
@app.route('/doctor_dashboard')
def doctor_dashboard():
    user = get_logged_in_user()
    return render_template('dashboard.html', user=user)

# Helper to get user by session
def get_logged_in_user():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    return User.query.get(user_id)

# Run App
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
