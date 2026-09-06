"""Entry point for running the server as a module (``python -m mcp_project_context_server``)."""
import argparse

from mcp_project_context_server.helpers.logs import ParseLogLevel, setup_logging
from mcp_project_context_server.server import run

parser = argparse.ArgumentParser()
parser.add_argument(
    "--log-level",
    action=ParseLogLevel,
    metavar="name=LEVEL",
    dest="log_level",
    default={},
    help="Override log level for a specific logger, e.g. urllib3=WARNING. "
         "Can be passed multiple times.",
)

arguments = parser.parse_args()
setup_logging(arguments.log_level)
run()
