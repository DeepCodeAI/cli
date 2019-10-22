import sys
import os
import argparse
from deepcode.src.modules.DeepCodeArgsParser import DeepCodeArgsParser


def cli_entry_point():
    deepcode_parser = DeepCodeArgsParser()
    deepcode_parser.parse()
