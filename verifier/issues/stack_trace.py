from .base import add_issue, Evidence
from .dradis_curl_issue import DradisCurlIssue
from ..util import SNIP
import re


class StackTrace(DradisCurlIssue):
    description = "Verify that stack traces are enabled"
    stacktrace_started = False

    def is_stacktrace_line(self, line):
        start_regex = re.compile(r"line \d+|Exception in thread|stack-error|Caused by:|Error:|<b>Exception</b>")
        stacktrace_regex = re.compile(r"at .*?\(|[\w\.\d]+\([\w\d]+\.(java|js):\d+\)")
        if start_regex.search(line):
            self.stacktrace_started = True
            return True
        elif self.stacktrace_started and stacktrace_regex.search(line):
            return True
        else:
            return False

    def edit(self, response):
        def edit_function(line):
            if self.is_stacktrace_line(line):
                return "$${{" + line + "}}$$"
            else:
                return False
        return self.edit_body(response, edit_function)

    def verify(self, url):
        request, response = self.do_request(url)
        evidence = Evidence(self.template.format(request, self.edit(response)))
        evidence.request = request
        evidence.response = response
        yield evidence


add_issue('stacktrace', StackTrace)
