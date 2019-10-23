import sys
import os
import argparse
from deepcode.src.modules.deepcode_lib import DeepCodeLib


def cli_entry_point():
    DeepCodeLib(isCliMode=True).activate_cli()
