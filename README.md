# llm-litellm

[![PyPI](https://img.shields.io/pypi/v/llm-litellm.svg)](https://pypi.org/project/llm-litellm/)
[![Changelog](https://img.shields.io/github/v/release/wanzheng/llm-litellm?include_prereleases&label=changelog)](https://github.com/wanzheng/llm-litellm/releases)
[![Tests](https://github.com/wanzheng/llm-litellm/workflows/Test/badge.svg)](https://github.com/wanzheng/llm-litellm/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/wanzheng/llm-litellm/blob/main/LICENSE)

[LLM](https://llm.datasette.io/) plugin for models hosted by [LiteLLM](https://litellm.ai/)

## Installation

First, [install the LLM command-line utility](https://llm.datasette.io/en/stable/setup.html).

Now install this plugin in the same environment as LLM.
```bash
llm install llm-litellm
```

## Configuration

You will need an API key from LiteLLM.

You can set that as an environment variable called `LLM_LITELLM_KEY`, or add it to the `llm` set of saved keys using:

```bash
llm keys set litellm
```
```
Enter key: <paste key here>
```

## Custom API Base URL
By default, the plugin uses LiteLLM's default API base URL. You can customize this by creating a litellm.yaml configuration file in your LLM user directory. To set a custom API base URL:

1. Create or edit litellm.yaml in your LLM user directory (`dirname "$(llm logs path)"`)

2. Add the following content:
```
api_base: "https://your-custom-api-base-url"
```

If no configuration file is found or if the api_base setting is missing, the plugin will use the default API base URL.

## Usage

To list available models, run:
```bash
llm models list
```
You should see a list that looks something like this:
```
LiteLLM: litellm/openai/gpt-3.5-turbo
LiteLLM: litellm/anthropic/claude-2
LiteLLM: litellm/meta-llama/llama-2-70b-chat
...
```
To run a prompt against a model, pass its full model ID to the `-m` option, like this:
```bash
llm -m litellm/anthropic/claude-2 "Five spooky names for a pet tarantula"
```
You can set a shorter alias for a model using the `llm aliases` command like so:
```bash
llm aliases set claude litellm/anthropic/claude-2
```
Now you can prompt Claude using:
```bash
cat llm_litellm.py | llm -m claude -s 'write some pytest tests for this'
```

Images are supported too, for some models:
```bash
llm -m litellm/anthropic/claude-3.5-sonnet 'describe this image' -a https://static.simonwillison.net/static/2024/pelicans.jpg
llm -m litellm/anthropic/claude-3-haiku 'extract text' -a page.png
```

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd llm-litellm
python3 -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
llm install -e '.[test]'
```
To run the tests:
```bash
pytest
```
To add new recordings and snapshots, run:
```bash
pytest --record-mode=once --inline-snapshot=create
```