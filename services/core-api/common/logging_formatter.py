import json
import logging
from datetime import datetime, timezone

class StructuredJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line_number": record.lineno,
        }

        # Context correlation tracking
        if hasattr(record, "correlation_id"):
            log_record["correlation_id"] = record.correlation_id
        if hasattr(record, "event_id"):
            log_record["event_id"] = record.event_id
        if hasattr(record, "task_id"):
            log_record["task_id"] = record.task_id

        # Attach exception trace if available
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)
