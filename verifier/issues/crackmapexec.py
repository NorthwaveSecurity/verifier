from .base import Issue, add_issue, add_expansion, Evidence
from verifier.util import highlight, IssueDoesNotExist, get_translation

class CME(Issue):
    description = "Parse crackmapexec output"
    _template = {
        "en": """
bc.. {}
"""
    }
    trigger = "TODO"

    def verify(self, target):
        output = self.content['output']
        res = []
        for line in output.splitlines():
            if line.startswith("$"):
                # CMD line
                res.append(line)
            if self.trigger in line:
                res.append(highlight(line, self.trigger))
        if not res:
            raise IssueDoesNotExist()
        yield Evidence(self.template.format("\n".join(res)))


class CME_SMB_Signing(CME):
    header = {
        "en": "SMB settings",
        "nl": "SMB configuratie"
    }
    footer = {
        "en": "SMB signing is not enforced",
        "nl": "SMB signing niet is vereist"
    }
    trigger = 'signing:False'


class CME_SMB_V1(CME):
    trigger = 'SMBv1:True'


add_issue('smb-signing', CME_SMB_Signing)
add_issue('smb-v1', CME_SMB_V1)
add_expansion('cme', ['smb-signing', 'smb-v1'])
