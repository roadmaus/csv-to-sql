import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, 
                             QMessageBox, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QTextEdit)
import main  
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor
import pickle
from PyQt5.QtWidgets import QGridLayout


class Worker(QThread):
    progress = pyqtSignal(str)
    error = pyqtSignal(str)
    success = pyqtSignal()
    failure = pyqtSignal()

    def __init__(self, csv_file_path, db_file_path, xlsx_file_path):
        super().__init__()
        self.csv_file_path = csv_file_path
        self.db_file_path = db_file_path
        self.xlsx_file_path = xlsx_file_path

    def run(self):
        try:
            main.main_process(self.csv_file_path, self.db_file_path, self.xlsx_file_path, self.progress.emit)
            self.success.emit()
        except Exception as e:
            self.error.emit(f"<font color='red'>An error occurred: {e}</font>")
            self.failure.emit()

class DataProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.csv_file_path = None
        self.db_file_path = None
        self.xlsx_file_path = None
        self.initUI()
        self.load_paths()

    def save_paths(self):
        with open('paths.pkl', 'wb') as f:
            pickle.dump((self.db_file_path, self.xlsx_file_path), f)

    def load_paths(self):
        try:
            with open('paths.pkl', 'rb') as f:
                self.db_file_path, self.xlsx_file_path = pickle.load(f)
                self.lbl_db_path.setText(self.format_label('Database', self.db_file_path))
                self.lbl_xlsx_path.setText(self.format_label('XLSX', self.xlsx_file_path))
                if self.db_file_path and self.xlsx_file_path:
                    self.btn_select_db.setStyleSheet("background-color: #d1ff5c;")
                if self.csv_file_path and self.db_file_path and self.xlsx_file_path:
                    self.btn_process.setStyleSheet("background-color: #5c6aff;")
        except FileNotFoundError:
            pass 

    def initUI(self):
        self.setWindowTitle('Fahrdaten-Manager')
        self.setGeometry(300, 300, 1000, 400)

        # Create a QVBoxLayout for the buttons
        button_layout = QVBoxLayout()

        # Labels to display selected file paths
        self.lbl_csv_path = QLabel(self.format_label('CSV', None))
        button_layout.addWidget(self.lbl_csv_path)

        self.lbl_db_path = QLabel(self.format_label('Database', None))
        button_layout.addWidget(self.lbl_db_path)

        self.lbl_xlsx_path = QLabel(self.format_label('XLSX', None))
        button_layout.addWidget(self.lbl_xlsx_path)

        # Select CSV Button with Icon
        self.btn_select_csv = QPushButton('', self)
        self.btn_select_csv.setIcon(QIcon('icons/csv_icon.png'))
        self.btn_select_csv.setIconSize(QSize(40, 40))
        self.btn_select_csv.setFixedSize(75, 55)  # Set the size of the button
        self.btn_select_csv.setStyleSheet("background-color: #ffd65c;")
        self.btn_select_csv.setToolTip('Wählen Sie eine CSV-Datei zur Verarbeitung aus.') 
        self.btn_select_csv.clicked.connect(self.select_csv)  # Connect to select_csv method
        button_layout.addWidget(self.btn_select_csv)

        # Select/Create Database Button with Icon
        self.btn_select_db = QPushButton('', self)
        self.btn_select_db.setIcon(QIcon('icons/db_icon.png'))
        self.btn_select_db.setIconSize(QSize(40, 40))
        self.btn_select_db.setFixedSize(75, 55) 
        self.btn_select_db.setStyleSheet("background-color: #ffd65c;")
        self.btn_select_db.setToolTip('Wählen Sie eine Datenbankdatei aus oder erstellen Sie eine.')
        self.btn_select_db.clicked.connect(self.select_database)  # Connect to select_database method
        button_layout.addWidget(self.btn_select_db)

        # Process Button with Icon
        self.btn_process = QPushButton('', self)
        self.btn_process.setIcon(QIcon('icons/process_icon.png'))
        self.btn_process.setIconSize(QSize(40, 40))
        self.btn_process.setFixedSize(75, 55)  # Set the size of the button
        self.btn_process.setStyleSheet("background-color: #808080;")  # Set the background color to grey
        self.btn_process.setToolTip('Verarbeiten Sie die ausgewählten Daten.')
        self.btn_process.clicked.connect(self.process_data)  # Connect to process_data method
        button_layout.addWidget(self.btn_process)
        
        # Create a QTextEdit for the console output
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)  # Make it read-only

        # Create a QHBoxLayout for the overall layout
        layout = QHBoxLayout()

        # Add the button layout and console output to the overall layout
        layout.addLayout(button_layout)
        layout.addWidget(self.console_output)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def format_label(self, file_type, path):
        if path:
            # File selected, show in normal text
            return f"<b>Selected {file_type} File:</b><br/><i style='font-size:8pt'>{path}</i>"
        else:
            # No file selected, show 'None' in orange
            return f"<b>Selected {file_type} File:</b> <span style='color:orange'>None</span>"

    def select_csv(self):
        self.csv_file_path, _ = QFileDialog.getOpenFileName(self, 'Open CSV File', '', 'CSV files (*.csv)')
        if self.csv_file_path:
            self.btn_select_csv.setStyleSheet("background-color: #d1ff5c;")
        self.lbl_csv_path.setText(self.format_label('CSV', self.csv_file_path))
        if self.csv_file_path and self.db_file_path and self.xlsx_file_path:
            self.btn_process.setStyleSheet("background-color: #5c6aff;")

    def select_database(self):
        choice = QMessageBox.question(self, 'Database Selection', 'Do you want to create a new database?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if choice == QMessageBox.Yes:
            self.db_file_path, _ = QFileDialog.getSaveFileName(self, "Create Database File", "", "SQLite Database Files (*.db)")
        else:
            self.db_file_path, _ = QFileDialog.getOpenFileName(self, "Select Database File", "", "SQLite Database Files (*.db)")
        
        if self.db_file_path:
            base, _ = os.path.splitext(self.db_file_path)
            self.xlsx_file_path = base + '.xlsx'
            self.btn_select_db.setStyleSheet("background-color: #d1ff5c;")
            self.lbl_db_path.setText(self.format_label('Database', self.db_file_path))
            self.lbl_xlsx_path.setText(self.format_label('XLSX', self.xlsx_file_path))
            self.save_paths()
            if self.csv_file_path and self.db_file_path and self.xlsx_file_path:
                self.btn_process.setStyleSheet("background-color: #5c6aff;")


    def process_data(self):
        if not all([self.csv_file_path, self.db_file_path, self.xlsx_file_path]):
            QMessageBox.critical(self, "Error", "Please select all files")
            return

        self.worker = Worker(self.csv_file_path, self.db_file_path, self.xlsx_file_path)
        self.worker.progress.connect(self.append_to_console)
        self.worker.error.connect(self.append_to_console)
        self.worker.start()
        self.save_paths()
        self.worker.success.connect(self.on_success)
        self.worker.failure.connect(self.on_failure)

    def on_success(self):
        self.btn_process.setStyleSheet("background-color: #82ff5c;")  # Green for success

    def on_failure(self):
        self.btn_process.setStyleSheet("background-color: #ff0000;")  # Red for failure

    def append_to_console(self, text):
        self.console_output.moveCursor(QTextCursor.End)
        self.console_output.insertHtml(text)
        self.console_output.insertPlainText("\n")  # Add a newline to separate entries
        self.console_output.moveCursor(QTextCursor.End)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DataProcessorApp()
    ex.show()
    sys.exit(app.exec_())
    