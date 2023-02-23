import re
import subprocess
from . import templates
from cachetools import cached


SNIP = '--snip--'
HIGHLIGHT_START = r"$${{"
HIGHLIGHT_END = r"}}$$"


def highlight(string, regex):
    return re.sub(regex, HIGHLIGHT_START + r"\g<0>" + HIGHLIGHT_END, string)


def prepend_command(command, output, sudo=False):
    return '{} {}\n{}'.format("#" if sudo else "$", ' '.join(command), output)


@cached(cache={}, key=lambda command: ' '.join(command))
def _run_command(command):
    try:
        result = subprocess.run(command, capture_output=True)
    except FileNotFoundError as e:
        raise Exception(f"The program {e.filename} is currently not installed. Please install it to verify this issue.")
    return result.stdout.replace(b'\r', b'').decode('utf-8')


def run_command(command, visual_command=None, sudo=False, do_prepend_command=True):
    if sudo:
        command = ["sudo"] + command
    output = _run_command(command)
    if do_prepend_command:
        output = prepend_command(visual_command or command, output, sudo=sudo)
    return output


def host_to_args(host):
    if isinstance(host, str):
        args = [host]
    elif isinstance(host, dict):
        args = host['args']
    elif isinstance(host, list):
        args = host
    else:
        args = []
    return args


def host_to_url(url, https=True):
    if https:
        prefix = "https://"
    else:
        prefix = "http://"
    if not url.startswith('http'):
        return prefix + url
    return url


def get_translation(value, language):
    if type(value) != dict:
        return value
    else:
        return value[language]


def format_request_response(request, response, format='dradis'):
    match format:
        case 'verifier':
            template = templates.request_response_verifier
        case _:
            template = templates.request_response
    return template.format(str(request).rstrip(), str(response).rstrip())


def truncate_response(response, length=1000):
    return response[:length] + "\n" + SNIP


class IssueDoesNotExist(Exception):
    pass

class PostProcessingFailed(Exception):
    def __init__(self, command_output):
        self.message = "Command output:\n\n" + command_output
        super().__init__(self.message)


