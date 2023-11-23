import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, 
                             QMessageBox, QVBoxLayout, QWidget, QLabel)
import main  
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt

class DataProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.csv_file_path = None
        self.db_file_path = None
        self.xlsx_file_path = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Data Processor App')
        self.setGeometry(300, 300, 500, 300)

        layout = QVBoxLayout()

        # Labels to display selected file paths
        self.lbl_csv_path = QLabel(self.format_label('CSV', None))
        layout.addWidget(self.lbl_csv_path)

        self.lbl_db_path = QLabel(self.format_label('Database', None))
        layout.addWidget(self.lbl_db_path)

        self.lbl_xlsx_path = QLabel(self.format_label('XLSX', None))
        layout.addWidget(self.lbl_xlsx_path)

        # Select CSV Button with Icon
        btn_select_csv = QPushButton('', self)
        btn_select_csv.setIcon(QIcon('icons/csv_icon.png'))
        btn_select_csv.setIconSize(QSize(40, 40))
        btn_select_csv.setToolTip('Select a CSV file to process') 
        btn_select_csv.clicked.connect(self.select_csv)  # Connect to select_csv method
        layout.addWidget(btn_select_csv)

        # Select/Create Database Button with Icon
        btn_select_db = QPushButton('', self)
        btn_select_db.setIcon(QIcon('icons/db_icon.png'))
        btn_select_db.setIconSize(QSize(40, 40))
        btn_select_db.setToolTip('Select or create a database file')
        btn_select_db.clicked.connect(self.select_database)  # Connect to select_database method
        layout.addWidget(btn_select_db)

        # Process Button with Icon
        btn_process = QPushButton('', self)
        btn_process.setIcon(QIcon('icons/process_icon.png'))
        btn_process.setIconSize(QSize(40, 40))
        btn_process.setToolTip('Process the selected Data')
        btn_process.clicked.connect(self.process_data)  # Connect to process_data method
        layout.addWidget(btn_process)

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
        self.lbl_csv_path.setText(self.format_label('CSV', self.csv_file_path))

    def select_database(self):
        choice = QMessageBox.question(self, 'Database Selection', 'Do you want to create a new database?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if choice == QMessageBox.Yes:
            self.db_file_path, _ = QFileDialog.getSaveFileName(self, "Create Database File", "", "SQLite Database Files (*.db)")
            if self.db_file_path:
                base, _ = os.path.splitext(self.db_file_path)
                self.xlsx_file_path = base + '.xlsx'
        else:
            self.db_file_path, _ = QFileDialog.getOpenFileName(self, "Select Database File", "", "SQLite Database Files (*.db)")
            if self.db_file_path:
                self.xlsx_file_path, _ = QFileDialog.getOpenFileName(self, "Select XLSX File", "", "Excel Files (*.xlsx)")
        
        self.lbl_db_path.setText(self.format_label('Database', self.db_file_path))
        self.lbl_xlsx_path.setText(self.format_label('XLSX', self.xlsx_file_path))

    def process_data(self):
        if not all([self.csv_file_path, self.db_file_path, self.xlsx_file_path]):
            QMessageBox.critical(self, "Error", "Please select all files")
            return

        try:
            main.main_process(self.csv_file_path, self.db_file_path, self.xlsx_file_path)
            QMessageBox.information(self, "Success", "Data processed successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

def main_gui():
    app = QApplication(sys.argv)
    ex = DataProcessorApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main_gui()