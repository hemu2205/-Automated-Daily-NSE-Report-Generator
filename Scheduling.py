import os
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from main import main as m
# File to store schedules
SCHEDULES_FILE = "C:\\NSE\\schedulers.txt"

# Initialize a Background Scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Dictionary to store job statuses
job_status = {}

# -------------------------------
# Functions for Managing Schedules
# -------------------------------

def load_schedules():
    """Load schedules from the file."""
    if os.path.exists(SCHEDULES_FILE):
        with open(SCHEDULES_FILE, 'r') as f:
            return [line.strip() for line in f.readlines()]
    return []

def save_schedule(scheduled_time):
    """Save a new schedule to the file."""
    with open(SCHEDULES_FILE, 'a') as f:
        f.write(f"{scheduled_time}\n")

def remove_schedule(scheduled_time):
    """Remove a completed schedule from the file."""
    schedules = load_schedules()
    schedules = [s for s in schedules if s != scheduled_time]
    with open(SCHEDULES_FILE, 'w') as f:
        for schedule in schedules:
            f.write(f"{schedule}\n")

# -------------------------------------
# Task to Simulate Report Generation
# -------------------------------------

def run_automation_task(scheduled_time):
    job_status[scheduled_time] = "In Progress"
    print(f"Task started at {datetime.now()} for schedule: {scheduled_time}")
    m()
    time.sleep(2)  # Simulate some processing
    job_status[scheduled_time] = "Completed"
    print("Report automation completed!")
    remove_schedule(scheduled_time)

# -------------------------------------
# Schedule Management
# -------------------------------------

def add_new_schedule(scheduled_datetime):
    """
    Adds a new schedule to the scheduler and saves it.
    Args:
        scheduled_datetime (datetime): The datetime at which the task will run.
    """
    scheduled_time = scheduled_datetime.strftime('%Y-%m-%d %H:%M:%S')
    
    # Save to file
    save_schedule(scheduled_time)

    # Initialize status
    job_status[scheduled_time] = "Scheduled"

    # Add to scheduler
    scheduler.add_job(
        run_automation_task,
        trigger=DateTrigger(run_date=scheduled_datetime),
        args=[scheduled_time],
        id=scheduled_time,
        name=f"Report Automation at {scheduled_time}"
    )
    print(f"Scheduled new task at {scheduled_time}")

def load_existing_schedules():
    """Load and re-add existing schedules to the scheduler."""
    schedules = load_schedules()
    for scheduled_time in schedules:
        try:
            scheduled_datetime = datetime.strptime(scheduled_time, '%Y-%m-%d %H:%M:%S')
            job_status[scheduled_time] = "Scheduled"
            scheduler.add_job(
                run_automation_task,
                trigger=DateTrigger(run_date=scheduled_datetime),
                args=[scheduled_time],
                id=scheduled_time,
                name=f"Re-added Report Automation at {scheduled_time}"
            )
        except Exception as e:
            job_status[scheduled_time] = "Failed to Schedule"
            print(f"Failed to re-add schedule {scheduled_time}: {e}")

# -------------------------------------
# Scheduler Initialization
# -------------------------------------

def start_scheduler():
    """Start the scheduler and load any existing schedules."""
    if not scheduler.running:
        scheduler.start()
    load_existing_schedules()
    print("Scheduler started and existing schedules loaded.")

def get_job_status():
    """Get the status of all scheduled jobs."""
    return job_status