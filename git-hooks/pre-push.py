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

def get_directory(file):
    return file[:file.rfind("/")]

def find_file_in_parents(dir, filename, root=os.environ.get("PWD"), stop_at=os.environ.get("PWD")):
    full_filepath = "/".join([root, dir, filename])

    while not exists(full_filepath):
        dir = dir[:dir.rfind("/")]
        full_filepath = "/".join([root, dir, filename])

    return full_filepath.replace("//", "/", -1)

def unique_list(l):
    return list(set(list(l)))

# stash uncommitted changes
git_stash()

# get branch
branch = git_branch()

# check changes being pushed
files_changed = git_diff_remote(branch)
directories = unique_list(map(lambda f: get_directory(f), files_changed))

# find closest Makefile for each directory
makefiles = unique_list(map(lambda d: find_file_in_parents(d, "Makefile"), directories))

# run `make test` on each unique Makefile and fail push if tests fail
for makefile in makefiles:
    # verify `test` target exists

    # get CWD for `make test` to be run in
    dir = get_directory(makefile)

    try:
        subprocess.run(["make", "test"], cwd=dir)
    except:
        print(f"Tests failed running `make test` in `{dir}`")
        git_unstash()
        exit(1)

# apply stash to restore uncommitted changes
git_unstash()
