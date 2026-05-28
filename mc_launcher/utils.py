import logging
from pathlib import Path

log_file = Path("launcher.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mc_launcher")
logger.info("🚀 Лаунчер запущен")