import logging
from shared.logging import configure_logging, LoggingConfig

configure_logging(LoggingConfig(level="INFO", format_type="JSON"))

from shared.logging.context import set_telemetry_context

set_telemetry_context({"request_id": "test-request-id", "user_id": "test-user-id"})

logger = logging.getLogger("test")
logger.info("my_event_name", extra={"tool_name": "search", "duration_ms": 120})
