import llm
from llm.default_plugins.openai_models import Chat, AsyncChat
from pathlib import Path
import json
import time
import httpx


DEFAULT_API_BASE = "https://openrouter.ai/api/v1"

def get_api_base():
    config_path = llm.user_dir() / "litellm.yaml"
    if not config_path.exists():
        return DEFAULT_API_BASE
    
    try:
        import yaml
        with open(config_path) as f:
            config = yaml.safe_load(f)
            return config.get("api_base", DEFAULT_API_BASE)
    except Exception:
        return DEFAULT_API_BASE

def get_litellm_models():
    api_base = get_api_base().rstrip('/')
    return fetch_cached_json(
        url=f"{api_base}/models",
        path=llm.user_dir() / "litellm_models.json",
        cache_timeout=3600,
    )["data"]


class LiteLLMChat(Chat):
    needs_key = "litellm"
    key_env_var = "LITELLM_KEY"

    def __str__(self):
        return "LiteLLM: {}".format(self.model_id)


class LiteLLMAsyncChat(AsyncChat):
    needs_key = "litellm"
    key_env_var = "LITELLM_KEY"

    def __str__(self):
        return "LiteLLM: {}".format(self.model_id)


@llm.hookimpl
def register_models(register):
    # Only do this if the litellm key is set
    key = llm.get_key("", "litellm", "LLM_LITELLM_KEY")
    if not key:
        return
    for model_definition in get_litellm_models():
        supports_images = get_supports_images(model_definition)
        kwargs = dict(
            model_id="litellm/{}".format(model_definition["id"]),
            model_name=model_definition["id"],
            vision=supports_images,
            api_base=get_api_base(),
            headers={"HTTP-Referer": "https://llm.datasette.io/", "X-Title": "LLM"},
        )
        register(
            LiteLLMChat(**kwargs),
            LiteLLMAsyncChat(**kwargs),
        )


class DownloadError(Exception):
    pass


def fetch_cached_json(url, path, cache_timeout):
    path = Path(path)

    # Create directories if not exist
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.is_file():
        # Get the file's modification time
        mod_time = path.stat().st_mtime
        # Check if it's more than the cache_timeout old
        if False and time.time() - mod_time < cache_timeout:
            # If not, load the file
            with open(path, "r") as file:
                return json.load(file)

    # Try to download the data
    try:
        key = llm.get_key("", "litellm", "LLM_LITELLM_KEY")
        headers = {"Authorization": f"Bearer {key}"} if key else {}
        response = httpx.get(url, headers=headers, follow_redirects=True)
        response.raise_for_status()  # This will raise an HTTPError if the request fails

        # If successful, write to the file
        with open(path, "w") as file:
            json.dump(response.json(), file)

        return response.json()
    except httpx.HTTPError:
        # If there's an existing file, load it
        if path.is_file():
            with open(path, "r") as file:
                return json.load(file)
        else:
            # If not, raise an error
            raise DownloadError(
                f"Failed to download data and no cache is available at {path}"
            )


def get_supports_images(model_definition):
    try:
        # e.g. `text->text` or `text+image->text`
        modality = model_definition["architecture"]["modality"]

        input_modalities = modality.split("->")[0].split("+")
        return "image" in input_modalities
    except Exception:
        return False
