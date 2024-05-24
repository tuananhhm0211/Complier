from parser.readGrammar import readGrammarTable
from parser.readToken import read
import copy

count = 0

class AST:

    def __init__(self, data, id, parent_id = None):
        """
        Initializes an AST node.

        :param data: name of node
        :param id: id of node
        :param parent_id: parent id of node

        """
        self.data = data
        self.children = []
        self.id = id
        self.parent_id = parent_id


    def add_node(self, child_node, id, parent_id):
        """
        add node to children of current node

        :param child_node: name of child node
        :param id: id of child node
        :param parent_id: parent id of child node

        """
        child_node = AST(child_node, id, parent_id= parent_id)
        self.children.append(child_node)
        global count
        count += 1

    def find_node(self, id):
        """
        find node by id

        :param id: id of node
        :return: node found

        """
        if self.id == id:
            return self
        for child in self.children:
            result = child.find_node(id)
            if result:
                return result
        return None

    def find_and_add(self, child_node, id, parent_id):
        """
        find and add node
        :param child_node: name of child node
        :param id: id of child node
        :param parent_id: parent id of child node

        """
        parent = self.find_node(parent_id)
        if parent:
            parent.add_node(child_node,id, parent_id)
        else:
            print("Invalid parent")

    def remove(self, id):
        """
        remove node by id

        :param id: id of node

        """
        node = self.find_node(id)
        parent = self.find_node(node.parent_id)
        parent.children.remove(node)

    def remove_parent(self, tree):
        """
        delete a parent with only 1 child: move the current node's children to
        the current node's position in the children of the current node's parent, remove current node

        :param tree: ast tree
        :return: ast tree

        """
        for child in self.children:
            child.remove_parent(tree)

        children = self.children
        if len(children) == 1 and self.parent_id is not None:
            parent_id = self.parent_id
            single_child = children[0]
            parent = tree.find_node(parent_id)
            current = tree.find_node(self.id)
            single_child.parent_id = self.parent_id
            index = parent.children.index(current)
            parent.children.insert(index, single_child)
            parent.children.remove(current)

        return tree


    def __repr__(self, level=0):
        """
        print ast

        :param level: level of node
        :return: str

        """
        ret = "  " * level + self.data + "\n"
        for child in self.children:
            ret += child.__repr__(level + 1)
        # ret += "  " * level
        return ret

def print_ast(tree, tabCount):
    """
    print ast with bracket

    :param tree: ast
    :param tabCount: number of tabs for decoration
    :return: str

    """
    str = ""
    for child in tree.children:
        if child.data in ["<assign-expr>", "<assign-expr-t>", "<equality-expr>", "<additive-expr>",
                          "<additive-expr-t>", "<multiplicative-expr>", "<multiplicative-expr-t>", "<relational-expr>"]:
            str += "("
            for child1 in child.children:
                if not child1.data.startswith("<") and not child1.data.endswith(">"):
                    str += child1.data + " "
                str += print_ast(child1, tabCount)
            str += ")"
            continue
        if not child.data.startswith("<") and not child.data.endswith(">"):
            if child.data == "{":
                str += "\n"
                str += "    " * tabCount
                str += child.data + "\n"
                tabCount += 1
                str += "    " * tabCount
                continue
            elif child.data == "}":
                tmp = "    "
                str = str[:-len(tmp)]
                tabCount -= 1
                str += child.data + "\n"
                str += "    " * tabCount
            elif child.data == ";":
                str += child.data + "\n"
                str += "    " * tabCount
            else:
                str += child.data + " "
        str += print_ast(child, tabCount)
    return str

def ll1_parser(input, parsing_table, type, init_ptr, ast):
    """

    :param input: list of token from file .verbose.vctoke
    :param parsing_table: dict from readGrammar function
    :param type: name of current state
    :param init_ptr: index of current token in input
    :param ast: ast tree
    :return: error (false or true), pointer, ast tree

    """
    ast = copy.deepcopy(ast)
    stack = [{"production": type, "parent": 0}]
    pointer = init_ptr
    id = count + 1
    while len(stack) > 0:
        # get the first element of the stack
        top = stack.pop()
        parent_id = top["parent"]

        # name of current state = type of token
        if top["production"] == input[pointer]["type"]:
            ast.find_and_add(input[pointer]["token"], id, parent_id)
            id += 1
            pointer += 1
            continue

        # name of current state = epsilon
        if top["production"] == "EPSILON":
            ast.remove(parent_id)
            continue

        # find next state if none return error, pointer, ast
        try:
            production = parsing_table[top["production"]][input[pointer]["type"]]
        except:
            return True, pointer, ast

        # add node
        ast.find_and_add("<" + top["production"] + ">", id, parent_id)
        id += 1

        # add list of next state to the stack
        for x in production[::-1]:
            stack.append({"production": x, "parent": id - 1})

    return False, pointer, ast


def parse(file, vc_token, parsing_table):
    ast = AST("program", 0)
    pointer = 0
    while pointer < len(vc_token) - 1:
        err1, pt1, ast1 = ll1_parser(vc_token, parsing_table, "var-decl", pointer, ast)
        err2, pt2, ast2 = ll1_parser(vc_token, parsing_table, "func-decl", pointer, ast)
        if err1 and err2:
            raise Exception(f'Syntax error at line {vc_token[pt2]["position"]}')
        elif err1 == False:
            pointer = pt1
            ast = ast1
        elif err2 == False:
            pointer = pt2
            ast = ast2

    return ast


def LL1_parser(file):
    transition_table = readGrammarTable("grammar")
    vc_token = read(f'lexer/{file}.verbose.vctok')
    ast = parse(file, vc_token, transition_table)

    print("Done")
    return ast

if __name__ == '__main__':
    ast = LL1_parser("example_gcd")
    ast = ast.remove_parent(ast)
    print(ast.__repr__())
    print(print_ast(ast, 0))