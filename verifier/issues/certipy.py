from .base import add_issue, CommandIssue, Evidence
from ..util import SNIP, highlight
import re

class Certipy(CommandIssue):
    _template = {
        "en": """\
Certipy output:

bc.. {}

{}
""",
    }
    _text = CommandIssue._text | {
        "vulnerable_authorities_header": {
            "en": "Vulnerable certificate authorities",
        },
        "vulnerable_templates_header": {
            "en": "Vulnerable templates",
        }
    }

    def postprocess(self, output):
        if "Got error" in output:
            raise Exception("Certipy error")
        lines = output.splitlines()
        if lines[1].startswith('usage'):
            raise Exception("Certipy help")
        current = None
        self.templates = []
        self.authorities = []
        active_type = None
        new_output = []
        for raw_line in lines:
            should_highlight = False
            line = raw_line.strip()
            if 'Certificate Authorities' == line:
                active_type = "authorities"
            elif 'Certificate Templates' == line:
                active_type = "templates"
            elif not active_type:
                new_output.append(raw_line)
            elif re.match(r'^\d+$', line):
                # New entry
                if active_type == "authorities":
                    current = {
                        "name": None,
                        "vulns": [],
                        "lines": []
                    }
                    self.authorities.append(current)
                else:
                    current = {
                        "name": None,
                        "vulns": [],
                        "enabled": None,
                        "enrollment_rights": None,
                        "lines": []
                    }
                    self.templates.append(current)
            elif line.startswith('Template Name') or line.startswith('CA Name'):
                current['name'] = line.split(':')[1].strip()
            elif line.startswith('ESC'):
                current['vulns'].append(line.split()[0])
                should_highlight = True
                if 'can enroll' in line:
                    current['enrollment_rights'] = line.split("'")[1]
            elif line.startswith('Enabled'):
                current['enabled'] = 'True' in line
            if should_highlight:
                raw_line = highlight(raw_line)
            if current:
                current['lines'].append(raw_line)

        new_output.append("Certificate Authorities")
        for authority in self.authorities:
            if authority['vulns']:
                new_output.append(SNIP)
                new_output += authority['lines']

        new_output.append("Certificate Templates")
        for template in self.templates:
            if template['vulns']:
                new_output.append(SNIP)
                new_output += template['lines']

        return '\n'.join(new_output)

    def format_table(self, table):
        table = [ '|' + '|'.join(row) + '|' for row in table ]
        return '\n'.join(table)

    def format_templates(self):
        header = (x.capitalize() for x in 
          (f"Template {self.t('name')}", self.t('vulnerabilities'), self.t('enabled'), f"Enrollment {self.t('rights')}")
        )
        table = [header]
        for template in self.templates:
            if not template['vulns']:
                continue
            table.append((
                template['name'],
                ', '.join(template['vulns']),
                self.bool_to_text(template['enabled']).capitalize(),
                template['enrollment_rights'])
            )
        if len(table) == 1:
            return ""
        else:
            # Contains vulnerable templates
            return f"""\
p. {self.t("vulnerable_templates_header")}:
            
{self.format_table(table)}

"""

    def format_authorities(self):
        header = (f"CA {self.t('name')}", self.t('vulnerabilities').capitalize())
        table = [header]
        for authority in self.authorities:
            if not authority['vulns']:
                continue
            table.append((authority['name'], ', '.join(authority['vulns'])))
        if len(table) == 1:
            return ""
        else:
            # Contains vulnerable authorities
            return f"""\
p. {self.t("vulnerable_authorities_header")}:
            
{self.format_table(table)}

"""

    def verify(self, domain):
        # TODO since certipy is also written in python, maybe we should call it directly
        output = self.run_command(command=["certipy", "find", "-vulnerable"]+self.args)
        evidence = Evidence(self.template.format(
            output, 
            (self.format_authorities()+self.format_templates()).strip()
        ))
        evidence.authorities = self.authorities
        evidence.templates = self.templates
        yield evidence

add_issue('certipy', Certipy)
