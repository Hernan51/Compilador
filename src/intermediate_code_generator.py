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

        elif node.name == "Declaration":
            pass  # Declaraciones no generan código intermedio

        elif node.name in ["EQ", "GT", "PLUS", "MINUS", "TIMES", "DIVIDE"]:
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
                    "EQ": "=="
                }[node.name]
                self.add_code(f"{temp} = {left} {operator} {right}")
                return temp
            else:
                print(f"DEBUG: Nodo {node.name} no tiene suficientes hijos.")

        elif node.name == "Assignment":
            if len(node.children) >= 2:
                target = node.children[0].value
                expression = self.generate_code(node.children[1])
                self.add_code(f"{target} = {expression}")
            else:
                print(f"DEBUG: Nodo Assignment no tiene suficientes hijos.")

        elif node.name == "If":
            if len(node.children) >= 2:
                condition = self.generate_code(node.children[0])
                label_true = self.new_label()
                label_false = self.new_label()
                label_end = self.new_label()

                self.add_code(f"if {condition} goto {label_true}")
                self.add_code(f"goto {label_false}")

                self.add_code(f"{label_true}:")
                self.generate_code(node.children[1])  # TrueBranch
                self.add_code(f"goto {label_end}")

                self.add_code(f"{label_false}:")
                if len(node.children) > 2:
                    self.generate_code(node.children[2])  # FalseBranch
                self.add_code(f"{label_end}:")
            else:
                print(f"DEBUG: Nodo If no tiene suficientes hijos.")

        elif node.name in ["TrueBranch", "FalseBranch"]:
            for child in node.children:
                self.generate_code(child)

        elif node.name == "Arithmetic":
            if len(node.children) >= 2:
                left = self.generate_code(node.children[0])
                right = self.generate_code(node.children[1])
                temp = self.new_temp()
                self.add_code(f"{temp} = {left} {node.value} {right}")
                return temp
            else:
                print(f"DEBUG: Nodo Arithmetic no tiene suficientes hijos.")

        elif node.name == "While":
            if len(node.children) >= 2:
                label_start = self.new_label()
                label_end = self.new_label()

                self.add_code(f"{label_start}:")
                condition = self.generate_code(node.children[0])
                self.add_code(f"if not {condition} goto {label_end}")
                self.generate_code(node.children[1])  # Cuerpo del while
                self.add_code(f"goto {label_start}")
                self.add_code(f"{label_end}:")
            else:
                print(f"DEBUG: Nodo While no tiene suficientes hijos.")

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

        elif node.name in ["Input", "Output", "Decrement"]:
            if len(node.children) >= 1:
                target = self.generate_code(node.children[0])
                operation = {
                    "Input": f"cin >> {target}",
                    "Output": f"cout << {target}",
                    "Decrement": f"{target} = {target} - 1"
                }[node.name]
                self.add_code(operation)
            else:
                print(f"DEBUG: Nodo {node.name} no tiene suficientes hijos.")

        elif node.name == "Number":
            return node.value

        elif node.name == "Identifier":
            return node.value

        else:
            print(f"DEBUG: Nodo no manejado: {node.name}")

    def get_code(self):
        """Obtener el código generado como una cadena."""
        return "\n".join(self.code)
