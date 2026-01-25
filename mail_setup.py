import smtplib as s
import re
import random
import os

# Utility to check if the email configuration exists
def twofa_exists():
    return os.path.exists('C:\\NSE\\config.txt')

# Function to retrieve the currently saved email
def get_saved_email():
    if twofa_exists():
        with open('C:\\NSE\\config.txt', 'r') as f:
            return f.read().strip()

# Function to create the config file for storing email
def add_gmail(gmail):
    try:
        if gmail:
            with open('C:\\NSE\\config.txt', 'w') as f:
                f.write(gmail)
            return "Email added successfully"
        else:
            return "Invalid email provided"
    except OSError as e:
        return f"Error occurred: {e}"

# Function to remove the stored Gmail
def remove_gmail():
    try:
        if twofa_exists():
            os.remove('C:\\NSE\\config.txt')
            return "Email removed successfully"
        else:
            return "No email configuration to remove"
    except OSError as e:
        return f"Error occurred: {e}"

# Validate email format
def validate_email(gmail):
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return bool(re.search(regex, gmail))

# Generate OTP
def otp_gen():
    return random.randint(1000, 9999)

# Send OTP email
def send_email(gmail, otp):
    sender_email = 'here220502@gmail.com'
    password = "odlx keen jlww svkb"
    subject = 'OTP for master key reset'
    body = f"Subject: {subject}\n\nYour OTP is: {otp}"

    try:
        with s.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(sender_email, password)
            smtp.sendmail(sender_email, gmail, body)
        return True
    except s.SMTPAuthenticationError as e:
        return f"Authentication error: {e}"
    except Exception as e:
        return f"Failed to send email: {e}"

# Verify OTP entered by the user
def verify_otp(user_input_otp, expected_otp):
    return user_input_otp == expected_otp

def initiate_email_setup(email, user_input_otp=None):
    """
    Validates the email, sends an OTP, and verifies the OTP.
    """
    if not validate_email(email):
        return "Invalid email format"

    otp = otp_gen()
    email_sent = send_email(email, otp)

    if email_sent is not True:
        return email_sent  # Return error message from email sending



    if verify_otp(user_input_otp, str(otp)):
        return add_gmail(email)
    else:
        return "OTP verification failed"