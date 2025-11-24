import ast
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class CallGraphVisitor(ast.NodeVisitor):
    def __init__(self):
        self.graph = {}
        self.current_function = None
        self.current_class = None

    def visit_ClassDef(self, node):
        prev_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = prev_class

    def visit_FunctionDef(self, node):
        func_name = node.name
        if self.current_class:
            func_name = f"{self.current_class}.{func_name}"
        
        prev_function = self.current_function
        self.current_function = func_name
        self.graph[func_name] = []
        
        self.generic_visit(node)
        
        self.current_function = prev_function

    def visit_Call(self, node):
        if self.current_function:
            callee = self._get_callee_name(node)
            if callee:
                self.graph[self.current_function].append(callee)
        # Continue traversing to find nested calls
        self.generic_visit(node)

    def _get_callee_name(self, node) -> str:
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            # e.g. self.method or module.func
            # We'll try to get the attribute name
            return node.func.attr
        return None

class CallGraphBuilder:
    """Builds a static call graph from source code."""
    
    def build(self, code: str) -> Dict[str, List[str]]:
        """
        Parse code and return adjacency list of calls.
        """
        try:
            tree = ast.parse(code)
            visitor = CallGraphVisitor()
            visitor.visit(tree)
            return visitor.graph
        except Exception as e:
            logger.error(f"Failed to build call graph: {e}")
            return {}
