import os
import logging
import logging.handlers
import json
from datetime import datetime
import shutil


class LoggingConfig:
    """Logging configuration for MetaTrader5 API calls"""
    
    def __init__(self, config_file="log_config.json"):
        self.config_file = config_file
        self.logs_dir = "logs"
        self.config = self._load_config()
        self._setup_logging()
    
    def _load_config(self):
        """Load logging configuration from JSON file or create default"""
        default_config = {
            "log_level": "INFO",
            "log_rotation": "app_run",  # Options: "app_run", "daily", "weekly", "monthly"
            "max_log_files": 10,
            "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "date_format": "%Y-%m-%d %H:%M:%S"
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # TODO - improve behavior merge with defaults for any missing keys
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                print(f"Error loading log config: {e}, using defaults")
                return default_config
        else:
            # Create default config file
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def _setup_logging(self):
        """Setup logging directory and handlers"""
        # Create logs directory if it doesn't exist
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
        
        # Clear logs on app run if configured
        if self.config["log_rotation"] == "app_run":
            self._clear_logs()
        
        # Setup logger
        logger = logging.getLogger("metatrader5")
        logger.setLevel(getattr(logging, self.config["log_level"]))
        
        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            self.config["log_format"],
            datefmt=self.config["date_format"]
        )
        
        # File handler
        log_file = os.path.join(self.logs_dir, f"metatrader5_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    def _clear_logs(self):
        """Clear all log files in logs directory"""
        if os.path.exists(self.logs_dir):
            for filename in os.listdir(self.logs_dir):
                file_path = os.path.join(self.logs_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting log file {file_path}: {e}")
    
    def get_logger(self, name="metatrader5"):
        """Get logger instance"""
        return logging.getLogger(name)


# Global logging instance
logging_config = LoggingConfig()
get_logger = logging_config.get_logger
