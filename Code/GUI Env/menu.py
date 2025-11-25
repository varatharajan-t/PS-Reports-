"""
************************************************************************************************************
SAP PROJECT SYSTEM - MAIN MENU INTERFACE (TKINTER)
************************************************************************************************************

SYSTEM REQUIREMENTS:
- Python 3.7+
- tkinter (built-in GUI library)
- All report modules: BudgetReport, BudgetUpdates, ProjectTypeWise, etc.

PURPOSE:
Central menu system providing unified access to all SAP Project System reporting tools.
Built using tkinter for cross-platform compatibility and native look-and-feel.
Serves as the main entry point for users to access various reporting functionalities.

MENU OPTIONS:
1. Budget Report - S_ALR_87013558: Standard SAP budget reporting
2. Budget Updates - S_ALR_87013560: Budget modification tracking
3. Project Type Wise - CN41N: Project classification analysis
4. Plan Variance - S_ALR_87013532: Plan vs actual variance analysis
5. Budget Variance - S_ALR_87013557: Budget vs actual variance analysis
6. Glimps of Projects: Project overview and analytics dashboard
7. Project Analysis: Comprehensive project data analysis
8. EXIT: Clean application termination

ARCHITECTURAL PATTERN:
- Controller Pattern: MenuApp class orchestrates all report modules
- Error Handling: Comprehensive exception management with user feedback
- Modular Design: Each report function isolated for maintainability
- User Experience: Centered window with consistent button styling

TECHNICAL FEATURES:
- Dynamic button generation from configuration array
- Exception handling with messagebox feedback
- Window centering calculation for optimal UX
- Custom styling with hover effects
- Icon support with fallback handling

AUTHOR: Varatharajan T.
CREATION DATE: 23/05/2024
LAST MODIFIED: 23/05/2024
************************************************************************************************************
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Importing modules
import BudgetReport as BR
import BudgetUpdates as BU
import ProjectTypeWise as PT
import PlanVariance as PV
import BudgetVariance as BV
import ProjectAnalysis as PA
import GlimpsOfProjects as GA


class MenuApp:
    """
    Main menu application class for SAP Project System reporting tools.

    Provides a centralized interface for accessing all reporting modules with:
    - Professional window layout and centering
    - Dynamic button generation with consistent styling
    - Comprehensive error handling and user feedback
    - Module integration with exception management

    Attributes:
        root (tk.Tk): Main tkinter window instance

    Design Patterns:
        - Command Pattern: Each button linked to specific command functions
        - Template Method: Standardized module execution with run_module()
        - Error Handler: Consistent exception management across all modules
    """

    def __init__(self, root):
        """
        Initialize the main menu application.

        Sets up the GUI window, applies styling, creates buttons, and configures
        the application icon. Handles window centering for optimal user experience.

        Args:
            root (tk.Tk): Main tkinter window instance

        Side Effects:
            - Centers window on screen
            - Sets window title and icon
            - Creates and configures all UI elements
        """
        self.root = root
        self.root.title("SAP Project System")
        self.center_window(400, 400)
        self.create_widgets()

        # Set the window icon (Ensure 'nlcil.ico' exists in the same directory or provide full path)
        icon = tk.PhotoImage(file="../Data/nlcil.png")
        self.root.iconphoto(False, icon)

    def center_window(self, width, height):
        # Calculate position to center the window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        # Button configurations
        buttons = [
            ("Budget Report - S_ALR_87013558", self.run_budget_report),
            ("Budget Updates - S_ALR_87013560", self.run_budget_updates),
            ("Project Type Wise - CN41N", self.run_project_type_wise),
            ("Plan Variance (% Achieved) - S_ALR_87013532", self.run_plan_variance),
            ("Budget Variance (% Achieved) - S_ALR_87013557", self.run_budget_variance),
            ("Glimps of Projects", self.run_glimps),
            ("Project Analysis", self.run_analysis),
            ("EXIT", self.root.quit),
        ]

        # Create buttons dynamically
        for text, command in buttons:
            button = ttk.Button(self.root, text=text, command=command)
            button.pack(pady=10, padx=20, fill=tk.X)

    # Run each report with exception handling
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
        try:
            module.main()
        except AttributeError:
            messagebox.showerror(
                "Error", f"{module.__name__} module does not have a 'main()' function."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run {module.__name__}: {e}")


if __name__ == "__main__":
    root = tk.Tk()

    # Define button styles
    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 10))
    style.map("TButton", background=[("active", "#d3d3d3")])  # Light gray on hover

    app = MenuApp(root)
    root.mainloop()
