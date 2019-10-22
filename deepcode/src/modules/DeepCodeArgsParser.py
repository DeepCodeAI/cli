import sys
import os
import argparse


class DeepCodeArgsParser:

    def __init__(self):
      # TODO: add help for options arguments
        self.parser = argparse.ArgumentParser(
            prog="deepcode", description="DeepCode CLI description", epilog="More description in the end")

        self.subparsers = self.parser.add_subparsers(
            help='CLI description', dest='cli_command')

        self.user_parser = self.subparsers.add_parser(
            'login', help='user help')
        self.user_parser = self.subparsers.add_parser(
            'logout', help='user help')

        self.config_parser = self.subparsers.add_parser(
            'config', help='config help', aliases=['c'])
        self.config_parser.add_argument(
            '-l', action='store_true', help='list help')

        self.analyze_parser = self.subparsers.add_parser(
            'analyze', help='config help', aliases=['a'])
        self.analyze_parser.add_argument(
            'path', type=str, help='path to analyze')
        self.analyze_parser.add_argument(
            '-f', '--format', choices=['json', 'txt'], help='list help')

    def parse(self):
        if len(sys.argv) == 1:
            self.parser.print_help()
            return None
        self.process_args(vars(self.parser.parse_args()))

    def process_args(self, args_dict):
        print(args_dict)
