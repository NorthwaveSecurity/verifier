# Dynamically import all subpackages
import pkgutil
__all__ = []
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    __all__.append(module_name)
from . import *

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


