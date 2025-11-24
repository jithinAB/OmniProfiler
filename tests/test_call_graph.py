import pytest
import ast
from code.profiler.static.call_graph import CallGraphBuilder

def test_build_call_graph_simple():
    code = """
def func_a():
    func_b()

def func_b():
    print("hello")
"""
    builder = CallGraphBuilder()
    graph = builder.build(code)
    
    # Graph should contain edges: func_a -> func_b, func_b -> print
    assert "func_a" in graph
    assert "func_b" in graph["func_a"]
    assert "func_b" in graph
    assert "print" in graph["func_b"]

def test_build_call_graph_class():
    code = """
class MyClass:
    def method_a(self):
        self.method_b()
    
    def method_b(self):
        pass
"""
    builder = CallGraphBuilder()
    graph = builder.build(code)
    
    # Simplified: MyClass.method_a -> self.method_b
    # AST parsing of 'self.method_b' might be tricky to resolve fully without type inference,
    # but we should at least see 'method_b' called.
    assert "MyClass.method_a" in graph
    assert "method_b" in graph["MyClass.method_a"] or "self.method_b" in graph["MyClass.method_a"]
