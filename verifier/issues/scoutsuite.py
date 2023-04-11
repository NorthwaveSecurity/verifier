from .base import add_issue, add_expansion, Issue
from ..util import host_to_url, HIGHLIGHT_START, HIGHLIGHT_END, IssueDoesNotExist
import os
from os.path import join
import json
from collections import defaultdict

class ScoutSuite(Issue):
    header = defaultdict(lambda: "TODO")
    _template = {
        "en": """Scoutsuite output:

bc.. {}
""",
    }

    def parse(self, scoutsuite_dir):
        dir = join(scoutsuite_dir, 'scoutsuite-results')
        for filename in os.listdir(dir):
            if filename.startswith("scoutsuite_results"):
                break
        path = join(dir, filename)
        with open(path) as f:
            self.contents = json.loads(f.read().partition('\n')[2])

    def get_template(self, info):
        return super().template.format(info)

    def verify(self, scoutsuite_dir):
        self.parse(scoutsuite_dir)


class GuestUsers(ScoutSuite):
    _subscript = {
        "en": "Total number of guest users",
    }

    @property
    def subscript(self):
        return self._subscript[self.language]

    def verify(self, scoutsuite_dir):
        super().verify(scoutsuite_dir)
        contents = ""
        try:
            service = self.contents['services']['aad']
            finding = service['findings']['aad-guest-users']
            items = finding['items']
            user = items[0]
            id = user.split('.')[2]
            user = service['users'][id]
        except KeyError:
            raise IssueDoesNotExist()

        highlighted_user = HIGHLIGHT_START + user['user_type'] + HIGHLIGHT_END

        info = f"""\
Name: {user['name']}
Type: {highlighted_user}

--snip--
{self.subscript}: {HIGHLIGHT_START}{len(items)}{HIGHLIGHT_END}"""
        yield self.get_template(info)


add_issue('guest-users', GuestUsers)

add_expansion('scoutsuite', ['guest-users'])
