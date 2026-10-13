import smtplib 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# Function to get the receiver's email from the configuration file
def get_receiver_add():
    try:
        with open("C:\\Projects\\NSEBOT\\config.txt") as f:
            email = f.read().strip()  
            if email:
                return email
    except FileNotFoundError:
        print("Config file not found. Initiating email setup.")
        return None

# Function to get the log file path
def get_log_file():
    return "C:\\Projects\\NSEBOT\\nse_report_downloader.log"

# Function to send the email with the provided details
def send_mail(status, num_downloaded=0, num_validated=0, num_renamed=0):
    receiver_add = get_receiver_add()
    
    # Check if the receiver email is available
    if not receiver_add:
        print("Receiver email address is not specified in config.txt.")
        return False
    
    # Set up the email parameters
    message = MIMEMultipart()
    message["From"] = 'nsebot22@gmail.com'
    password = "ixvq louc dlza scao"
    message["To"] = receiver_add

    # Check if no files are available to download
    if num_downloaded == 0 or "no reports" in status.lower():
        message["Subject"] = "NSE BOT: No Reports Are There to Download"
        body = f"""Hello,

This is to notify you that there are no reports available to download on the NSE portal.

Overall Status: {status}
Number of Files Downloaded: {num_downloaded}

Regards,
NSE Report Automation
"""
    else:
        message["Subject"] = "NSE BOT REPORT RETRIEVAL AUTOMATION RUN DETAILS"
        body = f"""Hello,

This is the summary of the latest report download automation run.

Overall Status: {status}

Number of Files that Downloaded: {num_downloaded}
Number of Files that are Validated: {num_validated}
Number of Files Renamed: {num_renamed}

Regards,
NSE Report Automation
"""

    # Attach the body to the email
    message.attach(MIMEText(body, "plain"))

    # Attach the log file to the email
    log_file = get_log_file()
    try:
        with open(log_file, "rb") as attachment:
            mime_base = MIMEBase("application", "octet-stream")
            mime_base.set_payload(attachment.read())
            encoders.encode_base64(mime_base)
            mime_base.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(log_file)}"
            )
            message.attach(mime_base)
    except FileNotFoundError:
        print(f"Log file not found: {log_file}. Skipping attachment.")

    # Send the email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(message["From"], password)
            server.send_message(message)
            print("Email sent successfully!")
            return True
    except Exception as e:
        print(f"Error occurred: {e}")
        return False