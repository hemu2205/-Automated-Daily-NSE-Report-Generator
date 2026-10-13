import os
import shutil
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("nse_report_downloader.log"),
        logging.StreamHandler()
    ]
)

def segregate(directory):
    if not os.path.exists(directory) or not os.listdir(directory):
        return False
    files = os.listdir(directory)
    for i in files:
        current = os.path.join(directory, i)
        if os.path.isdir(current):
            continue
        ext = i.split('.')[-1].lower() if '.' in i else 'other'
        target = os.path.join(directory, ext)
        os.makedirs(target, exist_ok=True)
        try:
            dest_file = os.path.join(target, i)
            shutil.move(current, dest_file)
            logging.info(f"moved file {current} to {target}")
        except Exception as e:
            logging.warning(f"Could not move {current}: {e}")
    return os.path.join(directory, "csv")