from stepic_plugins.base import BaseQuiz


class SchulteQuiz(BaseQuiz):
    name = 'schulte'

    class Schemas:
        source = {
            'table_size': int,
            'is_grid': bool,
            'is_gorbov_table': bool,
            'is_font_randomized': bool,
            'is_color_randomized': bool,
        }
        dataset = source
        reply = {
            'solved': bool,
            'time_seconds': int,
        }

    def __init__(self, source):
        super().__init__(source)
        self.source = source

    def generate(self):
        dataset = {
            'table_size': self.source.table_size,
            'is_grid': self.source.is_grid,
            'is_gorbov_table': self.source.is_gorbov_table,
            'is_font_randomized': self.source.is_font_randomized,
            'is_color_randomized': self.source.is_color_randomized,
        }
        return dataset, None

    def check(self, reply, clue):
        return reply['solved']
