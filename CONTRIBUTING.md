# Contributing to LANforge Scripts

Thank you for your interest in contributing to LANforge scripts!

Whether you've found a bug or would like us to implement something new, please contact us at [support@candelatech.com](mailto:support@candelatech.com). We appreciate all inquiries and will get back to you as soon as we can.

## LANforge Scripts Developer Notes

**For developer environment setup, please first follow the steps outlined in [here](./py-scripts/README.md#cloning-from-git-repository-usage).**

Pull requests (PRs) for new features or bug fixes from external contributors are welcomed. Internal Candela teams currently directly develop on the master branch without the use of PRs. As we have grown into a larger team, though, we are looking to change this.

This project leverages GitHub Actions and `flake8` to perform code linting to ensure consistent code quality and minimize manual review. To configure local code linting, please follow the steps outlined in [this section](#local-code-linting). **You will be asked to update your submission should your submission fail automated checks.**

As this project was developed without automated code linting, most Python scripts do not currently pass automated linting checks. These are marked with a `# flake8: noqa` at the top to opt-out the script from linting. We require new scripts to use the automated code linting and will slowly opt-in and address existing scripts as time permits.

### Running Automated Checks Locally

#### Overview

To avoid the headache of updating your PR and enable minimal back-and-forth, this project supports the same GitHub Actions-based automated code linting checks locally through Git pre-commit hooks. **We strongly encourage configuring pre-commit hooks before submitting a PR**, as passing automated code linting is a requirement for submission review.

If you haven't used Git pre-commit hooks before, pre-commit Git hooks are programs run locally *on commit*. This project uses the pre-commit hooks (using `pre-commit`) to run automated code linting locally, either on commit or manually by running `pre-commit run` (after setup). Pre-commit hooks can be useful for much more than automated code linting, though. Please review the `pre-commit` documentation [here](https://pre-commit.com/) for more information on pre-commit hooks as well as the `pre-commit` tool supported by this project.

#### Setup

**NOTE:** Some pre-commit hooks will auto-edit code when run (e.g. 'end-of-file-fixer'). This will require you to re-add the updated files and re-run `git commit` to fix the commit.

To configure Git pre-commit hooks, run the following steps:

0. **Setup development environment**

    Follow instructions [here](./py-scripts/README.md#cloning-from-git-repository-usage).

1. **Activate virtual environment**

    Virtual environment setup steps are outlined in the developer environment setup instructions [here](./py-scripts/README.md#cloning-from-git-repository-usage).

    Virtual environments are always a good idea for a new project, helping keep separate project
    dependencies separate from each other. You can keep using this virtual environment for other dependencies of this project as well.

    ```Bash
    # Substitute the path to your virtual environment here
    # This is likely to be something in the form of 'x/bin/activate'
    source venv/bin/activate
    ```

2. **Install the 'pre-commit' package**
    ```Bash
    pip install --upgrade pip && pip install pre-commit
    ```

3. **Configure this project's pre-commit hooks**
    ```Bash
    # The pre-commit configuration contains all required
    # pre-commit hook tool installation required to setup
    # local code linting tooling (flake8, black, etc.)
    pre-commit install
    ```

4. **Run the pre-commit hook before it runs on commit**
    ```Bash
    # Without staged any changes, this command will simply skip every
    # pre-commit step. However, it is still useful for visualizing
    # the process.
    #
    # The same steps will run when you enter 'git commit'
    pre-commit run
    ```

#### Unable to Commit Due to `pre-commit` Failure

During normal use `pre-commit` may prevent you from generating a commit due to a failure during its checks. **Generally, you should always fix issues highlighted (and sometimes fixed) by `pre-commit`.** However, there are times where you must skip these and force a commit. This section details how to do so.

In this repository, we configure `pre-commit` to perform basic sanity checks, including checks for trailing whitespace, non-PEP compliant whitespace usage, and YAML syntax checking. These checks are run when generating a commit (`git commit`) or when manually run (`pre-commit run`).

The tool itself will automatically fix some issues for you, helping avoid failures during automated code linting run on pull request and push. In this case, the fixes `pre-commit` makes require you to re-stage (`git add`) the fixed files and reattempt commit. Most of these checks (except YAML syntax checking) are also run during automated code linting, which is run on pull request and push.

We're slowly working to add more Python scripts to automated code linting using GitHub Actions. However, most scripts are not included at this point and we do not yet have a way to configure `pre-commit` to ignore non-included or non-Python scripts. Should you encounter failures during commit which you would like to bypass, re-run `git commit` with the `--no-verify` to bypass `pre-commit` and force a commit.

We ask that you force commits only in limited cases. The feedback and fixes from `pre-commit` are valuable and help us ensure code quality in this repository. Any failures during automated linting checks in GitHub Actions will require re-submission of your pull request to fix the issue.
