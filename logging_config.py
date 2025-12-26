import logging
import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

class DailyLogFileHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.date = None
        self.file = None
        self._update_file()

    def _update_file(self):
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        if current_date != self.date:
            self.date = current_date

            if self.file:
                self.file.close()

            file_path = os.path.join(LOG_DIR, f"{current_date}.log")
            self.file = open(file_path, "a", encoding="utf-8")

    def emit(self, record):
        self._update_file()
        log_entry = self.format(record)
        self.file.write(log_entry + "\n")
        self.file.flush()


logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

handler = DailyLogFileHandler()
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.propagate = False
