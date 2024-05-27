from .base import CommandIssue, add_issue, add_expansion, Evidence
from ..util import get_translation, highlight

class Amicontained(CommandIssue):
    description = "Interpret results of amicontained"
    header = "TODO"
    _template = {
        "en": """The AmIContained command shows that {}:

bc.. {{}}
"""
    }

    @property
    def template(self):
        header = get_translation(self.header, self.language)
        output = self._template[self.language].format(header)
        return self.append_links(output)

    def verify(self, *args):
        output = self.run_command(["amicontained"])
        yield Evidence(self.template.format(output))


class Seccomp(Amicontained):
    header = {
        "en": "Seccomp is disabled"
    }

    def postprocess(self, output):
        return highlight(output, "Seccomp: disabled")


class NetRaw(Amicontained):
    header = {
        "en": "the \"net_raw\" capability is granted"
    }

    def postprocess(self, output):
        return highlight(output, "net_raw")


add_issue('seccomp', Seccomp)
add_issue('net_raw', NetRaw)
add_expansion('amicontained', ['seccomp', 'net_raw'])
