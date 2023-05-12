from .base import add_issue, CommandIssue
from ..util import get_translation


class FTP(CommandIssue):
    description = "Run an ftp command without specific issue"
    header = "TODO"
    footer = "TODO"
    _template = {
        "en": """The following ftp command shows that {}.

bc.. {{}}

p. {}."""
    }
    stdin = ""

    @property
    def template(self):
        header = get_translation(self.header, self.language)
        footer = get_translation(self.footer, self.language)
        output = self._template[self.language].format(header, footer)
        return self.append_links(output)

    def verify(self, host):
        output = self.run_command(['ftp', '-nv', host], stdin=self.stdin)
        yield self.template.format(output.strip())


add_issue('ftp', FTP)
