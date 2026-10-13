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
    base, ext = os.path.splitext(duplicate_name)
    counter = 1
    new_name = f"{base}[{counter}]{ext}"
    while new_name in existing_names:
        counter += 1
        new_name = f"{base}[{counter}]{ext}"
    logging.info(f"Auto-resolved duplicate filename: '{duplicate_name}' -> '{new_name}'")
    return new_name

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