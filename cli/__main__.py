# August 2020, Lewis Gaul

"""
CLI entry-point.

"""

import pathlib
import subprocess
import sys
from typing import Any, Callable, Dict

# Any 3rd-party dependencies must be kept in bootstrap/.
import yaml

from cli.parser import CLIParser


_THIS_DIR = pathlib.Path(__file__).absolute().parent


def run_app(args):
    subprocess.run(["python3", "-m", "minegauler"])


def run_bot_cli(args):
    from bin.cli import run

    return run(args.remaining_argv)


_COMMANDS: Dict[str, Callable[[Any], int]] = {
    "run": run_app,
    "make-venv": lambda args: print("Not implemented"),
    "run-tests": lambda args: print("Not implemented"),
    "bump-version": lambda args: print("Not implemented"),
    "bot": run_bot_cli,
}


def main(argv):
    # Load the CLI schema.
    with open(_THIS_DIR / "cli.yaml") as f:
        schema = yaml.safe_load(f)

    # Parse argv.
    args = CLIParser(schema).parse_args(argv)
    print("Got args:", args)

    # Run the command!
    return _COMMANDS[args.command](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
