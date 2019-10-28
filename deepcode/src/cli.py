from deepcode.src.modules.deepcode_main import DeepCodeMainModule


def cli_entry_point():
    DeepCodeMainModule(is_cli_mode=True).activate_cli()
