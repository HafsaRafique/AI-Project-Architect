import ast


class PythonAnalyzer(ast.NodeVisitor):

    def __init__(self):

        self.functions = []
        self.classes = []
        self.imports = []
        self.routes = []

    def visit_FunctionDef(self, node):

        function = {
            "name": node.name,
            "line": node.lineno,
            "end_line": getattr(node, "end_lineno", node.lineno),
            "args": [arg.arg for arg in node.args.args],
            "decorators": [],
            "docstring": ast.get_docstring(node)
        }

        for decorator in node.decorator_list:

            if isinstance(decorator, ast.Call):

                if hasattr(decorator.func, "attr"):

                    function["decorators"].append(
                        decorator.func.attr
                    )

                    if decorator.func.attr in [
                        "get",
                        "post",
                        "put",
                        "delete",
                        "patch"
                    ]:

                        if decorator.args:

                            self.routes.append({
                                "method": decorator.func.attr.upper(),
                                "path": decorator.args[0].value,
                                "function": node.name
                            })

            elif isinstance(decorator, ast.Name):

                function["decorators"].append(
                    decorator.id
                )

        self.functions.append(function)

        self.generic_visit(node)

    def visit_ClassDef(self, node):

        self.classes.append({

        "name": node.name,

        "line": node.lineno,

        "end_line": getattr(node, "end_lineno", node.lineno),

        "bases": [
            base.id
            for base in node.bases
            if hasattr(base, "id")
        ],

        "docstring": ast.get_docstring(node)

    })

        self.generic_visit(node)

    def visit_Import(self, node):

        for n in node.names:

            self.imports.append(n.name)

    def visit_ImportFrom(self, node):

        if node.module:

            self.imports.append({
                "module": node.module,
                "names": [n.name for n in node.names]
            })

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

def analyze_python(filepath):

    with open(filepath, encoding="utf8") as f:
        source = f.read()

    tree = ast.parse(source)

    analyzer = PythonAnalyzer()
    module_docstring = ast.get_docstring(tree)

    analyzer.visit(tree)

    return {

    "module_docstring": module_docstring,

    "functions": analyzer.functions,

    "classes": analyzer.classes,

    "imports": analyzer.imports,

    "routes": analyzer.routes

}