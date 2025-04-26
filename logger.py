import logging
from logging.handlers import RotatingFileHandler

# Set up basic configuration for logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Create a logger instance
logger = logging.getLogger("shed-ext12drm")
logger.setLevel(logging.INFO)

# Optional: File handler to save logs to file (with rotation)
file_handler = RotatingFileHandler("shed-ext12drm.log", maxBytes=5*1024*1024, backupCount=2)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)
