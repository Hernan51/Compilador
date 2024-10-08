"""Main file of the application."""

import sys
import re
import os
from pathlib import Path
from parser_s import Parser
from lexer import get_lexical_analysis

from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QFrame,
    QHBoxLayout,
    QSizePolicy,
    QSplitter,
    QFileSystemModel,
    QTreeView,
    QVBoxLayout,
    QTabWidget,
    QFileDialog,
    QLabel,
)
from PyQt5.QtCore import Qt, QDir, QModelIndex
from PyQt5.QtGui import QFont
from PyQt5.Qsci import QsciScintilla
from anytree import RenderTree

from symbol_table import fill_symbol_table  # Reemplaza symbol_table_module con el archivo correcto
from symbol_table import SymbolTable  # Asegúrate de que el archivo y ruta sean correctos


from components.editor import Editor
from components.menu import set_up_menu
from components.dock_panels import (
    set_up_dock_panels,
    set_lexical_analysis_result,
    set_syntactic_analysis_result,
    set_semantic_analysis_result,
    set_hash_table
)
from components.side_bar import set_up_sidebar


class MainWindow(QMainWindow):
    """Main window of the application."""

    def __init__(self):  # Constructor
        super().__init__()  # Call the constructor of the parent class

        self.hsplit = QSplitter(Qt.Horizontal)  # Create a horizontal splitter
        self.tree_frame = QFrame()  # Create a frame to hold the tree view
        self.model = QFileSystemModel()  # Create a file system model
        self.tree_view = QTreeView()  # Create a tree view
        self.tab_view = QTabWidget()  # Create a tab view
        self.cursor_info_label = QLabel(
            "Line: , Column: "
        )  # Create a label to show the cursor position

        self.current_file = None  # Variable to store the current file

        self.init_ui()  # Call the method to initialize the UI

    def init_ui(self):
        """Initialize the UI of the window."""
        self.setWindowTitle("IDE")  # Set the title of the window
        self.resize(1100, 900)  # Set the size of the window

        self.window_font = QFont("Monospace", 12)  # Set the font of the window
        self.setFont(self.window_font)  # Set the font of the window

        self.setStyleSheet(open("./src/css/style.css", encoding="utf-8").read())

        set_up_menu(self)

        self.set_up_body()

        set_up_dock_panels(self)

        self.show()

    def get_editor(self) -> QsciScintilla:
        """Get the editor widget."""
        editor = Editor()
        editor.cursorPositionChangedSignal.connect(self.get_current_line_column)
        return editor

    def set_new_tab(self, path: Path, is_new_file=False):
        """Set a new tab with the editor."""
        editor = self.get_editor()

        if is_new_file:
            self.tab_view.addTab(editor, f"Untitled-{self.tab_view.count() + 1}")
            self.setWindowTitle("Untitled")
            self.statusBar().showMessage("New file created", 2000)
            self.tab_view.setCurrentIndex(self.tab_view.count() - 1)
            self.current_file = None
            return

        if not path.is_file():
            return
        if self.is_binary(path):
            self.statusBar().showMessage("Cannot open binary files", 2000)
            return

        # Check if the file is already open
        for i in range(self.tab_view.count()):
            if self.tab_view.tabText(i) == path.name:
                self.tab_view.setCurrentIndex(i)
                self.current_file = path
                return

        # Create new tab
        self.tab_view.addTab(editor, path.name)
        if not is_new_file:
            with open(path, "r", encoding="utf-8") as file:
                editor.setText(file.read())
        self.setWindowTitle(path.name)
        self.current_file = path
        self.tab_view.setCurrentIndex(self.tab_view.count() - 1)
        self.statusBar().showMessage(f"Opened {path}", 2000)

    def is_binary(self, path: Path) -> bool:
        """Check if a file is binary (e.g. image, video, etc.)"""
        with open(path, "rb") as file:
            return b"\0" in file.read(1024)  # Check for null bytes

    def new_file(self):
        """Create a new file."""
        self.set_new_tab(None, is_new_file=True)

    def open_file(self):
        """Open a file."""
        ops = QFileDialog.Options()  # Create a file dialog
        # ops |= QFileDialog.DontUseNativeDialog
        new_file, _ = QFileDialog.getOpenFileName(
            self, "Pick a file", "", "All Files (*)", options=ops
        )

        if new_file == "":
            self.statusBar().showMessage("Cancelled", 2000)
            return
        f = Path(new_file)
        self.set_new_tab(f)

    def save_file(self):
        """Save the current file."""
        if self.current_file is None and self.tab_view.count() > 0:
            self.save_as()

        if self.tab_view.count() > 0:
            editor = self.tab_view.currentWidget()
            self.current_file.write_text(editor.text(), encoding="utf-8")
            self.statusBar().showMessage(f"Saved {self.current_file}", 2000)

    def save_as(self):
        """Save the current file as a new file."""
        editor = self.tab_view.currentWidget()
        if editor is None:
            return

        file_path = QFileDialog.getSaveFileName(self, "Save as", os.getcwd())[0]
        if file_path == "":
            self.statusBar().showMessage("Cancelled", 2000)
            return
        path = Path(file_path)
        path.write_text(editor.text(), encoding="utf-8")
        self.tab_view.setTabText(self.tab_view.currentIndex(), path.name)
        self.statusBar().showMessage(f"Saved {path}", 2000)
        self.current_file = path

    def open_folder(self):
        """Open a folder in the file explorer."""
        ops = QFileDialog.Options()  # Create a file dialog
        ops |= QFileDialog.DontUseNativeDialog

        new_folder = QFileDialog.getExistingDirectory(
            self, "Pick a folder", "", options=ops
        )
        if new_folder:
            self.model.setRootPath(new_folder)
            self.tree_view.setRootIndex(self.model.index(new_folder))
            self.statusBar().showMessage(f"Opened {new_folder}", 2000)

    def copy(self):
        """Copy the selected text to the clipboard."""
        editor = self.tab_view.currentWidget()
        if editor is None:
            return
        editor.copy()

    


    def compile(self):
        """Compile the current file."""
        loc = 0  # Inicializa el LOC al inicio de la compilación

        if self.current_file is not None:
            # Realizar análisis léxico
            tkns, errs = get_lexical_analysis(self.current_file)
            set_lexical_analysis_result((tkns, errs))
            if self.current_file is not None:
                # Obtener las líneas de código enumeradas
                code_lines = enumerate_code_lines(self.current_file)

                # Imprimir las líneas de código enumeradas
                print("Líneas de código:")
                for line_num, code in code_lines.items():
                    print(f"Línea {line_num}: {code}")
            
            # Verificar si no hubo errores léxicos
            if errs == []:
                # Realizar análisis sintáctico y guardar el resultado en 'ast'
                parser = Parser(tkns)
                ast = parser.parse()
                
                # Mostrar el resultado sintáctico en el panel
                set_syntactic_analysis_result(ast)

                set_semantic_analysis_result(ast)

                # Renderizar el árbol sintáctico como una cadena
                tree_str = parser.render_tree(ast)
                print(tree_str)
                print("ast",ast)
                # Crear la tabla de símbolos
                symbol_table = SymbolTable()
                assign_lines = self.extract_assignment_lines(tkns)
                fill_symbol_table(ast, symbol_table,assign_lines)

                symbols = symbol_table.get_symbols()
                #print("symbols",symbols)
                #print("Tabla de símbolos generada:", symbols)
                # Mostrar la tabla de símbolos en el panel
                set_hash_table(symbols)

                
                # Mostrar el árbol sintáctico en consola (para depuración)
                #print(tree_str)

                # Indicar que la compilación fue exitosa
                self.statusBar().showMessage("Compilation successful", 2000)
            else:
                # Mostrar mensaje de error si hubo fallos en el análisis léxico
                self.statusBar().showMessage("Compilation failed due to lexical errors", 2000)

    
    def analyze_semantics(self, syntactic_result):
        """Genera el árbol semántico anotado a partir del resultado sintáctico."""
        tree_str = ""
        for pre, _, node in RenderTree(syntactic_result):
            tree_str += "%s%s\n" % (pre, node)
        return tree_str
    
    


    def close_tab(self, index):
        """Close the tab at the given index."""
        self.tab_view.removeTab(index)
        if self.tab_view.count() == 0:
            self.setWindowTitle("IDE")
            self.current_file = None

    def tree_view_clicked(self, index: QModelIndex):
        """Handle the click event on the tree view."""
        path = self.model.filePath(index)
        self.set_new_tab(Path(path))

    def get_current_line_column(self, line, index):
        """Get the current line and column of the cursor."""
        self.cursor_info_label.setText(f"Line: {1+line}, Column: {1+index}")

    def set_up_body(self):
        """Set up the body of the window."""
        # Body

        body_frame = QFrame()
        body_frame.setFrameShape(QFrame.NoFrame)
        body_frame.setFrameShadow(QFrame.Plain)
        body_frame.setLineWidth(0)
        body_frame.setMidLineWidth(0)
        body_frame.setContentsMargins(0, 0, 0, 0)
        body_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body_frame.setLayout(body)

        set_up_sidebar(self, body)

        body.addWidget(self.side_bar)

        # Split View

        # frame and layout to hold tree view (file explorer)
        self.tree_frame.setLineWidth(1)
        self.tree_frame.setMaximumWidth(400)
        self.tree_frame.setMinimumWidth(200)
        self.tree_frame.setBaseSize(100, 0)
        self.tree_frame.setContentsMargins(0, 0, 0, 0)
        tree_frame_layout = QVBoxLayout()
        tree_frame_layout.setContentsMargins(0, 0, 0, 0)
        tree_frame_layout.setSpacing(0)
        self.tree_frame.setStyleSheet(
            """
            QFrame {
            background-color: #21252b;
            border: none;
            padding: 5px;
            color: #D3D3D3;
            }
            QFrame:hover {
                color: white;
            }
            """
        )

        # Create file system model to show in tree view
        self.model.setRootPath(os.getcwd())

        # File system filters
        self.model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)

        # Tree View
        self.tree_view.setFont(self.window_font)
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(os.getcwd()))
        self.tree_view.setSelectionMode(QTreeView.SingleSelection)
        self.tree_view.setSelectionBehavior(QTreeView.SelectRows)
        self.tree_view.setEditTriggers(QTreeView.NoEditTriggers)

        # Context menu
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)

        # Handling click
        self.tree_view.clicked.connect(self.tree_view_clicked)
        self.tree_view.setIndentation(10)
        self.tree_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Hide header and hide other columns except for name
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setColumnHidden(1, True)
        self.tree_view.setColumnHidden(2, True)
        self.tree_view.setColumnHidden(3, True)

        # setup layout
        tree_frame_layout.addWidget(self.tree_view)
        self.tree_frame.setLayout(tree_frame_layout)

        # Tab widget to add editor to
        self.tab_view.setContentsMargins(0, 0, 0, 0)
        self.tab_view.setTabsClosable(True)
        self.tab_view.setMovable(True)
        self.tab_view.setDocumentMode(True)
        self.tab_view.tabCloseRequested.connect(self.close_tab)

        # Add tree view and tab view to split view
        self.hsplit.addWidget(self.tree_frame)
        self.hsplit.addWidget(self.tab_view)

        # Add cursor info label to status bar (permanent widget)
        self.statusBar().addPermanentWidget(self.cursor_info_label)

        body.addWidget(self.hsplit)
        body_frame.setLayout(body)

        self.setCentralWidget(body_frame)
    
    def extract_assignment_lines(self, tokens):
        """
        Extrae las líneas donde ocurren las asignaciones (ASSIGN) a partir del análisis léxico.
        """
        assign_lines = {}
        current_var = None

        for token in tokens:
            if token.type == "IDENTIFIER":
                # Almacenar el identificador actual para asociarlo con la siguiente asignación
                current_var = token.value
            elif token.type == "ASSIGN" and current_var is not None:
                # Guardar la línea de la asignación para la variable actual
                assign_lines[current_var] = token.lineno
                current_var = None  # Reiniciar la variable actual

        return assign_lines

    

