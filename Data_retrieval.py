import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime as t
import time
import random
import os
import zipfile
import socket

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("nse_report_downloader.log"),
        logging.StreamHandler()
    ]
)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("Mozilla/5.0")
chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
download_directory = "C:\\NSE\\nsefiles"
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_directory,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

driver = webdriver.Chrome(options=chrome_options)


def retry_operation(func, retries=3, base_delay=5):
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                delay = random.uniform(base_delay, base_delay + 2)
                logging.info(f"Retrying in {delay:.2f} seconds")
                time.sleep(delay)
            else:
                logging.error("Max retries reached.")
                driver.quit()


def load_nse_reports_page():
    retry_operation(
        lambda: driver.get("https://www.nseindia.com/all-reports"),
        retries=3,
        base_delay=5
    )
    retry_operation(
        lambda: WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "cr_equity_daily_Current"))
        ),
        retries=3,
        base_delay=5
    )
    logging.info("Page loaded successfully.")


def select_reports():
    try:
        container = retry_operation(
            lambda: WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "cr_equity_daily_Current"))
            ),
            retries=3,
            base_delay=5
        )
        reports = container.find_elements(By.CSS_SELECTOR, ".reportsDownload")
        report_names = []
        flag = False
        for report in reports:
            try:
                report_name = report.find_element(By.CLASS_NAME, "reportCardSegment").text
                logging.info(f"Found report: {report_name}")
                report_names.append(report_name)
                time.sleep(0.5)
                checkbox = report.find_element(By.XPATH, ".//label[@role='checkbox']")
                retry_operation(
                    lambda: WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable(checkbox)
                    ),
                    retries=2,
                    base_delay=3
                )
                driver.execute_script("arguments[0].scrollIntoView();", checkbox)
                time.sleep(random.uniform(0.5, 1))
                driver.execute_script("arguments[0].click();", checkbox)
                logging.info(f"Selected: {report_name}")
                flag = True
            except Exception as e:
                logging.warning(f"Error selecting report: {e}")
        return flag, report_names
    except Exception as e:
        logging.error(f"Error accessing reports container: {e}")
        return False, []


def download_reports(flag):
    if flag:
        retry_operation(
            lambda: WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, "MultiDwnld"))
            ),
            retries=3,
            base_delay=5
        )
        multi_download = driver.find_element(By.ID, "MultiDwnld")
        driver.execute_script("arguments[0].scrollIntoView();", multi_download)
        driver.execute_script("arguments[0].click();", multi_download)
        logging.info("Multi Download button clicked.")
    else:
        logging.info("No reports selected to download.")
        driver.quit()


def wait_for_downloads(filenames, download_dir=download_directory, timeout=30):
    try:
        if not os.path.exists(download_dir):
            logging.info(f"Download directory does not exist. Creating: {download_dir}")
            os.makedirs(download_dir, exist_ok=True)

        zip_file_path = retry_operation(
            lambda: check_for_zip(download_dir, timeout),
            retries=3,
            base_delay=10
        )
        if not zip_file_path:
            logging.error("Download failed or timed out.")
            return False

        logging.info("(data_retrieval) In Extraction Process")
        today = t.today().strftime("%d%m%y")
        extraction_dir = os.path.join(download_dir, today)
        logging.info(f"(data_retrieval) Extraction directory path: {extraction_dir}")
        os.makedirs(extraction_dir, exist_ok=True)

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extraction_dir)
            extracted_files = set(os.path.basename(f) for f in zip_ref.namelist())

        missing_files = [name for name in filenames if name not in extracted_files]
        if missing_files:
            logging.warning(f"Missing files: {missing_files}")
        else:
            logging.info("All files downloaded and verified successfully.")
        os.remove(zip_file_path)
        return True
    except Exception as e:
        logging.error(f"Unexpected error during download verification: {e}")
        return False


def check_for_zip(directory, timeout):
    end_time = time.time() + timeout
    while time.time() < end_time:
        for file_name in os.listdir(directory):
            if file_name.endswith(".zip"):
                return os.path.join(directory, file_name)
        time.sleep(1)
    raise TimeoutError("Zip file not found within the timeout period.")


def main():
    try:
        load_nse_reports_page()
        flag, report_names = select_reports()
        download_reports(flag)
        if flag:
            wait_for_downloads(report_names)
    finally:
        driver.quit()