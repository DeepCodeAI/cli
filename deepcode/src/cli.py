from deepcode.src.modules.deepcode_main import DeepCodeMainModule


def cli_entry_point():
    DeepCodeMainModule(isCliMode=True).activate_cli()
