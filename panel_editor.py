# panel_editor.py

import tkinter as tk
from tkinter import ttk, filedialog
import os
from PIL import Image, ImageTk

class PanelEditor(ttk.Frame):
    """UI component for editing a storyboard panel."""
    
    def __init__(self, master, on_panel_update=None):
        """Initialize the panel editor."""
        super().__init__(master)
        self.on_panel_update = on_panel_update
        self.current_panel = None
        self.image_display = None
        
        # Create the editor UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the panel editor UI."""
        # Main container with scrollbar
        self.canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Image section
        self._create_image_section()
        
        # Scene and shot info section
        self._create_scene_info_section()
        
        # Technical info section - Size, Type, Move, Equip
        self._create_technical_info_section()
        
        # Action info section
        self._create_action_info_section()
    
    def _create_image_section(self):
        """Create the image display and upload section."""
        image_frame = ttk.LabelFrame(self.scrollable_frame, text="Panel Image")
        image_frame.pack(fill="x", padx=10, pady=5)
        
        # Image display area
        self.image_container = ttk.Frame(image_frame, width=400, height=300)
        self.image_container.pack(padx=10, pady=10)
        self.image_container.pack_propagate(False)  # Keep the frame at fixed size
        
        # "No image" label
        self.no_image_label = ttk.Label(self.image_container, text="No image selected")
        self.no_image_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Upload button
        upload_button = ttk.Button(image_frame, text="Upload Image", command=self._upload_image)
        upload_button.pack(pady=(0, 10))
    
    def _create_scene_info_section(self):
        """Create the scene and shot info section."""
        info_frame = ttk.LabelFrame(self.scrollable_frame, text="Scene Information")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        # Grid for labels and inputs
        info_grid = ttk.Frame(info_frame)
        info_grid.pack(fill="x", padx=10, pady=10)
        
        # Scene Number
        ttk.Label(info_grid, text="Scene Number:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.scene_number_var = tk.StringVar()
        ttk.Entry(info_grid, textvariable=self.scene_number_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Shot Number
        ttk.Label(info_grid, text="Shot Number:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.shot_number_var = tk.StringVar()
        ttk.Entry(info_grid, textvariable=self.shot_number_var).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Camera
        ttk.Label(info_grid, text="Camera:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.camera_var = tk.StringVar(value="Camera 1")
        ttk.Entry(info_grid, textvariable=self.camera_var).grid(row=0, column=3, sticky="ew", padx=5, pady=5)
        
        # Lens
        ttk.Label(info_grid, text="Lens:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.lens_var = tk.StringVar()
        ttk.Entry(info_grid, textvariable=self.lens_var).grid(row=1, column=3, sticky="ew", padx=5, pady=5)
        
        # Configure grid columns to expand
        info_grid.columnconfigure(1, weight=1)
        info_grid.columnconfigure(3, weight=1)
    
    def _create_technical_info_section(self):
        """Create the technical info section with Size, Type, Move, Equip."""
        tech_frame = ttk.LabelFrame(self.scrollable_frame, text="Technical Information")
        tech_frame.pack(fill="x", padx=10, pady=5)
        
        # Grid for the technical info
        tech_grid = ttk.Frame(tech_frame)
        tech_grid.pack(fill="x", padx=10, pady=10)
        
        # Size
        ttk.Label(tech_grid, text="SIZE").grid(row=0, column=0, padx=10, pady=5)
        self.size_var = tk.StringVar()
        size_combo = ttk.Combobox(tech_grid, textvariable=self.size_var)
        size_combo['values'] = ("CLOSE UP", "WIDE", "MEDIUM", "SINGLE", "OTS", "MEDIUM 2 SHOT")
        size_combo.grid(row=1, column=0, padx=10, pady=5)
        
        # Type
        ttk.Label(tech_grid, text="TYPE").grid(row=0, column=1, padx=10, pady=5)
        self.type_var = tk.StringVar()
        type_combo = ttk.Combobox(tech_grid, textvariable=self.type_var)
        type_combo['values'] = ("OTS", "BAR LVL", "EYE LVL", "SHOULDER LVL")
        type_combo.grid(row=1, column=1, padx=10, pady=5)
        
        # Move
        ttk.Label(tech_grid, text="MOVE").grid(row=0, column=2, padx=10, pady=5)
        self.move_var = tk.StringVar(value="STATIC")
        move_combo = ttk.Combobox(tech_grid, textvariable=self.move_var)
        move_combo['values'] = ("STATIC", "PUSH", "STATIC or PUSH")
        move_combo.grid(row=1, column=2, padx=10, pady=5)
        
        # Equip
        ttk.Label(tech_grid, text="EQUIP").grid(row=0, column=3, padx=10, pady=5)
        self.equip_var = tk.StringVar(value="STICKS")
        equip_combo = ttk.Combobox(tech_grid, textvariable=self.equip_var)
        equip_combo['values'] = ("STICKS", "STICKS or GIMBAL", "GIMBAL")
        equip_combo.grid(row=1, column=3, padx=10, pady=5)
        
        # Configure grid columns to be equal width
        for i in range(4):
            tech_grid.columnconfigure(i, weight=1)
    
    def _create_action_info_section(self):
        """Create the action information section."""
        action_frame = ttk.LabelFrame(self.scrollable_frame, text="Action Information")
        action_frame.pack(fill="x", padx=10, pady=5)
        
        # Grid for action info
        action_grid = ttk.Frame(action_frame)
        action_grid.pack(fill="x", padx=10, pady=10)
        
        # Action
        ttk.Label(action_grid, text="Action:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.action_var = tk.StringVar()
        ttk.Entry(action_grid, textvariable=self.action_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Background
        ttk.Label(action_grid, text="Background:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.bgd_var = tk.StringVar(value="No")
        bgd_frame = ttk.Frame(action_grid)
        bgd_frame.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Radiobutton(bgd_frame, text="Yes", variable=self.bgd_var, value="Yes").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(bgd_frame, text="No", variable=self.bgd_var, value="No").pack(side=tk.LEFT, padx=5)
        
        # Description
        ttk.Label(action_grid, text="Description:").grid(row=2, column=0, sticky="nw", padx=5, pady=5)
        self.description_var = tk.StringVar()
        description_entry = tk.Text(action_grid, wrap=tk.WORD, height=4, width=40)
        description_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        # Connect text widget with StringVar (requires custom handling)
        def update_description_var(event=None):
            self.description_var.set(description_entry.get("1.0", "end-1c"))
        
        description_entry.bind("<KeyRelease>", update_description_var)
        
        # Notes
        ttk.Label(action_grid, text="Notes:").grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        self.notes_var = tk.StringVar()
        notes_entry = tk.Text(action_grid, wrap=tk.WORD, height=4, width=40)
        notes_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        
        # Connect text widget with StringVar (requires custom handling)
        def update_notes_var(event=None):
            self.notes_var.set(notes_entry.get("1.0", "end-1c"))
        
        notes_entry.bind("<KeyRelease>", update_notes_var)
        
        # Save changes button
        save_button = ttk.Button(action_frame, text="Save Changes", command=self._save_changes)
        save_button.pack(pady=10)
        
        # Configure grid columns
        action_grid.columnconfigure(1, weight=1)
        
        # Store text widgets for later access
        self.description_entry = description_entry
        self.notes_entry = notes_entry
    
    def _upload_image(self):
        """Handle image upload."""
        if not self.current_panel:
            return
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        
        if file_path:
            try:
                # Set the image in the panel
                self.current_panel.set_image(file_path)
                
                # Update the display
                self._update_image_display()
                
                # Notify about the change
                if self.on_panel_update:
                    self.on_panel_update(self.current_panel)
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to load image: {e}")
    
    def _update_image_display(self):
        """Update the image display with the current panel's image."""
        # Clear existing image if any
        for widget in self.image_container.winfo_children():
            if widget != self.no_image_label:
                widget.destroy()
        
        if self.current_panel and self.current_panel.image:
            # Hide the "No image" label
            self.no_image_label.place_forget()
            
            # Get a properly sized image for display
            display_image = self.current_panel.get_display_image((380, 280))
            
            if display_image:
                # Keep a reference to avoid garbage collection
                self.image_display = display_image
                
                # Create and display the image label
                image_label = ttk.Label(self.image_container, image=display_image)
                image_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            # Show the "No image" label
            self.no_image_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def _save_changes(self):
        """Save the changes to the current panel."""
        if not self.current_panel:
            return
        
        # Update panel properties from UI fields
        self.current_panel.shot_number = self.shot_number_var.get()
        self.current_panel.scene_number = self.scene_number_var.get()
        self.current_panel.camera = self.camera_var.get()
        self.current_panel.lens = self.lens_var.get()
        self.current_panel.size = self.size_var.get()
        self.current_panel.type = self.type_var.get()
        self.current_panel.move = self.move_var.get()
        self.current_panel.equip = self.equip_var.get()
        self.current_panel.action = self.action_var.get()
        self.current_panel.bgd = self.bgd_var.get()
        
        # Get text from Text widgets
        self.current_panel.description = self.description_entry.get("1.0", "end-1c")
        self.current_panel.notes = self.notes_entry.get("1.0", "end-1c")
        
        # Notify about the update
        if self.on_panel_update:
            self.on_panel_update(self.current_panel)
        
        # Show confirmation
        tk.messagebox.showinfo("Success", "Panel information saved successfully!")
    
    def load_panel(self, panel):
        """
        Load a panel into the editor.
        
        Args:
            panel: The Panel object to edit
        """
        self.current_panel = panel
        
        if not panel:
            return
        
        # Set UI fields from panel properties
        self.shot_number_var.set(panel.shot_number)
        self.scene_number_var.set(panel.scene_number)
        self.camera_var.set(panel.camera)
        self.lens_var.set(panel.lens)
        self.size_var.set(panel.size)
        self.type_var.set(panel.type)
        self.move_var.set(panel.move)
        self.equip_var.set(panel.equip)
        self.action_var.set(panel.action)
        self.bgd_var.set(panel.bgd)
        
        # Set text in Text widgets
        self.description_entry.delete("1.0", "end")
        self.description_entry.insert("1.0", panel.description)
        
        self.notes_entry.delete("1.0", "end")
        self.notes_entry.insert("1.0", panel.notes)
        
        # Update image display
        self._update_image_display()
