from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-to-random-string'

# Email Configuration (Optional - for sending emails)
EMAIL_CONFIG = {
    'SMTP_SERVER': 'smtp.gmail.com',
    'SMTP_PORT': 587,
    'EMAIL_ADDRESS': 'your-email@gmail.com',  # Change this
    'EMAIL_PASSWORD': 'your-app-password',     # Change this (use App Password)
    'RECIPIENT_EMAIL': 'info@dishaconsultant.com'  # Where to receive messages
}

# Context processor
@app.context_processor
def inject_year():
    return {'current_year': datetime.now().year}

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


def save_contact_message(data):
    """Save contact messages to a JSON file"""
    try:
        filename = 'contact_messages.json'
        messages = []
        
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                try:
                    messages = json.load(f)
                except:
                    messages = []
        
        data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        messages.append(data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=4, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error saving message: {e}")
        return False


def send_email(name, email, phone, subject, message):
    """Send email notification (Optional)"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['EMAIL_ADDRESS']
        msg['To'] = EMAIL_CONFIG['RECIPIENT_EMAIL']
        msg['Subject'] = f'New Contact Form Submission: {subject}'
        
        body = f"""
        New Contact Form Submission
        ===========================
        
        Name: {name}
        Email: {email}
        Phone: {phone}
        Subject: {subject}
        
        Message:
        {message}
        
        ---
        Sent from Disha Consultant Website
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(EMAIL_CONFIG['SMTP_SERVER'], EMAIL_CONFIG['SMTP_PORT'])
        server.starttls()
        server.login(EMAIL_CONFIG['EMAIL_ADDRESS'], EMAIL_CONFIG['EMAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Email Error: {e}")
        return False


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Check if AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        # Validation
        errors = []
        
        if not name or len(name) < 2:
            errors.append('Please enter a valid name (min 2 characters)')
        
        if not email or '@' not in email or '.' not in email:
            errors.append('Please enter a valid email address')
        
        if not phone or len(phone) < 10:
            errors.append('Please enter a valid phone number (min 10 digits)')
        
        if not subject:
            errors.append('Please select a subject')
        
        if not message or len(message) < 10:
            errors.append('Message must be at least 10 characters')
        
        # If errors found
        if errors:
            if is_ajax:
                return jsonify({
                    'success': False,
                    'errors': errors,
                    'message': ' | '.join(errors)
                }), 400
            
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('contact'))
        
        # Save the message
        contact_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'subject': subject,
            'message': message
        }
        
        saved = save_contact_message(contact_data)
        
        # Try to send email (optional - won't fail if email not configured)
        # Uncomment below if you've configured email
        # send_email(name, email, phone, subject, message)
        
        if saved:
            success_msg = f'Thank you {name}! Your message has been sent successfully. We will contact you soon.'
            
            if is_ajax:
                return jsonify({
                    'success': True,
                    'message': success_msg
                })
            
            flash(success_msg, 'success')
            return redirect(url_for('contact'))
        else:
            error_msg = 'Something went wrong. Please try again or call us directly.'
            
            if is_ajax:
                return jsonify({
                    'success': False,
                    'message': error_msg
                }), 500
            
            flash(error_msg, 'error')
            return redirect(url_for('contact'))
    
    return render_template('contact.html')


# Admin route to view messages (Optional)
@app.route('/admin/messages')
def admin_messages():
    try:
        if os.path.exists('contact_messages.json'):
            with open('contact_messages.json', 'r', encoding='utf-8') as f:
                messages = json.load(f)
            return jsonify(messages)
        return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)