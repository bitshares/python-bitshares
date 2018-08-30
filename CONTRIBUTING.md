# Contributing

## Introduction

You are here to help BitShares and the python-bitshares library?
Awesome, feel welcome and read the following sections in order to know
how to ask questions and how to work on something.

## Code of Conduct

All members of our community are expected to follow our [Code of
Conduct](CODE_OF_CONDUCT.md). Please make sure you are welcoming and
friendly in all of our spaces.

## Get in touch

Feel free to get in contact with the developer community on
[Telegram](https://t.me/pybitshares).

## Contributing to development

When contributing to this repository, please first discuss the change
you wish to make via issue, email, or any other method with the owners
of this repository before making a change.

Please note we have a code of conduct, please follow it in all your
interactions with the project.

### Your First Contribution

To familiarize yourself with the code and procedures, we recommend to
get started with:

* review a Pull Request
* fix an Issue
* update the documentation
* make a website
* write a tutorial

### Git Flow

This project makes heavy use of [git
flow](http://nvie.com/posts/a-successful-git-branching-model/). If you
are not familiar with it, then the most important thing for you to
understand is that:

**pull requests need to be made against the `develop` branch**!

### Contributor License Agreement

Upon submission of a pull request, you will be asked to sign the
[Contributor License Agreement](CLA.md) digitally through a
github-connected service.

### 1. Where do I go from here?

If you've noticed a bug or have a question, [search the issue
tracker][https://github.com/bitshares/python-bitshares/issues] to see if
someone else in the community has already created a ticket. If not, go
ahead and [make one][https://github.com/bitshares/python-bitshares/issues/new]!

### 2. Fork & create a branch

If this is something you think you can fix, then fork the repository and
create a branch with a descriptive name.

A good branch name would be (where issue #325 is the ticket you're working on):

    git checkout -b 325-new-fancy-feature

### 3. Get the test suite running

Make sure to add a unit tests for your your code contribution in
`tests/`. You may use other unit tests as template for your own tests.

Individual unit tests can be run by:

    python3 -m unittests tests/test_NEWFEATURE.py

The entire test suite can be run in a sandbox through

    tox

### 4. Did you find a bug?

* **Ensure the bug was not already reported** by [searching all issues][https://github.com/bitshares/python-bitshares/issues].

* If you're unable to find an open issue addressing the problem,
  [open a new one][https://github.com/bitshares/python-bitshares/issues/new]. Be sure
  to include a **title and clear description**, as much relevant
  information as possible, and a **code sample** or an **executable test
  case** demonstrating the expected behavior that is not occurring.

* If possible, use the relevant bug report templates to create the issue.
  Simply copy the content of the appropriate template into a .py file, make the
  necessary changes to demonstrate the issue, and **paste the content into the
  issue description**.

### 5. Implement your fix or feature

At this point, you're ready to make your changes! Feel free to ask for help;
everyone is a beginner at first

### 6. Get the style right

Your patch should follow the same conventions & pass the same code
quality checks as the rest of the project.
[Codeclimate](https://codeclimate.com/github/bitshares/python-bitshares)
will give you feedback in this regard. You can check & fix codeclimate's
feedback by running it locally using [Codeclimate's CLI](https://codeclimate.com/github/bitshares/python-bitshares), via
`codeclimate analyze`.

### 7. Make a Pull Request

**Pull requests are supposed to go against the `develop` branch, only!**

At this point, you should switch back to your `develop` branch and make
sure it's up to date with python-bitshares's `develop` branch:

    git remote add upstream git@github.com:bitshares/python-bitshares.git
    git checkout develop
    git pull upstream develop

Then update your feature branch from your local copy of develop, and push it!

    git checkout 325-new-fancy-feature
    git rebase develop
    git push --set-upstream origin 325-new-fancy-feature

Finally, go to GitHub and make a Pull Request :D

Travis CI will run our test suite against all supported Rails versions. We care
about quality, so your PR won't be merged until all tests pass. It's unlikely,
but it's possible that your changes pass tests in one Rails version but fail in
another. In that case, you'll have to setup your development environment (as
explained in step 3) to use the problematic Rails version, and investigate
what's going on!

### 7. Keeping your Pull Request updated

If a maintainer asks you to "rebase" your PR, they're saying that a lot of code
has changed, and that you need to update your branch so it's easier to merge.

To learn more about rebasing in Git, there are a lot of good git
rebasing resources but here's the suggested workflow:

    git checkout 325-new-fancy-feature
    git pull --rebase upstream develop
    git push --force-with-lease 325-new-fancy-feature

### 8. Merging a PR (maintainers only)

A PR can only be merged into `develop` by a maintainer if:

* Pull request goes against `develop` branch.
* It is passing CI.
* It has been approved by at least two maintainers. If it was a maintainer who opened the PR, only one extra approval is needed.
* It has no requested changes.
* It is up to date with current `develop`.
* Did the contributor sign the [CLA](CLA.md)

Any maintainer is allowed to merge a PR if all of these conditions are met.

### 9. Shipping a release (maintainers only)

Maintainers need to do the following to push out a release:

    git checkout develop
    git fetch origin
    git rebase origin/develop
    # get latest tag
    git tag -l
    # git flow
    git flow release start x.y.z
    # bump version in setup.py
    git add setup.py; git commit -m "version bump"
    git flow release finish

Bundling and pushing the release:

    make release
