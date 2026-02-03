# NSE Bot Report Downloader

An automated tool designed to download, validate, and manage reports from the National Stock Exchange (NSE) of India. This application features a user-friendly Streamlit interface, automated scheduling, email notifications, and robust data validation.

## Features

- **Automated Downloading**: Uses Selenium to navigate the NSE website and download selected reports.
- **Data Validation**: Automatically validates downloaded CSV files using Pandas (checks for file existence, column names, data types, and anomalies).
- **Email Notifications**: Sends email alerts with the status of the operation and attaches relevant logs or reports. Supports Gmail 2FA/App Passwords.
- **Scheduling**: Schedule report downloads to run automatically at specific dates and times using APScheduler.
- **User Interface**: A clean and interactive dashboard build with Streamlit to manage email settings, runs, and logs.
- **File Management**: Automatically unzips, renames with timestamps, and organizes files by type.

## Prerequisites

- Python 3.8 or higher
- Google Chrome Browser (for Selenium automation)
- A Gmail account (for sending notifications)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd NSE
    ```

2.  **Install dependencies:**
    You can install the required Python packages using pip:
    ```bash
    pip install selenium streamlit pandas apscheduler webdriver-manager
    ```

## Usage

1.  **Run the Streamlit Application:**
    Navigate to the project directory and run the following command:
    ```bash
    streamlit run Streamlit.py
    ```

2.  **Navigate the Dashboard:**
    - **Email Setup**: Configure your sender email. You will need to generate an App Password for your Gmail account if 2FA is enabled.
    - **NSE Report Downloader**: Manually trigger the report downloading process.
    - **Schedule Automation**: Set up future times for the bot to run automatically.
    - **Logs**: View real-time logs of the application's activities.

## Project Structure

- `NSE_MAIN.py`: Core script that handles the Selenium automation and main logic.
- `Streamlit.py`: The main entry point for the Streamlit web application.
- `Data_retrieval.py`: Functions for interacting with the web elements and downloading files.
- `csv_validation.py`: Logic for validating the integrity of downloaded CSV reports.
- `Scheduling.py`: Manages background scheduling tasks.
- `mail_setup.py`: Handles email configuration and OTP verification.

## Important Note

This tool is for educational purposes. Automated scraping of websites should be done responsibly and in accordance with the website's terms of service.
