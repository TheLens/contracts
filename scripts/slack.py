
'''Interactions with Slack.'''

from subprocess import call
from contracts import WEBHOOK_URL


class Slack(object):

    '''Methods for sending Slack webhooks.'''

    def _send_slack_webhook(self, fallback="", pretext="", text="", title="",
                            color='#36a64f', emoji=':oncoming_police_car:'):
        '''Sends webhook to Slack channel.'''

        command = (
            'curl ' +
            '-X ' +
            'POST ' +
            '--data-urlencode ' +
            '\'payload={' +
            '"username": "Contracts app", ' +
            '"icon_emoji": "%s", ' % emoji +
            '"attachments": [{' +
            '"fallback": "%s", ' % fallback +
            '"color": "%s", ' % color +
            '"pretext": "%s", ' % pretext +
            '"text": "%s", ' % text +
            '"title": "%s", ' % title +
            '"title_link": "Contracts", ' +
            '"mrkdwn_in": ["text", "pretext"]' +
            '}]}\' ' +
            WEBHOOK_URL)

        call(command, shell=True)

    def send_ssn_notice(self, doc_id, matching_string):
        '''Sends message to Slack channel alerting possible SSN in contract.'''

        fallback = "SSN detected"
        pretext = "A possible social security number " + \
            "(`%s`) was detected in the following document:" % matching_string
        text = "https://www.documentcloud.org/documents/" + doc_id + ".html"

        self._send_slack_webhook(fallback=fallback, pretext=pretext, text=text)
