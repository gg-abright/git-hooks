#!/usr/bin/env python3

import subprocess
import os
from os.path import exists


def git_stash():
    subprocess.run(["git", "stash"])

def git_unstash():
    subprocess.run(["git", "stash", "apply"])

def git_branch():
    branches = subprocess.run(["git", "branch"], text=True, capture_output=True)
    branch = next((b for b in branches.stdout.split("\n") if "*" in b), "master")
    return branch.strip(" *")

def git_diff_remote(branch, remote="origin"):
    diff_cmd = subprocess.run(["git", "diff", "--stat", remote + "/" + branch], text=True, capture_output=True)
    files = [f for f in diff_cmd.stdout.split("\n") if " | " in f]
    return list(map(lambda f: f.split("|")[0].strip(), files))

def unique_directories(file_list):
    return list(set(map(lambda f: f[:f.rfind("/")], file_list)))

def find_file_in_parents(dir, filename, root=os.environ["PWD"], stop_at=os.environ["PWD"]):
    full_filepath = "/".join([root, dir, filename])
    print("full filepath", dir, filename)

    while not exists(full_filepath):
        dir = dir[:dir.rfind("/")]
        full_filepath = "/".join([dir, filename])

    return full_filepath

# stash uncommitted changes
git_stash()

# get branch
branch = git_branch()

# check changes being pushed
files_changed = git_diff_remote(branch)
directories = unique_directories(files_changed)

# find closest Makefile for each directory
makefiles = list(set([map(lambda d: find_file_in_parents(d, "Makefile"), directories)]))
print(makefiles)

# run `make test` on each unique Makefile and fail push if tests fail

# apply stash to restore uncommitted changes
git_unstash()
