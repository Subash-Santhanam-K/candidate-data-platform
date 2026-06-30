import argparse


def create_parser() -> argparse.ArgumentParser:
    """Creates the command-line argument parser for the platform.

    Returns:
        argparse.ArgumentParser: Configured parser instance.
    """
    parser = argparse.ArgumentParser(description="Candidate Data Platform CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    process_parser = subparsers.add_parser("process", help="Process candidate files through the pipeline")
    process_parser.add_argument(
        "--adapter",
        required=True,
        help="Adapter type (e.g. resume, linkedin, github, csv)",
    )
    process_parser.add_argument(
        "--input",
        required=True,
        help="Path to input data file",
    )
    process_parser.add_argument(
        "--profile",
        required=True,
        help="Target visibility profile (e.g. minimal, recruiter, audit)",
    )

    return parser
