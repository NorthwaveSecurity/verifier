from .base import CommandIssue, add_issue
from ..util import host_to_url, get_translation
import os
import copy


class Curl(CommandIssue):
    description = "Run a curl command without specific issue"
    header = "TODO"
    footer = "TODO"
    _template = {
        "en": """The following curl command shows that {}.

bc.. {{}}

p. {}.""",
    }
    _links = []

    @property
    def template(self):
        header = get_translation(self.header, self.language)
        footer = get_translation(self.footer, self.language)
        output = self._template[self.language].format(header, footer)
        return self.prepend_description(self.append_links(output))

    def append_links(self, output):
        i = 1
        for link in self._links:
            output += f"\n\nbc. fn{i}. {link}"
            i += 1
        return output

    def run(self, url, args=None):
        if args is None:
            args = []

        args += self.extra_args
        visual_args = copy.copy(args)

        # Handle proxy settings
        if os.getenv('HTTP_PROXY') and url.startswith('http:'):
            args += ['-x', os.getenv('HTTP_PROXY')]
        elif os.getenv('HTTPS_PROXY') and url.startswith('https:'):
            args += ['-x', os.getenv('HTTPS_PROXY')]

        command = ["curl", "-k"] + args + [url]
        visual_command = ["curl"] + visual_args + [url]
        return self.run_command(command, visual_command=visual_command)

    def edit(self, output):
        """
        Edit result of curl before templating
        """
        return output

    def edit_url(self, url):
        """
        Edit URL before executing
        """
        return host_to_url(url)

    def verify(self, url, args=[]):
        url = self.edit_url(url)
        output_str = self.edit(self.run(url, args))
        yield self.template.format(output_str)


add_issue('curl', Curl)
