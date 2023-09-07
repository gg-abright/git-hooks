#!/usr/bin/env python3

import subprocess
import os
from os.path import exists


# git_stash returns True if files were stashed, False if no files were changed
def git_stash():
    stash_cmd = subprocess.run(["git", "stash"], text=True, capture_output=True)
    return not "No local changes to save" in stash_cmd.stdout

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

def git_modified_files():
    status_cmd = subprocess.run(["git", "status"], text=True, capture_output=True)
    modified = [f for f in status_cmd.stdout.split("\n") if "modified:" in f]
    return list(map(lambda f: f.split(":")[1].strip(), modified))

def git_add(files):
    subprocess.run(["git", "status"] + files)

def git_commit(msg):
    subprocess.run(["git", "commit", "-m", f"\"{msg}\""])

def get_directory(file):
    return file[:file.rfind("/")]

def find_file_in_parents(dir, filename, root=os.environ.get("PWD"), stop_at=os.environ.get("PWD")):
    full_filepath = "/".join([root, dir, filename])

    while not exists(full_filepath):
        directory = directory[:directory.rfind("/")]
        full_filepath = "/".join([root, directory, filename])

    return full_filepath.replace("//", "/", -1)

def unique_list(l):
    return list(set(list(l)))

def a_line_starts_with(filepath, prefix):
    with open(filepath) as f:
        for line in f:
            if line.startswith(prefix):
                return True

def run_make_target(makefilepath, target):
    # verify `test` target exists
    if not a_line_starts_with(makefilepath, f"{target}:"):
        return None

    # get CWD for `make <target>` to be run in
    directory = get_directory(makefilepath)

    return subprocess.run(["make", target], cwd=directory)

# stash uncommitted changes
stashed = git_stash()

# get branch
branch = git_branch()

# check changes being pushed
files_changed = git_diff_remote(branch)
directories = unique_list(map(lambda f: get_directory(f), files_changed))

# find closest Makefile for each directory
makefiles = unique_list(map(lambda d: find_file_in_parents(d, "Makefile"), directories))

# run `make test` and `make format` on each unique Makefile and fail push if tests fail
for makefile in makefiles:
    format_result = run_make_target(makefile, "format")
    modified = git_modified_files()

    if format_result is not None and len(modified) > 0:
        git_add(modified)
        git_commit("formatting")

    test_result = run_make_target(makefile, "test")

    if test_result is not None and test_result.returncode is not 0:
        print(f"Tests failed running `make test` in `{get_directory(makefile)}`")
        if stashed:
            git_unstash()
        exit(1)

# apply stash to restore uncommitted changes
if stashed:
    git_unstash()
