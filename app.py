from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'aa-solution-secret-key-change-this-123456'

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==================== DATABASE MODELS ====================

class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='new')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class HiringApplication(db.Model):
    __tablename__ = 'hiring_applications'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.String(50), nullable=False)
    qualification = db.Column(db.String(100), nullable=False)
    current_location = db.Column(db.String(100), nullable=False)
    skills = db.Column(db.Text, nullable=False)
    cover_letter = db.Column(db.Text)
    status = db.Column(db.String(20), default='new')  # new, reviewed, shortlisted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)


class Newsletter(db.Model):
    __tablename__ = 'newsletter'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)


# ==================== HELPERS ====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please login to access admin panel', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


@app.context_processor
def inject_globals():
    return {
        'current_year': datetime.now().year,
        'company_name': 'A&A Solution'
    }


def init_db():
    with app.app_context():
        db.create_all()
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(username='admin', email='admin@aasolution.com')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin created: admin / admin123")


# ==================== PUBLIC ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/countries')
def countries():
    return render_template('countries.html')

@app.route('/coaching')
def coaching():
    return render_template('coaching.html')

@app.route('/visa')
def visa():
    return render_template('visa.html')

@app.route('/hiring', methods=['GET', 'POST'])
def hiring():
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        position = request.form.get('position', '').strip()
        experience = request.form.get('experience', '').strip()
        qualification = request.form.get('qualification', '').strip()
        current_location = request.form.get('current_location', '').strip()
        skills = request.form.get('skills', '').strip()
        cover_letter = request.form.get('cover_letter', '').strip()
        
        errors = []
        if not full_name or len(full_name) < 2:
            errors.append('Please enter valid name')
        if not email or '@' not in email:
            errors.append('Please enter valid email')
        if not phone or len(phone) < 10:
            errors.append('Please enter valid phone')
        if not position:
            errors.append('Please select position')
        if not skills or len(skills) < 5:
            errors.append('Please enter your skills')
        
        if errors:
            if is_ajax:
                return jsonify({'success': False, 'message': ' | '.join(errors)}), 400
            for e in errors:
                flash(e, 'error')
            return redirect(url_for('hiring'))
        
        try:
            application = HiringApplication(
                full_name=full_name, email=email, phone=phone,
                position=position, experience=experience,
                qualification=qualification, current_location=current_location,
                skills=skills, cover_letter=cover_letter
            )
            db.session.add(application)
            db.session.commit()
            
            msg = f'Thank you {full_name}! Your application has been submitted successfully. We will contact you soon.'
            if is_ajax:
                return jsonify({'success': True, 'message': msg})
            flash(msg, 'success')
            return redirect(url_for('hiring'))
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            if is_ajax:
                return jsonify({'success': False, 'message': 'Submission failed'}), 500
            flash('Submission failed. Please try again.', 'error')
            return redirect(url_for('hiring'))
    
    return render_template('hiring.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        errors = []
        if not name or len(name) < 2: errors.append('Invalid name')
        if not email or '@' not in email: errors.append('Invalid email')
        if not phone or len(phone) < 10: errors.append('Invalid phone')
        if not subject: errors.append('Select subject')
        if not message or len(message) < 10: errors.append('Message too short')
        
        if errors:
            if is_ajax:
                return jsonify({'success': False, 'message': ' | '.join(errors)}), 400
            for e in errors: flash(e, 'error')
            return redirect(url_for('contact'))
        
        try:
            new_contact = Contact(name=name, email=email, phone=phone, subject=subject, message=message)
            db.session.add(new_contact)
            db.session.commit()
            msg = f'Thank you {name}! Message sent successfully.'
            if is_ajax: return jsonify({'success': True, 'message': msg})
            flash(msg, 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            db.session.rollback()
            if is_ajax: return jsonify({'success': False, 'message': 'Error'}), 500
            flash('Error occurred', 'error')
            return redirect(url_for('contact'))
    
    return render_template('contact.html')


@app.route('/newsletter', methods=['POST'])
def newsletter():
    email = request.form.get('email', '').strip()
    if not email or '@' not in email:
        return jsonify({'success': False, 'message': 'Invalid email'}), 400
    if Newsletter.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Already subscribed'}), 400
    try:
        db.session.add(Newsletter(email=email))
        db.session.commit()
        return jsonify({'success': True, 'message': 'Subscribed successfully!'})
    except:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed'}), 500


# ==================== ADMIN ROUTES ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Logged out', 'success')
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    stats = {
        'total_contacts': Contact.query.count(),
        'new_contacts': Contact.query.filter_by(status='new').count(),
        'total_applications': HiringApplication.query.count(),
        'new_applications': HiringApplication.query.filter_by(status='new').count(),
        'total_subscribers': Newsletter.query.count(),
        'recent_contacts': Contact.query.order_by(Contact.created_at.desc()).limit(5).all(),
        'recent_applications': HiringApplication.query.order_by(HiringApplication.created_at.desc()).limit(5).all()
    }
    return render_template('admin/dashboard.html', stats=stats)


@app.route('/admin/contacts')
@login_required
def admin_contacts():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    search = request.args.get('search', '').strip()
    query = Contact.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    if search:
        query = query.filter(db.or_(Contact.name.contains(search), Contact.email.contains(search)))
    contacts = query.order_by(Contact.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('admin/contacts.html', contacts=contacts, status_filter=status_filter, search=search)


@app.route('/admin/contact/<int:id>')
@login_required
def admin_contact_detail(id):
    contact = Contact.query.get_or_404(id)
    if contact.status == 'new':
        contact.status = 'read'
        db.session.commit()
    return render_template('admin/contact_detail.html', contact=contact)


@app.route('/admin/contact/<int:id>/delete', methods=['POST'])
@login_required
def admin_contact_delete(id):
    contact = Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    flash('Deleted', 'success')
    return redirect(url_for('admin_contacts'))


@app.route('/admin/applications')
@login_required
def admin_applications():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    query = HiringApplication.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    applications = query.order_by(HiringApplication.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('admin/applications.html', applications=applications, status_filter=status_filter)


@app.route('/admin/application/<int:id>')
@login_required
def admin_application_detail(id):
    application = HiringApplication.query.get_or_404(id)
    if application.status == 'new':
        application.status = 'reviewed'
        db.session.commit()
    return render_template('admin/application_detail.html', application=application)


@app.route('/admin/application/<int:id>/status', methods=['POST'])
@login_required
def admin_application_status(id):
    application = HiringApplication.query.get_or_404(id)
    new_status = request.form.get('status')
    if new_status in ['new', 'reviewed', 'shortlisted', 'rejected']:
        application.status = new_status
        db.session.commit()
        flash('Status updated', 'success')
    return redirect(url_for('admin_application_detail', id=id))


@app.route('/admin/application/<int:id>/delete', methods=['POST'])
@login_required
def admin_application_delete(id):
    app_obj = HiringApplication.query.get_or_404(id)
    db.session.delete(app_obj)
    db.session.commit()
    flash('Application deleted', 'success')
    return redirect(url_for('admin_applications'))


@app.route('/admin/subscribers')
@login_required
def admin_subscribers():
    subscribers = Newsletter.query.order_by(Newsletter.subscribed_at.desc()).all()
    return render_template('admin/subscribers.html', subscribers=subscribers)


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)