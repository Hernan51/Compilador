from parser_s import AnnotatedNode


class SymbolTable:
    def __init__(self):
        self.table = {}
        self.loc_counter = 0  # Contador de LOC para asignar a cada variable

    def add_usage(self, name, line):
        """
        Añadir la línea de uso de la variable a la tabla de símbolos.
        """
        if name in self.table:
            symbol = self.table[name][0]  # Acceder al símbolo (primer diccionario)

            # Añadir la línea si no está ya presente
            if str(line) not in symbol['lines']:
                symbol['lines'].append(str(line))


    def add_symbol(self, name, var_type, value, loc, line):
        # Filtrar nodos con nombre "Identifier"
        if name == "Identifier":
            print(f"Se ignoró un nodo genérico 'Identifier'.")
            return  # No hacemos nada si el nombre es "Identifier"

        # Definir un orden de prioridad de tipos
        type_priority = {"int": 1, "float": 2}  # Puedes agregar más tipos con sus prioridades.

        # Verificar si la variable ya está en la tabla
        if name in self.table:
            existing_type = self.table[name][0]["type"]
            existing_priority = type_priority.get(existing_type, 0)
            new_priority = type_priority.get(var_type, 0)

            # Solo actualiza el tipo si el nuevo es de mayor prioridad
            if new_priority > existing_priority:
                print(f"Actualizando tipo de '{name}' de {existing_type} a {var_type}")
                self.table[name][0]["type"] = var_type
        else:
            # Si la variable no está en la tabla, la añadimos
            loc = self.loc_counter  # Asignar LOC único
            self.table[name] = [{
                "type": var_type,
                "value": value,
                "loc": loc,
                "lines": [str(line)]
            }]
            self.loc_counter += 1  # Incrementar LOC


    def _add_single_symbol(self, name, var_type, value, loc, line):
        # Filtrar nodos con nombre "Identifier"
        if name == "Identifier":
            print(f"Se ignoró un nodo genérico 'Identifier'.")
            return  # No hacemos nada si el nombre es "Identifier"

        # Verificar si se está intentando hacer un downcast (float a int)
        if var_type == "int" and isinstance(value, float):
            value = "Error de tipo de datos"
            print(f"Error de tipo de datos: No se puede asignar un valor float a la variable '{name}' de tipo int.")

        # Imprimir el valor para verificar qué se está pasando
        print(f"Añadiendo símbolo: nombre={name}, tipo={var_type}, valor={value}, loc={loc}, línea={line}")

        # Si la variable no está en la tabla, la añadimos
        if name not in self.table:
            loc = self.loc_counter  # Asignar LOC único
            self.table[name] = [{
                "type": var_type,
                "value": value,
                "loc": loc,
                "lines": [str(line)]  # Aquí es donde se registra la línea
            }]
            self.loc_counter += 1  # Incrementar LOC
        else:
            # Si ya existe la variable, actualizamos sus líneas
            symbol = self.table[name][0]

            # Actualizamos las líneas donde aparece la variable
            if str(line) not in symbol['lines']:
                symbol['lines'].append(str(line))





    
    def get_symbols(self):
        # Devolver toda la tabla de símbolos
        return self.table

    def update_symbol(self, name, value, line):
        if name in self.table:
            symbol = self.table[name][0]
            print(f"Actualizando valor de '{name}' a {value} en la línea {line}")
            
            # Actualizar el valor del símbolo si no es None
            if value is not None:
                symbol['value'] = value  # Actualizamos el valor con lo que obtuvimos del AST
            
            # Agregar la línea si no está ya registrada
            if line is not None and str(line) not in symbol['lines']:
                symbol['lines'].append(str(line))
        else:
            print(f"Error: la variable '{name}' no se encuentra en la tabla de símbolos.")
        
        # Imprimir el estado de la tabla después de actualizar
        print(f"Tabla actualizada: {self.table}")




    def get_symbol(self, name):
        # Devolver un solo símbolo dado su nombre
        return self.table.get(name, None)

    def is_declared(self, name):
        # Verificar si un símbolo está declarado
        return name in self.table

    def is_initialized(self, name):
        return self.table.get(name, {}).get("initialized", False)

    def display(self):
        """
        Función para mostrar la tabla de símbolos sin mostrar None.
        """
        print(f"{'Variable':<10}{'Type':<10}{'Value':<10}{'LOC':<10}{'Lines':<20}{'Scope':<10}{'Const':<10}{'Init':<10}")
        
        for name, symbols in self.table.items():
            # Iteramos por cada símbolo en la lista (por si hay colisiones)
            for info in symbols:
                # Filtrar las líneas que no sean None y convertirlas a string
                lines = [str(line) for line in info["lines"] if line is not None]
                lines_str = ', '.join(lines) if lines else ''  # Evitar que salga None
                
                # Mostrar la fila de la tabla con la lista de líneas correcta
                print(f"{name:<10}{info['type']:<10}{info['value']:<10}{info['loc']:<10}{lines_str:<20}{info.get('scope', ''):<10}{info.get('is_const', ''):<10}{info.get('initialized', ''):<10}")

