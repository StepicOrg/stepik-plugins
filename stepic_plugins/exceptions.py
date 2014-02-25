class PluginError(Exception):
    pass


class FormatError(PluginError):
    pass


class QuizSetUpError(PluginError):
    pass


class UnknownPluginError(PluginError):
    pass
