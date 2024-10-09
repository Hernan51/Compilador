"""
File that contains the dock panels of the application
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow,
    QTextBrowser,
    QDockWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QTableWidget,
    QTableWidgetItem
)


lexer = []  # List to store the widgets of the lexer dock panel
syntactic = []  # List to store the widgets of the syntactic dock panel
semantic = []
hash_table = []  


def set_up_dock_panels(window: QMainWindow):
    """
    Sets up the dock panels of the window

    Args:
        window (QMainWindow): The window where the dock panels will be added

    Returns:
        None
    """

    # Panel for the Lexical Analysis
    lexer_panel = QDockWidget("Lexico", window)
    lexer_panel.setStyleSheet(open("./src/css/style.css", encoding="utf-8").read())
    lexer_widget = QTextBrowser()
    lexer_widget.setStyleSheet(open("./src/css/style.css", encoding="utf-8").read())
    lexer.append(lexer_widget)
    lexer_panel.setWidget(lexer_widget)
    window.addDockWidget(Qt.BottomDockWidgetArea, lexer_panel)

    # Panel for the Sintactic Analysis
    sintactic_panel = QDockWidget("Sintactico", window)
    sintactic_panel.setStyleSheet(open("./src/css/style.css", encoding="utf-8").read())
    sintactic_widget = QTreeWidget()
    sintactic_widget.setStyleSheet(open("./src/css/style.css", encoding="utf-8").read())
    sintactic_widget.setHeaderHidden(True)
    syntactic.append(sintactic_widget)
    sintactic_panel.setWidget(sintactic_widget)
    window.addDockWidget(Qt.BottomDockWidgetArea, sintactic_panel)

    # Panel for the Semantic Analysis
    # Panel for the Semantic Analysis
    semantic_panel = QDockWidget("Semantico", window)
    semantic_panel.setStyleSheet(open("./src/css/style.css", encoding="utf-8").read())
    semantic_widget = QTreeWidget()  # Cambiado a QTreeWidget para mostrar árboles
    semantic_widget.setStyleSheet(open("./src/css/style.css", encoding="utf-8").read())
    semantic_widget.setHeaderHidden(True)
    semantic.append(semantic_widget)  # Añadir a la lista 'semantic'
    semantic_panel.setWidget(semantic_widget)
    window.addDockWidget(Qt.BottomDockWidgetArea, semantic_panel)


    # Panel for the Hash Table
    hash_table_panel = QDockWidget("Hash Table", window)
    hash_table_panel.setStyleSheet(open("./src/css/style.css", encoding="utf-8").read())
    hash_table_widget = QTableWidget()  # Cambia de QTextBrowser a QTableWidget
    hash_table_widget.setColumnCount(5)  # Define el número de columnas
    hash_table_widget.setHorizontalHeaderLabels(["Variable", "Type", "Value", "LOC", "Lines"])  # Etiquetas de las columnas
        # Ajustar el ancho de cada columna de forma individual
    hash_table_widget.setColumnWidth(0, 150)  # Ancho para la columna "Variable"
    hash_table_widget.setColumnWidth(1, 100)  # Ancho para la columna "Type"
    hash_table_widget.setColumnWidth(2, 140)  # Ancho para la columna "Value"
    hash_table_widget.setColumnWidth(3, 80)   # Ancho para la columna "LOC"
    hash_table_widget.setColumnWidth(4, 250)  # Ancho para la columna "Lines"

    hash_table_widget.setStyleSheet(open("./src/css/style.css", encoding="utf-8").read())
    hash_table_panel.setWidget(hash_table_widget)
    window.addDockWidget(Qt.BottomDockWidgetArea, hash_table_panel)

    # Añadir el widget a una lista global si es necesario (por ejemplo, para acceder desde otras funciones)
    hash_table.append(hash_table_widget)


    # Panel for the Intermediate Code
    intermediate_code_panel = QDockWidget("Codigo Intermedio", window)
    intermediate_code_panel.setStyleSheet(
        open("./src/css/style.css", encoding="utf-8").read()
    )
    intermediate_code_widget = QTextBrowser()
    intermediate_code_widget.setStyleSheet(
        open("./src/css/style.css", encoding="utf-8").read()
    )
    intermediate_code_panel.setWidget(intermediate_code_widget)
    window.addDockWidget(Qt.BottomDockWidgetArea, intermediate_code_panel)

    # Panel for the Results
    results_panel = QDockWidget("Resultados", window)
    results_panel.setStyleSheet(open("./src/css/style.css", encoding="utf-8").read())
    results_widget = QTextBrowser()
    results_widget.setStyleSheet(open("./src/css/style.css", encoding="utf-8").read())
    results_panel.setWidget(results_widget)
    window.addDockWidget(Qt.BottomDockWidgetArea, results_panel)

    # panel for the Lexical Errors
    lexic_err_panel = QDockWidget("Err. Lexicos", window)
    lexic_err_panel.setStyleSheet(open("./src/css/style.css", encoding="utf-8").read())
    lexic_err_widget = QTextBrowser()
    lexer.append(lexic_err_widget)
    lexic_err_widget.setStyleSheet(open("./src/css/style.css", encoding="utf-8").read())
    lexic_err_panel.setWidget(lexic_err_widget)
    window.addDockWidget(Qt.BottomDockWidgetArea, lexic_err_panel)

    # Panel for the Sintactic Errors
    sintactic_err_panel = QDockWidget("Err. Sintacticos", window)
    sintactic_err_panel.setStyleSheet(
        open("./src/css/style.css", encoding="utf-8").read()
    )
    sintactic_err_widget = QTextBrowser()
    sintactic_err_widget.setStyleSheet(
        open("./src/css/style.css", encoding="utf-8").read()
    )
    sintactic_err_panel.setWidget(sintactic_err_widget)
    window.addDockWidget(Qt.BottomDockWidgetArea, sintactic_err_panel)

    # Panel for the Semantic Errors
    semantic_err_panel = QDockWidget("Err. Semanticos", window)
    semantic_err_panel.setStyleSheet(
        open("./src/css/style.css", encoding="utf-8").read()
    )
    semantic_err_widget = QTextBrowser()
    semantic_err_widget.setStyleSheet(
        open("./src/css/style.css", encoding="utf-8").read()
    )
    semantic_err_panel.setWidget(semantic_err_widget)
    window.addDockWidget(Qt.BottomDockWidgetArea, semantic_err_panel)

    window.tabifyDockWidget(lexer_panel, sintactic_panel)
    window.tabifyDockWidget(sintactic_panel, semantic_panel)
    window.tabifyDockWidget(semantic_panel, hash_table_panel)
    window.tabifyDockWidget(hash_table_panel, intermediate_code_panel)
    window.tabifyDockWidget(intermediate_code_panel, results_panel)
    window.tabifyDockWidget(results_panel, lexic_err_panel)
    window.tabifyDockWidget(lexic_err_panel, sintactic_err_panel)
    window.tabifyDockWidget(sintactic_err_panel, semantic_err_panel)

    # Allow the user to drag out the dock widgets
    window.setDockOptions(QMainWindow.AllowTabbedDocks | QMainWindow.AllowNestedDocks)


def set_lexical_analysis_result(results: list[str]):
    """Set the results of the lexical analysis in the dock panel"""
    tokens = ""
    errors = ""
    for element in results[0]:
        tokens += f"{element}\n"
    for element in results[1]:
        errors += f"{element}\n"
    lexer[0].setText(tokens)
    lexer[1].setText(errors)


def set_syntactic_analysis_result(ast):
    """Set the results of the sintactic analysis in the dock panel"""
    syntactic[0].clear()
    root_item = QTreeWidgetItem(syntactic[0], [ast.value])
    for child in ast.children:
        add_tree_item(root_item, child)
        syntactic[0].expandAll()

def set_semantic_analysis_result(ast):
    """Set the results of the semantic analysis in the dock panel as a collapsible tree."""
    if len(semantic) > 0:
        semantic[0].clear()  # Limpiar el contenido del panel semántico
        
        # Crear el nodo raíz con el nombre del programa
        root_item = QTreeWidgetItem(semantic[0], [ast.name])
        
        # Función recursiva para agregar nodos hijos
        def add_tree_items(parent_item, node):
            # Crear un nodo hijo para cada hijo del nodo actual
            for child in node.children:
                child_item = QTreeWidgetItem(parent_item, [child.name])

                # Verificar si el nodo tiene un tipo y valor antes de añadirlos
                if hasattr(child, 'type') and child.type is not None:
                    type_item = QTreeWidgetItem(child_item, [f"Type: {child.type}"])
                if hasattr(child, 'value') and child.value is not None:
                    value_item = QTreeWidgetItem(child_item, [f"Value: {child.value}"])

                # Llamada recursiva para agregar los nodos hijos de este nodo
                add_tree_items(child_item, child)
        
        # Llamada para agregar los nodos hijos desde la raíz
        add_tree_items(root_item, ast)
        
        # Expander todos los nodos del árbol para visualizarlos
        semantic[0].expandAll()
    else:
        print("Error: 'semantic' panel not initialized.")


def set_hash_table(symbols):
    """
    Actualiza la UI con el contenido de la tabla de símbolos.
    """
    # Calcular el número de filas
    hash_table[0].setRowCount(sum(len(entry) for entry in symbols.values()))
    
    idx = 0  # Índice de fila en la tabla

    # Iterar sobre los símbolos y sus posibles colisiones
    for var_name, symbol_list in symbols.items():
        for symbol in symbol_list:  # symbol_list es la lista de colisiones
            # Verificar si el símbolo es un diccionario
            if not isinstance(symbol, dict):
                raise TypeError(f"Se esperaba un diccionario en 'symbol', pero se obtuvo {type(symbol).__name__}")

            # Verificar que el símbolo tiene los campos requeridos
            if 'type' not in symbol or 'value' not in symbol or 'loc' not in symbol or 'lines' not in symbol:
                raise KeyError(f"Faltan campos en el símbolo '{var_name}'. Se esperaban 'type', 'value', 'loc', y 'lines'.")

            # variable name
            hash_table[0].setItem(idx, 0, QTableWidgetItem(var_name))
            hash_table[0].setItem(idx, 1, QTableWidgetItem(symbol["type"]))
            hash_table[0].setItem(idx, 2, QTableWidgetItem(str(symbol["value"])))
            hash_table[0].setItem(idx, 3, QTableWidgetItem(str(symbol["loc"])))

            # Validar y agregar las líneas
            valid_lines = [str(line) for line in symbol["lines"] if line is not None]
            hash_table[0].setItem(idx, 4, QTableWidgetItem(", ".join(valid_lines)))
            
            idx += 1  # Incrementar el índice de fila












def add_tree_item(parent, node):
    """Add a tree item to the tree widget"""
    item = QTreeWidgetItem(parent, [node.value])
    for child in node.children:
        add_tree_item(item, child)
    return item
