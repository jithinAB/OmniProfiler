import ast
import logging

try:
    from radon.complexity import cc_visit
    from radon.metrics import h_visit, mi_visit
    from radon.raw import analyze as raw_analysis
except ImportError:
    cc_visit = None
    h_visit = None
    mi_visit = None
    raw_analysis = None

from typing import Dict, Any

logger = logging.getLogger(__name__)

class ComplexityAnalyzer:
    """Analyzes code complexity using Radon."""

    def analyze_complexity(self, code: str) -> Dict[str, Dict[str, Any]]:
        """
        Calculate Cyclomatic Complexity.
        Returns a dict of {function_name: {complexity, lineno, endline, loc}}.
        """
        results = {}
        if not cc_visit:
            logger.warning("radon library not available, complexity analysis disabled")
            return {}

        try:
            blocks = cc_visit(code)
            for block in blocks:
                if hasattr(block, 'name'):
                    # Calculate function LOC
                    loc = getattr(block, 'endline', 0) - getattr(block, 'lineno', 0) + 1
                    results[block.name] = {
                        "complexity": block.complexity,
                        "lineno": getattr(block, 'lineno', 0),
                        "endline": getattr(block, 'endline', 0),
                        "loc": loc
                    }
        except Exception as e:
            logger.error(f"Failed to analyze complexity: {e}")

        return results

    def analyze_raw_metrics(self, code: str) -> Dict[str, int]:
        """
        Calculate raw metrics (LOC, SLOC, Comments, etc.).
        """
        if not raw_analysis:
            return {}
        
        try:
            raw = raw_analysis(code)
            return {
                "loc": raw.loc,
                "lloc": raw.lloc,
                "sloc": raw.sloc,
                "comments": raw.comments,
                "multi": raw.multi,
                "blank": raw.blank
            }
        except Exception as e:
            logger.error(f"Failed to analyze raw metrics: {e}")
            return {}

    def analyze_maintainability(self, code: str) -> float:
        """
        Calculate Maintainability Index (0-100).
        """
        if not mi_visit:
            return 0.0
            
        try:
            return mi_visit(code, multi=True)
        except Exception as e:
            logger.error(f"Failed to analyze maintainability: {e}")
            return 0.0

    def analyze_halstead(self, code: str) -> Dict[str, float]:
        """
        Calculate Halstead Metrics.
        Returns dict with volume, difficulty, effort.
        """
        if not h_visit:
            logger.warning("radon library not available, halstead analysis disabled")
            return {}

        try:
            metrics = h_visit(code)
            return {
                "volume": metrics.volume,
                "difficulty": metrics.difficulty,
                "effort": metrics.effort
            }
        except Exception as e:
            logger.error(f"Failed to analyze halstead metrics: {e}")
            return {}

    def analyze_big_o(self, code: str) -> Dict[str, str]:
        """
        Estimate Big O complexity based on loop nesting.
        Returns a dict of {function_name: complexity_string}.
        """
        try:
            tree = ast.parse(code)
            visitor = BigOVisitor()
            visitor.visit(tree)
            return visitor.results
        except Exception as e:
            logger.error(f"Failed to analyze Big O complexity: {e}")
            return {}

class BigOVisitor(ast.NodeVisitor):
    def __init__(self):
        self.results = {}
        self.current_function = None
        self.current_class = None
        self.loop_depth = 0
        self.max_loop_depth = 0
        self.is_recursive = False

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
        self.max_loop_depth = 0
        self.is_recursive = False
        
        self.generic_visit(node)
        
        # Determine Big O based on max loop depth
        if self.max_loop_depth == 0:
            complexity = "O(1)"
        elif self.max_loop_depth == 1:
            complexity = "O(n)"
        elif self.max_loop_depth == 2:
            complexity = "O(n^2)"
        elif self.max_loop_depth == 3:
            complexity = "O(n^3)"
        else:
            complexity = f"O(n^{self.max_loop_depth})"
            
        if self.is_recursive:
            complexity += " (Recursive)"
            
        self.results[func_name] = complexity
        self.current_function = prev_function

    def visit_For(self, node):
        self.loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node):
        self.loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_Call(self, node):
        # Simple recursion detection
        if self.current_function:
            callee = None
            if isinstance(node.func, ast.Name):
                callee = node.func.id
            elif isinstance(node.func, ast.Attribute):
                # Handle self.method calls
                if isinstance(node.func.value, ast.Name) and node.func.value.id == 'self':
                     if self.current_class:
                         callee = f"{self.current_class}.{node.func.attr}"
            
            if callee == self.current_function:
                self.is_recursive = True
                
        self.generic_visit(node)
