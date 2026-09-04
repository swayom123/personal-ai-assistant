import logging
import sys
from pathlib import Path
from typing import Optional

class StructuredFormatter(logging.Formatter):
    """Clean structured log formatter with timestamp, level, and logger name."""
    def format(self, record: logging.LogRecord) -> str:
        record_dict = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "request_id"):
            record_dict["request_id"] = getattr(record, "request_id")
        return f"[{record_dict['timestamp']}] [{record_dict['level']}] [{record_dict['name']}]: {record_dict['message']}"

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Configures structured logging across console and persistent file."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Ensure logs directory exists
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
        
    formatter = StructuredFormatter(datefmt="%Y-%m-%d %H:%M:%S")
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File Handler
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Silence overly chatty libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
