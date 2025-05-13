import logging, os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

# Configure logging
BASE_DIR_LOGS = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(BASE_DIR_LOGS, "logs")

# Ensure the 'logs' directory exists
os.makedirs(log_file_path, exist_ok=True)

log_filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
saved_file_path = os.path.join(log_file_path, log_filename)

# Use TimedRotatingFileHandler for log rotation at midnight
log_handler = TimedRotatingFileHandler(
    saved_file_path, when="midnight", interval=1, backupCount=7
)
log_handler.setLevel(logging.DEBUG)

# Define log format
formatter = logging.Formatter('%(levelname)s:     %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
log_handler.setFormatter(formatter)

# Add a console handler to log messages to the terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# Create the logger and add the handler
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.addHandler(console_handler)