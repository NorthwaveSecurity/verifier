from .base import CommandIssue, add_issue
from ..util import host_to_args, highlight, IssueDoesNotExist
import re


class NmapIssue(CommandIssue):
    _nse_header = {
        "en": "and the NSE script ‘{}’",
        "nl": "en het NSE script ‘{}’",
    }
    _template = {
        "en": """p. Using the tool Nmap {}

bc.. {{}}

""",
    }
    _header = {
        "en": "TODO",
    }
    _footer = {
        "en": "p. This shows that TODO",
    }

    description = "Run an Nmap NSE script"
    nse = ""
    flags = []
    port = None

    def parse_args(self, extra_args):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--script')
        args, extra_args = parser.parse_known_args(extra_args)
        if args.script:
            self.nse = args.script
        self.extra_args = extra_args

    def postprocess(self, output_str):
        index = output_str.find('\n\nNmap done')
        return output_str[:index]

    def command(self, host, port=None, ping=False):
        res = ['nmap']
        if not ping:
            res.append('-Pn')
        if port:
            res += ['-p', str(port)]
        if self.nse:
            res += ['--script', self.nse]
        if self.extra_args:
            res += self.extra_args
        res += self.flags
        return res + host_to_args(host)

    @property
    def footer(self):
        return self._footer[self.language]

    @property
    def header(self):
        return self._header[self.language]

    @property
    def nse_header(self):
        return self._nse_header[self.language]

    @property
    def template(self):
        lang_template = self._template[self.language]
        if self.nse:
            header = self.nse_header.format(self.nse) + ' ' + self.header
        else:
            header = self.header
        return self.prepend_description(lang_template.format(header) + self.footer)

    def verify(self, host, port=None):
        if not port:
            port = self.port
        command = self.command(host, port=port)
        output_str = self.run_command(command)
        yield self.template.format(output_str)


class DNSCacheSnoop(NmapIssue):
    nse = "dns-cache-snoop"
    description = "Verify DNS Cache Snooping"
    sudo = True
    flags = ["-sU"]
    nse = "dns-cache-snoop"
    port = 53

    def postprocess(self, output_str):
        output_str = highlight(output_str, r'\| dns-cache-snoop: \d+ of \d+ tested domains are cached.|\|_.[^\s]+')
        return super().postprocess(output_str)


class DNSRecursion(NmapIssue):
    nse = "dns-recursion"
    description = "Verify Recursive Query Cache Poisoning"
    trigger = "Recursion appears to be enabled"

    def postprocess(self, output_str):
        output_str = highlight(output_str, self.trigger)
        return super().postprocess(output_str)

    def verify(self, host, port=53):
        command = ['sudo', 'nmap', '-sU', '-p', str(port), '--script=dns-recursion.nse'] + host_to_args(host)
        output_str = self.run_command(command)
        if self.trigger not in output_str:
            raise IssueDoesNotExist()
        yield self.template.format(output_str)


class MDNSServiceDiscovery(NmapIssue):
    nse = "dns-service-discovery"
    description = "Verify exposure of service information"

    def verify(self, host, port=5353):
        command = ['sudo', 'nmap', '-sU', '--script=dns-service-discovery', '-p', str(port)] + host_to_args(host)
        output_str = self.run_command(command)
        output_str = self.postprocess(output_str)
        yield self.template.format(output_str)


class SSHAlgos(NmapIssue):
    nse = "ssh2-enum-algos"
    description = "Show the algorithms supported by the SSH server"

    def verify(self, host, port=22):
        command = ['nmap', '-Pn', '--script', self.nse, '-p', str(port)] + host_to_args(host)
        output_str = self.run_command(command)
        yield self.template.format(output_str)


class OutdatedNmapIssue(NmapIssue):
    """Show outdated software using Nmap"""
    software = "SOFTWARE"
    version_regex = None
    flags = ["-sV"]
    port = None

    @property
    def footer(self):
        return self._footer[self.language].format(self.version)

    @property
    def _header(self):
        return {
            "en": f"Detected software: {self.software}.",
        }

    @property
    def _footer(self):
        return {
            "en": "p. Detected version: {}.",
        }

    @property
    def description(self):
        return f"Verify outdated {self.software}"

    def postprocess(self, output_str):
        output_str = highlight(output_str, self.version_regex)
        return super().postprocess(output_str)

    def verify(self, host, port=None):
        if not port:
            port = self.port
        command = self.command(host, port)
        output_str = self.run_command(command)
        match = re.search(self.version_regex, output_str)
        if not match:
            raise IssueDoesNotExist()
        self.version = match.group(1)
        yield self.template.format(output_str)


class OutdatedMSSQL(OutdatedNmapIssue):
    nse = "ms-sql-info"
    version_regex = r"number: ([\d.]+)"
    software = "Microsoft SQL Server"
    flags = []
    port = 1433


class OutdatedMSDNS(OutdatedNmapIssue):
    software = "Microsoft DNS Server"
    version_regex = r"Microsoft DNS (\d+\.\d+\.\d+ \([A-F0-9]+\))"
    port = 53


class SMBSigning(NmapIssue):
    nse = 'smb2-security-mode'
    description = "Verify that SMB signing is not required"

    def verify(self, host, port=445):
        command = self.command(host, port)
        output_str = self.run_command(command)
        trigger = "Message signing enabled but not required"
        if trigger not in output_str:
            raise IssueDoesNotExist()
        output_str = highlight(output_str, trigger)
        yield self.template.format(output_str)


add_issue('dns-cache-snoop', DNSCacheSnoop)
add_issue('dns-recursion', DNSRecursion)
add_issue('mdns-service-discovery', MDNSServiceDiscovery)
add_issue('ssh-algos', SSHAlgos)
add_issue('outdated-mssql', OutdatedMSSQL)
add_issue('outdated-msdns', OutdatedMSDNS)
add_issue('smb-signing', SMBSigning)
add_issue('nmap', NmapIssue)
