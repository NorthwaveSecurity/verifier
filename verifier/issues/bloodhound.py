from .base import Issue, add_issue, add_expansion, Evidence
from ..util import IssueDoesNotExist, get_translation
from ..config import config

class Neo4jIssue(Issue):
    query = "TODO"
    footer = "TODO"
    _template = {
        "en": """BloodHound query:
        
bc.. {}

"""
    }

    def get_domain(tx):
        result = tx.run(
                f"MATCH (m:User) return m.domain LIMIT 1",
        )
        r = result.single()
        return r["m.domain"]

    @property
    def template(self):
        footer = get_translation(self.footer, self.language)
        # Escape brackets to prevent interpretation when template is formatted a second time
        query = self.query.replace('{', '{{').replace('}','}}')
        return self._template[self.language].format(query) + footer

    def process_records(self, records):
        raise NotImplementedError()

    def do_query(self, query, **kwargs):
        from neo4j import GraphDatabase
        bloodhound_config = config['bloodhound']
        with GraphDatabase.driver(bloodhound_config['url'], auth=(bloodhound_config['username'], bloodhound_config['password'])) as driver:
            driver.verify_connectivity()
            # print("Executing query: " + query)
            records, _, _ = driver.execute_query(query, **kwargs)
            return records

    def verify(self, domain, *args):
        # TODO use domain to select the target domain
        records = self.do_query(self.query)
        if not records:
            raise IssueDoesNotExist()
        yield Evidence(self.process_records(records))


class PrivilegedUsersNotInProtectedUsers(Neo4jIssue):
    query = "MATCH (m:User)-[r:MemberOf*1..]->(n:Group) WHERE n.objectid =~ '(?i)S-1-5-.*-512' return m.samaccountname, m.domain"
    footer = {
        "en": """Query to check membership of Protected Users group:

bc.. {}

p. Accounts with administrative rights not in Protected Users group of the {} domain:

bc.. {}
"""
    }

    def __init__(self, *args, **kwargs):
        self.query1 = "MATCH (m:User)-[r:MemberOf*1..]->(n:Group) WHERE n.name = 'PROTECTED USERS@{domain}' AND m.samaccountname = '{samaccountname}' return m.samaccountname"
        super().__init__(*args, **kwargs)

    def process_records(self, records):
        result_users = []
        user_domain = None
        # TODO this can probably be one query
        for samaccountname, domain in records:
            result = self.do_query(self.query1.format(domain=domain, samaccountname=samaccountname))
            if not result:
                result_users.append(samaccountname)
                if user_domain is None:
                    user_domain = domain

        if len(result_users):
            return self.template.format(self.query1, user_domain, '\n'.join(result_users))
        else:
            raise IssueDoesNotExist()


class ASREPRoastable(Neo4jIssue):
    query = "MATCH (u:User {dontreqpreauth: true}) RETURN u.samaccountname"
    footer = {
        "en": """AS-REP roastable accounts:

bc.. {}
"""
    }

    def process_records(self, records):
        if not records:
            raise IssueDoesNotExist()
        return self.template.format('\n'.join([r['u.samaccountname'] for r in records]))


class PasswordsInDescription(Neo4jIssue):
    query = "MATCH (c:User) WHERE c.description IS NOT NULL return c.name,c.description"
    footer = {
        "en": """Accounts with passwords in their description fields:

bc.. {}
"""
    }

    def process_records(self, records):
        if not records:
            raise IssueDoesNotExist()
        # TODO format as a table
        return self.template.format("\n".join([f"name: {r['c.name']}, description: {r['c.description']}" for r in records]))


class KrbtgtPasswordLastChanged(Neo4jIssue):
    query = "MATCH (n:User {samaccountname:'krbtgt'}) RETURN n.pwdlastset"
    footer = {
        "en": "Password of the krbtgt account was last changed on {}."
    }

    def process_records(self, records):
        import datetime
        if not records:
            raise Exception("No KRBTGT account, are you sure this is a Microsoft domain?")
        pwdlastset = records[0]['n.pwdlastset']
        ts = datetime.datetime.fromtimestamp(pwdlastset)
        now = datetime.datetime.now()
        delta = datetime.timedelta(days = 180)
        if ts < (now - delta):
            return self.template.format(ts)
        else:
            raise IssueDoesNotExist()
        

class EmptyPasswords(Neo4jIssue):
    query =  "MATCH (n:User {enabled: True, passwordnotreqd: True}) RETURN n.samaccountname"
    footer = {
        "en": """Users with empty passwords:

bc.. {}
"""
    }

    def process_records(self, records):
        if not records:
            raise IssueDoesNotExist()
        return self.template.format('\n'.join([r['n.samaccountname'] for r in records]))


class AdminLoginsNonDc(Neo4jIssue):
    query = "MATCH (n:User)-[:MemberOf]->(g:Group {objectid:'S-1-5-21-1746410392-2068921814-1504938015-512'}) WITH n MATCH p=(c:Computer)-[:HasSession]->(n) where NOT c.name =~ 'DC.*' RETURN p"
    footer = {
        "en": """Last sign in of domain admin to non-domain controller:

bc.. {}
"""
    }

    def process_records(self, records):
        if not records:
            raise IssueDoesNotExist()
        output = []
        for record in records:
            for path in record:
                for p in path:
                    system, user = p.nodes
                    output.append(f"{user['name']} was signed into {system['name']}.")
        return self.template.format('\n'.join(output))


add_issue('privileged-users-not-in-protected-users', PrivilegedUsersNotInProtectedUsers)
add_issue('as-rep-roastable', ASREPRoastable)
add_issue('passwords-in-description', PasswordsInDescription)
add_issue('krbtgt-password-last-changed', KrbtgtPasswordLastChanged)
add_issue('empty-passwords', EmptyPasswords)
add_issue('admin-logins-non-dc', AdminLoginsNonDc)
add_expansion('bloodhound', ['privileged-users-not-in-protected-users', 'as-rep-roastable', 'passwords-in-description', 'krbtgt-password-last-changed', 'empty-passwords', 'admin-logins-non-dc'])
