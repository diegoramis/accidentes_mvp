import os
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import qrcode

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / 'static' / 'uploads'
QR_DIR = BASE_DIR / 'static' / 'qrcodes'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
QR_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cambia-esta-clave-en-produccion'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'instance' / 'accidentes.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB por archivo

db = SQLAlchemy(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    accidents = db.relationship('AccidentCase', backref='owner', lazy=True)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)


class AccidentCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_token = db.Column(db.String(64), unique=True, nullable=False, default=lambda: uuid.uuid4().hex)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    event_date = db.Column(db.String(30), nullable=False)
    event_time = db.Column(db.String(20), nullable=False)
    location_text = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.String(40), nullable=False)
    longitude = db.Column(db.String(40), nullable=False)
    narrative = db.Column(db.Text, nullable=False)
    damaged_only = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(30), default='Registrado')
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    drivers = db.relationship('Driver', backref='accident_case', cascade='all, delete-orphan', lazy=True)
    vehicles = db.relationship('Vehicle', backref='accident_case', cascade='all, delete-orphan', lazy=True)
    photos = db.relationship('Photo', backref='accident_case', cascade='all, delete-orphan', lazy=True)


class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    accident_id = db.Column(db.Integer, db.ForeignKey('accident_case.id'), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    license_number = db.Column(db.String(60), nullable=False)
    phone = db.Column(db.String(40), nullable=True)


class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    accident_id = db.Column(db.Integer, db.ForeignKey('accident_case.id'), nullable=False)
    owner_name = db.Column(db.String(120), nullable=False)
    plate = db.Column(db.String(20), nullable=False)
    brand = db.Column(db.String(60), nullable=False)
    model = db.Column(db.String(60), nullable=False)
    color = db.Column(db.String(40), nullable=True)


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    accident_id = db.Column(db.Integer, db.ForeignKey('accident_case.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return User.query.get(uid)


@app.context_processor
def inject_user():
    return {'current_user': current_user()}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('Ya existe un usuario con ese correo.', 'danger')
            return redirect(url_for('register'))

        user = User(full_name=full_name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Usuario creado correctamente. Ahora inicia sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Correo o contraseña incorrectos.', 'danger')
            return redirect(url_for('login'))

        session['user_id'] = user.id
        flash('Sesión iniciada correctamente.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    cases = AccidentCase.query.filter_by(owner_id=user.id).order_by(AccidentCase.created_at.desc()).all()
    return render_template('dashboard.html', cases=cases)


@app.route('/accidents/new', methods=['GET', 'POST'])
def new_accident():
    user = current_user()
    if not user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        accident = AccidentCase(
            event_date=request.form['event_date'],
            event_time=request.form['event_time'],
            location_text=request.form['location_text'],
            latitude=request.form['latitude'],
            longitude=request.form['longitude'],
            narrative=request.form['narrative'],
            damaged_only=True,
            owner_id=user.id,
        )
        db.session.add(accident)
        db.session.flush()

        # Conductores
        for i in [1, 2]:
            driver = Driver(
                accident_id=accident.id,
                full_name=request.form.get(f'driver{i}_name', ''),
                license_number=request.form.get(f'driver{i}_license', ''),
                phone=request.form.get(f'driver{i}_phone', ''),
            )
            db.session.add(driver)

        # Vehículos
        for i in [1, 2]:
            vehicle = Vehicle(
                accident_id=accident.id,
                owner_name=request.form.get(f'vehicle{i}_owner', ''),
                plate=request.form.get(f'vehicle{i}_plate', ''),
                brand=request.form.get(f'vehicle{i}_brand', ''),
                model=request.form.get(f'vehicle{i}_model', ''),
                color=request.form.get(f'vehicle{i}_color', ''),
            )
            db.session.add(vehicle)

        categories = {
            'vehicle_review': request.files.getlist('vehicle_review'),
            'driver_licenses': request.files.getlist('driver_licenses'),
            'vehicle_damage': request.files.getlist('vehicle_damage'),
        }

        for category, files in categories.items():
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    unique_name = f"{uuid.uuid4().hex}.{ext}"
                    filepath = UPLOAD_DIR / unique_name
                    file.save(filepath)
                    db.session.add(Photo(accident_id=accident.id, category=category, file_path=f'uploads/{unique_name}'))

        db.session.commit()
        generate_qr(accident.public_token, request.url_root.rstrip('/'))
        flash('Caso registrado correctamente.', 'success')
        return redirect(url_for('case_detail', case_id=accident.id))

    return render_template('new_accident.html')


@app.route('/accidents/<int:case_id>')
def case_detail(case_id):
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    case = AccidentCase.query.filter_by(id=case_id, owner_id=user.id).first_or_404()
    return render_template('case_detail.html', case=case)


@app.route('/public/case/<token>')
def public_case(token):
    case = AccidentCase.query.filter_by(public_token=token).first_or_404()
    return render_template('public_case.html', case=case)


@app.route('/qrcodes/<path:filename>')
def qrcode_file(filename):
    return send_from_directory(QR_DIR, filename)


def generate_qr(token: str, base_url: str):
    public_url = f"{base_url}/public/case/{token}"
    img = qrcode.make(public_url)
    img.save(QR_DIR / f"{token}.png")


@app.cli.command('init-db')
def init_db_command():
    db.create_all()
    print('Base de datos inicializada.')


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
