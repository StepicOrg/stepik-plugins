from stepic_plugins.base import BaseQuiz

# I just want the future to happen faster.
# I can't imagine the future without robots.
# (Nolan Bushnell)

class RosQuiz(BaseQuiz):
    name = 'ros'

    class Schemas:
        source = {
            'generatorlaunch': str,
            'solverlaunch': str,
            'generatorpy': str,
            'solverpy': str,
            'paramsyaml': str,
        }

        reply = {
            'resultset': str,
        }
        dataset = {
            'file': str
        }

    def __init__(self, source):
        super().__init__(source)
        self.generatorlaunch = source.generatorlaunch
        self.solverlaunch = source.solverlaunch
        self.generatorpy = source.generatorpy
        self.solverpy = source.solverpy
        self.paramsyaml = source.paramsyaml

    def generate(self):
        # TODO: roslaunch stepic_dataset generator.launch
        dataset = {'file': 'ROS Dataset'}
        return dataset, 'ROS Clue'

    def clean_reply(self, reply, dataset):
        return reply.resultset

    def check(self, reply, clue):
        # TODO: roslaunch stepic_dataset solver.launch
        return 1, 'ROS Feedback'
