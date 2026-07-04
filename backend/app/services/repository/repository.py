import os

from app.services.repository.parser import parse_file

from app.services.graph.builder import RepositoryGraph

graph = RepositoryGraph()


IGNORE = {
    ".git",
    "__pycache__",
    ".venv",
    "node_modules",
    ".next",
    "dist",
    "build"
}


def analyze_repository(root):

    files = []

    for path, dirs, filenames in os.walk(root):

        dirs[:] = [
            d for d in dirs
            if d not in IGNORE
        ]

        for filename in filenames:

            full = os.path.join(path, filename)

            relative = os.path.relpath(full, root)

            try:

                metadata = parse_file(full)

                graph.add_file(relative)

                for func in metadata.get("functions", []):
                    graph.add_function(
                        relative,
                        func["name"]
                    )

                for cls in metadata.get("classes", []):
                    graph.add_class(
                        relative,
                        cls["name"]
                    )

                for imp in metadata.get("imports", []):
                    graph.add_import(
                        relative,
                        imp
                    )

                files.append({
                    "path": relative,
                    **metadata
                })

            except Exception as e:

                print(relative, e)

    return {
        "files": files,
        "graph": graph.to_json()
    }