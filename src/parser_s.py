from lexer import Token
from anytree import NodeMixin, RenderTree


class AnnotatedNode(NodeMixin):
    def __init__(self, name, value=None, type=None, line=None, children=None):
        self.name = name
        self.value = value
        self.type = type
        self.line = line
        if children:
            self.children = children

    def __str__(self):
        line_info = f"Line: {self.line}" if self.line is not None else "Line: Unknown"
        
        if self.value and self.type:
            return f"{self.name} (Type: {self.type}, Value: {self.value}, {line_info})"
        elif self.value:
            return f"{self.name} (Value: {self.value}, {line_info})"
        elif self.type:
            return f"{self.name} (Type: {self.type}, {line_info})"
        else:
            return f"{self.name} ({line_info})"



class Parser:
    def __init__(self, tokens: list[Token], symbol_table):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = self.tokens[self.current_token_index]
        self.symbol_table = symbol_table  

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token_index += 1
            if self.current_token_index < len(self.tokens):
                self.current_token = self.tokens[self.current_token_index]
        else:
            raise Exception(
                f"Unexpected token {self.current_token.type}, expected {token_type}"
            )

    def parse(self):
        return self.program()

    def program(self):
        token = self.current_token
        self.eat("MAIN")
        self.eat("LBRACE")
        declarations = self.declaration_list()
        statements = self.sentence_list()
        self.eat("RBRACE")
        
        # Filtrar cualquier None de la lista de children antes de crear el nodo
        valid_children = [child for child in declarations + statements if child is not None]
        
        return AnnotatedNode(
            name="Program",
            value=token.value,
            type="Main Program",
            children=valid_children,
        )


    def declaration_list(self):
        declarations = []
        while self.current_token and self.current_token.type in [
            "INT",
            "DOUBLE",
            "FLOAT",
        ]:
            declarations.append(self.declaration_statement())
        return declarations

    def declaration_statement(self):
        if self.current_token.type == "INT":
            return self.variable_declaration("int")
        elif self.current_token.type == "DOUBLE":
            return self.variable_declaration("double")
        elif self.current_token.type == "FLOAT":
            return self.variable_declaration("float")
        else:
            return self.sentence()

    def variable_declaration(self, var_type):
        """
        Procesa una declaración de variables como int x, y, z;
        y las añade a la tabla de símbolos de manera individual.
        """
        # Adaptar la espera según el tipo de variable (INT, FLOAT, etc.)
        if var_type == 'int':
            self.eat('INT')
        elif var_type == 'float':
            self.eat('FLOAT')
        # Agrega más tipos si es necesario, por ejemplo, 'char', 'double', etc.

        # Mientras haya variables separadas por comas
        while self.current_token.type == 'IDENTIFIER':
            var_name = self.current_token.value
            self.eat('IDENTIFIER')

            # Añadir cada variable por separado a la tabla de símbolos
            self.symbol_table.add_symbol(var_name, var_type, None, None, self.current_token.lineno)

            # Si hay una coma, comemos la coma y seguimos con la siguiente variable
            if self.current_token.type == 'COMMA':
                self.eat('COMMA')
            else:
                break

        # Consumir el punto y coma que termina la declaración
        self.eat('SEMICOLON')





    def identifier(self):
        ids = []
        while self.current_token.type == "IDENTIFIER":
            token = self.current_token  # Guarda el token para extraer la línea
            ids.append(AnnotatedNode(name="Identifier", value=token.value, type="Variable", line=token.lineno))
            self.eat("IDENTIFIER")
            if self.current_token.type == "COMMA":
                self.eat("COMMA")
        return ids


    def sentence_list(self):
        statements = []
        while self.current_token and self.current_token.type != "RBRACE":
            statements.append(self.sentence())
        return statements

    def sentence(self):
        if self.current_token.type == "IF":
            return self.if_statement()
        elif self.current_token.type == "WHILE":
            return self.while_loop_sentence()
        elif self.current_token.type == "DO":
            return self.do_while_loop_sentence()
        elif self.current_token.type == "CIN":
            return self.cin_sentence()
        elif self.current_token.type == "COUT":
            return self.cout_sentence()
        elif self.current_token.type == "IDENTIFIER":
            return self.assignment_or_increment_decrement()
        else:
            raise Exception(f"Unexpected token {self.current_token.type}")

    def assignment_or_increment_decrement(self):
        identifier_token = self.current_token.value
        line_number = self.current_token.lineno  # Guardar la línea donde ocurre

        # **Modificación 3**: Registrar el uso de la variable
        self.symbol_table.add_usage(identifier_token, line_number)  # Registrar uso de la variable
        self.eat("IDENTIFIER")
        
        if self.current_token.type == "ASSIGN":
            assign_token = self.current_token
            self.eat("ASSIGN")
            expression = self.sent_expression()
            self.eat("SEMICOLON")
            return AnnotatedNode(
                "Assignment",
                value=assign_token.value,
                type="Assignment",
                children=[AnnotatedNode("Identifier", value=identifier_token, type="Variable"), expression],
            )
        elif self.current_token.type == "INCREMENT_OPERATOR":
            operator_token = self.current_token
            self.eat("INCREMENT_OPERATOR")
            self.eat("SEMICOLON")
            return AnnotatedNode(
                name="Increment",
                value=operator_token.value,
                type="Increment",
                children=[AnnotatedNode(name="Identifier", value=identifier_token, type="Variable")],
            )
        elif self.current_token.type == "DECREMENT_OPERATOR":
            operator_token = self.current_token
            self.eat("DECREMENT_OPERATOR")
            self.eat("SEMICOLON")
            return AnnotatedNode(
                name="Decrement",
                value=operator_token.value,
                type="Decrement",
                children=[AnnotatedNode("Identifier", value=identifier_token, type="Variable")],
            )
        else:
            raise Exception(f"Unexpected token {self.current_token.type}")

    def sent_expression(self):
        if self.current_token.type == "SEMICOLON":
            self.eat("SEMICOLON")
            return AnnotatedNode("EmptyStatement")
        else:
            return self.expression()

    def if_statement(self):
        self.eat("IF")
        self.eat("LPAREN")
        condition = self.expression()
        self.eat("RPAREN")
        self.eat("LBRACE")
        true_branch = self.sentence_list()
        self.eat("RBRACE")

        if self.current_token and self.current_token.type == "ELSE":
            self.eat("ELSE")
            self.eat("LBRACE")
            false_branch = self.sentence_list()
            self.eat("RBRACE")
            return AnnotatedNode(
                name="If",
                value="if",
                type="Conditional",
                children=[
                    condition,
                    AnnotatedNode(name="TrueBranch", value="true_branch", children=true_branch),
                    AnnotatedNode(
                        name="FalseBranch", value="false_branch", children=false_branch
                    ),
                ],
            )
        else:
            return AnnotatedNode(
                name="If",
                value="if",
                type="Conditional",
                children=[
                    condition,
                    AnnotatedNode(name="TrueBranch", value="true_branch", children=true_branch),
                ],
            )

    def while_loop_sentence(self):
        self.eat("WHILE")
        self.eat("LPAREN")
        condition = self.expression()
        self.eat("RPAREN")
        self.eat("LBRACE")
        statements = self.sentence_list()
        self.eat("RBRACE")
        return AnnotatedNode(name="While", value="while", type="Loop", children=[condition] + statements)

    def do_while_loop_sentence(self):
        self.eat("DO")
        self.eat("LBRACE")
        statements = self.sentence_list()
        self.eat("RBRACE")
        self.eat("WHILE")
        self.eat("LPAREN")
        condition = self.expression()
        self.eat("RPAREN")
        return AnnotatedNode(name="DoWhile", value="do_while", type="Loop", children=statements + [condition])

    def cin_sentence(self):
        identifier = self.current_token.value
        self.eat("CIN")
        self.eat("IDENTIFIER")
        self.eat("SEMICOLON")
        return AnnotatedNode(name="Input", value=identifier, type="Input")

    def cout_sentence(self):
        identifier = self.current_token.value
        self.eat("COUT")
        expression = self.expression()
        self.eat("SEMICOLON")
        return AnnotatedNode(name="Output", value=identifier, type="Output", children=[expression])

    def expression(self):
        node = self.logical_expression()
        if self.current_token and self.current_token.type in [
            "LT",
            "LE",
            "GT",
            "GE",
            "EQ",
            "NE",
        ]:
            token = self.current_token
            self.eat(token.type)
            node = AnnotatedNode(
                name=token.type,
                value=token.value,
                type="Comparison",
                children=[node, self.logical_expression()],
            )
        return node

    def logical_expression(self):
        node = self.simple_expression()
        while self.current_token and self.current_token.type in ["AND", "OR"]:
            token = self.current_token
            self.eat(token.type)
            node = AnnotatedNode(
                name=token.type,
                value=token.value,
                type="Logical Operation",
                children=[node, self.simple_expression()],
            )
        return node

    def simple_expression(self):
        node = self.term()
        while self.current_token and self.current_token.type in ["PLUS", "MINUS"]:
            token = self.current_token
            self.eat(token.type)
            node = AnnotatedNode(
                name=token.type, value=token.value, type="Arithmetic", children=[node, self.term()]
            )
        return node

    def term(self):
        node = self.factor()
        while self.current_token and self.current_token.type in [
            "TIMES",
            "DIVIDE",
            "MOD",
        ]:
            token = self.current_token
            self.eat(token.type)
            node = AnnotatedNode(
                name=token.type, value=token.value, type="Arithmetic", children=[node, self.factor()]
            )
        return node

    def factor(self):
        node = self.component()
        while self.current_token and self.current_token.type == "POW":
            token = self.current_token
            self.eat("POW")
            node = AnnotatedNode(
                name=token.type, value=token.value, type="Exponentiation", children=[node, self.component()]
            )
        return node

    def component(self):
        if self.current_token.type == "LPAREN":
            self.eat("LPAREN")
            node = self.expression()
            self.eat("RPAREN")
            return node
        elif self.current_token.type in [
            "INTEGER_NUMBER",
            "REAL_NUMBER",
            "NEGATIVE_INTEGER_NUMBER",
            "NEGATIVE_REAL_NUMBER",
        ]:
            value = self.current_token.value
            self.eat(self.current_token.type)
            return AnnotatedNode(name="Number", value=value, type="Literal")
        elif self.current_token.type == "IDENTIFIER":
            identifier = self.current_token.value
            self.eat("IDENTIFIER")
            return AnnotatedNode(name="Identifier", value=identifier, type="Variable")
        else:
            raise Exception(f"Unexpected token {self.current_token.type}")

    def render_tree(self, ast):
        tree_str = ""
        for pre, _, node in RenderTree(ast):
            tree_str += "%s%s\n" % (pre, node)
        return tree_str

    


# Example usage
if __name__ == "__main__":
    import sys
    from pathlib import Path
    from anytree.exporter import DotExporter
    from lexer import get_lexical_analysis

    args = sys.argv
    if len(args) < 2:
        print("No arguments provided")
    elif len(args) > 2:
        print("Bad arguments")
    else:
        file_path = Path(args[1])
        if not file_path.exists():
            print("File does not exist")
        else:
            tkns, errs = get_lexical_analysis(file_path)

            parser = Parser(tkns)
            ast = parser.parse()

            # Render the tree as a string
            tree_str = parser.render_tree(ast)

            print(tree_str)

            # Optionally, export the tree to a file (e.g., a dot file for visualization)
            #DotExporter(ast).to_dotfile("ast.dot")
