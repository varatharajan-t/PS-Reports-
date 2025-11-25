# ***********************************************************************************
# This program displays a menu and executes the user selection option
# Author: Varatharajan T. Date of Creation: 23/05/2024 Modified on: 23/05/2024
# Converted to PySide6 by: Varatharajan T.
# ***********************************************************************************

import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

# Importing modules
import BudgetReport as BR
import BudgetUpdates as BU
import ProjectTypeWise as PT
import PlanVariance as PV
import BudgetVariance as BV
import ProjectAnalysis as PA
import GlimpsOfProjects as GA


class MenuApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SAP Project System")
        self.setFixedSize(400, 400)  # Fixed window size
        self.center_window()

        # Set window icon
        self.setWindowIcon(QIcon("../Data/nlcil.png"))

        self.init_ui()

    def center_window(self):
        """
        Centers the application window on the screen.
        """
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def init_ui(self):
        """
        Initializes the user interface and creates buttons.
        """
        container = QWidget()
        layout = QVBoxLayout()

        # Button configurations
        buttons = [
            ("Budget Report - S_ALR_87013558", self.run_budget_report),
            ("Budget Updates - S_ALR_87013560", self.run_budget_updates),
            ("Project Type Wise - CN41N", self.run_project_type_wise),
            ("Plan Variance (% Achieved) - S_ALR_87013532", self.run_plan_variance),
            ("Budget Variance (% Achieved) - S_ALR_87013557", self.run_budget_variance),
            ("Glimps of Projects", self.run_glimps),
            ("Project Analysis", self.run_analysis),
            ("EXIT", self.close),
        ]

        # Create buttons dynamically
        for text, handler in buttons:
            button = QPushButton(text)
            button.setStyleSheet(
                """
                QPushButton {
                    font-size: 14px;
                    padding: 8px;
                    background-color: #f0f0f0;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #d3d3d3;
                }
                """
            )
            button.clicked.connect(handler)
            layout.addWidget(button)

        container.setLayout(layout)
        self.setCentralWidget(container)

    # Handlers for each button
    def run_budget_report(self):
        self.run_module(BR)

    def run_budget_updates(self):
        self.run_module(BU)

    def run_project_type_wise(self):
        self.run_module(PT)

    def run_plan_variance(self):
        self.run_module(PV)

    def run_budget_variance(self):
        self.run_module(BV)

    def run_glimps(self):
        self.run_module(GA)

    def run_analysis(self):
        self.run_module(PA)

    def run_module(self, module):
        """
        Runs the specified module if it has a 'main' function.
        Args:
            module: Python module to be executed.
        """
        try:
            module.main()
        except AttributeError:
            QMessageBox.critical(
                self,
                "Error",
                f"{module.__name__} module does not have a 'main()' function.",
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run {module.__name__}: {e}")


def main():
    """
    Entry point for the application.
    """
    app = QApplication(sys.argv)
    window = MenuApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
