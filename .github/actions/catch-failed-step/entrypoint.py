"""Gets the final failed step in a given workflow"""

import os

from github import Github

DEFAULT_STEP_NAME_WHEN_NO_STEP_FAILED = "No failed steps"


def main():
    token = os.getenv("INPUT_GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    run_id = int(os.getenv("GITHUB_RUN_ID"))

    github_client = Github(token)
    repo = github_client.get_repo(repo_name)
    workflow_run = repo.get_workflow_run(run_id)

    failed_step_name = DEFAULT_STEP_NAME_WHEN_NO_STEP_FAILED
    for job in workflow_run.jobs():
        if job.conclusion == "failure":
            failed_step_name = job.name
    print(f"::set-output name=failed-step-name::{failed_step_name}")  # noqa


if __name__ == "__main__":
    main()
