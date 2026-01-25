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
    files = os.listdir(directory)
    if not os.listdir(directory):
        return False
    for i in files:
        current = os.path.join(directory,i)
        target = os.path.join(directory,i.split('.')[-1])
        try:
            os.mkdir(target)
            shutil.move(current,target)
            logging.info(f"moved file {current} to {target}")
        except OSError:
            shutil.move(current,target)
            logging.info(f"moved file {current} to {target}")
    return os.path.join(directory,"csv")