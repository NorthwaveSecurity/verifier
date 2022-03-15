from .curl import Curl
from .base import add_issue
from ..util import IssueDoesNotExist, SNIP, highlight


class HTTPLinks(Curl):
    description = "Verify that HTTP links are included in a website"

    def edit(self, output):
        lines = output.split('\n')
        trigger = 'http://'
        curl_line = lines[0]
        lines = [line.strip() for line in lines if trigger in line]
        if not lines:
            raise IssueDoesNotExist()
        lines.insert(0, curl_line)
        output = f"\n{SNIP}\n".join(lines)
        url_regex = r"http:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
        return highlight(output, url_regex)


add_issue('http-links', HTTPLinks)
