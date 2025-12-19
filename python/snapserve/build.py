from os import system, makedirs
import os.path as op
from snapserve.main import app
import json


openapi_bin = "node node_modules/openapi-typescript-codegen/bin/index.js"

def run(cmd: str) -> None:
    print(cmd)
    system(cmd)


def build_openapi(output_file: str) -> None:
    """ Generate the openapi.json file """
    print("Exporting the OpenAPI schema specifications")
    with open(output_file, 'w+') as afp:
        api = app.openapi()
        json.dump(api, afp, indent=4)


def build_client(json_f, build_path):
    print("Regenerate the Typescript API")
    run("{} --input {} --output {} --client axios".format(openapi_bin, json_f, build_path))


def build(build_path):
    makedirs(build_path, exist_ok=True)
    json_f = op.join(build_path, "openapi.json")
    build_openapi(json_f)
    build_client(json_f, op.join(build_path, "client"))


if __name__ == "__main__":
    build(op.join(op.dirname(__file__), "..", "..", "build", "api"))