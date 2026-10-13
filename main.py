import Data_retrieval as d
import duplicates_handler as dh
import time
import os 
import shutil
from datetime import date
import logging
from csv_validation import FilePath, run_validations
from segregation import segregate
from notification import send_mail as s

# Silence noisy third-party loggers
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("selenium").setLevel(logging.ERROR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("nse_report_downloader.log"),
        logging.StreamHandler()
    ]
)

download_directory = "C:\\Projects\\NSEBOT\\nsefiles"

def main():
    status = "Failed"
    num_downloaded = 0
    num_validated = 0
    today = date.today().strftime("%d%m%y")
    today_folder = os.path.join(download_directory, today)

    try:
        d.load_nse_reports_page()
        time.sleep(2)
        flag, report_names = d.select_reports()
        time.sleep(2)

        if not flag or not report_names:
            logging.info("No reports found or selected to download on the NSE portal.")
            status = "No reports are there to download"
            return status

        d.download_reports(flag)
        download_success = d.wait_for_downloads(report_names, download_directory, 30)

        if not download_success or not os.path.exists(today_folder) or len(os.listdir(today_folder)) == 0:
            logging.warning(f"No reports were downloaded into {today_folder}.")
            status = "No reports are there to download"
            return status

        if dh.handle_redundant_files(today_folder):
            logging.info("All files successfully verified for duplicates.")
        else:
            logging.warning("Duplicate check encountered issues or no files present.")

        num_downloaded = len(os.listdir(today_folder))
        csv_files = segregate(today_folder)

        if csv_files and os.path.exists(csv_files):
            for file_name in os.listdir(csv_files):
                file_path = os.path.join(csv_files, file_name)
                file_obj = FilePath(file_path)
                if not run_validations(file_obj):
                    logging.warning(f"Validation failed for: {file_name}")
                else:
                    num_validated += 1

        status = "success"        
            
    except Exception as e:
        logging.critical(f"(Main) Critical error occurred: {e}")
        status = f"Failed: {e}"
    finally:
        try:
            s(status, num_downloaded, num_validated, 0)
        except Exception as mail_err:
            logging.warning(f"Notification error: {mail_err}")
        d.quit_driver()

    return status

if __name__ == "__main__":
    main()