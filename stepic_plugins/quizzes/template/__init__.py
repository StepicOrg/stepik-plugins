from stepic_plugins.base import BaseQuiz


class FooBarQuiz(BaseQuiz):
    name = 'foo-bar'

    class Schemas:
        source = ...
        reply = ...
        dataset = ...  # remove if you don't need it

    def __init__(self, source):
        super().__init__(source)

    def clean_reply(self, reply, dataset):
        pass

    def check(self, reply, clue):
        pass

    def generate(self): # remove if you don't need it
        pass
