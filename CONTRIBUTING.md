# Contributing to LANforge Scripts

Thank you for your interest in contributing to LANforge scripts!

Whether you've found a bug or would like us to implement something new, please contact us at [support@candelatech.com](mailto:support@candelatech.com). We appreciate all inquiries and will get back to you as soon as we can.

## LANforge Scripts Developer Notes

Pull requests (PRs) for new features or bug fixes from external contributors are welcomed. Internal Candela teams currently directly develop on the master branch without the use of PRs. As we have grown into a larger team, though, we are looking to change this.

This project leverages GitHub Actions and `flake8` to perform code linting to ensure consistent code quality and minimize manual review. To configure local code linting, please follow the steps outlined in [this section](#local-code-linting). **You will be asked to update your submission should your submission fail automated checks.**

As this project was developed without automated code linting, most Python scripts do not currently pass automated linting checks. These are marked with a `# flake8: noqa` at the top to opt-out the script from linting. We require new scripts to use the automated code linting and will slowly opt-in and address existing scripts as time permits.

### Running Automated Checks Locally

To avoid the headache of updating your PR and enable minimal back-and-forth, this project supports the same GitHub Actions-based automated code linting checks locally through Git pre-commit hooks. **We strongly encourage configuring pre-commit hooks before submitting a PR**, as passing automated code linting is a requirement for submission review.

If you haven't used Git pre-commit hooks before, pre-commit Git hooks are programs run locally *on commit*. This project uses the pre-commit hooks (using `pre-commit`) to run automated code linting locally, either on commit or manually by running `pre-commit run` (after setup). Pre-commit hooks can be useful for much more than automated code linting, though. Please review the `pre-commit` documentation [here](https://pre-commit.com/) for more information on pre-commit hooks as well as the `pre-commit` tool supported by this project.

#### Setup
**NOTE:** Some pre-commit hooks will auto-edit code when run (e.g. 'end-of-file-fixer'). This will require you to re-add the updated files and re-run `git commit` to fix the commit.

To configure Git pre-commit hooks, run the following steps:

1. **Setup and activate virtual environment**

    **TODO:** Move virtual environment setup to another initial setup section, add `update_dependencies.py` instructions

    ```Bash
    # Virtual environments are always a good idea
    # for a new project, helping keep separate project
    # dependencies separate from each other.
    #
    # You can keep using this virtual environment for other
    # dependencies of this project as well
    virtualenv venv && source venv/bin/activate
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

4. ** Run the pre-commit hook before it runs on commit**
    ```Bash
    # Without staged any changes, this command will simply skip every
    # pre-commit step. However, it is still useful for visualizing
    # the process.
    #
    # The same steps will run when you enter 'git commit'
    pre-commit run
    ```
