from .base import Issue, add_issue, add_expansion, Evidence
from dradis_curl import Request, Response
from ..util import highlight

class Sessionafterlogout(Issue):
    description = "Verify that session is still valid after logout. Requires content (-c)."
    _template = {
        "en": """Logout request:
        
bc.. {}

p. Response:

bc.. {}

p. Request in the same (logged-out) session:

bc.. {}

p. Response:

bc.. {}""",
    }
    
    def verify(self, host):
        highlight_regex = r"(Set-)?Cookie: [^\r\n]+"
        length=3
        logout = Request(text=self.content['logout'], show_sensitive_length=length)
        logout_resp = Response(text=self.content['logout_response'], show_sensitive_length=length)
        request = Request(text=self.content['request'], show_sensitive_length=length)
        response = Response(text=self.content['response'], show_sensitive_length=length)
        logout_str = highlight(str(logout), highlight_regex)
        logout_resp_str = highlight(str(logout_resp), highlight_regex)
        request_str = highlight(str(request), highlight_regex)
        response_str = highlight(str(response), highlight_regex)
        evidence = Evidence(self.template.format(
            logout_str, logout_resp_str,
            request_str, response_str
        ))
        evidence.logout_str = logout_str
        evidence.logout_resp_str = logout_resp_str
        evidence.request_str = request_str
        evidence.response_str = response_str
        yield evidence


add_issue('session-after-logout', Sessionafterlogout)
# add_expansion('expansion-name ', [
#     'issue-name',
#     'issue-name1',
# ])
