from .base import add_issue
from .curl import Curl
from .ftp import FTP
from ..util import SNIP, highlight, IssueDoesNotExist
import re


class Outdated:
    _software = "SOFTWARE"
    _version = "VERSION"
    vuln_link = None

    @property
    def header(self):
        _header = {
            "en": f"{self._software} version {self._version} is in use",
        }
        if self.vuln_link:
            _header["en"] += ". This version contains known vulnerabilities<1>"
            self._links.append(self.vuln_link)
        return _header

    @property
    def description(self):
        if self._software == "SOFTWARE":
            return "Verify an outdated front-end library"
        else:
            return "Verify an outdated version of {}".format(self._software)

    def edit(self, output):
        regex = re.compile(rf"{self._software}{self._version_regex}")
        version_search = re.search(regex, output)
        if not version_search:
            raise IssueDoesNotExist()
        self._version = version_search.group(1)
        return highlight(output, regex)


class NVDLinkMixin:
    @property
    def vuln_link(self):
        return f"https://nvd.nist.gov/vuln/search/results?form_type=Advanced&results_type=overview&search_type=all&isCpeNameSearch=false&cpe_version=cpe:/:{self._vendor}:{self._software}:{self._version}"


class OutdatedWeb(Outdated, Curl):
    pass


class OutdatedFTP(NVDLinkMixin, Outdated, FTP):
    def postprocess(self, output):
        return self.edit(output)


class OutdatedVSFTPd(OutdatedFTP):
    _software = "vsFTPd"
    _vendor = "vsftpd_project"
    _version_regex = r" ([\d\.]+)"


class OutdatedHTTPHeader(NVDLinkMixin, OutdatedWeb):
    _version_regex = r"/([\d\.]+)"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra_args = ["-I"]


class OutdatedNginx(OutdatedHTTPHeader):
    _software = "nginx"
    _vendor = "f5"


class OutdatedWordpress(OutdatedWeb):
    _software = "WordPress"

    def edit(self, output):
        version_regex = re.compile(r"https://wordpress.org/\?v=([\d\.]+)")
        split = output.split('\n')
        new_output = split[:2]
        new_output.append(SNIP)
        for i, line in enumerate(split):
            if re.search(version_regex, line):
                new_output.append(line)
                break
        new_output.append(SNIP)
        output = '\n'.join(new_output)
        version_search = re.search(version_regex, output)
        if not version_search:
            raise IssueDoesNotExist()
        self._version = version_search.group(1)
        output = highlight(output, version_regex)
        return output

    def edit_url(self, url):
        postfix = '/start/feed/'
        if not url.endswith(postfix):
            url += postfix
        return super().edit_url(url)


class OutdatedWebHeaderComment(OutdatedWeb):
    version_prefix = 'v'

    def __init__(self, *args, **kwargs):
        self.version_regex = re.compile(self._software + ' ' + r'(?:JavaScript Library )?' + self.version_prefix + r'([\d\.]+)')
        super(OutdatedWeb, self).__init__(*args, **kwargs)

    def edit(self, output):
        index = output.find('*/')
        output = output[:index+3] + SNIP
        version_search = re.search(self.version_regex, output)
        if not version_search:
            raise IssueDoesNotExist()
        self._version = version_search.group(1)
        output = highlight(output, self.version_regex)
        return output


class OutdatedBootstrap(OutdatedWebHeaderComment):
    _software = "Bootstrap"

    @property
    def vuln_link(self):
        return f"https://snyk.io/vuln/npm:bootstrap@{self._version}"


class OutdatedJQuery(OutdatedWebHeaderComment):
    _software = "jQuery"

    @property
    def vuln_link(self):
        return f"https://snyk.io/test/npm/jquery/{self._version}"


class OutdatedJQueryUIDialog(OutdatedWebHeaderComment):
    _software = "jQuery UI Dialog"
    version_prefix = ""


class OutdatedJQueryUI(OutdatedWebHeaderComment):
    _software = "jQuery UI"
    version_prefix = "- v"

    @property
    def vuln_link(self):
        return f"https://snyk.io/vuln/npm:jquery-ui@{self._version}"


class OutdatedModernizr(OutdatedWebHeaderComment):
    _software = "modernizr"
    version_prefix = ""

    @property
    def vuln_link(self):
        return f"https://snyk.io/test/npm/modernizr/{self._version}"


class OutdatedPLUpload(OutdatedWebHeaderComment):
    _software = "plupload"

    def __init__(self, *args, **kwargs):
        self.version_regex = r"(\d+\.[\d\.]+)"
        super(OutdatedWeb, self).__init__(*args, **kwargs)


add_issue('outdated-web', OutdatedWeb)
add_issue('outdated-bootstrap', OutdatedBootstrap)
add_issue('outdated-jquery', OutdatedJQuery)
add_issue('outdated-wordpress', OutdatedWordpress)
add_issue('outdated-jquery-ui', OutdatedJQueryUI)
add_issue('outdated-jquery-ui-dialog', OutdatedJQueryUIDialog)
add_issue('outdated-modernizr', OutdatedModernizr)
add_issue('outdated-plupload', OutdatedPLUpload)
add_issue('outdated-nginx', OutdatedNginx)
add_issue('outdated-vsftpd', OutdatedVSFTPd)
