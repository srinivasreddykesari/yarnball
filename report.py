import sys
import pprint
import traceback
import time
import subprocess
from subprocess import PIPE
import json
import argparse
import os
import re
import logging
import git
from pythonjsonlogger import jsonlogger
from datetime import datetime as dt
import requests
from termcolor import colored
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from jinja2 import Template
from flask import Flask, render_template
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

header = 'Author message commit-id'.split()

t = Template('''
<html>
    <body>
        <table border="1">

            <tr>
            {%- for col in header %}
                <td>{{col}}</td>
            {%- endfor %}
            </tr>

            {% for row in rows -%}
            <tr>
            {%- for col in row %}
                <td>{{col if col is not none else '' }}</td> 
            {%- endfor %}
            </tr>
            {% endfor %}

        </table>
    </body>
</html>
''')

def parse_args():
    parser = argparse.ArgumentParser(description='deployer.py ')
    parser.add_argument(
        "-H", "--Help", help="python report.py -r <git repo> -o <owner> -b <branch>", required=False, default="")
    parser.add_argument("-u", "--baseurl",
                        help="github base url", required=False, default="")
    parser.add_argument("-o", "--owner", help="github owner",
                        required=True, default="")
    parser.add_argument("-r", "--repo", help="github repo",
                        required=True, default="")
    parser.add_argument("-b", "--branch", help="git branch",
                        required=True, default="")
    parser.add_argument(
        "-c", "--commit", help="number of commits to retrieve", required=False, default="")
    parser.add_argument(
        "-p", "--path", help="output html repo path", required=False, default="")
    parser.add_argument(
        "-t", "--token", help="github access token", required=False, default="")
    return parser



# authenticate to github
def _connect_github(url, token, raw=False):
    """
    url: Full URL to GET
    """

    github_req_headers = {}
    if token:
        github_req_headers = {
            'Authorization': 'token %s' % token
        }

    try:
        response = requests.get(url, headers=github_req_headers, verify=False)
        if response.status_code >= 200 and response.status_code < 300:
            if raw:
                return (response.status_code, response.text)
            else:
                return (response.status_code, response.json())
        else:
            return (response.status_code, '{}')
    except requests.exceptions.Timeout as errt:
        print('Timeout in requests:\n%s' % errt)
        return (None, {})
    except requests.exceptions.RequestException as e:
        print('Exception request:\n%s' % e)
        return (None, {})

def _get_commits_url(baseurl, owner, repo, branch, commit):
    data = {'base_url': baseurl, 'owner': owner,
            'repo': repo, 'branch': branch, 'commit': commit}
    url = "%(base_url)s/repos/%(owner)s/%(repo)s/commits?per_page=%(commit)s&sha=%(branch)s" % data
    print("commit url= %s " % url)

    return url

def get_branch_commits(baseurl, owner, repo, branch, commit, token):
    url = _get_commits_url(baseurl, owner, repo, branch, commit)
    (status, response) = _connect_github(url, token)

    print("status = %s" % (status))
    print(len(response))

    if status == 404:  # Not found
        raise Exception(
            "Please provide token as an argument if it is a private repo")
    if status is None or status != requests.codes.ok:
        raise Exception("Github response error or non-200")
    else:
        if len(response) == 0:
            print('# github Response size 0: %s' % url)
            return False, []
    return True, response


def main():

    args = parse_args()
    argument = args.parse_args()

    if argument.Help:
        print("Usage: {0}".format(argument.Help))
        status = True

    if argument.baseurl:
        print("baseurl: {0}".format(argument.baseurl))
        baseurl = argument.baseurl
    else:
        baseurl = 'https://api.github.com'

    if argument.owner:
        print("owner: {0}".format(argument.owner))
        owner = argument.owner
    else:
        owner = 'None'

    if argument.repo:
        print("repo: {0}".format(argument.repo))
        repo = argument.repo
    else:
        repo = 'master'

    if argument.branch:
        print("branch: {0}".format(argument.branch))
        branch = argument.branch
    else:
        branch = 'master'

    if argument.commit:
        print("commit: {0}".format(argument.commit))
        commit = argument.commit
    else:
        commit = 5

    if argument.token:
        print("token: {0}".format(argument.token))
        token = argument.token
    else:
        token = ''

    if argument.path:
        print("path: {0}".format(argument.path))
        path = argument.path
        path = path.rstrip('/')
    else:
        path = '/tmp'

    try:
        status, resp = get_branch_commits(
            baseurl, owner, repo, branch, commit, token)
        print("ret status=%s" % status)
    except Exception as e:
        print("Error retrieving commits:", e)
        return 0

    resp_dict = []
    com_info = ()

    for item in resp:
        print("=====> %s" % item['commit'])
        com_info = (item['commit']['author']['name'], item['commit']
                    ['message'], item['commit']['tree']['sha'])
        resp_dict.append(com_info)
        com_info = ()
    print("List of tuples")
    print(resp_dict)

    with open(path + '/report.html', 'w') as fh:
        fh.write(t.render(header=header, rows=resp_dict))

if __name__ == '__main__':
    main()
