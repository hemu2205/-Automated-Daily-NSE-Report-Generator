import os
import logging
from Data_retrieval import download_directory 
from datetime import date
import random

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("nse_report_downloader.log"),
        logging.StreamHandler()
    ]
)

def resolve_duplicate_name(existing_names, duplicate_name):
    max_attempts = 3
    temp_name = None

    while max_attempts:
        temp_name = input(f"File '{duplicate_name}' is a duplicate. Enter a new name: ").strip()
        if temp_name and temp_name not in existing_names:
            return temp_name  
        logging.warning(f"Invalid or duplicate name '{temp_name}'. Attempts remaining: {max_attempts - 1}")
        max_attempts -= 1
    logging.warning("Max attempts exceeded. Allocating a new filename automatically.")
    auto_name = f"{duplicate_name}[1]"
    while auto_name in existing_names:  
        auto_name = auto_name.replace("]", f"{random.randint(1, 9)}]")
    logging.info(f"Auto-allocated filename: {auto_name}")
    return auto_name

def handle_redundant_files(directory):
    """Handle duplicate files in the specified directory."""
    try:
        folder_path = directory
        if not os.path.exists(folder_path):
            logging.warning(f"Directory '{folder_path}' does not exist.")
            return False
        try:
            report_names = os.listdir(folder_path)
        except FileNotFoundError:
            logging.error(f"Directory not found: {folder_path}")
            return False
        except PermissionError:
            logging.error(f"Permission denied to access directory: {folder_path}")
            return False
        except OSError as e:
            logging.error(f"OS error while accessing directory: {e}")
            return False
        if not report_names:
            logging.info(f"No files found in directory: {folder_path}")
            return False

        unique_names = set()
        for name in report_names:
            logging.debug(f"Checking file: {name}")
            if name in unique_names:
                logging.info(f"Duplicate detected: {name}")
                new_name = resolve_duplicate_name(unique_names, name)
                old_path = os.path.join(folder_path, name)
                new_path = os.path.join(folder_path, new_name)
                logging.debug(f"Renaming {old_path} to {new_path}")
                try:
                    os.rename(old_path, new_path)
                    logging.info(f"Renamed '{name}' to '{new_name}'")
                except FileNotFoundError:
                    logging.error(f"File not found for renaming: {old_path}")
                    return False
                except PermissionError:
                    logging.error(f"Permission denied to rename file: {old_path}")
                    return False
                except OSError as e:
                    logging.error(f"OS error while renaming file '{old_path}' to '{new_path}': {e}")
                    return False
            else:
                unique_names.add(name)

        logging.info("All duplicates handled successfully.")
        return True  
    except FileNotFoundError:
        logging.error(f"Directory not found: {directory}")
        return False
    except PermissionError:
        logging.error(f"Permission denied to access directory: {directory}")
        return False
    except OSError as e:
        logging.error(f"(Duplicates handler) OS error while handling files: {e}")
        return False
    except Exception as e:
        logging.error(f"(Duplicates handler) Unexpected error: {e}")
        return False