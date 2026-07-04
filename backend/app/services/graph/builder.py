import networkx as nx


class RepositoryGraph:

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_file(self, path):
        self.graph.add_node(
            path,
            type="file"
        )

    def add_function(self, file_path, function_name):

        function_node = f"{file_path}:{function_name}"

        self.graph.add_node(
            function_node,
            type="function",
            name=function_name
        )

        self.graph.add_edge(
            file_path,
            function_node,
            relation="contains"
        )

    def add_class(self, file_path, class_name):

        class_node = f"{file_path}:{class_name}"

        self.graph.add_node(
            class_node,
            type="class",
            name=class_name
        )

        self.graph.add_edge(
            file_path,
            class_node,
            relation="contains"
        )

    def add_import(self, file_path, imported_module):

        self.graph.add_node(
            imported_module,
            type="module"
        )

        self.graph.add_edge(
            file_path,
            imported_module,
            relation="imports"
        )

    def to_json(self):

        nodes = []

        for node, data in self.graph.nodes(data=True):

            nodes.append({
                "id": node,
                **data
            })

        edges = []

        for source, target, data in self.graph.edges(data=True):

            edges.append({
                "source": source,
                "target": target,
                **data
            })

        return {
            "nodes": nodes,
            "edges": edges
        }