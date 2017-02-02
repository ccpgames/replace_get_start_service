"""
Replaces sm.GetService("<service>") and sm.StartService("<service>") calls with Get<service>Service
and Start<service>Service calls, adding the necessary import at the top.
"""
import argparse
import os
import subprocess
from typing import List, Iterable, Optional


def add_import(lines: List[str], location: str, imports_to_add: List[str]):
    index = 0
    last_import_line = -1
    line = lines[index]
    while True:
        if line.startswith('"""') or line.startswith("'''"):
            # Skip multi-line comments
            marker = line[:3]
            if not line[3:].endswith(marker):
                index += 1
                line = lines[index]
                while not (line.startswith(marker) or line.endswith(marker)):
                    index += 1
                    line = lines[index]
                index += 1
                line = lines[index]

        if len(line.strip()) == 0 or line.startswith("import ") or line.startswith("from ") or line.startswith("#"):
            if line.startswith("import ") or line.startswith("from "):
                next_line = lines[index + 1]
                if next_line.startswith(" "):
                    index += 1
                    line = lines[index]
                    while line.startswith(" "):
                        index += 1
                        line = lines[index]
                    index -= 1
                    line = lines[index]
                last_import_line = index

            while line.endswith("\\"):
                index += 1
                line = lines[index]
            else:
                index += 1
                line = lines[index]
        else:
            break

    import_line = "from {0} import {1}\n".format(location, ", ".join(imports_to_add))
    lines.insert(last_import_line + 1, import_line)


def process_file(input_file: Iterable, service: str, import_from: str) -> Optional[list]:
    service_for_method_name = service[0].upper() + service[1:]
    search_get = "sm.GetService(\"{0}\")".format(service)
    search_get_self = "self." + search_get
    replace_get = "Get{0}Service()".format(service_for_method_name)
    found_any_get = False

    search_start = "sm.StartService(\"{0}\")".format(service)
    search_start_self = "self." + search_start
    replace_start = "Start{0}Service()".format(service_for_method_name)
    found_any_start = False

    lines = []
    for line in input_file:
        if search_get_self in line:
            line = line.replace(search_get_self, replace_get)
            found_any_get = True
        if search_get in line:
            line = line.replace(search_get, replace_get)
            found_any_get = True
        if search_start_self in line:
            line = line.replace(search_start_self, replace_start)
            found_any_start = True
        if search_start in line:
            line = line.replace(search_start, replace_start)
            found_any_start = True
        lines.append(line)

    if found_any_get or found_any_start:
        imports_to_add = []
        if found_any_get:
            imports_to_add.append("Get{0}Service".format(service_for_method_name))
        if found_any_start:
            imports_to_add.append("Start{0}Service".format(service_for_method_name))
        add_import(lines, import_from, imports_to_add)
        return lines
    else:
        return None


def process_filename(filename: str, service: str, import_from: str):
    with open(filename) as input_file:
        # noinspection PyBroadException
        try:
            new_content = process_file(input_file, service, import_from)
        except Exception:
            print("Exception while processing %s" % filename)
            return

    if new_content:
        subprocess.run(["p4", "edit", filename])
        with open(filename, "w") as output:
            output.writelines(new_content)


def run(folder: str, service: str, import_from: str):
    for root, dirs, files in os.walk(folder):
        for each in files:
            if each.endswith(".py"):
                filename = os.path.join(root, each)
                process_filename(filename, service, import_from)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("service")

    args = parser.parse_args()
    import_from = "services.{0}".format(args.service.lower())
    run(".", args.service, import_from)


if __name__ == "__main__":
    main()
