from stepic_plugins.base import BaseQuiz


class FooBarQuiz(BaseQuiz):
    name = 'foo-bar'

    class Schemas:
        source = ...
        dataset = ...  # remove if you don't need it
        reply = ...

    def __init__(self, source):
        super().__init__(source)

    def generate(self): # remove if you don't need it
        pass

    def clean_reply(self, reply, dataset):
        pass

    def check(self, reply, clue):
        pass
