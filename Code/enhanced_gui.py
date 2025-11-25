"""
Enhanced GUI Framework with Progress Indicators and Better UX
"""

import sys
from typing import Callable, Optional
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QProgressBar,
    QLabel,
    QTextEdit,
    QMessageBox,
    QFileDialog,
    QGroupBox,
    QGridLayout,
    QStatusBar,
    QSplashScreen,
)
from PySide6.QtCore import QThread, Signal, QTimer, Qt
from PySide6.QtGui import QFont, QIcon, QPixmap
from error_handler import SAPReportLogger


class WorkerThread(QThread):
    """Worker thread for background processing."""

    progress_updated = Signal(int, str)  # percentage, message
    task_completed = Signal(object)  # result
    error_occurred = Signal(Exception)  # error

    def __init__(self, task_func: Callable, *args, **kwargs):
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
        self.logger = SAPReportLogger("WorkerThread")

    def run(self):
        """Execute task in background thread."""
        try:
            self.progress_updated.emit(0, "Starting task...")

            # Add progress callback to kwargs if supported
            if "progress_callback" in self.task_func.__code__.co_varnames:
                self.kwargs["progress_callback"] = self.progress_updated.emit

            result = self.task_func(*self.args, **self.kwargs)

            self.progress_updated.emit(100, "Task completed successfully!")
            self.task_completed.emit(result)

        except Exception as e:
            self.logger.log_error("Worker thread error", e)
            self.error_occurred.emit(e)


