# -*- coding: utf-8 -*-
"""
Created on November 2024

@author: Ghimciuc Ioan
"""

import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from src.reports.motion_report import MotionReport
from src.utils.vicon_nexus import ViconNexusAPI
from src.exporters import motion_report_pdf_exporter, motion_report_xlsx_exporter


class ReportGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gait Report Generator - by Ghimciuc Ioan")
        self.root.geometry("700x200")
        self.root.minsize(500, 200)
        self.root.maxsize(900, 200)

        self.subject_names = []
        self.vicon_available = False

        # Initialize Vicon API and handle potential errors
        try:
            self.vicon = ViconNexusAPI()
            self.subject_names = self.vicon.GetSubjectNames()
            self.vicon_available = True
        except Exception as e:
            messagebox.showerror("Vicon Connection Error", "Vicon Nexus API is not accessible. Please ensure Vicon is running.")
            self.vicon = None

        # Subject Name Dropdown (Combobox for modern design)
        tk.Label(root, text="Numele subiectului:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.selected_subject = tk.StringVar(value=self.subject_names[0] if self.subject_names else "")
        self.subject_menu = ttk.Combobox(root, textvariable=self.selected_subject, values=self.subject_names, state="readonly")
        self.subject_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.subject_menu.bind("<<ComboboxSelected>>", self.update_report_name)

        # Output Directory
        tk.Label(root, text="Folderul pentru salvare:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.output_directory = tk.Entry(root, width=30)
        exports_folder_path = r'C:\Vicon\Rezultate\Rezultate Analiza Mers'
        self.output_directory.insert(0, exports_folder_path)  # Default value
        self.output_directory.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        tk.Button(root, text="Browse", command=self.browse_output_directory).grid(row=2, column=2, padx=5, pady=5)

        # Reference Angles File
        tk.Label(root, text="Fișierul cu unghiurile etalon:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.reference_file_path = tk.Entry(root, width=30)
        reference_angles_file_path = os.path.join(exports_folder_path, 'Unghiurile_Perry.xlsx')
        self.reference_file_path.insert(0, reference_angles_file_path)  # Default value
        self.reference_file_path.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        tk.Button(root, text="Browse", command=self.browse_reference_file).grid(row=1, column=2, padx=5, pady=5)

        # Report Name (default to subject name)
        tk.Label(root, text="Numele raportului:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.report_name_entry = tk.Entry(root, width=30)
        self.report_name_entry.insert(0, self.selected_subject.get())  # Default to subject name
        self.report_name_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Checkbox for exporting device data
        self.export_device_data = tk.BooleanVar(value=True)
        tk.Label(root, text="Exportă și datele dispozitivelor:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        tk.Checkbutton(root, variable=self.export_device_data).grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Generate Report Button
        self.generate_button = tk.Button(root, text="Generează raportul", command=self.generate_report)
        self.generate_button.grid(row=5, column=0, columnspan=3, pady=10, padx=10, sticky="ew")

        # Disable button if Vicon is not available
        if not self.vicon_available:
            self.generate_button.config(state="disabled")

        # Make the widgets resize with the window
        root.grid_columnconfigure(1, weight=1)

    def update_report_name(self, *args):
        # Update report name based on selected subject
        self.report_name_entry.delete(0, tk.END)
        self.report_name_entry.insert(0, self.selected_subject.get())

    def browse_reference_file(self):
        file_path = filedialog.askopenfilename(title="Select Reference Angles File", filetypes=[("Excel Files", "*.xlsx")])
        if file_path:
            self.reference_file_path.delete(0, tk.END)
            self.reference_file_path.insert(0, file_path)

    def browse_output_directory(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_directory.delete(0, tk.END)
            self.output_directory.insert(0, directory)

    def generate_report(self):
        subject_name = self.selected_subject.get()
        reference_file_path = self.reference_file_path.get()
        output_directory = self.output_directory.get()
        report_name = self.report_name_entry.get()
        include_device_data = self.export_device_data.get()

        if not subject_name or not reference_file_path or not output_directory or not report_name:
            messagebox.showwarning("Missing Information", "Please fill out all fields.")
            return

        try:
            report = MotionReport(self.vicon, subject_name, reference_file_path)
            motion_report_pdf_exporter.export(report, report_name, output_directory, include_device_data)
            motion_report_xlsx_exporter.export(report, report_name, output_directory)
            messagebox.showinfo("Success", f"Report '{report_name}' generated successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = ReportGeneratorApp(root)
    root.mainloop()
