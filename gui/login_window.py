import sqlite3
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from gui.bmi_calculator import BMICalculator

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - BMI Calculator")
        self.conn = sqlite3.connect("data/bmi_data.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE
            )
        """)
        self.conn.commit()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Enter Username:"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        login_button = QPushButton("Login / Create User")
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text().strip()

        if not username:
            QMessageBox.warning(self, "Error", "Username cannot be empty.")
            return

        self.cursor.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (username,))
        self.conn.commit()

        self.hide()
        self.bmi_window = BMICalculator(username)
        self.bmi_window.show()