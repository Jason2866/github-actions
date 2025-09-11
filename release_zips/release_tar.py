#!/usr/bin/env python

from github import Github, GithubException, Auth
import os
import shutil
import glob
import subprocess


def main():
    ref = os.environ.get("GITHUB_REF", None)
    if not ref:
        raise SystemExit("Not an event based on a push. Workflow configuration is wrong?")
    REF_PREFIX = "refs/tags/"
    if not ref.startswith(REF_PREFIX):
        raise SystemExit("Ref {} is not a tag. Workflow configuration is wrong?".format(ref))
    tag = ref[len(REF_PREFIX):]

    github_actor = os.environ["GITHUB_ACTOR"]
    github_token = os.environ["GITHUB_TOKEN"]
    github_repo = os.environ["GITHUB_REPOSITORY"]

    print("Connecting to GitHub...")
    auth = Auth.Token(github_token)
    github = Github(auth=auth)
    repo = github.get_repo(github_repo)

    if repo.private:
        # For private repos, git needs authentication (but set so that the
        # remote URL doesn't embed the temporary credentials in the tar.xz file or
        # even store the temporary credential token in the filesystem.)
        subprocess.run(["git",  "config", "--global", "credential.https://github.com.username", github_actor], check=True)
        helper_cmd  = "!f() { test \"$1\" = get && echo \"password=$GITHUB_TOKEN\"; }; f"  # shell command
        subprocess.run(["git", "config", "--global", "credential.https://github.com.helper", helper_cmd], check=True)

    git_url = "https://github.com/{}.git".format(github_repo)
    repo_name = github_repo.split("/")[1]
    directory = "{}-{}".format(repo_name, tag)

    print("Doing a full recursive clone of {} ({}) into {}...".format(git_url, tag, directory))
    # note: it may be easier to use github's "checkout" action here, with the correct args
    subprocess.run(["git", "clone", "--recursive", "--branch", tag, git_url, directory], check=True)

    # remove docs
    shutil.rmtree(directory + "/docs", ignore_errors=True)

    tarfile = "{}.tar.xz".format(directory)

    print("Creating tar.xz archive {}...".format(tarfile))
    # Create tar.xz with maximum compression
    subprocess.run(["tar", "-cJf", "--exclude=.*", tarfile, directory], check=True, env={**os.environ, "XZ_OPT": "-9"})

    try:
        release = repo.get_release(tag)
        print("Existing release found...")
        if any(asset.name == tarfile for asset in release.get_assets()):
            raise SystemExit("A release for tag {} already exists and has a tar.xz file {}. Workflow configured wrong?".format(tag, tarfile))
    except GithubException:
        print("Creating release...")
        is_prerelease = "-" in tag  # tags like vX.Y-something are pre-releases
        release_repo_name = os.environ.get('RELEASE_PROJECT_NAME', repo_name)
        name = "{} {} {}".format(release_repo_name,
                                 "Pre-release" if is_prerelease else "Release",
                                 tag)
        release = repo.create_git_release(tag, name,
                                          "(Draft created by Action)",
                                          draft=True, prerelease=is_prerelease)

    print("Attaching tar.xz file...")
    release.upload_asset(tarfile)

    print("Release URL is {}".format(release.html_url))


if __name__ == "__main__":
    main()
