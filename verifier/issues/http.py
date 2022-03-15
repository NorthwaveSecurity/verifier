from .curl import Curl, add_issue
from ..util import host_to_url, truncate_response, highlight


class HTTP(Curl):
    description = "Show that the website can be accessed over HTTP"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra_args.append("-I")

    def edit(self, output):
        """
        Edit result of curl before templating
        """
        output = truncate_response(output)
        return highlight(output, self.url)

    def edit_url(self, url):
        """
        Edit URL before executing
        """
        self.url = host_to_url(url, False)
        return self.url


add_issue('http', HTTP)
