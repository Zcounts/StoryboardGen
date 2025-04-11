# Update to app.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
from PIL import Image, ImageTk

from pdf_exporter import PDFExporter

from panel import Panel
from panel_editor import PanelEditor

class StoryboardApp:
    """Main application class for the Storyboard Generator."""
    
    def __init__(self, master):
        """Initialize the application."""
        self.master = master
        self.current_project = None
        self.project_dir = None
        self.panels = []
        self.current_panel_index = -1
        
        # Create the main UI components
        self._create_menu()
        self._create_main_frame()
        
        # Set up initial state
        self._new_project()
    
    def _create_menu(self):
        """Create the application menu bar."""
        # (Same as before)
        # ...
    
    def _create_main_frame(self):
        """Create the main application frame."""
        # Create main frame with left and right panes
        self.main_frame = ttk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left frame - Panels list
        self.left_frame = ttk.Frame(self.main_frame)
        self.main_frame.add(self.left_frame, weight=1)
        
        # Right frame - Panel editor
        self.right_frame = ttk.Frame(self.main_frame)
        self.main_frame.add(self.right_frame, weight=3)
        
        # Set up panels list
        self._setup_panels_list()
        
        # Set up panel editor
        self._setup_panel_editor()
    
    def _setup_panels_list(self):
        """Set up the panels list in the left frame."""
        # (Same as before, we'll enhance this later)
        # ...
    
    def _setup_panel_editor(self):
        """Set up the panel editor in the right frame."""
        # Panel editor title
        ttk.Label(self.right_frame, text="Panel Editor").pack(pady=(0, 10), anchor=tk.W)
        
        # Create the panel editor
        self.panel_editor = PanelEditor(self.right_frame, on_panel_update=self._on_panel_update)
        self.panel_editor.pack(fill=tk.BOTH, expand=True)
        
        # Initially disable the panel editor
        self._update_panel_editor()
    
    def _on_panel_update(self, panel):
        """Handle panel update event from the editor."""
        if panel and panel in self.panels:
            # Update the panels list to reflect changes
            self._update_panels_list()
    
    def _update_panel_editor(self):
        """Update the panel editor with the currently selected panel."""
        if 0 <= self.current_panel_index < len(self.panels):
            # Load the selected panel into the editor
            self.panel_editor.load_panel(self.panels[self.current_panel_index])
        else:
            # No panel selected, clear the editor
            self.panel_editor.load_panel(None)
    
    def _new_project(self):
        """Create a new project."""
        self.current_project = None
        self.project_dir = None
        self.panels = []
        self.current_panel_index = -1
        self._update_panels_list()
        self._update_panel_editor()
    
    def _open_project(self):
        """Open an existing project."""
        # Select project directory
        project_dir = filedialog.askdirectory(title="Open Storyboard Project")
        
        if not project_dir:
            return
        
        # Check for project data file
        data_file = os.path.join(project_dir, "data.json")
        
        if not os.path.exists(data_file):
            messagebox.showerror("Error", "Invalid project directory. No data.json file found.")
            return
        
        try:
            # Load project data
            with open(data_file, 'r') as f:
                project_data = json.load(f)
            
            # Set project properties
            self.current_project = project_data.get('name', os.path.basename(project_dir))
            self.project_dir = project_dir
            
            # Load panels
            self.panels = []
            for panel_data in project_data.get('panels', []):
                panel = Panel.from_dict(panel_data, project_dir)
                self.panels.append(panel)
            
            # Sort panels by order
            self.panels.sort(key=lambda p: p.order)
            
            # Update UI
            self._update_panels_list()
            self.current_panel_index = 0 if self.panels else -1
            self._update_panel_editor()
            
            # Update window title
            self.master.title(f"Storyboard Generator - {self.current_project}")
            
            messagebox.showinfo("Success", f"Project '{self.current_project}' opened successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open project: {e}")
    
    def _save_project(self):
        """Save the current project."""
        if not self.project_dir:
            # If no project directory yet, ask for one
            project_dir = filedialog.askdirectory(title="Save Storyboard Project")
            
            if not project_dir:
                return
            
            self.project_dir = project_dir
            
            # Create images directory if it doesn't exist
            os.makedirs(os.path.join(project_dir, "images"), exist_ok=True)
            
            # Set current project name if not set
            if not self.current_project:
                self.current_project = os.path.basename(project_dir)
        
        try:
            # Create project data
            project_data = {
                'name': self.current_project,
                'panels': []
            }
            
            # Add panels to project data
            for i, panel in enumerate(self.panels):
                # Update panel order
                panel.order = i
                
                # If the panel has an image, ensure it's in the project directory
                if panel.image_path and not panel.image_path.startswith(self.project_dir):
                    panel.set_image(panel.image_path, self.project_dir)
                
                # Add panel data to project
                project_data['panels'].append(panel.to_dict())
            
            # Write project data to file
            with open(os.path.join(self.project_dir, "data.json"), 'w') as f:
                json.dump(project_data, f, indent=4)
            
            # Update window title
            self.master.title(f"Storyboard Generator - {self.current_project}")
            
            messagebox.showinfo("Success", f"Project saved to {self.project_dir}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save project: {e}")
    
    def _export_pdf(self):
        """Export the storyboard as PDF."""
        if not self.panels:
            messagebox.showerror("Error", "No panels to export. Add some panels first.")
            return
        
        # Ask for export location
        export_path = filedialog.asksaveasfilename(
            title="Export Storyboard",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if not export_path:
            return
        
        try:
            # For now, show a placeholder message
            messagebox.showinfo("Export", "PDF export feature will be implemented in the next step.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {e}")
    
    def _add_panel(self):
        """Add a new panel to the storyboard."""
        # Create a new panel
        panel = Panel()
        
        # If we have existing panels, set default values from the last panel
        if self.panels:
            last_panel = self.panels[-1]
            panel.scene_number = last_panel.scene_number
            panel.camera = last_panel.camera
        
        # Add to the list
        self.panels.append(panel)
        
        # Update UI
        self._update_panels_list()
        
        # Select the new panel
        self.current_panel_index = len(self.panels) - 1
        self.panels_listbox.selection_clear(0, tk.END)
        self.panels_listbox.selection_set(self.current_panel_index)
        self.panels_listbox.see(self.current_panel_index)
        
        # Update editor
        self._update_panel_editor()
    
    def _delete_panel(self):
        """Delete the selected panel."""
        if 0 <= self.current_panel_index < len(self.panels):
            # Remove the panel
            del self.panels[self.current_panel_index]
            
            # Update UI
            self._update_panels_list()
            
            # Adjust the selection
            if self.panels:
                if self.current_panel_index >= len(self.panels):
                    self.current_panel_index = len(self.panels) - 1
                self.panels_listbox.selection_set(self.current_panel_index)
            else:
                self.current_panel_index = -1
            
            # Update editor
            self._update_panel_editor()
    
    def _move_panel_up(self):
        """Move the selected panel up in the order."""
        if 0 < self.current_panel_index < len(self.panels):
            # Swap with the previous panel
            self.panels[self.current_panel_index], self.panels[self.current_panel_index-1] = \
                self.panels[self.current_panel_index-1], self.panels[self.current_panel_index]
            
            # Update UI
            self._update_panels_list()
            
            # Update selection
            self.current_panel_index -= 1
            self.panels_listbox.selection_clear(0, tk.END)
            self.panels_listbox.selection_set(self.current_panel_index)
            
            # Update panel orders
            for i, panel in enumerate(self.panels):
                panel.order = i
    
    def _move_panel_down(self):
        """Move the selected panel down in the order."""
        if 0 <= self.current_panel_index < len(self.panels) - 1:
            # Swap with the next panel
            self.panels[self.current_panel_index], self.panels[self.current_panel_index+1] = \
                self.panels[self.current_panel_index+1], self.panels[self.current_panel_index]
            
            # Update UI
            self._update_panels_list()
            
            # Update selection
            self.current_panel_index += 1
            self.panels_listbox.selection_clear(0, tk.END)
            self.panels_listbox.selection_set(self.current_panel_index)
            
            # Update panel orders
            for i, panel in enumerate(self.panels):
                panel.order = i
    
    def _on_panel_select(self, event):
        """Handle panel selection event."""
        selection = self.panels_listbox.curselection()
        
        if selection:
            # Get the selected index
            selected_index = selection[0]
            
            if 0 <= selected_index < len(self.panels):
                # Update the current panel index
                self.current_panel_index = selected_index
                
                # Update the panel editor
                self._update_panel_editor()
    
    def _update_panels_list(self):
        """Update the panels list in the UI."""
        # Clear the current list
        self.panels_listbox.delete(0, tk.END)
        
        # Add all panels
        for i, panel in enumerate(self.panels):
            display_text = f"Shot {i+1}"
            if panel.shot_number:
                display_text = f"Shot {panel.shot_number}"
            self.panels_listbox.insert(tk.END, display_text)
        
        # Update selection
        if 0 <= self.current_panel_index < len(self.panels):
            self.panels_listbox.selection_set(self.current_panel_index)

    # Update to app.py - import the PDFExporter

from pdf_exporter import PDFExporter

# Then update the _export_pdf method:

def _export_pdf(self):
    """Export the storyboard as PDF."""
    if not self.panels:
        messagebox.showerror("Error", "No panels to export. Add some panels first.")
        return
    
    # Ask for export location
    export_path = filedialog.asksaveasfilename(
        title="Export Storyboard",
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")]
    )
    
    if not export_path:
        return
    
    try:
        # Create a PDF exporter
        exporter = PDFExporter()
        
        # Export the panels
        project_name = self.current_project or "Storyboard"
        pdf_path = exporter.export_storyboard(self.panels, export_path, project_name)
        
        messagebox.showinfo("Success", f"Storyboard exported to {pdf_path}")
        
        # Ask if user wants to open the PDF
        if messagebox.askyesno("Open PDF", "Would you like to open the exported PDF?"):
            self._open_file(pdf_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export PDF: {str(e)}")
    
def _open_file(self, path):
    """Open a file with the default application."""
    import os
    import platform
    import subprocess
    
    try:
        if platform.system() == 'Darwin':  # macOS
            subprocess.call(('open', path))
        elif platform.system() == 'Windows':  # Windows
            os.startfile(path)
        else:  # linux variants
            subprocess.call(('xdg-open', path))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open file: {str(e)}")
