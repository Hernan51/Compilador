from parser_s import AnnotatedNode


class SymbolTable:
    def __init__(self):
        self.table = {}

    def add_symbol(self, name, var_type, value, loc, line):
        if name not in self.table:
            self.table[name] = {
                "type": var_type,
                "value": value,
                "loc": loc,
                "lines": [line]
            }
        else:
            # Actualiza las líneas si ya existe
            if line not in self.table[name]["lines"]:
                self.table[name]["lines"].append(line)

    def update_symbol(self, name, value, line):
        if name in self.table:
            self.table[name]["value"] = value
            if line not in self.table[name]["lines"]:
                self.table[name]["lines"].append(line)

    def get_symbols(self):
        # Devolver toda la tabla de símbolos
        return self.table
    
    def get_symbol(self, name):
        # Devolver un solo símbolo dado su nombre
        return self.table.get(name, None)

    def is_declared(self, name):
        return name in self.table

    def is_initialized(self, name):
        return self.table.get(name, {}).get("initialized", False)

    def display(self):
        """
        Función para mostrar la tabla de símbolos.
        """
        print(f"{'Variable':<10}{'Type':<10}{'Value':<10}{'LOC':<10}{'Lines':<20}{'Scope':<10}{'Const':<10}{'Init':<10}")
        for name, info in self.table.items():
            print(f"{name:<10}{info['type']:<10}{info['value']:<10}{info['loc']:<10}{','.join(map(str, info['lines'])):<20}{info['scope']:<10}{info['is_const']:<10}{info['initialized']:<10}")

    

def fill_symbol_table(ast_node, symbol_table, loc=0):
    """
    Recorre el árbol sintáctico 'ast_node' y llena la tabla de símbolos 'symbol_table'.
    Utiliza las líneas de los nodos para reflejar correctamente las declaraciones y usos.
    """
    if ast_node.name == "VariableDeclaration":
        for child in ast_node.children:
            if child.name == "Identifier":
                var_name = child.value
                var_type = ast_node.value
                line = ast_node.line  # Usar la línea almacenada en el nodo
                symbol_table.add_symbol(
                    name=var_name,
                    var_type=var_type,
                    value=None,  # No tiene valor inicial hasta la asignación
                    loc=loc+1,  # Asigna la localización de la declaración
                    line=line  # Asigna la línea de declaración
                )
                loc += 1  # Incrementa el LOC para cada nueva declaración
    
    if ast_node.name == "Assignment":
        var_name = ast_node.children[0].value  # El nombre de la variable
        expression_node = ast_node.children[1]  # El valor de la expresión o número
        var_value = evaluate_expression(expression_node, symbol_table)  # Evaluar la expresión
        line = ast_node.line  # Usar la línea del nodo de asignación
        if var_name in symbol_table.get_symbols():
            symbol_table.table[var_name]["value"] = var_value  # Actualiza el valor
            # Añadir la línea actual si no está ya
            if line not in symbol_table.table[var_name]["lines"]:
                symbol_table.table[var_name]["lines"].append(line)

    # Recorre los hijos y pasa el loc actualizado
    for child in ast_node.children:
        fill_symbol_table(child, symbol_table, loc)






def evaluate_expression(node, symbol_table):
    """
    Evalúa una expresión a partir del nodo del árbol y la tabla de símbolos.
    """
    if node.name == "Number":
        return node.value  # Si es un número, regresa el valor directamente
    elif node.name == "Identifier":
        var_name = node.value
        if var_name in symbol_table.get_symbols():
            return symbol_table.get_symbol(var_name)["value"]  # Regresa el valor de la variable
    elif node.name == "TIMES":
        # Evaluar la operación de multiplicación (TIMES)
        left_value = evaluate_expression(node.children[0], symbol_table)
        right_value = evaluate_expression(node.children[1], symbol_table)
        return float(left_value) * float(right_value)
    # Puedes añadir más operadores aquí como PLUS, MINUS, DIVIDE, etc.









