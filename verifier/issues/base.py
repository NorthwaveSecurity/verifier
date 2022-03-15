from ..util import prepend_command, run_command
from collections import defaultdict


class Issue:
    description = None
    _template = defaultdict(lambda: "{}")

    def __init__(self, language="en", content=None, extra_args=None, proxy=None):
        self.language = language
        if content:
            self.content = content
        else:
            self.content = {}
        if extra_args:
            if extra_args[0] == "--":
                self.extra_args = extra_args[1:]
            else:
                self.extra_args = extra_args
        else:
            self.extra_args = []
        self.parse_args(self.extra_args)
        if proxy is not None:
            self.handle_proxy(proxy)

    def verify(self):
        """Should yield evidences"""
        raise NotImplementedError()

    def parse_args(self, args):
        """
        Override to parse extra aguments
        """
        pass

    def postprocess(self, output):
        """
        Override to add postprocessing
        """
        return output

    def prepend_description(self, template):
        return "#[Description]#\n" + template

    def handle_proxy(self, proxy):
        raise NotImplementedError

    @property
    def template(self):
        return self.prepend_description(self._template[self.language])

    @property
    def standard_issue_id(self):
        return self._standard_issue_id[self.language]


class CommandIssue(Issue):
    proxychains = False
    sudo = False

    def handle_proxy(self, proxy):
        self.proxychains = True

    def run_command(self, command, visual_command=None, do_prepend_command=True):
        visual_command = visual_command or command
        if 'output' in self.content:
            if do_prepend_command:
                output = prepend_command(visual_command, self.content['output'], sudo=self.sudo)
            else:
                output = self.content['output']
        else:
            if self.proxychains:
                command = ['proxychains'] + command
            output = run_command(command, visual_command=visual_command, sudo=self.sudo, do_prepend_command=do_prepend_command)
        output = self.postprocess(output)
        return output


issues = {}

expansions = {}


def add_issue(key, issue_class):
    if not issues.get(key) is None:
        Exception(f"An issue with key {key} already exists")
    issues[key] = issue_class


def add_expansion(key, issue_list):
    if not expansions.get(key) is None:
        Exception(f"An issue group with key {key} already exists")
    if not issues.get(key) is None:
        Exception(f"An issue with key {key} already exists, expansions cannot override issues")
    expansions[key] = issue_list