class ProgressDialog(QWidget):
    """Enhanced progress dialog with detailed status."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Processing Report...")
        self.setFixedSize(450, 300)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)

        self.setup_ui()

    def setup_ui(self):
        """Setup progress dialog UI."""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("SAP Report Processing")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """
        )

        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Details text area
        details_group = QGroupBox("Processing Details")
        details_layout = QVBoxLayout(details_group)

        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(120)
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)

        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_processing)

        # Layout assembly
        layout.addWidget(title_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addWidget(details_group)
        layout.addWidget(self.cancel_button)

    def update_progress(self, percentage: int, message: str):
        """Update progress display."""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(message)
        self.details_text.append(f"[{percentage}%] {message}")

        # Auto-scroll to bottom
        scrollbar = self.details_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def cancel_processing(self):
        """Handle cancel request."""
        reply = QMessageBox.question(
            self,
            "Cancel Processing",
            "Are you sure you want to cancel the current operation?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.close()


class EnhancedMenuApp(QMainWindow):
    """Enhanced main menu with modern UI and progress indicators."""

    def __init__(self):
        super().__init__()
        self.logger = SAPReportLogger("EnhancedMenuApp")
        self.current_worker = None
        self.progress_dialog = None

        self.setup_ui()
        self.setup_statusbar()

    def setup_ui(self):
        """Setup the main UI."""
        self.setWindowTitle("SAP Project System - Enhanced Interface")
        self.setFixedSize(600, 500)
        self.center_window()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Title section
        title_label = QLabel("SAP Project System Reports")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2E4057; margin: 20px;")

        # Report buttons group
        reports_group = QGroupBox("Available Reports")
        reports_layout = QGridLayout(reports_group)

        self.create_report_buttons(reports_layout)

        # System info group
        info_group = QGroupBox("System Information")
        info_layout = QVBoxLayout(info_group)

        self.system_info_label = QLabel("System ready for processing")
        self.last_operation_label = QLabel("No operations performed yet")

        info_layout.addWidget(self.system_info_label)
        info_layout.addWidget(self.last_operation_label)

        # Assembly
        main_layout.addWidget(title_label)
        main_layout.addWidget(reports_group)
        main_layout.addWidget(info_group)
        main_layout.addStretch()

    def create_report_buttons(self, layout: QGridLayout):
        """Create enhanced report buttons."""
        reports = [
            (
                "Budget Report",
                "Generate standard budget reports",
                self.run_budget_report,
            ),
            ("Budget Updates", "Track budget modifications", self.run_budget_updates),
            (
                "Project Analytics",
                "Interactive project dashboard",
                self.run_project_analytics,
            ),
            (
                "Variance Analysis",
                "Plan vs actual analysis",
                self.run_variance_analysis,
            ),
            ("Project Type Wise", "Classify projects by type", self.run_project_types),
            ("Year End Reports", "Generate year-end summaries", self.run_year_end),
        ]

        for i, (title, description, handler) in enumerate(reports):
            button = self.create_enhanced_button(title, description, handler)
            layout.addWidget(button, i // 2, i % 2)

    def create_enhanced_button(
        self, title: str, description: str, handler: Callable
    ) -> QPushButton:
        """Create an enhanced button with styling."""
        button = QPushButton(f"{title}\n{description}")
        button.setMinimumHeight(80)
        button.clicked.connect(handler)

        button.setStyleSheet(
            """
            QPushButton {
                background-color: #F8F9FA;
                border: 2px solid #DEE2E6;
                border-radius: 8px;
                padding: 10px;
                text-align: left;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E9ECEF;
                border-color: #ADB5BD;
            }
            QPushButton:pressed {
                background-color: #DEE2E6;
            }
        """
        )

        return button

    def setup_statusbar(self):
        """Setup enhanced status bar."""
        statusbar = QStatusBar()
        self.setStatusBar(statusbar)

        # Status message
        self.status_message = QLabel("Ready")
        statusbar.addWidget(self.status_message)

        # Progress bar in status bar
        self.status_progress = QProgressBar()
        self.status_progress.setVisible(False)
        self.status_progress.setMaximumWidth(200)
        statusbar.addPermanentWidget(self.status_progress)

        # System time
        self.time_label = QLabel()
        statusbar.addPermanentWidget(self.time_label)

        # Update time every second
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)

    def update_time(self):
        """Update time display."""
        from datetime import datetime

        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(current_time)

    def center_window(self):
        """Center window on screen."""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def run_report_with_progress(self, report_function: Callable, report_name: str):
        """Execute report with progress indication."""
        try:
            # Show progress dialog
            self.progress_dialog = ProgressDialog(self)
            self.progress_dialog.show()

            # Show status bar progress
            self.status_progress.setVisible(True)
            self.status_message.setText(f"Processing {report_name}...")

            # Create worker thread
            self.current_worker = WorkerThread(report_function)
            self.current_worker.progress_updated.connect(self.update_progress)
            self.current_worker.task_completed.connect(self.handle_completion)
            self.current_worker.error_occurred.connect(self.handle_error)

            # Start processing
            self.current_worker.start()

        except Exception as e:
            self.logger.log_error(f"Error starting {report_name}", e)
            self.show_error_message(f"Failed to start {report_name}", str(e))

    def update_progress(self, percentage: int, message: str):
        """Update progress displays."""
        if self.progress_dialog:
            self.progress_dialog.update_progress(percentage, message)

        self.status_progress.setValue(percentage)
        self.status_message.setText(f"Processing: {message}")

    def handle_completion(self, result):
        """Handle successful completion."""
        self.cleanup_progress_ui()
        self.status_message.setText("Operation completed successfully")
        self.last_operation_label.setText(
            f"Last operation completed at {datetime.now().strftime('%H:%M:%S')}"
        )

        QMessageBox.information(self, "Success", "Report generated successfully!")

    def handle_error(self, error: Exception):
        """Handle processing errors."""
        self.cleanup_progress_ui()
        self.status_message.setText("Operation failed")

        self.show_error_message("Processing Error", str(error))

    def cleanup_progress_ui(self):
        """Clean up progress UI elements."""
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None

        self.status_progress.setVisible(False)

        if self.current_worker:
            self.current_worker = None

    def show_error_message(self, title: str, message: str):
        """Show enhanced error message."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setDetailedText("Check the log files for more detailed information.")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    # Report handler methods
    def run_budget_report(self):
        """Handle budget report execution."""
        import BudgetReport

        self.run_report_with_progress(BudgetReport.main, "Budget Report")

    def run_budget_updates(self):
        """Handle budget updates execution."""
        import BudgetUpdates

        self.run_report_with_progress(BudgetUpdates.main, "Budget Updates")

    def run_project_analytics(self):
        """Handle project analytics execution."""
        import GlimpsOfProjects

        self.run_report_with_progress(GlimpsOfProjects.main, "Project Analytics")

    def run_variance_analysis(self):
        """Handle variance analysis execution."""
        import PlanVariance

        self.run_report_with_progress(PlanVariance.main, "Variance Analysis")

    def run_project_types(self):
        """Handle project types execution."""
        import ProjectTypeWise

        self.run_report_with_progress(ProjectTypeWise.main, "Project Type Analysis")

    def run_year_end(self):
        """Handle year-end reports execution."""
        import YearEnd558

        self.run_report_with_progress(YearEnd558.main, "Year End Reports")


def main():
    """Launch enhanced GUI application."""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("SAP Project System")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("SAP Reporting Suite")

    # Show splash screen
    splash_pixmap = QPixmap(300, 200)
    splash_pixmap.fill(Qt.lightGray)
    splash = QSplashScreen(splash_pixmap)
    splash.showMessage("Loading SAP Project System...", Qt.AlignBottom | Qt.AlignCenter)
    splash.show()

    # Initialize main window
    window = EnhancedMenuApp()

    # Close splash and show main window
    splash.finish(window)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
