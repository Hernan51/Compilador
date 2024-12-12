class IntermediateCodeGenerator:
    def __init__(self):
        self.temp_counter = 0
        self.label_counter = 0
        self.code = []

    def new_temp(self):
        """Generar un nuevo temporal."""
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self):
        """Generar una nueva etiqueta."""
        self.label_counter += 1
        return f"L{self.label_counter}"

    def add_code(self, line):
        """Agregar una línea de código intermedio."""
        self.code.append(line)

    def generate_code(self, node):
        """Recorrer el AST y generar código intermedio."""
        print(f"DEBUG: Procesando nodo {node.name} con {len(node.children) if node.children else 0} hijos.")

        if node.name == "Program":
            for child in node.children:
                self.generate_code(child)

        elif node.name == "While":
            if len(node.children) >= 2:
                label_start = self.new_label()
                label_end = self.new_label()
                self.add_code(f"{label_start}:")
                
                # Generar la condición del While
                condition = self.generate_code(node.children[0])
                self.add_code(f"if not {condition} goto {label_end}")
                
                # Procesar recursivamente cada nodo dentro del cuerpo
                body = node.children[1:]  # Los nodos dentro del cuerpo del While
                for child in body:
                    self.generate_code(child)
                
                # Solo agregar incremento si está explícito en el AST
                increment_nodes = [child for child in body if child.name == "Increment"]
                for inc in increment_nodes:
                    self.generate_code(inc)

                self.add_code(f"goto {label_start}")
                self.add_code(f"{label_end}:")
            else:
                print("DEBUG: Nodo While no tiene suficientes hijos.")

        elif node.name == "Increment":
            if len(node.children) >= 1:
                target = self.generate_code(node.children[0])  # El nodo que se incrementará
                temp = self.new_temp()  # Temporal para almacenar la operación
                self.add_code(f"{temp} = {target} + 1")
                self.add_code(f"{target} = {temp}")
            else:
                print("DEBUG: Nodo Increment no tiene suficientes hijos.")



        elif node.name == "If":
            if len(node.children) >= 2:
                # Generar la condición
                condition = self.generate_code(node.children[0])  # Nodo de la condición
                label_true = self.new_label()  # Etiqueta para TrueBranch
                label_false = self.new_label()  # Etiqueta para FalseBranch o fin de condición
                label_end = self.new_label() if len(node.children) > 2 else label_false  # Etiqueta final, si hay FalseBranch
                
                # Instrucciones para la condición
                self.add_code(f"if {condition} goto {label_true}")
                self.add_code(f"goto {label_false}")
                
                # Generar código para TrueBranch
                self.add_code(f"{label_true}:")
                self.generate_code(node.children[1])  # TrueBranch
                if len(node.children) > 2:  # Si hay un FalseBranch, se requiere salto al final
                    self.add_code(f"goto {label_end}")
                
                # Generar código para FalseBranch (si existe)
                if len(node.children) > 2:
                    self.add_code(f"{label_false}:")
                    self.generate_code(node.children[2])  # FalseBranch
                
                # Etiqueta final
                self.add_code(f"{label_end}:")
            else:
                print("DEBUG: Nodo If no tiene suficientes hijos.")





        elif node.name == "AND":
            left = self.generate_code(node.children[0])  # Genera el código para el hijo izquierdo
            right = self.generate_code(node.children[1])  # Genera el código para el hijo derecho
            temp = self.new_temp()  # Crea un temporal para almacenar el resultado
            self.add_code(f"{temp} = {left} and {right}")  # Genera la instrucción
            return temp  # Retorna el temporal

        elif node.type == "Comparison":
            left = self.generate_code(node.children[0])  # Lado izquierdo de la comparación
            right = self.generate_code(node.children[1])  # Lado derecho de la comparación
            temp = self.new_temp()  # Crea un temporal
            self.add_code(f"{temp} = {left} {node.value} {right}")  # Genera la comparación
            return temp


    

        elif node.name == "DoWhile":
            if len(node.children) >= 2:
                label_start = self.new_label()
                self.add_code(f"{label_start}:")
                for stmt in node.children[:-1]:
                    self.generate_code(stmt)
                condition = self.generate_code(node.children[-1])
                self.add_code(f"if {condition} goto {label_start}")
            else:
                print(f"DEBUG: Nodo DoWhile no tiene suficientes hijos.")

        elif node.name == "Switch":
            condition = self.generate_code(node.children[0])
            end_label = self.new_label()
            for child in node.children[1:]:
                if child.name == "Case":
                    case_label = self.new_label()
                    case_value = child.value
                    self.add_code(f"if {condition} == {case_value} goto {case_label}")
                    self.add_code(f"goto {end_label}")
                    self.add_code(f"{case_label}:")
                    for stmt in child.children:
                        self.generate_code(stmt)
                elif child.name == "Default":
                    default_label = self.new_label()
                    self.add_code(f"{default_label}:")
                    for stmt in child.children:
                        self.generate_code(stmt)
            self.add_code(f"{end_label}:")

        elif node.name == "Assignment":
            if len(node.children) >= 2:
                target = node.children[0].value
                value_node = node.children[1]
                if value_node.name == "Literal":
                    temp = self.new_temp()
                    self.add_code(f"{temp} = {value_node.value}")
                    self.add_code(f"{target} = {temp}")
                else:
                    expression = self.generate_code(value_node)
                    self.add_code(f"{target} = {expression}")

        elif node.name in ["EQ", "GT","LT", "PLUS", "MINUS", "TIMES", "DIVIDE"]:
            if len(node.children) >= 2:
                left = self.generate_code(node.children[0])
                right = self.generate_code(node.children[1])
                temp = self.new_temp()
                operator = {
                    "PLUS": "+",
                    "MINUS": "-",
                    "TIMES": "*",
                    "DIVIDE": "/",
                    "GT": ">",
                    "LT": "<",
                    "EQ": "=="
                }[node.name]
                self.add_code(f"{temp} = {left} {operator} {right}")
                return temp
            else:
                print(f"DEBUG: Nodo {node.name} no tiene suficientes hijos.")

        elif node.name in ["Input", "Output", "Decrement"]:
            if len(node.children) >= 1:
                target_node = node.children[0]
                if node.name == "Input":
                    target = self.generate_code(target_node)
                    self.add_code(f"cin >> {target}")
                elif node.name == "Output":
                    target = self.generate_code(target_node)
                    if target_node.name == "Literal":
                        self.add_code(f'cout << "{target_node.value}"')
                    else:
                        self.add_code(f"cout << {target}")
                elif node.name == "Decrement":
                    target = self.generate_code(target_node)
                    self.add_code(f"{target} = {target} - 1")
            elif node.name == "Input":
                # Nodo Input sin hijos pero con un identificador en el AST
                target = node.value if hasattr(node, 'value') else "<undefined>"
                self.add_code(f"cin >> {target}")
            else:
                print(f"DEBUG: Nodo {node.name} no tiene suficientes hijos.")

        elif node.name == "Number":
            return node.value

        elif node.name == "Identifier":
            return node.value

        elif node.name == "Literal":
            return f'"{node.value}"'

        elif node.name == "Declaration":
            # No se genera código, pero reconocemos el nodo
            pass

        else:
            print(f"DEBUG: Nodo no manejado: {node.name} (Tipo: {node.type if hasattr(node, 'type') else 'Desconocido'})")
            for child in node.children:
                self.generate_code(child)

    def get_code(self):
        """Obtener el código generado como una cadena."""
        return "\n".join(self.code)
