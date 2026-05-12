from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
)
from PySide6.QtGui import QFont, QIcon
import sys

# Importing modules (Ensure these modules do NOT create QApplication inside their main())
import BudgetReport as BR
import BudgetUpdates as BU
import ProjectTypeWise as PT
import PlanVariance as PV
import BudgetVariance as BV


class MenuApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SAP Project System")
        self.setFixedSize(350, 300)
        self.center_window()

        # Set the window icon (Change 'nlcil.png' to your actual file)
        self.setWindowIcon(QIcon("nlcil.png"))

        self.create_widgets()

    def center_window(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def create_widgets(self):
        layout = QVBoxLayout()

        # Button configurations
        buttons = [
            ("Budget Report", lambda: self.run_module(BR)),
            ("Budget Updates", lambda: self.run_module(BU)),
            ("Project Type Wise", lambda: self.run_module(PT)),
            ("Plan Vs Expenses (% Achieved)", lambda: self.run_module(PV)),
            ("Budget Vs Expenses (% Achieved)", lambda: self.run_module(BV)),
            ("EXIT", self.close),
        ]

        # Create buttons dynamically
        for text, command in buttons:
            button = QPushButton(text)
            button.setFont(QFont("Helvetica", 10))
            button.clicked.connect(command)
            layout.addWidget(button)

        self.setLayout(layout)

    def run_module(self, module):
        """Runs the given module's `main()` function safely."""
        try:
            module.main()  # Call the module's main function (it should NOT create a new QApplication)
        except AttributeError:
            QMessageBox.critical(
                self,
                "Error",
                f"{module.__name__} module does not have a 'main()' function.",
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run {module.__name__}: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create QApplication once
    window = MenuApp()
    window.show()
    sys.exit(app.exec())
