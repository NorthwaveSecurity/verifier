from .base import Issue, add_issue, add_expansion, Evidence
from verifier.util import highlight, IssueDoesNotExist, get_translation
import re

class CME(Issue):
    description = "Parse crackmapexec output"
    _template = {
        "en": """
bc.. {}
"""
    }
    triggers = []

    def verify(self, target):
        output = self.content['output']
        res = []
        for line in output.splitlines():
            if line.startswith("$"):
                # CMD line
                res.append(line)
            for trigger in self.triggers:
                if trigger in line:
                    res.append(highlight(line, trigger))
        if not res:
            raise IssueDoesNotExist()
        yield Evidence(self.template.format("\n".join(res)))


class CME_SMB_Signing(CME):
    triggers = ['signing:False']


class CME_SMB_V1(CME):
    triggers = ['SMBv1:True']


class CME_password_policy(CME):

    def verify(self, target):
        output = self.content['output']
        found = False
        res = []
        for line in output.splitlines():
            if "Account Lockout Threshold: None" in line:
                found = True
                res.append(highlight(line))
            elif "Minimum password length" in line:
                found = True
                num = int(re.search(r"length: (\d+)", line).group(1))
                if num >= 11:
                    continue
                res.append(highlight(line))
            else:
                res.append(line)
        if not found:
            raise IssueDoesNotExist()
        yield Evidence(self.template.format("\n".join(res)))



add_issue('password-policy', CME_password_policy)
add_issue('smb-signing', CME_SMB_Signing)
add_issue('smb-v1', CME_SMB_V1)
add_expansion('cme', ['smb-signing', 'smb-v1', 'password-policy'])
