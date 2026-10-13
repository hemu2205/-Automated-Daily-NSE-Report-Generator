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

# Silence noisy third-party loggers
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("selenium").setLevel(logging.ERROR)

download_directory = "C:\\Projects\\NSEBOT\\nsefiles"

_driver = None

def init_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.page_load_strategy = "eager"
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    if not os.path.exists(download_directory):
        os.makedirs(download_directory, exist_ok=True)
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "profile.default_content_settings.popups": 0
    })
    drv = webdriver.Chrome(options=chrome_options)
    drv.set_page_load_timeout(35)
    try:
        drv.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": download_directory
        })
    except Exception:
        pass
    return drv

def get_driver():
    global _driver
    if _driver is None:
        _driver = init_driver()
    else:
        try:
            _ = _driver.title
        except Exception:
            _driver = init_driver()
    return _driver

def quit_driver():
    global _driver
    if _driver is not None:
        try:
            _driver.quit()
        except Exception:
            pass
        _driver = None

class _DriverProxy:
    def __getattr__(self, name):
        if name == "quit":
            return quit_driver
        return getattr(get_driver(), name)

driver = _DriverProxy()


def retry_operation(func, retries=3, base_delay=3):
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            if attempt < retries - 1:
                delay = random.uniform(base_delay, base_delay + 2)
                logging.info(f"Attempt {attempt + 1} did not succeed ({type(e).__name__}). Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
            else:
                logging.error(f"Operation failed after {retries} attempts: {e}")
                return None


def load_nse_reports_page():
    def _hit_nse():
        current_url = ""
        try:
            current_url = driver.current_url or ""
        except Exception:
            pass

        # Prime cookies on homepage first if not already visited
        if "nseindia.com" not in current_url:
            try:
                logging.info("Connecting to NSE homepage to establish session...")
                driver.get("https://www.nseindia.com")
                time.sleep(1.5)
            except Exception as e:
                logging.warning(f"Homepage priming note: {e}")

        logging.info("Navigating to NSE All Reports page...")
        driver.get("https://www.nseindia.com/all-reports")
        reports = WebDriverWait(driver, 20).until(
            lambda d: d.find_elements(By.CSS_SELECTOR, "#cr_equity_daily_Current .reportsDownload")
        )
        if not reports:
            raise RuntimeError("Report cards not found inside equity section.")
        return True

    res = retry_operation(_hit_nse, retries=3, base_delay=3)
    if not res:
        logging.error("Failed to load NSE all-reports page after retries.")
        raise RuntimeError("Failed to load NSE all-reports page.")
    logging.info("NSE Reports page loaded successfully.")


def select_reports():
    try:
        reports = retry_operation(
            lambda: WebDriverWait(driver, 20).until(
                lambda d: d.find_elements(By.CSS_SELECTOR, "#cr_equity_daily_Current .reportsDownload")
            ),
            retries=3,
            base_delay=5
        )
        if not reports:
            logging.warning("No reports found in the container.")
            return False, []

        report_names = []
        flag = False
        for report in reports:
            try:
                name_elem = None
                for selector in [".reportCardSegmentDaily", ".reportCardSegment", ".chk_container", ".card-body"]:
                    elems = report.find_elements(By.CSS_SELECTOR, selector)
                    if elems and elems[0].text.strip():
                        name_elem = elems[0]
                        break

                raw_name = name_elem.text.strip() if name_elem else "Unknown_Report"
                clean_name = raw_name.split('\n')[0].strip()
                logging.info(f"Found report: {clean_name}")
                report_names.append(clean_name)
                time.sleep(0.3)

                checkbox = report.find_element(By.XPATH, ".//label[contains(@class,'chk_container')] | .//label[@role='checkbox']")
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable(checkbox))
                driver.execute_script("arguments[0].scrollIntoView();", checkbox)
                time.sleep(random.uniform(0.3, 0.6))
                driver.execute_script("arguments[0].click();", checkbox)
                logging.info(f"Selected: {clean_name}")
                flag = True
            except Exception as e:
                logging.warning(f"Error selecting report: {e}")
        return flag, report_names
    except Exception as e:
        logging.error(f"Error accessing reports container: {e}")
        return False, []


def download_reports(flag):
    if flag:
        try:
            multi_download = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#cr_equity_daily_downloadbtn, #MultiDwnld"))
            )
            driver.execute_script("arguments[0].scrollIntoView();", multi_download)
            driver.execute_script("arguments[0].click();", multi_download)
            logging.info("Multi Download button clicked.")
        except Exception as e:
            logging.error(f"Error clicking Multi Download button: {e}")
    else:
        logging.info("No reports selected to download.")


def wait_for_downloads(filenames, download_dir=download_directory, timeout=30):
    try:
        if not os.path.exists(download_dir):
            logging.info(f"Download directory does not exist. Creating: {download_dir}")
            os.makedirs(download_dir, exist_ok=True)

        zip_file_path = retry_operation(
            lambda: check_for_zip(download_dir, timeout),
            retries=2,
            base_delay=5
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

        logging.info(f"All {len(extracted_files)} files downloaded and extracted successfully.")
        try:
            os.remove(zip_file_path)
        except Exception as e:
            logging.warning(f"Could not remove temporary zip {zip_file_path}: {e}")

        # Clean any auxiliary download files left in download_dir
        for item in os.listdir(download_dir):
            if item.endswith(".crdownload") or item.endswith(".htm") or item.endswith(".html"):
                try:
                    os.remove(os.path.join(download_dir, item))
                except Exception:
                    pass
        return True
    except Exception as e:
        logging.error(f"Unexpected error during download verification: {e}")
        return False


def check_for_zip(directory, timeout):
    end_time = time.time() + timeout
    while time.time() < end_time:
        if os.path.exists(directory):
            zip_files = [f for f in os.listdir(directory) if f.endswith(".zip")]
            for z in zip_files:
                z_path = os.path.join(directory, z)
                try:
                    if os.path.getsize(z_path) > 0:
                        with zipfile.ZipFile(z_path, 'r') as test_z:
                            if test_z.namelist():
                                return z_path
                except (zipfile.BadZipFile, PermissionError, OSError):
                    pass
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
        quit_driver()