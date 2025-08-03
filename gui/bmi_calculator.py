import sqlite3
import datetime
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt

class BMICalculator(QWidget):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle(f"BMI Calculator - User: {username}")
        self.username = username
        self.conn = sqlite3.connect("data/bmi_data.db")
        self.cursor = self.conn.cursor()
        self.bmi = None
        self.category = None
        self.unit_mode = "Metric"  # Default unit

        # Create table if not exists
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                date TEXT,
                weight REAL,
                height REAL,
                bmi REAL,
                category TEXT
            )
        """)
        self.conn.commit()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Unit selection dropdown
        self.unit_select = QComboBox()
        self.unit_select.addItems(["Metric (kg/cm)", "Imperial (lbs/in)"])
        self.unit_select.currentIndexChanged.connect(self.change_unit_mode)

        # Input fields
        self.weight_input = QLineEdit()
        self.height_input = QLineEdit()
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)

        # Labels and inputs
        layout.addWidget(QLabel("Unit System:"))
        layout.addWidget(self.unit_select)
        layout.addWidget(QLabel("Weight:"))
        layout.addWidget(self.weight_input)
        layout.addWidget(QLabel("Height (cm or inches):"))
        layout.addWidget(self.height_input)

        # Buttons
        calc_button = QPushButton("Calculate BMI")
        save_button = QPushButton("Save")
        view_button = QPushButton("View History")

        calc_button.clicked.connect(self.calculate_bmi)
        save_button.clicked.connect(self.save_bmi)
        view_button.clicked.connect(self.view_history)

        # Add widgets to layout
        layout.addWidget(calc_button)
        layout.addWidget(self.result_label)

        button_layout = QHBoxLayout()
        button_layout.addWidget(save_button)
        button_layout.addWidget(view_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def change_unit_mode(self):
        # Change between Metric and Imperial
        self.unit_mode = "Metric" if self.unit_select.currentIndex() == 0 else "Imperial"

    def calculate_bmi(self):
        try:
            weight = float(self.weight_input.text())
            height = float(self.height_input.text())
            if weight <= 0 or height <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter valid positive numbers.")
            return

        # Convert units if needed
        if self.unit_mode == "Imperial":
            weight *= 0.453592      # lbs → kg
            height *= 0.0254        # inches → meters
        else:
            height /= 100           # cm → meters

        # Calculate BMI
        bmi = round(weight / (height ** 2), 2)

        # Determine BMI category
        if bmi < 18.5:
            category = "Underweight"
            color = "orange"
        elif bmi < 24.9:
            category = "Normal weight"
            color = "green"
        elif bmi < 29.9:
            category = "Overweight"
            color = "darkorange"
        else:
            category = "Obese"
            color = "red"

        # Display result
        self.bmi = bmi
        self.category = category
        self.result_label.setText(f"BMI: {bmi} ({category})")
        self.result_label.setStyleSheet(f"color: {color}; font-weight: bold")

    def save_bmi(self):
        if self.bmi is None or self.category is None:
            self.calculate_bmi()
            if self.bmi is None:
                return

        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute("""
            INSERT INTO bmi_records (username, date, weight, height, bmi, category)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            self.username,
            date,
            self.weight_input.text(),
            self.height_input.text(),
            self.bmi,
            self.category
        ))
        self.conn.commit()
        QMessageBox.information(self, "Saved", "BMI record saved.")

    def view_history(self):
        self.cursor.execute("""
            SELECT date, bmi FROM bmi_records
            WHERE username = ?
            ORDER BY date
        """, (self.username,))
        records = self.cursor.fetchall()

        if not records:
            QMessageBox.information(self, "No Data", "No records found.")
            return

        dates = [r[0] for r in records]
        bmis = [r[1] for r in records]

        # Plot BMI history
        plt.figure(figsize=(8, 4))
        plt.plot(dates, bmis, marker='o', color='blue')
        plt.xticks(rotation=45)
        plt.xlabel("Date")
        plt.ylabel("BMI")
        plt.title(f"{self.username}'s BMI History")
        plt.tight_layout()
        plt.show()

    def closeEvent(self, event):
        self.conn.close()
