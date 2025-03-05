from pathlib import Path

from event.json import json_load

PATH_TO_HERE = Path(__file__).parent
PATH_TO_ROOT = PATH_TO_HERE.parent.parent


def read_terraform_output(path: str):
    with open(
        PATH_TO_ROOT / "infrastructure" / "terraform" / "per_workspace" / "output.json"
    ) as f:
        tf_output = json_load(f)

    for part in path.split("."):
        tf_output = tf_output[part]
    return tf_output