def extract_symbols_from_tree(tree_str):
        """
        Procesa el tree_str para extraer los símbolos (variables, tipos, valores).
        """
        symbol_table = {}

        # Expresiones regulares para capturar los diferentes elementos del árbol
        variable_decl_pattern = re.compile(r'VariableDeclaration \(Type: Variable, Value: (\w+)\)')
        identifier_pattern = re.compile(r'Identifier \(Type: Variable, Value: (\w+)\)')
        assignment_pattern = re.compile(r'Assignment \(Type: Assignment, Value: =\)')
        number_pattern = re.compile(r'Number \(Type: Literal, Value: ([\d\.]+)\)')
        
        lines = tree_str.split('\n')  # Dividir el tree_str en líneas

        current_type = None
        current_assignment = None
        
        for line in lines:
            # Detectar una declaración de variable
            match_decl = variable_decl_pattern.search(line)
            if match_decl:
                current_type = match_decl.group(1)
                continue
            
            # Detectar un identificador
            match_id = identifier_pattern.search(line)
            if match_id:
                var_name = match_id.group(1)
                if var_name not in symbol_table:
                    symbol_table[var_name] = {'type': current_type, 'value': None, 'loc': len(symbol_table), 'lines': []}
            
            # Detectar una asignación
            match_assign = assignment_pattern.search(line)
            if match_assign:
                current_assignment = True
                
                continue

            # Detectar un valor literal en una asignación
            match_number = number_pattern.search(line)
            if match_number and current_assignment:
                value = float(match_number.group(1))
                last_var = list(symbol_table.keys())[-1]
                symbol_table[last_var]['value'] = value
                current_assignment = False  # Terminar la asignación

        return symbol_table

def enumerate_code_lines(file_path):
        """
        Lee un archivo y devuelve un diccionario con el número de línea como clave y
        la línea de código correspondiente como valor.
        
        Args:
        - file_path: La ruta al archivo de código fuente (self.current_file)
        
        Returns:
        - Un diccionario con el número de línea como clave y el contenido de la línea como valor.
        """
        code_lines = {}
        
        try:
            with open(file_path, 'r') as f:
                for line_number, line in enumerate(f, start=1):
                    code_lines[line_number] = line.strip()
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {file_path}")
        
        return code_lines
    
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    sys.exit(app.exec())
