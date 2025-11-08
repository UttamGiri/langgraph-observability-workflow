import logging
import json
import os
from datetime import datetime


LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "langgraph_run.log")),
        logging.StreamHandler()
    ]
)


def log_step(node_name, inputs, outputs):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "node": node_name,
        "inputs": inputs,
        "outputs": outputs
    }
    logging.info(json.dumps(log_entry, indent=2))
