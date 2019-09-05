#!/usr/local/bin/python3
import urllib
import sys
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from colorama import Fore, Style
from azure.devops.v5_1.work_item_tracking.models import WorkItem
from azure.devops.v5_1.git.git_client import GitClient
import pprint

# Create a connection to the org
personal_access_token = open("access_token", "r").read().strip()
organization_url = 'https://triumphbcap.visualstudio.com'
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

work_items = [int(x.strip()) for x in open(sys.argv[1], "r").readlines()]
pr_ids = []
pull_requests = []
wit_client = connection.clients.get_work_item_tracking_client()
git_client = connection.clients.get_git_client()

# Get all Pull Request ID's off of work items
for item_id in work_items:
    work_item = wit_client.get_work_item(item_id, expand="Relations")
    for rel in work_item.relations:
        if rel.attributes["name"] == 'Pull Request':
            pr_ids.append(int(urllib.parse.unquote(rel.url).split('/')[-1]))

# Remove duplicate PRs
pr_ids = list(dict.fromkeys(pr_ids))
pr_ids.sort()

# Get Pull Requests from ADO API
for pr_id in pr_ids:
    pull_requests.append(git_client.get_pull_request_by_id(pr_id))

[print(x.last_merge_commit.commit_id) for x in pull_requests if x.merge_status == 'succeeded' and x.target_ref_name == 'refs/heads/develop']
#[pprint.pprint(x.__dict__) for x in pull_requests if x.merge_status == 'succeeded' and x.target_ref_name == 'refs/heads/develop']
print(Style.RESET_ALL)