# Función para llenar la tabla de símbolos a partir del árbol anotado
def fill_symbol_table(node, symbol_table, assign_lines, loc=None):
    if node is None:
        return

    # Recorrer los hijos del nodo del árbol
    for child in node.children:
        
        # Declaración de variables
        if isinstance(child, AnnotatedNode) and child.name == "VariableDeclaration":
            var_type = child.value
            var_name = child.children[0].value
            line = child.line  # Usamos la línea del nodo

            # Solo agregamos la variable si la línea no es None y el nombre es válido
            if line is not None and var_name != "Identifier":
                print(f"Declaración de variable '{var_name}' en la línea {line}")
                symbol_table.add_symbol(var_name, var_type, "", loc, line)

        # Asignación de variables del tipo [variable] = algo
        elif isinstance(child, AnnotatedNode) and child.name == "Assignment":
            var_name = None
            var_value = None
            line = child.line  # Usamos la línea del nodo de asignación

            # Recorrer los hijos de Assignment para encontrar el identificador y el valor
            for child_node in child.children:
                if child_node.name == "Identifier" and child_node.value != "Identifier":  # Filtrar "Identifier"
                    var_name = child_node.value
                    print(f"Variable identificada en la asignación: {var_name}")
                elif child_node.name in ["Literal", "Number"]:
                    var_value = child_node.value  # Tomamos el valor directamente del nodo
                    print(f"Valor extraído del nodo: {var_value}")

            # Verificación del valor antes de actualizar la tabla de símbolos
            print(f"Variable '{var_name}', valor: {var_value}, línea: {line}")

            # Verificar que la variable esté en la tabla de símbolos
            if var_name in symbol_table.table:
                var_type = symbol_table.table[var_name][0]['type']

                # **Verificar si el valor es None antes de intentar convertirlo**
                if var_value is not None:
                    try:
                        # Convertir el valor si es un número flotante o entero
                        var_value_converted = float(var_value) if '.' in str(var_value) else int(var_value)
                    except ValueError:
                        var_value_converted = var_value
                else:
                    var_value_converted = None

                # Verificar si es un downcast
                if var_type == "int" and isinstance(var_value_converted, float):
                    # Si intentamos asignar un float a una variable int, es un error
                    var_value = "Error de tipo de datos"
                    print(f"Error: No se puede asignar un float a la variable '{var_name}' de tipo int.")

            # Actualizamos el símbolo en la tabla con el valor (o error) y la línea de asignación
            if var_name is not None:
                symbol_table.update_symbol(var_name, var_value, line)

        # Uso de variables en expresiones del tipo [variable], pero filtrando nodos genéricos "Identifier"
        elif isinstance(child, AnnotatedNode) and child.name == "Identifier" and child.value != "Identifier":
            var_name = child.value
            line = child.line  # Usamos la línea del nodo donde aparece la variable
            if line is not None:  # Solo agregar si la línea no es None
                symbol_table.add_usage(var_name, line)
                print(f"Uso de la variable '{var_name}' en la línea {line}")

        # Llamada recursiva para procesar los hijos
        fill_symbol_table(child, symbol_table, assign_lines, loc)







def update_variable_lines_in_expression(node, symbol_table, line):
    """
    Recorre una expresión para identificar todas las variables usadas
    y registra las líneas correspondientes.
    """
    if node is None:
        return

    if node.name == "Identifier":
        var_name = node.value
        # Registrar que la variable fue usada en la línea de la expresión
        symbol_table.add_usage(var_name, line)

    # Procesar recursivamente las expresiones
    for child in node.children:
        update_variable_lines_in_expression(child, symbol_table, line)




# Función para evaluar expresiones aritméticas
def evaluate_expression(node, symbol_table):
    if node.name == "Number":
        return node.value  # Si es un número, devuelve el valor directamente
    elif node.name == "Identifier":
        var_name = node.value
        symbol = symbol_table.get_symbol(var_name)
        if symbol:
            return symbol[0]['value']  # Retorna el valor almacenado en la tabla de símbolos
        else:
            print(f"Error: variable '{var_name}' no tiene valor asignado.")
            return None
    elif node.name == "TIMES":  # Multiplicación
        left_value = evaluate_expression(node.children[0], symbol_table)
        right_value = evaluate_expression(node.children[1], symbol_table)
        return float(left_value) * float(right_value)
    # Puedes añadir más operadores aquí (PLUS, MINUS, DIVIDE, etc.)




