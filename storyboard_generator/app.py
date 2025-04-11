# storyboard_generator/app.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import copy
from PIL import Image, ImageTk

# Import the components
from storyboard_generator.panel import Panel
from storyboard_generator.panel_editor import PanelEditor
from storyboard_generator.panels_list import PanelsList
from storyboard_generator.pdf_exporter import PDFExporter
from storyboard_generator.pdf_preview import PDFPreview

class StoryboardApp:
    """Main application class for the Storyboard Generator."""
    
    def __init__(self, root):
        """Initialize the application."""
        self.root = root
        
        # Set theme colors
        self.bg_color = "#1E1E1E"  # Dark background
        self.text_color = "#FFFFFF"  # White text
        self.accent_color = "#2D2D30"  # Slightly lighter than background
        
        # Configure window appearance
        self.root.configure(background=self.bg_color)
        
        # Set up custom styles
        self._setup_styles()
        
        # Initialize application state
        self.panels = []
        self.current_project_path = None
        self.modified = False
        
        # Create the UI
        self._create_menu()
        self._create_main_layout()
        self._create_components()
        
        # Update window title
        self._update_title()
        
        # Create empty project to start with
        self._new_project()
    
    def _setup_styles(self):
        """Set up custom styles for the UI."""
        style = ttk.Style()
        
        # Configure theme to start with
        style.theme_use('alt')  # Using 'alt' as a base theme
        
        # Configure dark theme styles
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.text_color)
        style.configure("TButton", background=self.accent_color, foreground=self.text_color)
        style.configure("TEntry", fieldbackground=self.accent_color, foreground=self.text_color)
        style.configure("TNotebook", background=self.bg_color)
        style.configure("TNotebook.Tab", background=self.accent_color, foreground=self.text_color, padding=[10, 2])
        
        # Fix dropdown menu and combobox styles - this helps with the technical info section visibility
        style.configure("TCombobox", fieldbackground=self.accent_color, foreground=self.text_color, background=self.accent_color)
        style.map("TCombobox", 
            fieldbackground=[("readonly", self.accent_color)],
            selectbackground=[("readonly", self.accent_color)],
            selectforeground=[("readonly", self.text_color)])
        
        # Fix canvas styles
        style.configure("Canvas", background=self.bg_color)
        
        # Fix labelframe styles - these have been causing white borders
        style.configure("TLabelframe", background=self.bg_color)
        style.configure("TLabelframe.Label", background=self.bg_color, foreground=self.text_color)
        
        # Fix selection styles
        style.map("TNotebook.Tab",
            background=[("selected", self.accent_color)],
            foreground=[("selected", self.text_color)]
        )
        
        # Configure radiobutton styles
        style.configure("TRadiobutton", background=self.bg_color, foreground=self.text_color)
        style.map("TRadiobutton",
            background=[("active", self.bg_color)],
            foreground=[("active", self.text_color)]
        )
        
        # Fix entry readonly style which was causing contrast issues
        style.map("TEntry",
            fieldbackground=[("readonly", "#2D2D30")],
            foreground=[("readonly", self.text_color)]
        )
        
        # Selected panel style
        style.configure("Selected.TFrame", background="#2A4D69")  # Blue-ish selected color
        style.configure("Selected.TLabel", background="#2A4D69", foreground=self.text_color)  # Added this
        
        # Hover panel style
        style.configure("Hover.TFrame", background="#3E3E42")  # Darker gray for hover
        style.configure("Hover.TLabel", background="#3E3E42", foreground=self.text_color)  # Added this
        
        # Configure styles for specific widgets
        style.configure("PanedWindow", background=self.bg_color)
    
    def _create_menu(self):
        """Create the application menu."""
        menubar = tk.Menu(self.root, bg=self.accent_color, fg=self.text_color)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.accent_color, fg=self.text_color)
        file_menu.add_command(label="New Project", command=self._new_project)
        file_menu.add_command(label="Open Project", command=self._open_project)
        file_menu.add_command(label="Save Project", command=self._save_project)
        file_menu.add_command(label="Save Project As", command=self._save_project_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export to PDF", command=self._export_to_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._exit_app)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.accent_color, fg=self.text_color)
        help_menu.add_command(label="About", command=self._show_about)
        
        # Add menus to menubar
        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def _create_main_layout(self):
        """Create the main application layout."""
        # Create main paned window to divide panels list and editor
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL, style="PanedWindow")
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left frame for panels list
        self.panels_frame = ttk.Frame(self.main_paned, style="TFrame")
        
        # Right paned window to divide editor and preview
        self.right_paned = ttk.PanedWindow(self.main_paned, orient=tk.VERTICAL, style="PanedWindow")
        
        # Add frames to main paned window
        self.main_paned.add(self.panels_frame, weight=1)
        self.main_paned.add(self.right_paned, weight=3)
        
        # Editor frame
        self.editor_frame = ttk.Frame(self.right_paned, style="TFrame")
        
        # Preview frame
        self.preview_frame = ttk.Frame(self.right_paned, style="TFrame")
        
        # Add frames to right paned window
        self.right_paned.add(self.editor_frame, weight=2)
        self.right_paned.add(self.preview_frame, weight=1)
    
    def _create_components(self):
        """Create and initialize the application components."""
        # Create PDF exporter
        self.pdf_exporter = PDFExporter()
        
        # Create panels list
        self.panels_list = PanelsList(
            self.panels_frame,
            on_select=self._on_panel_select,
            on_add=self._add_panel,
            on_delete=self._delete_panel,
            on_move_up=self._move_panel_up,
            on_move_down=self._move_panel_down,
            on_duplicate=self._duplicate_panel
        )
        self.panels_list.pack(fill=tk.BOTH, expand=True)
        
        # Create panel editor
        self.panel_editor = PanelEditor(
            self.editor_frame,
            on_panel_update=self._on_panel_update
        )
        self.panel_editor.pack(fill=tk.BOTH, expand=True)
        
        # Create PDF preview
        self.pdf_preview = PDFPreview(
            self.preview_frame,
            pdf_exporter=self.pdf_exporter
        )
        self.pdf_preview.pack(fill=tk.BOTH, expand=True)
    
    def _update_title(self):
        """Update the window title with the current project name."""
        title = "Storyboard Generator"
        if self.current_project_path:
            project_name = os.path.basename(self.current_project_path)
            title = f"{project_name} - {title}"
        if self.modified:
            title = f"*{title}"
        self.root.title(title)
    
    def _new_project(self):
        """Create a new empty project."""
        # Check if there are unsaved changes
        if self.modified and self.panels:
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "There are unsaved changes. Would you like to save before creating a new project?"
            )
            if response is None:  # Cancel
                return
            if response:  # Yes
                if not self._save_project():
                    return  # Cancel if save was cancelled
        
        # Clear current project
        self.panels = []
        self.current_project_path = None
        self.modified = False
        
        # Update UI
        self.panels_list.update_panels(self.panels)
        self.panel_editor.load_panel(None)
        self.pdf_preview.update_preview(None)
        
        # Update window title
        self._update_title()
    
    def _open_project(self):
        """Open an existing project."""
        # Check if there are unsaved changes
        if self.modified and self.panels:
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "There are unsaved changes. Would you like to save before opening a different project?"
            )
            if response is None:  # Cancel
                return
            if response:  # Yes
                if not self._save_project():
                    return  # Cancel if save was cancelled
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Open Storyboard Project",
            filetypes=[("Storyboard Project", "*.sbp"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Load project file
            with open(file_path, 'r') as file:
                project_data = json.load(file)
            
            # Extract project directory for relative paths
            project_dir = os.path.dirname(file_path)
            
            # Load panels
            panels_data = project_data.get('panels', [])
            self.panels = []
            
            for panel_data in panels_data:
                panel = Panel.from_dict(panel_data, project_dir)
                self.panels.append(panel)
            
            # Sort panels by order
            self.panels.sort(key=lambda p: p.order)
            
            # Update project path
            self.current_project_path = file_path
            self.modified = False
            
            # Update UI
            self.panels_list.update_panels(self.panels)
            
            # Select first panel if available
            if self.panels:
                self.panels_list.select_panel(0)
                self.panel_editor.load_panel(self.panels[0])
                self.pdf_preview.update_preview(self.panels[0])
            else:
                self.panel_editor.load_panel(None)
                self.pdf_preview.update_preview(None)
            
            # Update window title
            self._update_title()
            
            messagebox.showinfo("Success", f"Project loaded successfully from:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open project: {str(e)}")
    
    def _save_project(self):
        """Save the current project."""
        # If no path is set, use Save As dialog
        if not self.current_project_path:
            return self._save_project_as()
        
        try:
            # Create project directory if it doesn't exist
            project_dir = os.path.dirname(self.current_project_path)
            os.makedirs(project_dir, exist_ok=True)
            
            # Create images directory if it doesn't exist
            images_dir = os.path.join(project_dir, "images")
            os.makedirs(images_dir, exist_ok=True)
            
            # Prepare panels data
            panels_data = []
            
            for i, panel in enumerate(self.panels):
                # Update panel order
                panel.order = i
                
                # Handle image paths
                if panel.image_path and os.path.exists(panel.image_path):
                    # If the image is not already in the project dir, copy it
                    if not panel.image_path.startswith(project_dir):
                        # Generate a new filename based on the panel ID
                        filename = f"{panel.id}_{os.path.basename(panel.image_path)}"
                        dest_path = os.path.join(images_dir, filename)
                        
                        # Copy the image file
                        import shutil
                        shutil.copy2(panel.image_path, dest_path)
                        
                        # Update the path to be relative
                        panel.image_path = os.path.join("images", filename)
                    elif panel.image_path.startswith(project_dir):
                        # Convert absolute path to relative
                        panel.image_path = os.path.relpath(panel.image_path, project_dir)
                
                # Add panel data
                panels_data.append(panel.to_dict())
            
            # Create project data
            project_data = {
                'version': '1.0',
                'panels': panels_data
            }
            
            # Save project file
            with open(self.current_project_path, 'w') as file:
                json.dump(project_data, file, indent=2)
            
            # Update modified flag
            self.modified = False
            
            # Update window title
            self._update_title()
            
            messagebox.showinfo("Success", f"Project saved successfully to:\n{self.current_project_path}")
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save project: {str(e)}")
            return False
    
    def _save_project_as(self):
        """Save the current project with a new name."""
        # Open save dialog
        file_path = filedialog.asksaveasfilename(
            title="Save Storyboard Project",
            defaultextension=".sbp",
            filetypes=[("Storyboard Project", "*.sbp"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return False
        
        # Update project path
        self.current_project_path = file_path
        
        # Save project
        return self._save_project()
    
    def _export_to_pdf(self):
        """Export the storyboard to a PDF file."""
        if not self.panels:
            messagebox.showerror("Error", "No panels to export.")
            return
        
        # Get project name if available
        project_name = "Storyboard"
        if self.current_project_path:
            project_name = os.path.splitext(os.path.basename(self.current_project_path))[0]
        
        # Open save dialog
        file_path = filedialog.asksaveasfilename(
            title="Export to PDF",
            defaultextension=".pdf",
            filetypes=[("PDF Document", "*.pdf"), ("All Files", "*.*")],
            initialfile=f"{project_name}.pdf"
        )
        
        if not file_path:
            return
        
        try:
            # Export using the PDF exporter
            self.pdf_exporter.export_storyboard(self.panels, file_path, project_name)
            
            messagebox.showinfo("Success", f"Storyboard exported to PDF successfully:\n{file_path}")
            
            # Ask if user wants to open the PDF
            if messagebox.askyesno("Open PDF", "Would you like to open the exported PDF?"):
                self._open_file(file_path)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export to PDF: {str(e)}")
    
    def _open_file(self, file_path):
        """Open a file with the default application."""
        import subprocess
        import platform
        
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', file_path])
            else:  # Linux
                subprocess.call(['xdg-open', file_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")
    
    def _exit_app(self):
        """Exit the application."""
        # Check if there are unsaved changes
        if self.modified and self.panels:
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "There are unsaved changes. Would you like to save before exiting?"
            )
            if response is None:  # Cancel
                return
            if response:  # Yes
                if not self._save_project():
                    return  # Cancel if save was cancelled
        
        # Exit the application
        self.root.quit()
    
    def _show_about(self):
        """Show the about dialog."""
        messagebox.showinfo(
            "About Storyboard Generator",
            "Storyboard Generator 1.0\n\n"
            "A simple desktop application for creating, editing, and exporting storyboards for film production.\n\n"
            "Created with Python and Tkinter."
        )
    
    def _on_panel_select(self, index):
        """Handle panel selection from the list."""
        if 0 <= index < len(self.panels):
            panel = self.panels[index]
            self.panel_editor.load_panel(panel)
            self.pdf_preview.update_preview(panel)
    
    def _add_panel(self):
        """Add a new panel to the storyboard."""
        # Create a new panel
        panel = Panel()
        
        # Set default scene number based on existing panels
        if self.panels:
            # Use the scene number of the last panel
            last_panel = self.panels[-1]
            panel.scene_number = last_panel.scene_number
        
        # Add to the panels list
        self.panels.append(panel)
        
        # Update panels list
        self.panels_list.update_panels(self.panels)
        
        # Select the new panel
        self.panels_list.select_panel(len(self.panels) - 1)
        self.panel_editor.load_panel(panel)
        self.pdf_preview.update_preview(panel)
        
        # Mark as modified
        self.modified = True
        self._update_title()
    
    def _delete_panel(self):
        """Delete the selected panel."""
        index = self.panels_list.selected_index
        if 0 <= index < len(self.panels):
            # Ask for confirmation
            if messagebox.askyesno("Delete Panel", "Are you sure you want to delete this panel?"):
                # Remove from the list
                del self.panels[index]
                
                # Update panels list
                self.panels_list.update_panels(self.panels)
                
                # Select an appropriate panel
                if self.panels:
                    new_index = min(index, len(self.panels) - 1)
                    self.panels_list.select_panel(new_index)
                    self.panel_editor.load_panel(self.panels[new_index])
                    self.pdf_preview.update_preview(self.panels[new_index])
                else:
                    self.panel_editor.load_panel(None)
                    self.pdf_preview.update_preview(None)
                
                # Mark as modified
                self.modified = True
                self._update_title()
    
    def _move_panel_up(self):
        """Move the selected panel up in the list."""
        index = self.panels_list.selected_index
        if 0 < index < len(self.panels):
            # Swap panels
            self.panels[index], self.panels[index-1] = self.panels[index-1], self.panels[index]
            
            # Update panels list
            self.panels_list.update_panels(self.panels)
            
            # Select the moved panel
            self.panels_list.select_panel(index-1)
            
            # Mark as modified
            self.modified = True
            self._update_title()
    
    def _move_panel_down(self):
        """Move the selected panel down in the list."""
        index = self.panels_list.selected_index
        if 0 <= index < len(self.panels) - 1:
            # Swap panels
            self.panels[index], self.panels[index+1] = self.panels[index+1], self.panels[index]
            
            # Update panels list
            self.panels_list.update_panels(self.panels)
            
            # Select the moved panel
            self.panels_list.select_panel(index+1)
            
            # Mark as modified
            self.modified = True
            self._update_title()
    
    def _duplicate_panel(self):
        """Duplicate the selected panel."""
        index = self.panels_list.selected_index
        if 0 <= index < len(self.panels):
            # Get the panel to duplicate
            original_panel = self.panels[index]
            
            # Create a deep copy
            panel_data = original_panel.to_dict()
            new_panel = Panel.from_dict(panel_data)
            
            # Generate a new ID
            import uuid
            new_panel.id = str(uuid.uuid4())
            
            # Add a copy indicator to the shot number
            if new_panel.shot_number:
                new_panel.shot_number += " (copy)"
            else:
                new_panel.shot_number = "(copy)"
            
            # Insert after the original
            self.panels.insert(index + 1, new_panel)
            
            # Update panels list
            self.panels_list.update_panels(self.panels)
            
            # Select the new panel
            self.panels_list.select_panel(index + 1)
            self.panel_editor.load_panel(new_panel)
            self.pdf_preview.update_preview(new_panel)
            
            # Mark as modified
            self.modified = True
            self._update_title()
    
    def _on_panel_update(self, panel):
        """Handle updates to a panel."""
        # Update the panels list display
        self.panels_list.update_panels(self.panels)
        
        # Ensure the same panel stays selected
        index = next((i for i, p in enumerate(self.panels) if p.id == panel.id), -1)
        if index >= 0:
            self.panels_list.select_panel(index)
        
        # Update the preview
        self.pdf_preview.update_preview(panel)
        
        # Mark as modified
        self.modified = True
        self._update_title()
