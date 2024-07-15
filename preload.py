import argparse


def preload(parser: argparse.ArgumentParser):
    parser.add_argument("--mo-show-dir-settings", action='store_true', help="Enable models dir change in settings")
    parser.add_argument("--mo-debug", action='store_true', help="Enable Model Organizer Debug Mode")
    parser.add_argument("--mo-database-dir", type=str, help="Path to directory wiFth database", default=None)
