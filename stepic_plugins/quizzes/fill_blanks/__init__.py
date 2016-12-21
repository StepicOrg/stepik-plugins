from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError
from stepic_plugins.utils import clean_html


class ComponentType:
    INPUT = 'input'
    SELECT = 'select'
    TEXT = 'text'

    all = {INPUT, SELECT, TEXT}


class FillBlanksQuiz(BaseQuiz):
    name = 'fill-blanks'

    class Schemas:
        source = {
            'components': [{
                'type': str,
                'text': str,
                'options': [{
                    'text': str,
                    'is_correct': bool,
                }],
            }],
            'is_case_sensitive': bool,
        }
        dataset = {
            'components': [{
                'type': str,
                'text': str,
                'options': [str],
            }],
        }
        reply = {
            'blanks': [str],
        }

    def __init__(self, source):
        super().__init__(source)
        if any(comp.type not in ComponentType.all for comp in self.source.components):
            raise FormatError("Invalid component type")
        self.blanks = [comp for comp in self.source.components if comp.type != ComponentType.TEXT]
        if not self.blanks:
            raise FormatError("The problem should contain at least one blank block")

        for component in self.source.components:
            if component.type != ComponentType.TEXT:
                continue
            text = component.text
            component.text = clean_html(component.text, strip=False)
            is_incorrect_html = lambda a, b: component.text.replace(a, b).count(b) != text.count(b)
            if is_incorrect_html('&gt;', '>') or is_incorrect_html('&lt;', '<'):
                raise FormatError('Incorrect html: {}'.format(text))

    def generate(self):
        dataset = {
            'components': [{
                'type': component.type,
                'text': component.text,
                'options': ([option.text for option in component.options]
                            if component.type == ComponentType.SELECT else []),
            } for component in self.source.components]
        }
        clue = [[option.text.strip() for option in blank.options if option.is_correct]
                for blank in self.blanks]
        return dataset, clue

    def clean_reply(self, reply, dataset):
        if len(reply.blanks) != len(self.blanks):
            raise FormatError("Reply has a wrong number of blanks")
        blanks = [blank.strip() for blank in reply.blanks]
        return blanks

    def check(self, reply, clue):
        for blank_value, correct_values in zip(reply, clue):
            if not self.source.is_case_sensitive:
                blank_value = blank_value.lower()
                correct_values = [v.lower() for v in correct_values]
            if blank_value not in correct_values:
                return False
        return True
