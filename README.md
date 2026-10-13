# Automated Daily NSE Report Generator

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red.svg)](https://streamlit.io/)
[![Selenium](https://img.shields.io/badge/Selenium-4.x-green.svg)](https://www.selenium.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An automated end-to-end pipeline and interactive dashboard to download, extract, validate, organize, and monitor daily reports from the **National Stock Exchange (NSE) of India**.

---

## Table of Contents

- [Overview](#overview)
- [Architecture & Workflow](#architecture--workflow)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Streamlit Dashboard](#1-launch-streamlit-dashboard)
  - [Run on Custom Port](#2-running-on-custom-port-eg-port-3500)
  - [Direct CLI Pipeline](#3-run-automation-directly-via-cli)
- [Dashboard Pages](#dashboard-pages)
- [Data Validation Rules](#data-validation-rules)
- [Troubleshooting](#troubleshooting)
- [Disclaimer](#disclaimer)

---

## Overview

Market participants, analysts, and traders frequently require daily operational and trade reports from the NSE portal. The **Automated Daily NSE Report Generator** eliminates repetitive manual downloads by combining:

- **Selenium-powered Web Automation** for seamless navigation and downloads.
- **Pandas Data Validation Engine** ensuring file integrity, schema consistency, and anomaly detection.
- **File Segregation & Duplicate Handling** to organize archives and prevent overwrites.
- **APScheduler Background Jobs** for scheduled unattended execution.
- **SMTP Email Notifications** delivering status summaries, file metrics, and log attachments.
- **Interactive Streamlit UI** for one-click manual execution, schedule management, email configuration, and live log inspection.

---

## Architecture & Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                       Streamlit UI                          │
│        (Email Setup | Manual Run | Scheduling | Logs)       │
└──────────────────────────────┬──────────────────────────────┘
                               │ triggers
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                          main.py                            │
│                  Pipeline Orchestration                     │
└──────┬───────────────────────┼───────────────────────┬──────┘
       │                       │                       │
       ▼                       ▼                       ▼
┌──────────────┐       ┌───────────────┐       ┌──────────────┐
│Data_retrieval│       │ segregation.py│       │csv_validation│
│   Selenium   │──────▶│       &       │──────▶│  DataFrame   │
│  Downloader  │       │duplicates_hdlr│       │  Validator   │
└──────────────┘       └───────────────┘       └──────┬───────┘
                                                      │
                                                      ▼
                                               ┌──────────────┐
                                               │ notification │
                                               │  SMTP Alerts │
                                               └──────────────┘
```

---

## Key Features

- **Automated Report Fetching**: Navigates the NSE reports portal using Selenium WebDriver, dynamically selects daily reports, and manages download streams.
- **Zip Archive Extraction & File Management**: Unpacks downloaded `.zip` files, organizes them into date-stamped directories, and segregates CSV files.
- **Duplicate & Redundancy Handler**: Checks for duplicate downloads and prevents data corruption.
- **Data Validation Suite**:
  - Verifies file format and existence.
  - Loads data via Pandas DataFrames.
  - Checks for column naming errors and invalid headers.
  - Verifies data type consistency across fields.
  - Detects nulls, anomalies, and schema deviations.
- **Background Task Scheduling**: Integrated APScheduler allows setting future execution dates and times with persistent job tracking.
- **Automated Email Notifications**: Sends HTML/text summaries with counts of downloaded and validated files along with attached execution logs.
- **Live Log Viewer**: Inspect and clear application logs directly within the Streamlit interface.

---

## Project Structure

```
├── Data_retrieval.py        # Selenium WebDriver initialization, NSE interaction, and file unzipping
├── NSE_MAIN.py              # Main Selenium workflow runner and navigation logic
├── Scheduling.py            # APScheduler background job manager and persistent scheduler store
├── Streamlit.py             # Streamlit web application frontend
├── config.txt               # Config file storing the recipient email address
├── csv_validation.py        # Pandas validation class checking schema, types, and anomalies
├── duplicates_handler.py    # Redundancy detector and duplicate file handler
├── mail_setup.py            # 2FA OTP verification and recipient email management
├── main.py                  # Master pipeline script orchestrating download -> validation -> alert
├── notification.py          # SMTP email dispatcher with log attachments and run summaries
├── nse_report_downloader.log# Execution log file
├── schedulers.txt           # Persistent store for scheduled jobs
├── segregation.py           # Segregates downloaded files by format into subfolders
└── streamlit1.py            # Alternative UI layout variant
```

---

## Prerequisites

- **Python**: Version `3.8` or higher
- **Google Chrome**: Installed on the host system
- **Gmail Account**: With an App Password enabled (for SMTP notifications)

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/hemu2205/-Automated-Daily-NSE-Report-Generator.git
   cd -Automated-Daily-NSE-Report-Generator
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install selenium streamlit pandas apscheduler webdriver-manager
   ```

---

## Configuration

1. **Email Setup**:
   - The recipient email is configured in `config.txt` or via the **Email Setup** page in the Streamlit dashboard.
   - For SMTP delivery, ensure an active Gmail App Password is configured in `notification.py` and `mail_setup.py`.

2. **Download Directory**:
   - By default, files are downloaded and processed in `nsefiles/<date>/`. Paths can be modified in `main.py` and `Data_retrieval.py`.

---

## Usage

### 1. Launch Streamlit Dashboard
```bash
streamlit run Streamlit.py
```
Open your browser at `http://localhost:8501`.

### 2. Running on Custom Port (e.g., Port 3500)
```bash
python -m streamlit run Streamlit.py --server.port 3500 --server.address 0.0.0.0
```
Open your browser at:
- **Local:** `http://localhost:3500`
- **Network:** `http://<your-ip>:3500`

### 3. Run Automation Directly via CLI
To run the automated downloader pipeline without the web interface:
```bash
python main.py
```

---

## Dashboard Pages

| Page | Description |
|---|---|
| **Email Setup** | Register or update the notification recipient email with OTP verification. |
| **NSE Report Downloader** | One-click manual execution of the report downloading, segregation, and validation pipeline. |
| **Schedule Automation** | Schedule future automated runs at specific dates and 24-hour times using APScheduler. |
| **Logs** | Real-time log monitor displaying the latest 100 log lines with a one-click refresh and log clear option. |

---

## Data Validation Rules

Each downloaded CSV is passed through `csv_validation.py` which executes the following checks:

1. **File Existence & Format**: Verifies the file is non-empty and has a valid `.csv` extension.
2. **Parsing**: Confirms the file can be parsed into a Pandas DataFrame.
3. **Column Names**: Ensures column headers are valid strings without null values.
4. **Data Types**: Validates that columns have consistent inferred data types.
5. **Anomaly Checks**: Checks for missing fields, unexpected NaNs, or truncated records.

---

## Troubleshooting

- **Chrome / ChromeDriver Mismatch**: Ensure your Google Chrome browser is updated. `selenium` uses Chrome WebDriver matching your installed Chrome version.
- **Port In Use**: If port `8501` or `3500` is already in use, specify another port:
  ```bash
  streamlit run Streamlit.py --server.port 8502
  ```
- **SMTP Authentication Error**: Gmail requires a 16-character **App Password** (with 2-Factor Authentication enabled), not your account login password.
- **Missing Reports on Holidays**: The NSE portal does not publish reports on trading holidays and weekends. In this case, the bot logs an informational status and sends a "No reports available" alert.

---

## Disclaimer

This software is developed for educational and personal research purposes. Automated interaction with web portals should always comply with the [National Stock Exchange of India Terms of Use](https://www.nseindia.com/). The authors assume no liability for misuse.
