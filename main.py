from gui.login_window import LoginWindow
from PyQt5.QtWidgets import QApplication
import sys

def main():
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()