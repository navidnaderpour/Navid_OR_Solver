import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os


class NavidORSolverMain:

    BG_COLOR = "#f4f6f9"
    HEADER_COLOR = "#0d47a1"
    BUTTON_COLOR = "#1565c0"
    CARD_COLOR = "#ffffff"

    def __init__(self, root):
        self.root = root
        self.root.title("Navid OR Solver")
        self.root.geometry("900x600")
        self.root.configure(bg=self.BG_COLOR)
        self.root.resizable(False, False)

        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self._create_header()
        self._create_body()

    def _create_header(self):
        header = tk.Frame(self.root, bg=self.HEADER_COLOR, height=90)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Navid OR Solver",
            font=("Segoe UI", 26, "bold"),
            bg=self.HEADER_COLOR,
            fg="white"
        ).pack(pady=(15, 0))

        tk.Label(
            header,
            text="Operations Research Solver Suite",
            font=("Segoe UI", 12),
            bg=self.HEADER_COLOR,
            fg="#bbdefb"
        ).pack()

    def _create_body(self):
        body = tk.Frame(self.root, bg=self.BG_COLOR)
        body.pack(fill=tk.BOTH, expand=True, padx=40, pady=35)

        tk.Label(
            body,
            text="Please select the solver you want to use:",
            font=("Segoe UI", 18, "bold"),
            bg=self.BG_COLOR,
            fg=self.HEADER_COLOR
        ).pack(pady=(0, 25))

        card = tk.Frame(body, bg=self.CARD_COLOR, bd=1, relief=tk.SOLID)
        card.pack(fill=tk.BOTH, expand=True, padx=70, pady=10)

        self._add_solver_button(
            card,
            title="Simplex Solver",
            description="Solve Linear Programming problems using Simplex methods.",
            filename="simplex_solver_gui.py"
        )

        self._add_solver_button(
            card,
            title="Transportation Solver",
            description="Solve transportation problems using optimization methods.",
            filename="transport_solver_gui.py"
        )

        self._add_solver_button(
            card,
            title="Network Solver",
            description="Solve shortest path, maximum flow, and MST problems.",
            filename="network_solver_gui.py"
        )

        tk.Label(
            body,
            text="Prepared by Navid Naderpour",
            font=("Segoe UI", 10),
            bg=self.BG_COLOR,
            fg="#607d8b"
        ).pack(pady=(15, 0))

    def _add_solver_button(self, parent, title, description, filename):
        frame = tk.Frame(parent, bg=self.CARD_COLOR)
        frame.pack(fill=tk.X, padx=30, pady=18)

        left = tk.Frame(frame, bg=self.CARD_COLOR)
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            left,
            text=title,
            font=("Segoe UI", 15, "bold"),
            bg=self.CARD_COLOR,
            fg=self.HEADER_COLOR,
            anchor="w"
        ).pack(anchor="w")

        tk.Label(
            left,
            text=description,
            font=("Segoe UI", 10),
            bg=self.CARD_COLOR,
            fg="#455a64",
            anchor="w"
        ).pack(anchor="w", pady=(4, 0))

        tk.Button(
            frame,
            text="OPEN",
            font=("Segoe UI", 11, "bold"),
            bg=self.BUTTON_COLOR,
            fg="white",
            width=14,
            height=2,
            command=lambda: self._open_solver(filename)
        ).pack(side=tk.RIGHT, padx=10)

    def _open_solver(self, filename):
        file_path = os.path.join(self.base_dir, filename)

        if not os.path.exists(file_path):
            messagebox.showerror(
                "File Not Found",
                f"Cannot find this file:\n\n{filename}\n\nMake sure it is in the same folder."
            )
            return

        try:
            subprocess.Popen([sys.executable, file_path])
        except Exception as e:
            messagebox.showerror(
                "Run Error",
                f"Could not open {filename}\n\nError:\n{e}"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = NavidORSolverMain(root)
    root.mainloop()