from .base import Issue, add_issue, Evidence
from collections import defaultdict
from ..util import run_command


class NmapPortScan(Issue):
    description = "Performs a TCP and UDP scan using Nmap"
    _template = {
        "en": "Target host: {}.\r\nOpen ports:\r\n\r\n{}",
    }
    args = ["-oG", "-"]
    tcp_args = ["--top-ports", "1000"]
    udp_args = ["-sU", "--top-ports", "4"]
    ports = []

    def collect_open_ports(self, lines):
        for line in lines:
            if "Ports" in line:
                port_list = line.split(':')[2].split(',')
                for i in range(len(port_list)):
                    port_entry = port_list[i].strip()
                    if "open" in port_entry:
                        self.ports.append(port_entry)

    def create_command(self, target, protocol='tcp'):
        cmd = ['nmap'] + self.args
        match protocol:
            case 'tcp':
                cmd += self.tcp_args
            case 'udp':
                cmd += self.udp_args
        cmd.append(target)
        return cmd + self.extra_args

    def run_scan(self, target, protocol='tcp'):
        cmd = self.create_command(target, protocol)
        if protocol in self.content:
            output = self.content[protocol]
        else:
            output = run_command(cmd, do_prepend_command=False, sudo=True)
        self.collect_open_ports(output.splitlines())

    def generate_output(self, target):
        table = [
            "table(PortScanTable).",
            "|_.Port|_.Type|_.State|_.Service|_.Header|"
        ]
        base_table_string = "|{0}|{1}|{2}|{3}|{4}|"
        for port_data in self.ports:
            port = port_data.split('/')[0]
            state = port_data.split('/')[1].replace('|', '/')
            p_type = port_data.split('/')[2].replace('|', '/')
            service = port_data.split('/')[4].replace('|', '/')
            header = port_data.split('/')[6].replace('|', '/')
            table.append(base_table_string.format(port, p_type, state, service, header))
        table = '\n'.join(table)
        return self.template.format(target, table)

    def verify(self, target):
        self.run_scan(target, 'tcp')
        self.run_scan(target, 'udp')
        yield Evidence(self.generate_output(target))


add_issue("portscan", NmapPortScan)
