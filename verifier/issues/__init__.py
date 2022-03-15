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
from .base import Issue, expansions, issues, add_issue, add_expansion

add_expansion('all', [
    'all-missing-headers',
    'server-version',
    'dnssec',
])
