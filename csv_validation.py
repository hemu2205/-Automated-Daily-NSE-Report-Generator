import os
import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("nse_report_downloader.log"),
        logging.StreamHandler()
    ]
)

class FilePath:
    def __init__(self, file_path):
        self.file_path = file_path
        self.dataframe = None

    def file_exists(self):
        """Check if the file exists and is a valid CSV."""
        try:
            if not os.path.exists(self.file_path):
                logging.error(f"File not found: {self.file_path}")
                return False
            if not self.file_path.endswith('.csv'):
                logging.error(f"Invalid file format. Expected .csv, got: {self.file_path}")
                return False
            logging.info(f"File found and is a CSV: {self.file_path}")
            return True
        except Exception as e:
            logging.error(f"Unexpected error during file existence check: {e}")
            return False

    def load_csv(self):
        """Load the CSV file into a pandas DataFrame."""
        try:
            self.dataframe = pd.read_csv(self.file_path)
            logging.info("CSV loaded successfully.")
            return True
        except FileNotFoundError:
            logging.error(f"CSV file not found: {self.file_path}")
            return False
        except pd.errors.EmptyDataError:
            logging.error(f"CSV file is empty: {self.file_path}")
            return False
        except pd.errors.ParserError as e:
            logging.error(f"Error parsing CSV file: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error while loading CSV: {e}")
            return False

    def validate_columns(self):
        """Ensure all columns are present and have valid names."""
        try:
            if self.dataframe is None:
                logging.error("No DataFrame loaded for validation.")
                return False

            if self.dataframe.columns.hasnans:
                logging.error("Column names contain NaN values.")
                return False

            if not all(isinstance(col, str) for col in self.dataframe.columns):
                logging.error("Some column names are not strings.")
                return False

            logging.info("Column names are valid.")
            return True
        except Exception as e:
            logging.error(f"Unexpected error during column validation: {e}")
            return False

    def validate_data_types(self):
        """Check if each column has consistent data types."""
        try:
            if self.dataframe is None:
                logging.error("No DataFrame loaded for validation.")
                return False

            for column in self.dataframe.columns:
                column_data = self.dataframe[column]
                inferred_type = pd.api.types.infer_dtype(column_data, skipna=True)
                if inferred_type == 'mixed':
                    logging.warning(f"Column '{column}' has mixed data types.")
                    return False
                logging.info(f"Column '{column}' data type: {inferred_type}")

            logging.info("All columns have consistent data types.")
            return True
        except Exception as e:
            logging.error(f"Unexpected error during data type validation: {e}")
            return False

    def validate_no_anomalies(self):
        """Check for anomalies like empty rows or missing values."""
        try:
            if self.dataframe is None:
                logging.error("No DataFrame loaded for validation.")
                return False

            if self.dataframe.isnull().any().any():
                missing = self.dataframe.isnull().sum()
                for col, count in missing.items():
                    if count > 0:
                        logging.warning(f"Column '{col}' has {count} missing values.")
                return False

            logging.info("No missing values or anomalies detected.")
            return True
        except Exception as e:
            logging.error(f"Unexpected error during anomaly validation: {e}")
            return False

def run_validations(file_path_obj):
    """Run all validation checks."""
    try:
        if not file_path_obj.file_exists():
            return False

        if not file_path_obj.load_csv():
            return False

        if not file_path_obj.validate_columns():
            return False

        if not file_path_obj.validate_data_types():
            return False

        if not file_path_obj.validate_no_anomalies():
            return False

        logging.info("CSV file is valid!")
        return True
    except Exception as e:
        logging.error(f"Unexpected error during validation process: {e}")
        return False
