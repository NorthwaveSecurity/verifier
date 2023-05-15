from . import LFI
from . import session_after_logout
from . import nuclei
from . import curl
from . import outdated_web
from . import nmap
from . import missing_header
from . import dnssec
from . import server_version
from . import cors
from . import http_links
from . import track_trace
from . import http
from . import cookie_flags
from . import stack_trace
from . import path_disclosure
from . import portscan
from . import sslyze
from . import scoutsuite
from . import crackmapexec
from . import ssh
from . import amicontained
from .base import Issue, CommandIssue, expansions, issues, add_issue, add_expansion

add_expansion('all', [
    'all-missing-headers',
    'server-version',
    'dnssec',
    'cookie-flags',
])

def get_issue(id, lang="en", content=None, extra_args=None, **kwargs):
    try:
        issue_class = issues[id.lower()]
        return issue_class(language=lang, content=content, extra_args=extra_args, **kwargs)
    except KeyError:
        raise ValueError(f"Issue {id} does not exist.")


