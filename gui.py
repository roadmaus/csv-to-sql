import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, 
                             QMessageBox, QVBoxLayout, QWidget, QLabel)
import main  

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
        self.lbl_csv_path = QLabel('Selected CSV File: None', self)
        layout.addWidget(self.lbl_csv_path)

        self.lbl_db_path = QLabel('Selected Database File: None', self)
        layout.addWidget(self.lbl_db_path)

        self.lbl_xlsx_path = QLabel('Selected XLSX File: None', self)
        layout.addWidget(self.lbl_xlsx_path)

        # Select CSV Button
        btn_select_csv = QPushButton('Select CSV File', self)
        btn_select_csv.clicked.connect(self.select_csv)
        layout.addWidget(btn_select_csv)

        # Select/Create Database Button
        btn_select_db = QPushButton('Select/Create Database', self)
        btn_select_db.clicked.connect(self.select_database)
        layout.addWidget(btn_select_db)

        # Process Button
        btn_process = QPushButton('Process Data', self)
        btn_process.clicked.connect(self.process_data)
        layout.addWidget(btn_process)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_csv(self):
        self.csv_file_path, _ = QFileDialog.getOpenFileName(self, 'Open CSV File', '', 'CSV files (*.csv)')
        self.lbl_csv_path.setText(f'Selected CSV File: {self.csv_file_path}')

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
        
        self.lbl_db_path.setText(f'Selected Database File: {self.db_file_path}')
        self.lbl_xlsx_path.setText(f'Selected XLSX File: {self.xlsx_file_path}')

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