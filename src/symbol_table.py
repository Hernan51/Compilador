import re
from parser_s import AnnotatedNode
import math


class SymbolTable:
    def __init__(self):
        self.table = {}
        self.loc_counter = 0  # Contador de LOC para asignar a cada variable
        self.errors = []
    
    def update_value(self, var_name, value, assignment_node=None):
        """
        Actualiza el valor de una variable en la tabla de símbolos, verificando la compatibilidad de tipos.
        Si hay un error de tipo, se registra el error, pero se conserva el último valor válido.
        """
        if var_name in self.table:
            variable_info = self.table[var_name][0]  # Obtener la información de la variable
            var_type = variable_info['type']
            print(f"DEBUG: Actualizando '{var_name}' de tipo '{var_type}' con el valor '{value}'.")

            # Verificar si el tipo es 'int' y el valor es un float
            try:
                # Intentar convertir el valor a float si contiene un punto decimal
                is_float = '.' in str(value)
                numeric_value = float(value) if is_float else int(value)
            except ValueError:
                numeric_value = value  # Si no se puede convertir, mantenemos el valor original.

            # Validar si se está intentando asignar un float a una variable de tipo int
            if var_type == 'int' and is_float:
                error_message = f"Error: No se puede asignar un valor float '{value}' a la variable '{var_name}' de tipo int."
                self.errors.append(error_message)
                print(f"DEBUG: {error_message}")

                # No actualizar el valor en la tabla de símbolos, conservar el último valor válido.
                variable_info['error'] = "Error de tipo de datos"

                # Agregar un nodo de error al árbol si se proporciona el nodo de la asignación.
                if assignment_node:
                    error_node = AnnotatedNode(
                        name="Error",
                        value=error_message,
                        type="TypeError",
                        children=[],
                    )
                    assignment_node.add_child(error_node)
            else:
                # Asignar el valor si es compatible
                variable_info['value'] = numeric_value
                # Si el valor era válido, eliminar cualquier error previo
                if 'error' in variable_info:
                    del variable_info['error']
        else:
            error_message = f"Error: La variable '{var_name}' no está declarada."
            self.errors.append(error_message)
            print(f"DEBUG: {error_message}")
            if assignment_node:
                error_node = AnnotatedNode(
                    name="Error",
                    value=error_message,
                    type="NameError",
                    children=[],
                )
                assignment_node.add_child(error_node)





    def add_usage(self, name, line):
        """
        Añadir la línea de uso de la variable a la tabla de símbolos.
        """
        if name in self.table:
            symbol = self.table[name][0]  # Acceder al símbolo (primer diccionario)

            


    def add_symbol(self, name, var_type, value, loc):
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

    def update_symbol(self, name, value):
        if name in self.table:
            symbol = self.table[name][0]
            print(f"Actualizando valor de '{name}' a {value} en la línea ")
            
            # Actualizar el valor del símbolo si no es None
            if value is not None:
                symbol['value'] = value  # Actualizamos el valor con lo que obtuvimos del AST
            
            # Agregar la línea si no está ya registrada
            
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
        Función para mostrar la tabla de símbolos con la columna de errores.
        """
        print(f"{'Variable':<10}{'Type':<10}{'Value':<10}{'LOC':<10}{'Lines':<20}{'Error':<20}")
        
        for name, symbols in self.table.items():
            for info in symbols:
                lines_str = ', '.join(str(line) for line in info.get('lines', []) if line)
                error = info.get('error', '')
                print(f"{name:<10}{info['type']:<10}{info['value']:<10}{info['loc']:<10}{lines_str:<20}{error:<20}")

# Función para llenar la tabla de símbolos a partir del árbol anotado
def fill_symbol_table(node, symbol_table, loc=None):
    if node is None:
        return

    # Recorrer los hijos del nodo del árbol
    for child in node.children:
        
        # Declaración de variables
        if isinstance(child, AnnotatedNode) and child.name == "VariableDeclaration":
            var_type = child.value
            var_name = child.children[0].value
           

            

        # Asignación de variables del tipo [variable] = algo
        elif isinstance(child, AnnotatedNode) and child.name == "Assignment":
            var_name = None
            var_value = None
            

            # Recorrer los hijos de Assignment para encontrar el identificador y el valor
            for child_node in child.children:
                if child_node.name == "Identifier" and child_node.value != "Identifier":
                    var_name = child_node.value
                elif child_node.name in ["Literal", "Number"]:
                    var_value = child_node.value

            # Actualizamos la tabla de símbolos
            if var_name is not None:
                # Obtener el tipo de la variable desde la tabla de símbolos
                var_info = symbol_table.get_symbol(var_name)
                var_type = var_info[0]['type'] if var_info else 'unknown'

                is_float = '.' in str(var_value)  # Comprobar si el valor es un número flotante

                # Si la variable es de tipo int y el valor es flotante, asignar 0 y registrar el error
                if var_type == 'int' and is_float:
                    print(f"DEBUG: Asignando 0 a la variable '{var_name}' debido a valor flotante.")
                    symbol_table.update_symbol(var_name, "Error de tipo de dato")
                else:
                    # Si la variable es de tipo float o el valor no es flotante, actualizar con el valor dado
                    print(f"DEBUG: Actualizando '{var_name}' de tipo '{var_type}' con el valor '{var_value}'.")
                    symbol_table.update_symbol(var_name, var_value)












# Función para evaluar expresiones aritméticas
def evaluate_expression(self, node, symbol_table):
    """
    Recursively evaluates an expression node using the values from the symbol table.
    """
    if node.name == 'Number':
        try:
            value = float(node.value) if '.' in node.value else int(node.value)
            print(f"DEBUG: Evaluating Number: {node.value} -> {value}")
            return value
        except ValueError:
            print(f"DEBUG: Error converting number: {node.value}")
            return "Error de tipo de datos"

    if node.name == 'Identifier':
        var_info = symbol_table.table.get(node.value)
        if var_info and var_info[0]['value'] is not None:
            variable_value = var_info[0]['value']
            # Si hay un error de tipo de datos registrado, manejar el caso.
            if 'error' in var_info[0] and var_info[0]['error'] == "Error de tipo de datos":
                print(f"DEBUG: Variable '{node.value}' tiene un error de tipo de datos.")
                # Utilizar el valor numérico si es válido, a pesar del error.
                if isinstance(variable_value, (int, float)):
                    return variable_value
                else:
                    return "Error de tipo de datos"
            return variable_value
        else:
            print(f"DEBUG: Error: Variable '{node.value}' usada antes de ser asignada.")
            return "Error de tipo de datos"

    # Evaluar nodos aritméticos.
    if node.name in ['PLUS', 'MINUS', 'TIMES', 'DIVIDE']:
        left_val = self.evaluate_expression(node.children[0], symbol_table)
        right_val = self.evaluate_expression(node.children[1], symbol_table)

        # Si alguno de los valores tiene un error, propagar el error.
        if left_val == "Error de tipo de datos" or right_val == "Error de tipo de datos":
            print(f"DEBUG: Propagando error de tipo de datos en la operación {node.name}.")
            return "Error de tipo de datos"
        
        try:
            # Realizar la operación si ambos valores son válidos.
            if node.name == 'PLUS':
                result = left_val + right_val
            elif node.name == 'MINUS':
                result = left_val - right_val
            elif node.name == 'TIMES':
                result = left_val * right_val
            elif node.name == 'DIVIDE':
                result = 1

            
            print(f"DEBUG: Result of {node.name}: {result}")
            node.result = result
            return result
        except TypeError:
            print(f"DEBUG: Error en la operación {node.name} debido a tipos incompatibles.")
            return "Error de tipo de datos"
    
    return None







