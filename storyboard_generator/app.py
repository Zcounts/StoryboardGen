# storyboard_generator/app.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import copy
from PIL import Image, ImageTk

# Use relative imports for modules in the same package
from .pdf_exporter import PDFExporter
from .panel import Panel
from .panel_editor import PanelEditor
from .panels_list import PanelsList
from .pdf_preview import PDFPreview

class StoryboardApp:
    """Main application class for the Storyboard Generator."""
    
    def __init__(self, master):
        """Initialize the application."""
        self.master = master
        self.current_project = None
        self.project_dir = None
        self.panels = []
        self.current_panel_index = -1
        
        # Set theme colors
        self.bg_color = "#1E1E1E"  # Dark background
        self.text_color = "#FFFFFF"  # White text
        self.accent_color = "#2D2D30"  # Slightly lighter than background
        
        # Configure styles
        self._setup_styles()
        
        # Create the main UI components
        self._create_menu()
        self._create_main_frame()
        
        # Set up initial state
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
        
        # Fix dropdown menu and combobox styles
        style.configure("TCombobox", fieldbackground=self.accent_color, foreground="black", background=self.accent_color)
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
        
        # Selected panel style
        style.configure("Selected.TFrame", background="#2A4D69")  # Blue-ish selected color
        
        # Configure styles for specific widgets
        style.configure("PanedWindow", background=self.bg_color)
    
    def _create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.master, bg=self.accent_color, fg=self.text_color)
        self.master.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.accent_color, fg=self.text_color)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self._new_project)
        file_menu.add_command(label="Open Project", command=self._open_project)
        file_menu.add_command(label="Save Project", command=self._save_project)
        file_menu.add_separator()
        file_menu.add_command(label="Export to PDF", command=self._export_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)
    
    def _create_main_frame(self):
        """Create the main application frame."""
        # Configure the main window
        self.master.configure(bg=self.bg_color)
        
        # Create main horizontal pane for left panel list and right content
        self.main_paned = ttk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left frame - Panels list
        self.left_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.left_frame, weight=1)
        
        # Right frame - Panel editor and preview
        self.right_paned = ttk.PanedWindow(self.main_paned, orient=tk.HORIZONTAL)
        self.main_paned.add(self.right_paned, weight=3)
        
        # Editor frame
        self.editor_frame = ttk.Frame(self.right_paned)
        self.right_paned.add(self.editor_frame, weight=1)
        
        # Preview frame
        self.preview_frame = ttk.Frame(self.right_paned)
        self.right_paned.add(self.preview_frame, weight=1)
        
        # Set up panels list
        self._setup_panels_list()
        
        # Set up panel editor
        self._setup_panel_editor()
        
        # Set up preview pane
        self._setup_preview_pane()
    
    def _setup_panels_list(self):
        """Set up the panels list in the left frame."""
        # Create the custom panels list
        self.panels_list = PanelsList(
            self.left_frame,
            on_select=self._on_panel_select,
            on_add=self.add_panel,
            on_delete=self.delete_panel,
            on_move_up=self.move_panel_up,
            on_move_down=self.move_panel_down,
            on_duplicate=self.duplicate_panel
        )
        self.panels_list.pack(fill=tk.BOTH, expand=True)
    
    def _setup_panel_editor(self):
        """Set up the panel editor in the right frame."""
        # Panel editor title
        ttk.Label(self.editor_frame, text="Panel Editor").pack(pady=(10, 5), padx=10, anchor=tk.W)
        
        # Create the panel editor
        self.panel_editor = PanelEditor(self.editor_frame, on_panel_update=self._on_panel_update)
        self.panel_editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Initially disable the panel editor
        self._update_panel_editor()
    
    def _setup_preview_pane(self):
        """Set up the PDF preview pane."""
        # Create PDF exporter
        self.pdf_exporter = PDFExporter()
        
        # Create the preview widget
        self.pdf_preview = PDFPreview(self.preview_frame, pdf_exporter=self.pdf_exporter)
        self.pdf_preview.pack(fill=tk.BOTH, expand=True)
    
    def _on_panel_update(self, panel):
        """Handle panel update event from the editor."""
        if panel and panel in self.panels:
            # Update the panels list to reflect changes
            self._update_panels_list()
            
            # Update the preview
            self._update_preview()
    
    def _update_panel_editor(self):
        """Update the panel editor with the currently selected panel."""
        if 0 <= self.current_panel_index < len(self.panels):
            # Load the selected panel into the editor
            self.panel_editor.load_panel(self.panels[self.current_panel_index])
        else:
            # No panel selected, clear the editor
            self.panel_editor.load_panel(None)
    
    def _update_preview(self):
        """Update the PDF preview."""
        if 0 <= self.current_panel_index < len(self.panels):
            # Show preview of the selected panel
            self.pdf_preview.update_preview(self.panels[self.current_panel_index])
        else:
            # No panel selected, clear the preview
            self.pdf_preview.update_preview(None)
    
    def _new_project(self):
        """Create a new project."""
        self.current_project = None
        self.project_dir = None
        self.panels = []
        self.current_panel_index = -1
        self._update_panels_list()
        self._update_panel_editor()
        self._update_preview()
        
        # Update window title
        self.master.title("Storyboard Generator")
    
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
            
            # Assign shot letters if missing
            self._update_shot_letters()
            
            # Update UI
            self._update_panels_list()
            self.current_panel_index = 0 if self.panels else -1
            self._update_panel_editor()
            self._update_preview()
            
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
    
    def _update_shot_letters(self):
        """Update shot letters based on scene groups."""
        # Group panels by scene
        scene_groups = {}
        for panel in self.panels:
            scene_number = panel.scene_number
            if scene_number not in scene_groups:
                scene_groups[scene_number] = []
            scene_groups[scene_number].append(panel)
        
        # For each scene, assign shot letters
        for scene_number, scene_panels in scene_groups.items():
            # Sort by order within scene
            scene_panels.sort(key=lambda p: p.order)
            
            # Assign shot letters A, B, C, etc.
            for i, panel in enumerate(scene_panels):
                panel.shot_number = self._get_shot_letter(i)
    
    def _get_shot_letter(self, index):
        """
        Get shot letter for a given index.
        A, B, C, ... Z, AA, BB, etc.
        
        Args:
            index: The 0-based index of the shot
        
        Returns:
            str: The shot letter
        """
        if index < 26:
            # A-Z
            return chr(65 + index)
        else:
            # AA, BB, etc.
            letter_index = (index - 26) // 26
            return chr(65 + letter_index) * 2
    
    def add_panel(self):
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
        
        # Update shot letters
        self._update_shot_letters()
        
        # Update UI
        self._update_panels_list()
        
        # Select the new panel
        self.current_panel_index = len(self.panels) - 1
        self.panels_list.select_panel(self.current_panel_index)
        
        # Update editor and preview
        self._update_panel_editor()
        self._update_preview()
    
    def delete_panel(self):
        """Delete the selected panel."""
        if 0 <= self.current_panel_index < len(self.panels):
            # Ask for confirmation
            if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this panel?"):
                return
                
            # Remove the panel
            del self.panels[self.current_panel_index]
            
            # Update shot letters
            self._update_shot_letters()
            
            # Update UI
            self._update_panels_list()
            
            # Adjust the selection
            if self.panels:
                if self.current_panel_index >= len(self.panels):
                    self.current_panel_index = len(self.panels) - 1
                self.panels_list.select_panel(self.current_panel_index)
            else:
                self.current_panel_index = -1
            
            # Update editor and preview
            self._update_panel_editor()
            self._update_preview()
    
    def duplicate_panel(self):
        """Duplicate the selected panel."""
        if 0 <= self.current_panel_index < len(self.panels):
            # Get the current panel
            current_panel = self.panels[self.current_panel_index]
            
            # Create a new panel as a copy
            new_panel = Panel()
            new_panel.scene_number = current_panel.scene_number
            new_panel.camera = current_panel.camera
            new_panel.lens = current_panel.lens
            new_panel.size = current_panel.size
            new_panel.type = current_panel.type
            new_panel.move = current_panel.move
            new_panel.equip = current_panel.equip
            new_panel.action = current_panel.action
            new_panel.bgd = current_panel.bgd
            new_panel.bgd_notes = current_panel.bgd_notes
            new_panel.hair_makeup = current_panel.hair_makeup
            new_panel.props = current_panel.props
            new_panel.vfx = current_panel.vfx
            new_panel.description = current_panel.description
            new_panel.notes = current_panel.notes
            
            # Copy image if exists
            if current_panel.image_path and os.path.exists(current_panel.image_path):
                try:
                    new_panel.set_image(current_panel.image_path, self.project_dir)
                except:
                    pass
            
            # Insert after current panel
            self.panels.insert(self.current_panel_index + 1, new_panel)
            
            # Update shot letters
            self._update_shot_letters()
            
            # Update UI
            self._update_panels_list()
            
            # Select the new panel
            self.current_panel_index += 1
            self.panels_list.select_panel(self.current_panel_index)
            
            # Update editor and preview
            self._update_panel_editor()
            self._update_preview()
    
    def move_panel_up(self):
        """Move the selected panel up in the order."""
        if 0 < self.current_panel_index < len(self.panels):
            # Swap with the previous panel
            self.panels[self.current_panel_index], self.panels[self.current_panel_index-1] = \
                self.panels[self.current_panel_index-1], self.panels[self.current_panel_index]
            
            # Update shot letters
            self._update_shot_letters()
            
            # Update UI
            self._update_panels_list()
            
            # Update selection
            self.current_panel_index -= 1
            self.panels_list.select_panel(self.current_panel_index)
            
            # Update panel orders
            for i, panel in enumerate(self.panels):
                panel.order = i
            
            # Update preview
            self._update_preview()
    
    def move_panel_down(self):
        """Move the selected panel down in the order."""
        if 0 <= self.current_panel_index < len(self.panels) - 1:
            # Swap with the next panel
            self.panels[self.current_panel_index], self.panels[self.current_panel_index+1] = \
                self.panels[self.current_panel_index+1], self.panels[self.current_panel_index]
            
            # Update shot letters
            self._update_shot_letters()
            
            # Update UI
            self._update_panels_list()
            
            # Update selection
            self.current_panel_index += 1
            self.panels_list.select_panel(self.current_panel_index)
            
            # Update panel orders
            for i, panel in enumerate(self.panels):
                panel.order = i
            
            # Update preview
            self._update_preview()
    
    def _on_panel_select(self, index):
        """Handle panel selection event."""
        if 0 <= index < len(self.panels):
            # Update the current panel index
            self.current_panel_index = index
            
            # Update the panel editor
            self._update_panel_editor()
            
            # Update preview
            self._update_preview()
    
    def _update_panels_list(self):
        """Update the panels list in the UI."""
        # Update the custom panels list
        self.panels_list.update_panels(self.panels)
