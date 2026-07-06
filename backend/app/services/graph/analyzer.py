class GraphAnalyzer:

    def summarize(self, graph: dict):

        summary = {
            "total_files": 0,
            "total_functions": 0,
            "total_classes": 0,
            "total_modules": 0
        }

        files = {}

        # ------------------------
        # nodes
        # ------------------------

        for node in graph["nodes"]:

            node_type = node["type"]

            if node_type == "file":

                summary["total_files"] += 1

                files[node["id"]] = {
                    "path": node["id"],
                    "functions": [],
                    "classes": [],
                    "imports": []
                }

            elif node_type == "function":
                summary["total_functions"] += 1

            elif node_type == "class":
                summary["total_classes"] += 1

            elif node_type == "module":
                summary["total_modules"] += 1

        # ------------------------
        # edges
        # ------------------------

        node_lookup = {
            node["id"]: node
            for node in graph["nodes"]
        }

        for edge in graph["edges"]:

            source = edge["source"]
            target = edge["target"]
            relation = edge["relation"]

            if source not in files:
                continue

            target_node = node_lookup.get(target)

            if target_node is None:
                continue

            if relation == "contains":

                if target_node["type"] == "function":
                    files[source]["functions"].append(
                        target_node["name"]
                    )

                elif target_node["type"] == "class":
                    files[source]["classes"].append(
                        target_node["name"]
                    )

            elif relation == "imports":

                files[source]["imports"].append(target)

        return {
            "summary": summary,
            "files": list(files.values())
        }