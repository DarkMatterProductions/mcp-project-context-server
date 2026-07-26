import argparse
import logging
import sys
import uuid
from pathlib import Path


class ParseLogLevel(argparse.Action):
    """
    Collects repeated --log-level name=LEVEL flags into a dict.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        d = getattr(namespace, self.dest) or {}
        try:
            name, level = values.split("=", 1)
        except ValueError:
            raise argparse.ArgumentError(
                self, f"expected format name=LEVEL, got '{values}'"
            )
        d[name] = level
        setattr(namespace, self.dest, d)


def setup_logging(logger_levels: dict[str, int | str] | None = None):
    """
    Configure the root logger to log to stdout and to _LOG_PATH.

    logger_levels: optional dict of {"<library_name>": <log_level>}
        to override the level for specific loggers, e.g.
        {"urllib3": "WARNING", "botocore": logging.WARNING}
        Values can be int constants (logging.WARNING) or level
        name strings ("WARNING", "debug", etc. - case-insensitive).
    """
    _PROCESS_ID = uuid.uuid4().hex[:8]
    _LOG_PATH = Path.home() / ".mcp-data" / "logs" / f"project-context-server-{_PROCESS_ID}.log"


    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    file_handler = logging.FileHandler(_LOG_PATH, mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)

    # Guard against duplicate handlers if setup_logging() runs more than once
    if not root.handlers:
        root.addHandler(file_handler)
        root.addHandler(stream_handler)

    # --- Per-logger level overrides ---
    for name, level in (logger_levels or {}).items():
        if isinstance(level, str):
            level = level.upper()
        logging.getLogger(name).setLevel(level)