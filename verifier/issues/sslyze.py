from .base import CommandIssue, add_expansion, add_issue, Evidence
from ..util import SNIP, IssueDoesNotExist, HIGHLIGHT_START, HIGHLIGHT_END
from collections import defaultdict

class SSLyzeIssue(CommandIssue):
    description = "Run SSLyze"
    _header = {
        "en": "SSLyze output:",
        "nl": "SSLyze output:"
    }
    _footer = defaultdict(lambda: "TODO")
    _template = {
        "en": """{}

bc.. {}

p. {}""",
        "nl": """{}

bc.. {}

p. {}""",

    }

    def run_sslyze(self, host):
        return super().run_command(["sslyze", host])

    def verify(self, host):
        result = self.run_sslyze(host)
        yield Evidence(self.template.format(self.header, result.rstrip(), self.footer))

    def postprocess(self, output):
        i = output.index("COMPLIANCE AGAINST MOZILLA")
        lines = output.splitlines()
        output = "\n".join(lines[:5] + [SNIP, ""]) + output[i:]
        return super().postprocess(output)

    @property
    def header(self):
        return self._header[self.language]

    @property
    def footer(self):
        return self._footer[self.language]


class SSLyzeTLSVersions(SSLyzeIssue):
    _footer = {
        "en": "Outdated TLS versions are supported.",
        "nl": "Verouderde TLS versies worden ondersteund.",
    }
    def postprocess(self, output):
        output = super().postprocess(output)
        lines = output.splitlines()
        found = False
        new_lines = []
        for line in lines:
            if "tls_versions" in line:
                found = True
                new_lines.append(HIGHLIGHT_START + line + HIGHLIGHT_END)
                break
            else:
                new_lines.append(line)
        if not found:
            raise IssueDoesNotExist
        return "\n".join(new_lines)


class SSLyzeWeakCiphers(SSLyzeIssue):
    _footer = {
        "en": "Weak TLS ciphers are supported.",
        "nl": "Zwakke TLS ciphers worden ondersteund.",
    }
    def postprocess(self, output):
        output = super().postprocess(output)
        lines = output.splitlines()
        found = False
        new_lines = []
        for line in lines:
            if "ciphers" in line:
                found = True
                line = HIGHLIGHT_START + line + HIGHLIGHT_END
            new_lines.append(line)
        if not found:
            raise IssueDoesNotExist
        return "\n".join(new_lines)


add_issue("sslyze-raw", SSLyzeIssue)
add_issue("sslyze-versions", SSLyzeTLSVersions)
add_issue("sslyze-ciphers", SSLyzeWeakCiphers)

add_expansion("sslyze", ["sslyze-versions", "sslyze-ciphers"])
