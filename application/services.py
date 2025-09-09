import hashlib, json, yaml
from openapi_spec_validator import validate_spec


def compute_sha256(obj) -> str:
    """Convert object into JSON and compute sha256 for comparison of the spec to the latest spec."""
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def parse_and_validate_spec(file) -> tuple:
    """Parse uploaded file into dict, detect format, validate openAPI."""
    content = file.read()
    try:
        data = json.loads(content.decode("utf-8"))
        fmt = "json"
    except Exception:
        try:
            data = yaml.safe_load(content.decode("utf-8"))
            fmt = "yaml"
        except Exception:
            raise ValueError("Invalid JSON/YAML file")

    if not isinstance(data, dict) or "openapi" not in data:
        raise ValueError("Not a valid openAPI spec")

    validate_spec(data)

    return data, fmt
