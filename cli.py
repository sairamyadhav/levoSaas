#!/usr/bin/env python3
import argparse
import requests
import os
import sys

API_BASE_URL = "http://127.0.0.1:8000/api"


def import_schema(args):
    """
    levo import --spec /path/to/openapi.[yaml|json] --application app-name [--service service-name]
    """
    if not os.path.exists(args.spec):
        print(f"Spec file not found: {args.spec}")
        sys.exit(1)

    with open(args.spec, "rb") as f:
        files = {"schema_file": f}
        data = {"application": args.application}
        if args.service:
            data["service"] = args.service

        response = requests.post(f"{API_BASE_URL}/schemas/upload/", files=files, data=data)

    if response.status_code in (200, 201):
        print("Schema imported successfully")
        print(response.json())
    else:
        print(f"Failed to import schema: {response.status_code}")
        print(response.text)


def main():
    parser = argparse.ArgumentParser(prog="levo", description="Levo CLI Wrapper")
    subparsers = parser.add_subparsers(dest="command")

    # levo import
    import_parser = subparsers.add_parser("import", help="Import API schema")
    import_parser.add_argument("--spec", required=True, help="Path to OpenAPI schema (json|yaml)")
    import_parser.add_argument("--application", required=True, help="Application name")
    import_parser.add_argument("--service", help="Service name")
    import_parser.set_defaults(func=import_schema)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
