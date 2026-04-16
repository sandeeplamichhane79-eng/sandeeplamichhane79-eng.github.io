#!/usr/bin/env python3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import urllib.parse

app = Flask(__name__)
CORS(app)

# Email configuration
EMAIL_ADDRESS = "sandeeplamichhane79@gmail.com"
EMAIL_PASSWORD = "your-app-password"  # You'll need to set up an app password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# WhatsApp configuration
WHATSAPP_PHONE = "+9779816528022"  # Your WhatsApp number
WHATSAPP_API_KEY = "your-whatsapp-api-key"  # You'll need to set up WhatsApp API

def send_whatsapp_message(name, email, message):
    try:
        # Format WhatsApp message
        whatsapp_message = f"""
        *New Portfolio Message!*
        
        *Name:* {name}
        *Email:* {email}
        *Message:* {message}
        
        ---
        *Sent from:* Sandeep's Portfolio Website
        """
        
        # Using WhatsApp API (you'll need to set up an account with a service like Twilio, WATI, or similar)
        # For now, I'll use a simple WhatsApp API call structure
        api_url = f"https://api.whatsapp.com/v1/messages"
        
        headers = {
            'Authorization': f'Bearer {WHATSAPP_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'to': WHATSAPP_PHONE,
            'type': 'text',
            'text': {
                'body': whatsapp_message
            }
        }
        
        # Send WhatsApp message
        response = requests.post(api_url, json=data, headers=headers)
        
        if response.status_code == 200:
            return True, "WhatsApp message sent successfully!"
        else:
            return False, f"WhatsApp API error: {response.text}"
    
    except Exception as e:
        return False, f"Failed to send WhatsApp message: {str(e)}"

def send_email(name, email, message):
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS
        msg['Subject'] = f"New Portfolio Message from {name}"
        
        # Email body
        body = f"""
        New message from your portfolio website:
        
        Name: {name}
        Email: {email}
        Message: {message}
        
        ---
        Sent from: {request.remote_addr if 'request' in globals() else 'Unknown'}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to SMTP server and send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True, "Email sent successfully!"
    
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"

def send_notifications(name, email, message):
    """Send both email and WhatsApp notifications"""
    results = []
    
    # Send email
    email_success, email_result = send_email(name, email, message)
    results.append(f"Email: {'Success' if email_success else 'Failed'}")
    
    # Send WhatsApp message
    whatsapp_success, whatsapp_result = send_whatsapp_message(name, email, message)
    results.append(f"WhatsApp: {'Success' if whatsapp_success else 'Failed'}")
    
    # Return combined result
    if email_success or whatsapp_success:
        return True, f"Notifications sent! ({', '.join(results)})"
    else:
        return False, f"Failed to send notifications. ({', '.join(results)})"

@app.route('/send-email', methods=['POST'])
def send_email_route():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(key in data for key in ['name', 'email', 'message']):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
        
        name = data['name'].strip()
        email = data['email'].strip()
        message = data['message'].strip()
        
        # Basic validation
        if not name or not email or not message:
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400
        
        if '@' not in email or '.' not in email:
            return jsonify({
                'success': False,
                'message': 'Invalid email address'
            }), 400
        
        # Send both email and WhatsApp notifications
        success, result = send_notifications(name, email, message)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Message sent successfully! You\'ll receive notifications via both email and WhatsApp.'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send message. Please try again.'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500

@app.route('/')
def index():
    return "Email server is running!"

if __name__ == '__main__':
    print("Starting email server on port 5001...")
    print("Make sure to set up Gmail App Password first!")
    app.run(host='0.0.0.0', port=5001, debug=True)
