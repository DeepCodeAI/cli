from deepcode.src.modules.deepcode_main import DeepCodeMainModule


class DeepcodeModule:
    def __init__(self):
        self.__deepcode_module = DeepCodeMainModule(is_cli_mode=False)

        self.__analyze_func = self.__deepcode_module.module_analyze_actions

    def analyze(self, path, is_repo):
        return self.__analyze_func(path, is_repo)


deepcode_module = DeepcodeModule()
