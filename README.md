# Connecting Party Manager

## Overview

## Table of Contents

1. [Setup](#setup)
   1. [Prerequisites](#1-prerequisites)
      1. [Utiise ASDF Tool Manager](#1-utiise-asdf-tool-manager)
   2. [Install python dependencies](#2-install-python-dependencies)

---

## Setup

### 1. Prerequisites

#### 1. Utiise ASDF Tool Manager

For an easy way to make sure your local system matches the requirements needed you can use `asdf tool manager`. This tool fetches the required versions of the libraries needed and sets the directory to use that version instead of your system's default version. To get it up and running,

- Install `asdf` using the instructions given here. https://asdf-vm.com/guide/getting-started.html. You can check it installed properly by using the command `asdf --version`
- Install the dependencies using the `cpm-dependencies.sh` bash script. `bash cpm-dependencies.sh`
- You should be good to go.

### 2. Install python dependencies

At the root of the repo, run:

```shell
poetry install
poetry shell
pre-commit install
```

NOTE

- You will know if you are correctly in the shell when you see the following before your command line prompt `(connecting-party-manager-py3.11)` (the version may change based on the version of python)
- If it says (.venv) then you are not using the correct virtual environment
- As mentioned above you at least need Python 3.11 installed globally to run the project, Poetry will handle the rest
- The terraform version can be found in the .terraform-version file at the root

---
