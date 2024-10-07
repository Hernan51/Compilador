from parser_s import AnnotatedNode


class SymbolTable:
    def __init__(self):
        self.table = {}
        self.loc_counter = 0  # Contador de LOC para asignar a cada variable

    def add_symbol(self, name, var_type, value, loc, line):
        # Si la variable no está en la tabla, la añadimos como una lista de diccionarios
        if name not in self.table:
            loc = self.loc_counter  # Asignar LOC único
            self.table[name] = [{"type": var_type, "value": value, "loc": loc, "lines": [line]}]
            self.loc_counter += 1  # Incrementar LOC
        else:
            # Si ya existe la variable, verificar si tiene el mismo tipo
            for symbol in self.table[name]:
                if symbol['type'] == var_type:
                    # Actualizamos el valor y las líneas
                    symbol['value'] = value
                    if line is not None and line not in symbol['lines']:
                        symbol['lines'].append(line)
                    return
            # Si no existe un símbolo con el mismo tipo, agregamos una nueva entrada (colisión)
            loc = self.loc_counter
            self.table[name].append({"type": var_type, "value": value, "loc": loc, "lines": [line]})
            self.loc_counter += 1  # Incrementar LOC para la nueva variable

    def get_symbols(self):
        # Devolver toda la tabla de símbolos
        return self.table




    def update_symbol(self, name, value, line):
        if name in self.table:
            self.table[name]["value"] = value
            if line is not None and line not in self.table[name]["lines"]:
                self.table[name]["lines"].append(line)


   
    
    def get_symbol(self, name):
        # Devolver un solo símbolo dado su nombre
        return self.table.get(name, None)

    def is_declared(self, name):
        return name in self.table

    def is_initialized(self, name):
        return self.table.get(name, {}).get("initialized", False)

def display(self):
    """
    Función para mostrar la tabla de símbolos sin mostrar None.
    """
    print(f"{'Variable':<10}{'Type':<10}{'Value':<10}{'LOC':<10}{'Lines':<20}{'Scope':<10}{'Const':<10}{'Init':<10}")
    
    for name, info in self.table.items():
        # Filtrar las líneas que no sean None y convertirlas a string
        lines = [str(line) for line in info["lines"] if line is not None]
        lines_str = ', '.join(lines) if lines else ''  # Evitar que salga None
        
        # Mostrar la fila de la tabla con la lista de líneas correcta
        print(f"{name:<10}{info['type']:<10}{info['value']:<10}{info['loc']:<10}{lines_str:<20}{info.get('scope', ''):<10}{info.get('is_const', ''):<10}{info.get('initialized', ''):<10}")


def fill_symbol_table(node, symbol_table, loc=None):
    if node is None:
        return
    
    # Recorrer los hijos del nodo del árbol
    for child in node.children:
        if isinstance(child, AnnotatedNode) and child.name == "VariableDeclaration":
            # Acceder a los hijos de VariableDeclaration
            var_type = child.value  # Aquí capturamos el tipo de la variable
            var_name = child.children[0].value  # Capturamos el nombre de la variable
            line = child.line  # Número de línea donde se declaró la variable

            # Añadir la variable a la tabla de símbolos usando encadenamiento
            symbol_table.add_symbol(var_name, var_type, None, loc, line)

        elif isinstance(child, AnnotatedNode) and child.name == "Assignment":
            # Procesar una asignación
            var_name = None
            var_value = None
            line = child.line  # Línea donde ocurre la asignación

            # Recorrer los hijos de Assignment para encontrar el identificador y el valor
            for child_node in child.children:
                if child_node.name == "Identifier":
                    var_name = child_node.value  # Nombre de la variable a la izquierda de la asignación
                elif child_node.name == "Literal" or child_node.name == "Number":
                    var_value = child_node.value  # Valor literal o numérico asignado

            if var_name is not None and var_name in symbol_table.table:
                # Actualizar el valor de la variable en la tabla
                for symbol in symbol_table.table[var_name]:
                    symbol['value'] = var_value
                    if line not in symbol['lines']:
                        symbol['lines'].append(line)

        # Llamada recursiva para procesar los hijos
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









