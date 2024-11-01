from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QComboBox, QPushButton,
    QWidget, QMessageBox, QLabel, QLineEdit, QHBoxLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from pymongo import MongoClient
import json
import sys


class MongoDBExporter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MongoDB Collection Exporter")
        self.setGeometry(300, 300, 500, 250)
        self.setStyleSheet("background-color: #f0f0f0;")

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        uri_label = QLabel("MongoDB URI:")
        uri_label.setFont(QFont("Arial", 12))
        self.uri_input = QLineEdit("mongodb://localhost:27017/")
        self.uri_input.setFont(QFont("Arial", 12))
        self.uri_input.setStyleSheet("padding: 5px;")

        uri_layout = QHBoxLayout()
        uri_layout.addWidget(uri_label)
        uri_layout.addWidget(self.uri_input)

        main_layout.addLayout(uri_layout)

        db_label = QLabel("Select Database:")
        db_label.setFont(QFont("Arial", 12))
        self.db_combo_box = QComboBox()
        self.db_combo_box.setFont(QFont("Arial", 12))
        self.db_combo_box.setStyleSheet("padding: 5px;")

        collection_label = QLabel("Select Collection:")
        collection_label.setFont(QFont("Arial", 12))
        self.collection_combo_box = QComboBox()
        self.collection_combo_box.setFont(QFont("Arial", 12))
        self.collection_combo_box.setStyleSheet("padding: 5px;")

        self.load_button = QPushButton("Load Databases")
        self.load_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.load_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
        self.load_button.clicked.connect(self.load_databases)

        self.start_button = QPushButton("Start Export")
        self.start_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.start_button.setStyleSheet("background-color: #2196F3; color: white; padding: 10px; border-radius: 5px;")
        self.start_button.clicked.connect(self.export_collection)

        main_layout.addWidget(db_label)
        main_layout.addWidget(self.db_combo_box)
        main_layout.addWidget(collection_label)
        main_layout.addWidget(self.collection_combo_box)
        main_layout.addWidget(self.load_button)
        main_layout.addWidget(self.start_button)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def load_databases(self):
        uri = self.uri_input.text() or 'mongodb://localhost:27017/'

        try:
            self.client = MongoClient(uri)
            databases = self.client.list_database_names()

            if databases:
                self.db_combo_box.clear()
                self.db_combo_box.addItems(databases)
                self.load_collections()
                self.db_combo_box.currentIndexChanged.connect(self.load_collections)
            else:
                QMessageBox.warning(self, "Warning", "No databases found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to connect to MongoDB.\n{str(e)}")
            print(f"Error: {str(e)}")

    def load_collections(self):
        db_name = self.db_combo_box.currentText()
        if db_name:
            self.db = self.client[db_name]
            collections = self.db.list_collection_names()
            self.collection_combo_box.clear()
            self.collection_combo_box.addItem("All")
            self.collection_combo_box.addItems(collections)

    def export_collection(self):
        selected_collection = self.collection_combo_box.currentText()
        if not selected_collection:
            QMessageBox.warning(self, "Warning", "No collection selected!")
            return

        if selected_collection == "All":
            all_data = {}
            for collection_name in self.db.list_collection_names():
                collection = self.db[collection_name]
                all_data[collection_name] = list(collection.find({}, {"_id": False}))
            
            file_name = f"{self.db.name}_all_collections.json"
            with open(file_name, 'w', encoding='utf-8') as file:
                json.dump(all_data, file, ensure_ascii=False, indent=4)
            
            QMessageBox.information(self, "Success", f"All collections exported to {file_name} successfully.")
        else:

            self.export_to_json(selected_collection)
            QMessageBox.information(self, "Success", f"Collection '{selected_collection}' exported successfully.")

    def export_to_json(self, collection_name):
        collection = self.db[collection_name]
        data = list(collection.find({}, {"_id": False}))

        file_name = f"{collection_name}.json"
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MongoDBExporter()
    window.show()
    sys.exit(app.exec())
