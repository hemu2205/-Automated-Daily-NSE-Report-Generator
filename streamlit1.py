import streamlit as st

import os
from mail_setup import (
    validate_email,
    send_email,
    initiate_email_setup,
    twofa_exists,
    add_gmail,
    remove_gmail,
    get_saved_email,
    otp_gen,
)
from main import main as run_main_script
from Scheduling import add_new_schedule, start_scheduler, get_job_status
from datetime import datetime

# Streamlit Page Configuration
st.set_page_config(
    page_title="NSE Report Automation",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Gradient Background
GRADIENT_START = "#F4F7FC"
GRADIENT_END = "#E9ECF2"

st.markdown(
    f"""
    <style>
       
        body {{
            background: linear-gradient(to bottom right, {GRADIENT_START}, {GRADIENT_END});
            margin: 0;
            font-family: 'arial', sans-serif;
            color: #333;
        }}
        .main {{ padding: 2rem; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Color Palette
PRIMARY_COLOR = "#1E293B"
SECONDARY_COLOR = "#2563EB"
ACCENT_COLOR = "#14B8A6"
CARD_COLOR = "#FEF9C3"
CARD_BORDER = "#CBD5E1"

# Add custom CSS and animations
def add_custom_styles():
    st.markdown(
        f"""
        <style>
            /* Global Styling */
            h1, h2, h3 {{
                color: {PRIMARY_COLOR};
                text-align: center;
            }}

            .stButton > button {{
                background-color: {SECONDARY_COLOR};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.3s, transform 0.2s ease-in-out;
            }}

            .stButton > button:hover {{
                background-color: {ACCENT_COLOR};
                transform: scale(1.1);
            }}

            .stButton > button:active {{
                transform: scale(0.95);
            }}

            .st-radio label {{
                font-size: 18px;
                color: {PRIMARY_COLOR};
            }}

            .st-markdown {{
                text-align: center;
                animation: fadeIn 1s;
            }}

            /* Animations */
            @keyframes fadeIn {{
                from {{
                    opacity: 0;
                }}
                to {{
                    opacity: 1;
                }}
            }}

            /* Navigation Bar */
            .sidebar .sidebar-content {{
                background-color: "#CD5C5C";
                padding-top: 30px;
            }}

            .sidebar .sidebar-content a {{
                color:{PRIMARY_COLOR};
                font-size: 18px;
                display: block;
                padding: 10px 20px;
                text-decoration: none;
                transition: background-color 0.3s ease;
            }}

            .sidebar .sidebar-content a:hover {{
                background-color:"#CD5C5C";
            }}

            /* Page Sections */
            .page-section {{
                background-color: {CARD_COLOR};
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# Apply styles
add_custom_styles()

# Define session state keys
if "email_setup" not in st.session_state:
    st.session_state.email_setup = twofa_exists()
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "otp" not in st.session_state:
    st.session_state.otp = None
if "email" not in st.session_state:
    st.session_state.email = ""

# Streamlit App Navigation
st.sidebar.title("Navigation")
st.sidebar.markdown("""
<nav>
  <ul style="list-style-type: none; padding: 0;">
    <li><a href="#" style="text-decoration: none; color: white; font-size: 20px;">Email Setup</a></li>
    <li><a href="#" style="text-decoration: none; color: white; font-size: 20px;">NSE Report Downloader</a></li>
    <li><a href="#" style="text-decoration: none; color: white; font-size: 20px;">Schedule Automation</a></li>
    <li><a href="#" style="text-decoration: none; color: white; font-size: 20px;">Logs</a></li>
  </ul>
</nav>
""", unsafe_allow_html=True)

page = st.sidebar.radio("Go to", ("Email Setup", "NSE Report Downloader", "Schedule Automation", "Logs"))

if page == "Email Setup":
    st.title("Email Management for Two-Factor Authentication")
    st.markdown("Manage your email address for authentication process.")
    
    # Check if two-factor authentication is set up
    if not st.session_state.email_setup:
        st.warning("Two-factor authentication is not set up. Please enter your email to get started.")
        email_input = st.text_input("Email", value=st.session_state.email).strip()

        if st.button("Validate Email"):
            if validate_email(email_input):
                st.session_state.email = email_input
                otp = otp_gen()
                st.session_state.otp = otp
                email_sent = send_email(email_input, otp)
                if email_sent:
                    st.session_state.otp_sent = True
                    st.success("OTP sent to your email!")
                else:
                    st.error("Failed to send OTP. Please try again.")
            else:
                st.error("Invalid email address. Please try again.")

        if st.session_state.otp_sent:
            st.markdown("### Step 2: Enter the OTP sent to your email")
            otp_input = st.text_input("Enter OTP", type="password").strip()
            if st.button("Verify OTP"):
                if otp_input.isdigit() and int(otp_input) == st.session_state.otp:
                    if initiate_email_setup(st.session_state.email):
                        st.session_state.email_setup = True
                        st.success("Two-factor authentication set up successfully!")
                    else:
                        st.error("Failed to save email for two-factor authentication.")
                else:
                    st.error("Invalid OTP. Please try again.")
    else:
    # Show saved email if two-factor authentication exists
        saved_email = get_saved_email()
        st.success(f"Current email setup: {saved_email}")
        
        # Options to update or remove email
        st.markdown("### Manage Email Settings", unsafe_allow_html=True)
        action = st.radio("Choose an action:", ("Update Email", "Remove Email"))

        if action == "Update Email":
            new_email = st.text_input("Enter new email address").strip()
            if st.button("Update Email"):
                if validate_email(new_email):
                    otp = otp_gen()  # Generate OTP
                    if send_email(new_email, otp):
                        st.session_state.otp_sent = True
                        st.session_state.otp = otp  # Save OTP in session state
                        st.session_state.new_email = new_email  # Save email in session state
                        st.success("OTP successfully sent. Please enter it below.")
                    else:
                        st.error("Failed to send OTP. Try again!")
                else:
                    st.error("Invalid email format. Please try again.")

            if st.session_state.get("otp_sent", False):
                user_otp = st.text_input("Enter the OTP sent to your email", type="password").strip()
                if st.button("Verify OTP"):
                    if user_otp == str(st.session_state.get("otp")):
                        add_gmail(st.session_state.get("new_email"))
                        st.success(f"Email updated successfully to {st.session_state.get('new_email')}")
                        st.session_state.otp_sent = False  # Reset OTP session state
                    else:
                        st.error("Invalid OTP. Please try again.")


        elif action == "Remove Email":
            if st.button("Remove Email"):
                if remove_gmail():
                    st.success("Email removed successfully!")
                    st.session_state.email_setup = False
                else:
                    st.error("Failed to remove email. Try again.")


if page == "NSE Report Downloader":
    st.title("NSE Report Downloader")
    st.markdown(
    """
    <div style="text-align: center;">
        Automate downloading, validating, and organizing NSE reports with a simple click.
    </div>
    """,
    unsafe_allow_html=True
)


    if not st.session_state.email_setup:
        st.warning("Please set up your email first on the Email Setup page.")
    else:
        st.markdown("### Actions", unsafe_allow_html=True)
        
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("Run Report Automation"):
                st.info("Starting report automation process...")
                try:
                    run_main_script()  
                    st.success("Report automation completed successfully!")

                except Exception as e:
                    st.error(f"An error occurred: {e}")


elif page == "Schedule Automation":
    from Scheduling import add_new_schedule, load_schedules, start_scheduler, get_job_status
    start_scheduler()
    st.title("Schedule Automated Runs with Status")
    st.markdown("### Scheduled Report Status")
    statuses = get_job_status()
    if statuses:
        for scheduled_time, status in statuses.items():
            st.markdown(f"- **{scheduled_time}**: {status}")
    else:
        st.markdown("No scheduled reports found.")
    st.markdown("### Set New Schedule")
    date_input = st.date_input("Select Date", min_value=datetime.today().date())
    time_input = st.text_input("Enter Time (HH:MM)", value="00:00")

    try:
        time_obj = datetime.strptime(time_input, "%H:%M").time()
        valid_time = True
    except ValueError:
        valid_time = False

    if st.button("Schedule Report"):
        if valid_time:
            scheduled_datetime = datetime.combine(date_input, time_obj)
            if scheduled_datetime > datetime.now():
                add_new_schedule(scheduled_datetime)
                st.success(f"Scheduled report automation at {scheduled_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                st.error("Please select a future date and time.")
        else:
            st.error("Invalid time format. Use HH:MM (24-hour).")
    
    if st.button("Refresh Status"):
        statuses = get_job_status()
        st.rerun()
elif page == "Logs":
     st.title("Application Logs")
     log_file_path = "C:\\NSE\\nse_report_downloader.log" # Path to the log file

     if os.path.exists(log_file_path):
        st.subheader("Latest Logs")
        
        with open(log_file_path, "r") as log_file:
            logs = log_file.readlines()
            logs_display = "\n".join(logs[-50:])  # Display last 50 lines of the log file
            
        st.text_area("Logs", logs_display, height=400)
        
        if st.button("Refresh Logs"):
            st.rerun()
     else:
        st.warning("Log file not found! Ensure logs are being generated.")