import re
import sys

import yaml

from test_helpers.terraform import read_terraform_output

TEMPLATE_REGEX = re.compile(r"^\$\{\s{1}terraform_output\(\"(.*)\"\)\s{1}\}$")
EQUALITY_REGEX = re.compile(
    r"^\$\{\s{1}terraform_output\(\"(.*)\"\)\s{1}==\s{1}\"(\w+)\"\s{1}\}$"
)
INEQUALITY_REGEX = re.compile(
    r"^\$\{\s{1}terraform_output\(\"(.*)\"\)\s{1}!=\s{1}\"(\w+)\"\s{1}\}$"
)


def _render_template_value(template_match: re.Match) -> str:
    (path,) = template_match.groups()
    return read_terraform_output(path=path)


def _render_equality(equality_match: re.Match) -> bool:
    (path, expected) = equality_match.groups()
    received = read_terraform_output(path=path)
    return received == expected


def _render_inequality(equality_match: re.Match) -> bool:
    (path, not_expected) = equality_match.groups()
    received = read_terraform_output(path=path)
    return received != not_expected


def render_template(obj: dict | list):
    if isinstance(obj, dict):
        return {k: render_template(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [render_template(v) for v in obj]
    elif isinstance(obj, str):
        match = TEMPLATE_REGEX.match(obj)
        if match is not None:
            return _render_template_value(match)

        match = EQUALITY_REGEX.match(obj)
        if match is not None:
            return _render_equality(match)

        match = INEQUALITY_REGEX.match(obj)
        if match is not None:
            return _render_inequality(match)

        return obj
    else:
        return obj


if __name__ == "__main__":
    _, filepath = sys.argv

    with open(filepath) as f:
        data: dict[str, str] = yaml.load(f, Loader=yaml.SafeLoader)
    rendered_data = render_template(obj=data)
    print(yaml.dump(data=rendered_data))  # noqa: T201
