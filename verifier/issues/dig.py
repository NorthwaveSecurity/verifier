from .base import CommandIssue


class DigIssue(CommandIssue):
    def postprocess(self, output_str):
        index = output_str.find('\n\n;; Query time')
        return output_str[:index]
