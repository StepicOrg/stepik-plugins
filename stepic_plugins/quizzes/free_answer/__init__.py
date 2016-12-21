from stepic_plugins.base import BaseQuiz
from stepic_plugins.schema import attachment
from stepic_plugins.utils import clean_html


class FreeAnswerQuiz(BaseQuiz):
    name = 'free-answer'

    class Schemas:
        source = {
            'is_attachments_enabled': bool,
            'is_html_enabled': bool,
            'manual_scoring': bool,
        }
        dataset = {
            'is_attachments_enabled': bool,
            'is_html_enabled': bool,
        }
        reply = {
            'text': str,
            'attachments': [attachment],
        }

    def generate(self):
        dataset = {
            'is_attachments_enabled': self.source.is_attachments_enabled,
            'is_html_enabled': self.source.is_html_enabled,
        }
        return dataset, None

    def clean_reply(self, reply, dataset):
        sanitized_text = clean_html(reply.text)
        if sanitized_text != reply.text:
            cleaned_reply = reply._original
            cleaned_reply['text'] = sanitized_text
            return cleaned_reply
        return reply

    def check(self, reply, clue):
        if not clean_html(reply['text'], tags=['img']).strip() and not reply['attachments']:
            return False, 'Empty reply. Please write some text.'
        return True
