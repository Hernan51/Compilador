from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QInputDialog
from components.dock_panels import write_to_results_panel
import re

class InterpreterThread(QThread):
    request_input_signal = pyqtSignal(str)  # Señal para solicitar un valor
    input_received_signal = pyqtSignal(str)  # Señal para recibir un valor
    finished_signal = pyqtSignal()  # Señal cuando la ejecución finaliza

    def __init__(self, intermediate_code, symbol_table):
        super().__init__()
        self.code = intermediate_code.splitlines()
        self.symbol_table = symbol_table  # Tabla de símbolos como diccionario
        self.current_line = 0  # Índice de la línea actual
        self.labels = self.map_labels()  # Mapa de etiquetas a líneas de código
        self.input_received = None  # Almacena el valor de entrada recibido
        self.waiting_for_input = False  # Bandera para controlar espera

    def map_labels(self):
        """
        Mapea las etiquetas (como L1:) a sus respectivas líneas en el código.
        """
        labels = {}
        for idx, line in enumerate(self.code):
            line = line.strip()
            if line.endswith(":"):
                label = line.split(":")[0].strip()
                labels[label] = idx
        print("Etiquetas mapeadas:", labels)
        return labels

    def run(self):
        """
        Ejecuta el intérprete línea por línea.
        """
        while self.current_line < len(self.code):
            line = self.code[self.current_line].strip()
            if not line or ":" in line:  # Ignorar etiquetas y líneas vacías
                self.current_line += 1
                continue
            self.process_line(line)
        self.finished_signal.emit()

    def process_line(self, line):
        """
        Procesa cada línea del código intermedio.
        """
        if line.startswith("cin >>"):
            var = line.split(">>")[1].strip()
            self.request_input_signal.emit(var)
            self.waiting_for_input = True

            # Esperar la entrada del usuario
            while self.waiting_for_input:
                self.msleep(100)

            try:
                value = self.input_received
                
                # Asignar el valor directamente a la tabla de símbolos
                self.symbol_table[var] = value

                #write_to_results_panel(f"DEBUG: {var} = {self.symbol_table[var]}")
            except Exception as e:
                # Mostrar mensaje de error y asignar un valor predeterminado
                write_to_results_panel(f"Error al ingresar valor para '{var}': {e}")
                self.symbol_table[var] = 0  # Asignar un valor predeterminado
            self.current_line += 1



        elif line.startswith("cout <<"):
            var = line.split("<<", 1)[1].strip()
            self.handle_output(var)
            self.current_line += 1

        elif "=" in line and not line.startswith("cout <<"):
            var, expr = line.split("=", 1)
            var = var.strip()
            expr = expr.strip()
            self.symbol_table[var] = self.evaluate_expression(expr)
            self.current_line += 1

        elif "=" in line and "==" in line:
            # Comparaciones de igualdad
            var, expr = line.split("=", 1)
            var = var.strip()
            expr = expr.strip()

            if "==" in expr:
                left, right = expr.split("==")
                left_value = self.symbol_table.get(left.strip(), "")
                right_value = right.strip().strip('"')  # Eliminar comillas de la cadena
                result = left_value == right_value

            self.symbol_table[var] = result
            #write_to_results_panel(f"DEBUG: {var} = {result}")
            self.current_line += 1



        elif "=" in line and (">=" in line or ">" in line or "==" in line):  # Comparaciones simples
            var, expr = line.split("=", 1)
            var = var.strip()
            expr = expr.strip()

            if "==" in expr:  # Comparación de igualdad
                left, right = expr.split("==")
                left_value = self.symbol_table.get(left.strip(), "")
                right_value = right.strip().strip('"')  # Eliminar comillas
                result = left_value == right_value
            elif ">=" in expr:  # Comparación >=
                left, right = expr.split(">=")
                left_value = self.symbol_table.get(left.strip(), 0)
                right_value = float(right.strip())
                result = left_value >= right_value
            elif ">" in expr:  # Comparación >
                left, right = expr.split(">")
                left_value = self.symbol_table.get(left.strip(), 0)
                right_value = float(right.strip())
                result = left_value > right_value

            # Guardar el resultado en la tabla de símbolos
            self.symbol_table[var] = result
            #write_to_results_panel(f"DEBUG: {var} = {result}")
            self.current_line += 1





        elif "if not" in line:
            condition = line.split("if not")[1].split("goto")[0].strip()
            label = line.split("goto")[1].strip()
            condition_value = not bool(self.symbol_table.get(condition, False))
            if condition_value:
                self.current_line = self.labels[label]
                return
            self.current_line += 1

        elif "if" in line and "goto" in line:  # Condicionales con saltos
            condition, label = line.split("goto")
            condition = condition.split("if")[-1].strip()
            label = label.strip()

            # Evaluar la condición
            condition_value = self.symbol_table.get(condition, False)
           #write_to_results_panel(f"DEBUG: Evaluando '{condition}' -> {condition_value}")

            if condition_value and label in self.labels:
                self.current_line = self.labels[label]
            else:
                self.current_line += 1

        elif "goto" in line:  # Saltos incondicionales
            label = line.split("goto")[1].strip()
            if label in self.labels:
                #write_to_results_panel(f"DEBUG: Saltando a {label}")
                self.current_line = self.labels[label]
            else:
                #write_to_results_panel(f"Error: Etiqueta '{label}' no encontrada.")
                self.current_line += 1

        elif "=" in line and (">=" in line or ">" in line or "==" in line):  # Comparaciones simples
            var, expr = line.split("=", 1)
            var = var.strip()
            expr = expr.strip()

            if "==" in expr:  # Comparación de igualdad
                left, right = expr.split("==")
                left_value = self.symbol_table.get(left.strip(), "")
                right_value = right.strip()
                result = left_value == right_value
            elif ">=" in expr:  # Comparación >=
                left, right = expr.split(">=")
                left_value = self.symbol_table.get(left.strip(), 0)
                right_value = float(right.strip())
                result = left_value >= right_value
            elif ">" in expr:  # Comparación >
                left, right = expr.split(">")
                left_value = self.symbol_table.get(left.strip(), 0)
                right_value = float(right.strip())
                result = left_value > right_value

            # Guardar el resultado en la tabla de símbolos
            self.symbol_table[var] = result
            #write_to_results_panel(f"DEBUG: {var} = {result}")
            self.current_line += 1


        elif "=" in line and "and" in line:  # Manejo de condiciones compuestas con `and`
            var, expr = line.split("=", 1)
            var = var.strip()
            expr = expr.strip()

            # Dividir las subcondiciones
            conditions = expr.split("and")
            result = True  # Inicializar como `True` para combinar resultados
            for condition in conditions:
                condition = condition.strip()

                # Evaluar cada subcondición
                if "==" in condition:  # Comparación de igualdad
                    left, right = condition.split("==")
                    left_value = self.symbol_table.get(left.strip(), "")
                    right_value = right.strip().strip('"')  # Eliminar comillas de la cadena
                    sub_result = left_value == right_value
                elif ">=" in condition:  # Comparación >=
                    left, right = condition.split(">=")
                    left_value = self.symbol_table.get(left.strip(), 0)
                    right_value = float(right.strip())
                    sub_result = left_value >= right_value
                elif ">" in condition:  # Comparación >
                    left, right = condition.split(">")
                    left_value = self.symbol_table.get(left.strip(), 0)
                    right_value = float(right.strip())
                    sub_result = left_value > right_value
                else:  # Manejar variables booleanas o numéricas simples
                    sub_result = bool(self.symbol_table.get(condition.strip(), False))

                # Combinar resultados parciales
                result = result and sub_result
                #write_to_results_panel(f"DEBUG: Subcondición '{condition}' -> {sub_result}")

            # Guardar el resultado final en la tabla de símbolos
            self.symbol_table[var] = result
            #write_to_results_panel(f"DEBUG: {var} = {result}")
            self.current_line += 1


        else:
            write_to_results_panel(f"Error: Línea no reconocida -> {line}")
            self.current_line += 1

    def handle_output(self, var):
        """
        Maneja la salida de datos (cout).
        """
        if var.startswith('"') and var.endswith('"'):
            write_to_results_panel(var.strip('"'))
        elif var in self.symbol_table:
            write_to_results_panel(f"{var} = {self.symbol_table[var]}")
        else:
            write_to_results_panel(f"Error: '{var}' no está definido.")

    def evaluate_expression(self, expr):
        """
        Evalúa una expresión matemática simple utilizando la tabla de símbolos.
        """
        try:
            for var in self.symbol_table:
                expr = expr.replace(var, str(self.symbol_table[var]))
            return eval(expr)
        except Exception as e:
            write_to_results_panel(f"Error al evaluar '{expr}': {e}")
            return 0

    def receive_input(self, value):
        """
        Recibe el valor ingresado por el usuario y continúa la ejecución.
        """
        self.input_received = value
        self.waiting_for_input = False

# Función global para abrir un cuadro de diálogo y solicitar un valor
def request_input(variable_name):
    """
    Solicita un valor al usuario mediante un cuadro de diálogo.

    Args:
        variable_name (str): Nombre de la variable solicitada.

    Returns:
        str: Valor ingresado por el usuario.
    """
    value, ok = QInputDialog.getText(None, "Ingreso de Valor", f"Ingrese el valor para '{variable_name}':")
    if ok and value:
        return value
    return "0"  # Valor predeterminado si el usuario cancela
