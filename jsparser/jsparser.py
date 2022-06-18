import argparse
from datetime import timedelta
from timeit import default_timer as timer
from typing import List, Callable

from tree_sitter import Language, Parser, Tree, Node

ENC = "utf8"

JS_LANGUAGE = Language('build/languages.so', 'javascript')


def cli():
    argparser = argparse.ArgumentParser(description='Parse some javascript')
    argparser.add_argument('--source-path', type=str, help='path of the file to be parsed')
    argparser.add_argument('--module', type=str, help='the name of the module to search for')
    argparser.add_argument('--property', type=str, help='the property of the module to search for')

    args = argparser.parse_args()
    src_path = args.source_path
    module_name = args.module
    prop_name = args.property

    start = timer()

    find_invocations(module_name, prop_name, src_path)

    end = timer()
    print(timedelta(seconds=end - start))


def find_invocations(module_name: str, prop_name: str, src_path: str) -> [str, List[Node]]:
    tree = parse_js(src_path)

    module_assignments = find_module_assignment(import_name=f'require("{module_name}")', tree=tree)
    if len(module_assignments) == 0:
        print(f"no import found for module: '{module_name}'")
        return None, []
    module_assignment = module_assignments[0]
    var_name = str(module_assignment.text, ENC)
    invocations = find_prop_references(var_name=var_name, prop_name=prop_name, tree=tree)

    print(f'module "{module_name}" imported as {var_name}')
    print(f"all occurrences of {var_name} calling {prop_name}:")

    raw_src = str(tree.text, ENC).splitlines()
    for invocation in invocations:
        ln = invocation.start_point[0]
        full_line = raw_src[ln]
        print(f"line {ln + 1}: {full_line}")

    return var_name, invocations


def find_module_assignment(import_name: str, tree: Tree) -> List[Node]:
    results = []
    root_node = tree.root_node
    nodes = find_node(root_node, node_type("variable_declarator", "assignment_expression"))
    for node in nodes:
        call_exps = find_node(node, node_type("call_expression"))
        if len(call_exps) == 0:
            continue
        call_exp = call_exps[0]
        if str(call_exp.text, ENC) == import_name:
            identifier_node = find_node(node, node_type("identifier"))[0]
            results.append(identifier_node)
    return results


def find_node(node: Node, predicate: Callable[[Node], bool]) -> List[Node]:
    results = []
    if predicate(node) is True:
        results.append(node)
    for child in node.children:
        results.extend(find_node(child, predicate))
    return results


def node_type(*ntypes: str) -> Callable[[Node], bool]:
    """Predicate that evaluates whether a Node's type matches any of the supplied values."""
    return lambda n: n.type in ntypes


def chain_predicates(*predicates: Callable[[Node], bool], next_func=lambda n: n) -> Callable[[Node], bool]:
    """
    Predicate that evaluates a series of predicates against a Node.

    :param next_func: a function that takes a Node input and returns the Node
           to evaluate against the next predicate in the chain
    :param predicates: one or more Node predicates
    :return: whether the supplied Node matches the all predicates in the chain
    """

    def chain(start_node: Node) -> bool:
        current_node = start_node
        for predicate in predicates:
            if current_node is None:
                return False  # alternatively raise an exception
            if predicate(current_node) is False:
                return False
            current_node = next_func(current_node)
        return True

    return chain


def is_property_invoked(node):
    if node.parent is None:
        return False
    psibling = node.parent.next_sibling
    return psibling is not None and psibling.type == "arguments"


def find_prop_references(var_name, prop_name, tree) -> List[Node]:
    fs_props = find_node(
        tree.root_node,
        predicate=chain_predicates(lambda n: n.text == bytes(prop_name, ENC)
                                             and node_type("property_identifier")(n) and is_property_invoked(n),
                                   # is_property_invoked() is kind of beyond the scope of the prompt
                                   node_type("."),
                                   lambda n: n.text == bytes(var_name, ENC)
                                             and node_type("identifier")(n),
                                   next_func=lambda n: n.prev_sibling
                                   )
    )

    return fs_props


def parse_js(src_path) -> Tree:
    src = load_src(src_path)
    parser = Parser()
    parser.set_language(JS_LANGUAGE)
    return parser.parse(bytes(src, ENC))


def load_src(src_path):
    with open(src_path, mode='r', encoding=ENC) as file:
        return file.read()


if __name__ == '__main__':
    cli()
