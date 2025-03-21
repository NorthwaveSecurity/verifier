import logging
from .base import Runner as Base
from ..verifier import export_evidences
from ..verifier import get_proxy, verify_host
from ..config import config
import xml.etree.ElementTree as ET

class NessusRunner(Base):
    name = "nessus"
    help = "Process nessus export and import issues into your Dradis project"

    def add_arguments(self):
        super().add_arguments()
        self.parser.add_argument("nessus_file", help="Nessus input file")

        # TODO: find a better way to use VerifyRunner's add_verify_arguments
        self.parser.add_argument("-x", "--export-file", help="Export results to file for later import")
        self.parser.add_argument("-l", "--lang", choices=["en", "nl"], default="en", help="Reporting language")
        self.parser.add_argument("--proxy", nargs='?', help="Use the given proxy server, insert anything to use proxychains", default=get_proxy())

    # nessus id -> std issue id
    nessus_standard_issue_mapping = {
        # <nessus_id>: {"en": "<dradis_id>"},
    }

    # nessus id -> verifier issue id
    nessus_verifier_mapping = {
        97861: 'ntp-mode6',
        50345: 'x-frame-options',
        84502: 'strict-transport-security', # 1 HSTS missing finding
        # 142960: 'strict-transport-security',
        98715:  'strict-transport-security', # and 1 HSTS can be improved finding
        112551: 'content-security-policy',
        50344: 'content-security-policy',

        # 70658: 'ssh-weak-algos', # SSH Server CBC Mode Ciphers Enabled -- will be captured by 70657
        70657: 'ssh-weak-algos', # Nessus plugin lists all algo's, verifier will select weak ones.

        ### HTTP Server version disclosures
        10107: 'server-version', # HTTP Server Type and Version
        # 48204: 'server-version', # Apache HTTP Server Version
        # 194915: 'server-version', # Eclipse Jetty Web Server Detection

        26928: 'weakcipher',
        70544: 'mediumcipher',
        104743: 'oldtls',
        121010: 'oldtls',
        20007: 'ssl',
        51192: 'untrusted',
        15901: 'untrusted',
        57582: 'untrusted',
        #45411: 'untrusted', -> hostname mismatch could also be due to IP scanning, therefore disabled this one.
        #45410: 'untrusted', -> same as above
        69551: 'weakkey',
        112493: 'expired',
        11213: 'trace',
        11213: 'track',
        85601: 'http-only-flag',
        98064: 'secure-flag',
        85602: 'secure-flag',
        700100: 'smb-v1',
        53513: 'smb-v1',
        12217: 'dns-cache-snoop',
        3703: 'dns-recursion',
        64784: 'outdated-mssql',
        74496: 'outdated-msdns',
        57608: 'smb-signing',
        58453: 'rdp-nla',
    }

    nessus_ignored = [
        11219,  # Nessus SYN scanner
        45590,  # Device Type
        19506,  # Nessus Scan Information
        24260,  # HyperText Transfer Protocol (HTTP)
        11936,  # OS Identification
        22964,  # Service Detection
        67123,  # ModSecurity Version
        54615,  # Device Type
        42822,  # Strict Transport Security (STS) Detection
        66334,  # Patch Report 
        43111,  # HTTP Methods Allowed (per directory)
        83298,  # SSL Certificate Chain Contains Certificates Expiring Soon
        110723, # Target Credential Status by Authentication Protocol - No Credentials Provided
        10287,  # Traceroute Information
        142960, # HSTS Missing From HTTPS Server (RFC 6797)
        117886, # OS Security Patch Assessment Not Available
        25220,  # TCP/IP Timestamps Supported
        12053,  # Host Fully Qualified Domain Name (FQDN) Resolution

        ### HTTP Server type and versions ignored since plugin 10107 is a catch-all
        48204,  # Apache HTTP Server Version
        194915, # Eclipse Jetty Web Server Detection

        #### SSH handled by catch-all 70657: SSH Algorithms and Languages Supported
        153954, # SSH Host Keys < 2048 Bits Considered Weak
        153588, # SSH SHA-1 HMAC Algorithms Enabled
        70658,  # SSH Server CBC Mode Ciphers Enabled

        # Ignored TLS findings, they get handled in a different module
        42873,  # SSL Medium Strength Cipher Suites Supported (SWEET32)
        156899, # SSL/TLS Recommended Cipher Suites,
        56984,  # SSL / TLS Versions Supported
        56471,  # SSL Certificate Chain Not Sorted
        56472,  # SSL Certificate Chain Contains Unnecessary Certificates
        57041,  # SSL Perfect Forward Secrecy Cipher Suites Supported 
        21643,  # SSL Cipher Suites Supported
        84821,  # TLS ALPN Supported Protocol Enumeration
        94761,  # SSL Root Certification Authority Certificate Information
        10863,  # SSL Certificate Information  
        42981,  # SSL Certificate Expiry - Future Expiry
        157288, # TLS Version 1.1 Deprecated Protocol
    ]

    @staticmethod
    def parse_nessus_file(file):
        logging.info("[+] Parsing Nessus file...")
        # Lines below parse the Nessus file.
        # We look through the Report XML item, find all the hosts in there that have ReportItems.
        tree = ET.parse(file)
        root = tree.getroot()
        report = root.find('Report')
        report_hosts = report.findall("ReportHost")
        issues_per_host = {}

        # For every report host we find all ReportItems, and add a key/value pair to the dictionary. This maps one host to multiple pluginID's.
        for report_host in report_hosts:
            hostname = report_host.attrib['name']
            issues_per_host[hostname] = []
            
            items = report_host.findall('ReportItem')

            # for every ReportItem, get the plugin_output, ID and Name
            for item in items:
                output = item.findtext("plugin_output")
                issues_per_host[hostname].append({
                    'nessus_plugin_id': item.attrib['pluginID'],
                    'nessus_title': item.attrib['pluginName'],
                    'nessus_port': item.attrib['port'],
                    'nessus_output': output
                })

        return issues_per_host


    def caller(self, args, extra_args):
        if args.proxy:
            logging.info(f"Using proxy server: {args.proxy}")
        evidences = []
        if 'save' in args:
            save = args.save or config['DEFAULT'].get('evidence_saver')
        else:
            save = None

        result = self.parse_nessus_file(args.nessus_file)
        evidences = []
        not_found = []
        for host, nessus_issues in result.items():
            for nessus_obj in nessus_issues:
                nessus_id = int(nessus_obj['nessus_plugin_id'])
                port = nessus_obj['nessus_port']
                verifier_host = f"{host}:{port}" #{"host": host, "port": port}

                if nessus_id not in self.nessus_verifier_mapping and nessus_id not in self.nessus_standard_issue_mapping:
                    if nessus_id not in self.nessus_ignored:
                        not_found.append((nessus_id, nessus_obj['nessus_title']))
                    continue
 
                try: 
                    # first try verifier issues since they will properly verify the issue as we like it
                    issue_id = self.nessus_verifier_mapping[nessus_id]
                    content = nessus_obj['nessus_output']
                    # issue = get_issue(issue_id, lang=args.lang, extra_args=extra_args)
                except KeyError: 
                    # if there is no verifier issue, pass the nessus content to the issue
                    issue_id = 'nessus'
                    nessus_obj["std_issue_id"] = self.nessus_standard_issue_mapping[nessus_id]
                    content = nessus_obj

                print(nessus_id, issue_id, host)

                for evidence in verify_host(
                        issue_id, 
                        verifier_host, 
                        content={'nessus': content}, 
                        save=save,
                        proxy=args.proxy,
                        export_file=args.export_file, 
                        extra_args=extra_args):
                    evidences.append(evidence)

        if evidences and args.export_file:
            export_evidences(evidences, args.export_file)

        if not_found:
            print("\n\nThe following nessus items were NOT verified nor reported; perform manual investigation!")
            for (nessus_id, nessus_title) in not_found:
                logging.error(f"[!] Nesuss issue {nessus_id}: {nessus_title} not verified")
