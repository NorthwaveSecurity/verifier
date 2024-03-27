from .nmap import SSHAlgos
from .base import add_issue, add_expansion, Evidence
from ..util import highlight
import re

# Note, this list is not complete yet. Adapt it based on Nessus output
weak_algos = [
    # https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/09-Testing_for_Weak_Cryptography/04-Testing_for_Weak_Encryption
    r"arcfour",
    r"-cbc(@openssh.org)?", 
    r"-md5(-|$)",
    r"blowfish",
    r"-sha1(-|$)",

    # https://www.tenable.com/plugins/nessus/153953
    # https://datatracker.ietf.org/doc/rfc9142/
    r"diffie-hellman-group-exchange-sha1",
    r"diffie-hellman-group1-sha1",
    r"gss-gex-sha1-",
    r"gss-group1-sha1-",
    r"gss-group14-sha1-",
    r"rsa1024-sha1",
]

class SSHWeakAlgos(SSHAlgos):
    _footer = {
        "en": "p. This shows that weak algorithms are in use.",
    }

    def postprocess(self, output_str):
        lines = []
        for line in output_str.splitlines():
            for alg in weak_algos:
                if re.search(alg, line.strip()):
                    line = highlight(line)
                    break
            lines.append(line)
        return '\n'.join(lines)


add_issue('ssh-weak-algos', SSHWeakAlgos)
