from collections.abc import Callable
from typing import Any
import typing
from ..util import prepend_command, run_command, PostProcessingFailed
from ..translator import Translator
from ..config import config
from collections import defaultdict
from json import JSONDecoder, JSONEncoder
from dataclasses import dataclass
import pickle
import base64


@dataclass
class Evidence:
    output: str
    issue: 'Issue' = None
    issue_id: str = None
    host: 'typing.Any' = None
    lang: str = "en"
    label: str = None

    def __repr__(self):
        return self.output


@dataclass
class Host:
    hostname: str = None
    port: int = None


class Issue(Translator):
    description = None
    _template = defaultdict(lambda: "{}")
    _standard_issue_path = defaultdict(lambda: None)

    def __init__(self, language="en", content=None, extra_args=None, proxy=None):
        super().__init__(language=language)
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
        self._links = []
        self.parse_args(self.extra_args)
        if proxy is not None:
            self.handle_proxy(proxy)

    def evidence(self, *args, **kwargs):
        return Evidence(*args, issue=self, **kwargs)

    def verify(self):
        """Should yield Evidences"""
        raise NotImplementedError()

    def parse_args(self, args):
        """
        Override to parse extra aguments
        """
        self.args = args

    def postprocess(self, output):
        """
        Override to add postprocessing
        """
        return output

    def append_links(self, output):
        i = 1
        for link in self._links:
            output += f"\n\nbc. fn{i}. {link}"
            i += 1
        return output

    def handle_proxy(self, proxy):
        raise NotImplementedError
    
    @classmethod
    def from_dict(cls, dict):       
        i = cls(dict["language"])
        i._standard_issue_path = dict["_standard_issue_path"]
        i._standard_issue_id = dict["_standard_issue_id"]
        return i

    @property
    def template(self):
        return self._template[self.language]

    @property
    def standard_issue_id(self):
        return self._standard_issue_id[self.language]

    @property
    def standard_issue_path(self):
        return self._standard_issue_path.get(self.language)


class IssueEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Issue):
            i = {
                "_standard_issue_path": obj._standard_issue_path,
                "_standard_issue_id": obj._standard_issue_id if obj._standard_issue_id else None,
                "language": obj.language
            }
            return i
        # Let the base class default method raise the TypeError
        return super().default(obj)


class IssueDecoder(JSONDecoder):
    def __init__(self, **kwargs):
        kwargs["object_hook"] = self.object_hook
        super().__init__(**kwargs)

    def object_hook(self, obj):
        try:
            if "_standard_issue_path" in obj and "_standard_issue_id" in obj and "language" in obj:
                return Issue.from_dict(obj)
            else:
                return obj
        except Exception as e:
            return obj


class CommandIssue(Issue):
    proxychains = False
    sudo = False

    def handle_proxy(self, proxy):
        self.proxychains = True

    def run_command(self, command, visual_command=None, do_prepend_command=True, stdin="", env=None):
        visual_command = visual_command or command
        if 'output' in self.content:
            if do_prepend_command:
                output = prepend_command(visual_command, self.content['output'], sudo=self.sudo)
            else:
                output = self.content['output']
        else:
            if self.proxychains:
                command = [config.get('proxy', 'proxychains_path')] + command
            output = run_command(command, visual_command=visual_command, sudo=self.sudo, do_prepend_command=do_prepend_command, stdin=stdin, env=env)
        try:
            new_output = self.postprocess(output)
            return new_output
        except Exception:
            raise PostProcessingFailed(output)


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


