import Data_retrieval as d
import duplicates_handler as dh
import time
import os 
from datetime import date
import logging
from csv_validation import FilePath,run_validations
from segregation import segregate
from notification import send_mail as s


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("nse_report_downloader.log"),
        logging.StreamHandler()
    ]
)

download_directory = "C:\\NSE\\nsefiles"

def main():
    try:
        status = "Failed"
        d.load_nse_reports_page()
        time.sleep(2)
        flag, report_names = d.select_reports()
        time.sleep(3)
        d.download_reports(flag)
        d.wait_for_downloads(report_names, download_directory, 30)
        today = date.today().strftime("%d%m%y")
        today_folder = os.path.join(download_directory,today)
        if dh.handle_redundant_files(today_folder):
            logging.info("All file successfully verified for duplicates")
        else:
            logging.warning("Files Could not be verified for duplicates")
            exit()
        num_downloaded = len(os.listdir(today_folder))
        csv_files = segregate(today_folder)

        
        for file_name in os.listdir(csv_files):
            file_path = os.path.join(csv_files, file_name)
            file_obj = FilePath(file_path)
            if not run_validations(file_obj):
                logging.warning(f"Validation failed for: {file_name}")
        status = "success"        
            
    except Exception as e:
        logging.critical(f"(Main)Critical error occurred: {e}")
        os.remove(today_folder)
    finally:
        s(status,num_downloaded,num_downloaded,0)
        time.sleep(15)
        d.driver.quit()

if __name__ == "__main__":
    main()