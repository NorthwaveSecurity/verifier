from .base import CommandIssue


class DigIssue(CommandIssue):
    dns_server = None

    def parse_args(self, args):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--dns", help="DNS server")
        args = parser.parse_args(args)
        if args.dns:
            self.dns_server = args.dns

    def run_command(self, command):
        new_command = ['dig']
        if self.dns_server:
            new_command.append(f"@{self.dns_server}")
        new_command += command
        output_str = super().run_command(new_command)
        if "ANSWER: 0" in output_str:
            print(new_command)
            raise Exception("No answer section, did you provide the correct hostname?")
        return output_str

    def postprocess(self, output_str):
        index = output_str.find('\n\n;; Query time')
        return output_str[:index]
