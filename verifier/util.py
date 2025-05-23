import re
import subprocess
from . import templates
from cachetools import cached


SNIP = '--snip--'
HIGHLIGHT_START = r"$${{"
HIGHLIGHT_END = r"}}$$"


def highlight(string, regex=None):
    if not regex:
        start_whitespace = re.search(r"^\s*", string).group(0)
        end_whitespace = re.search(r"\s*$", string).group(0)
        return start_whitespace + HIGHLIGHT_START + string.strip() + HIGHLIGHT_END + end_whitespace
    return re.sub(regex, HIGHLIGHT_START + r"\g<0>" + HIGHLIGHT_END, string)


def prepend_command(command, output, sudo=False):
    return '{} {}\n{}'.format("#" if sudo else "$", ' '.join(command), output)


@cached(cache={}, key=lambda command, **_: ' '.join(command))
def _run_command(command, stdin="", env=None):
    try:
        p_stdin = subprocess.PIPE
        proc = subprocess.Popen(command, stdin=p_stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        stdout, stderr = proc.communicate(stdin)
    except FileNotFoundError as e:
        raise Exception(f"The program {e.filename} is currently not installed. Please install it to verify this issue.")
    return stdout.replace(b'\r', b'').decode('utf-8')


def run_command(command, visual_command=None, sudo=False, do_prepend_command=True, stdin="", env=None):
    if sudo:
        command = ["sudo"] + command
    output = _run_command(command, stdin=stdin, env=env)
    if do_prepend_command:
        output = prepend_command(visual_command or command, output, sudo=sudo)
    return output


def host_to_args(host):
    """Used for translating hostname to argument for popen.
    Ignores the port when it is present, since the port argument is module specific."""
    if isinstance(host, str):
        if ':' in host:
            # handle when port is included.
            args = [host.split(':')[0]]
        else:
            args = [host]
    elif isinstance(host, dict):
        args = host['args']
    elif isinstance(host, list):
        args = host
    else:
        args = []
    return args


def host_to_url(url, https=True):
    # handle when port is included in URL (and not starts with a protocol handler)
    if not url.startswith('http') and ":" in url:
        (host, port) = url.split(":")
        https_ports = [443, 8443, 4443]

        if int(port) in https_ports:
            prefix = "https://"
        else:
            prefix = "http://"
    else:
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


