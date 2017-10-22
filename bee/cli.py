# -*- coding: utf-8 -*-

"""Console script for bee."""

import click
import json
import os
import sys
from git import Repo

import logging
logging.basicConfig(level=logging.INFO)

# APPROVED_LIST = ['batavia', 'voc', 'toga', 'briefcase', 'beekeeper']
PYBEE_ORG = 'pybee'

def main():
    cli(obj={})


@click.group()
@click.option('--beeware-home', envvar='BEEWARE_HOME', default='.')
@click.pass_context
def cli(ctx, beeware_home):
    repos_json = os.path.join(os.path.dirname(__file__), 'repos.json')
    repos = {}
    with open(repos_json, 'r') as repos_file:
        repos = json.load(repos_file)
    ctx.obj['home'] = os.path.expanduser(beeware_home)
    ctx.obj['repos'] = repos


@cli.command()
@click.pass_context
def sync(ctx):
    for entry in os.listdir(ctx.obj['home']):
        if entry in ctx.obj['repos']:
            repo_path = os.path.join(ctx.obj['home'], entry)
            if os.path.isdir(repo_path):
                print("Checking repo {}".format(entry))
                try:
                    repo = Repo(repo_path)
                    if repo.is_dirty():
                        print("{} is currently 'dirty', skipping.".format(entry))
                        continue
                    if repo.active_branch != ctx.obj['repos'][entry]['default_branch']:
                        current_branch = repo.active_branch.name
                        repo.git.checkout(ctx.obj['repos'][entry]['default_branch'])
                    for remote in repo.remotes:
                        if remote.name == 'origin' and next((url for url in remote.urls if PYBEE_ORG in url), None):
                            remote.fetch()
                        repo.git.pull(rebase=True)
                    repo.git.checkout(current_branch)
                except Exception as e:
                    print("Error: {} {}".format(sys.exc_info()[0], e))


if __name__ == "__main__":
    main()
