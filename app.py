from flask import Flask, request
from jira.client import JIRA
import json
import re

host = '0.0.0.0'
port = 5000

jira_login = 'ivs'
with open('password', 'r') as content_file:
   jira_password = content_file.read()

jira = JIRA(options={'server': 'https://jira.zeo.lcl', 'verify':False}, basic_auth=(jira_login, jira_password))

issue_regex = re.compile('(ZDWC\S+)')
reviewer_regex = re.compile('(@[^\s@]+)')

app = Flask(__name__)

@app.route('/',methods=['POST'])
def index():
   data = json.loads(request.data.decode("utf-8"))

   for commit in data['commits']:
      parse_commit(commit)
      
   return "OK"

def parse_commit(commit):
   message = commit['message']

   reviewers = reviewer_regex.findall(message)   
   for issue_number in issue_regex.findall(message):
      if str(jira.issue(issue_number).fields.status) == 'In Progress':
         jira.transition_issue(issue_number, 101, comment = make_commit_message(reviewers))   

def make_commit_message(reviewers):
   return 'reviewed by {}'.format(' '.join(map(lambda name : '[~{}]'.format(name.translate(dict.fromkeys(map(ord, '@'), None))), reviewers)))

if __name__ == '__main__':
   app.run(host, port)
 
