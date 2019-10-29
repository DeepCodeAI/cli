from deepcode.src.modules.deepcode_main import DeepCodeMainModule


class DeepcodeModule:
    def __init__(self):
        self.__deepcode_module = DeepCodeMainModule(is_cli_mode=False)

        self.__analyze_func = self.__deepcode_module.module_analyze_actions

    def analyze(self, parent_path, child_path, is_repo):
        paths = {'parent_path': parent_path, 'child_path': child_path}
        return self.__analyze_func(paths, is_repo)


deepcode_module = DeepcodeModule()
