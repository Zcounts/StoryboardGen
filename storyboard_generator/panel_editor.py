# storyboard_generator/panel_editor.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
        self.custom_values = {
            'size': set(["CLOSE UP", "WIDE", "MEDIUM", "SINGLE", "OTS", "MEDIUM 2 SHOT"]),
            'type': set(["OTS", "BAR LVL", "EYE LVL", "SHOULDER LVL"]),
            'move': set(["STATIC", "PUSH", "STATIC or PUSH"]),
            'equip': set(["STICKS", "STICKS or GIMBAL", "GIMBAL"])
        }
        
        # Create the editor UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the panel editor UI."""
        # Set theme colors
        self.bg_color = "#1E1E1E"  # Dark background
        self.text_color = "#FFFFFF"  # White text
        self.accent_color = "#2D2D30"  # Slightly lighter than background
        
        # Configure styles
        style = ttk.Style()
        style.configure("Dark.TFrame", background=self.bg_color)
        style.configure("Dark.TLabel", background=self.bg_color, foreground=self.text_color)
        style.configure("Dark.TButton", background=self.accent_color, foreground=self.text_color)
        style.configure("Dark.TEntry", fieldbackground=self.accent_color, foreground=self.text_color)
        style.map("Dark.TButton",
            background=[("active", "#3E3E42")],
            foreground=[("active", self.text_color)]
        )
        
        # Main container with scrollbar
        self.config(style="Dark.TFrame")
        self.canvas = tk.Canvas(self, background=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="Dark.TFrame")
        
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
        
        # New sections for additional fields
        self._create_additional_info_section()
    
    def _create_image_section(self):
        """Create the image display and upload section."""
        image_frame = ttk.LabelFrame(self.scrollable_frame, text="Panel Image", style="Dark.TLabelframe")
        image_frame.pack(fill="x", padx=10, pady=5)
        
        # Image display area
        self.image_container = ttk.Frame(image_frame, width=400, height=300, style="Dark.TFrame")
        self.image_container.pack(padx=10, pady=10)
        self.image_container.pack_propagate(False)  # Keep the frame at fixed size
        
        # "No image" label
        self.no_image_label = ttk.Label(self.image_container, text="No image selected", style="Dark.TLabel")
        self.no_image_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Upload button
        upload_button = ttk.Button(image_frame, text="Upload Image", command=self._upload_image, style="Dark.TButton")
        upload_button.pack(pady=(0, 10))
    
    def _create_scene_info_section(self):
        """Create the scene and shot info section."""
        info_frame = ttk.LabelFrame(self.scrollable_frame, text="Scene Information", style="Dark.TLabelframe")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        # Grid for labels and inputs
        info_grid = ttk.Frame(info_frame, style="Dark.TFrame")
        info_grid.pack(fill="x", padx=10, pady=10)
        
        # Scene Number
        ttk.Label(info_grid, text="Scene Number:", style="Dark.TLabel").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.scene_number_var = tk.StringVar(value="1")
        scene_entry = ttk.Entry(info_grid, textvariable=self.scene_number_var, style="Dark.TEntry")
        scene_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        scene_entry.bind("<FocusOut>", self._on_scene_number_change)
        
        # Shot Number (letter)
        ttk.Label(info_grid, text="Shot Letter:", style="Dark.TLabel").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.shot_number_var = tk.StringVar()
        shot_entry = ttk.Entry(info_grid, textvariable=self.shot_number_var, style="Dark.TEntry")
        shot_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Full Shot Number Preview (read-only)
        ttk.Label(info_grid, text="Full Shot Number:", style="Dark.TLabel").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.full_shot_var = tk.StringVar()
        full_shot_entry = ttk.Entry(info_grid, textvariable=self.full_shot_var, state="readonly", style="Dark.TEntry")
        full_shot_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        # Camera
        ttk.Label(info_grid, text="Camera:", style="Dark.TLabel").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.camera_var = tk.StringVar(value="Camera 1")
        ttk.Entry(info_grid, textvariable=self.camera_var, style="Dark.TEntry").grid(row=0, column=3, sticky="ew", padx=5, pady=5)
        
        # Lens
        ttk.Label(info_grid, text="Lens:", style="Dark.TLabel").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.lens_var = tk.StringVar()
        ttk.Entry(info_grid, textvariable=self.lens_var, style="Dark.TEntry").grid(row=1, column=3, sticky="ew", padx=5, pady=5)
        
        # Configure grid columns to expand
        info_grid.columnconfigure(1, weight=1)
        info_grid.columnconfigure(3, weight=1)
    
    def _create_technical_info_section(self):
        """Create the technical info section with Size, Type, Move, Equip."""
        tech_frame = ttk.LabelFrame(self.scrollable_frame, text="Technical Information", style="Dark.TLabelframe")
        tech_frame.pack(fill="x", padx=10, pady=5)
        
        # Grid for the technical info
        tech_grid = ttk.Frame(tech_frame, style="Dark.TFrame")
        tech_grid.pack(fill="x", padx=10, pady=10)
        
        # Size
        ttk.Label(tech_grid, text="SIZE", style="Dark.TLabel").grid(row=0, column=0, padx=10, pady=5)
        self.size_var = tk.StringVar()
        size_combo = ttk.Combobox(tech_grid, textvariable=self.size_var, style="Dark.TCombobox")
        size_combo['values'] = tuple(self.custom_values['size'])
        size_combo.grid(row=1, column=0, padx=10, pady=5)
        size_combo.bind("<KeyRelease>", lambda e: self._add_custom_value('size', self.size_var.get()))
        
        # Type
        ttk.Label(tech_grid, text="TYPE", style="Dark.TLabel").grid(row=0, column=1, padx=10, pady=5)
        self.type_var = tk.StringVar()
        type_combo = ttk.Combobox(tech_grid, textvariable=self.type_var, style="Dark.TCombobox")
        type_combo['values'] = tuple(self.custom_values['type'])
        type_combo.grid(row=1, column=1, padx=10, pady=5)
        type_combo.bind("<KeyRelease>", lambda e: self._add_custom_value('type', self.type_var.get()))
        
        # Move
        ttk.Label(tech_grid, text="MOVE", style="Dark.TLabel").grid(row=0, column=2, padx=10, pady=5)
        self.move_var = tk.StringVar(value="STATIC")
        move_combo = ttk.Combobox(tech_grid, textvariable=self.move_var, style="Dark.TCombobox")
        move_combo['values'] = tuple(self.custom_values['move'])
        move_combo.grid(row=1, column=2, padx=10, pady=5)
        move_combo.bind("<KeyRelease>", lambda e: self._add_custom_value('move', self.move_var.get()))
        
        # Equip
        ttk.Label(tech_grid, text="EQUIP", style="Dark.TLabel").grid(row=0, column=3, padx=10, pady=5)
        self.equip_var = tk.StringVar(value="STICKS")
        equip_combo = ttk.Combobox(tech_grid, textvariable=self.equip_var, style="Dark.TCombobox")
        equip_combo['values'] = tuple(self.custom_values['equip'])
        equip_combo.grid(row=1, column=3, padx=10, pady=5)
        equip_combo.bind("<KeyRelease>", lambda e: self._add_custom_value('equip', self.equip_var.get()))
        
        # Configure grid columns to be equal width
        for i in range(4):
            tech_grid.columnconfigure(i, weight=1)
        
        # Store references to combo boxes for updating values
        self.tech_combos = {
            'size': size_combo,
            'type': type_combo,
            'move': move_combo,
            'equip': equip_combo
        }
    
    def _create_action_info_section(self):
        """Create the action information section."""
        action_frame = ttk.LabelFrame(self.scrollable_frame, text="Action Information", style="Dark.TLabelframe")
        action_frame.pack(fill="x", padx=10, pady=5)
        
        # Grid for action info
        action_grid = ttk.Frame(action_frame, style="Dark.TFrame")
        action_grid.pack(fill="x", padx=10, pady=10)
        
        # Action
        ttk.Label(action_grid, text="Action:", style="Dark.TLabel").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.action_var = tk.StringVar()
        ttk.Entry(action_grid, textvariable=self.action_var, style="Dark.TEntry").grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Background
        ttk.Label(action_grid, text="Background:", style="Dark.TLabel").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.bgd_var = tk.StringVar(value="No")
        bgd_frame = ttk.Frame(action_grid, style="Dark.TFrame")
        bgd_frame.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Radiobutton(bgd_frame, text="Yes", variable=self.bgd_var, value="Yes", command=self._toggle_bgd_notes, style="Dark.TRadiobutton").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(bgd_frame, text="No", variable=self.bgd_var, value="No", command=self._toggle_bgd_notes, style="Dark.TRadiobutton").pack(side=tk.LEFT, padx=5)
        
        # Background notes (initially hidden)
        self.bgd_notes_label = ttk.Label(action_grid, text="Background Notes:", style="Dark.TLabel")
        self.bgd_notes_var = tk.StringVar()
        self.bgd_notes_entry = ttk.Entry(action_grid, textvariable=self.bgd_notes_var, style="Dark.TEntry")
        
        # Description
        ttk.Label(action_grid, text="Description:", style="Dark.TLabel").grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        self.description_var = tk.StringVar()
        description_entry = tk.Text(action_grid, wrap=tk.WORD, height=4, width=40, bg=self.accent_color, fg=self.text_color)
        description_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        
        # Connect text widget with StringVar (requires custom handling)
        def update_description_var(event=None):
            self.description_var.set(description_entry.get("1.0", "end-1c"))
        
        description_entry.bind("<KeyRelease>", update_description_var)
        
        # Notes
        ttk.Label(action_grid, text="Notes:", style="Dark.TLabel").grid(row=4, column=0, sticky="nw", padx=5, pady=5)
        self.notes_var = tk.StringVar()
        notes_entry = tk.Text(action_grid, wrap=tk.WORD, height=4, width=40, bg=self.accent_color, fg=self.text_color)
        notes_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        
        # Connect text widget with StringVar (requires custom handling)
        def update_notes_var(event=None):
            self.notes_var.set(notes_entry.get("1.0", "end-1c"))
        
        notes_entry.bind("<KeyRelease>", update_notes_var)
        
        # Configure grid columns
        action_grid.columnconfigure(1, weight=1)
        
        # Store text widgets for later access
        self.description_entry = description_entry
        self.notes_entry = notes_entry
    
    def _create_additional_info_section(self):
        """Create the section for hair/makeup, props, and VFX."""
        additional_frame = ttk.LabelFrame(self.scrollable_frame, text="Additional Information", style="Dark.TLabelframe")
        additional_frame.pack(fill="x", padx=10, pady=5)
        
        # Grid for additional info
        additional_grid = ttk.Frame(additional_frame, style="Dark.TFrame")
        additional_grid.pack(fill="x", padx=10, pady=10)
        
        # Hair/Makeup
        ttk.Label(additional_grid, text="Hair/Makeup:", style="Dark.TLabel").grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        self.hair_makeup_var = tk.StringVar()
        hair_makeup_entry = tk.Text(additional_grid, wrap=tk.WORD, height=3, width=40, bg=self.accent_color, fg=self.text_color)
        hair_makeup_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Connect text widget with StringVar
        def update_hair_makeup_var(event=None):
            self.hair_makeup_var.set(hair_makeup_entry.get("1.0", "end-1c"))
        
        hair_makeup_entry.bind("<KeyRelease>", update_hair_makeup_var)
        
        # Props
        ttk.Label(additional_grid, text="Props:", style="Dark.TLabel").grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        self.props_var = tk.StringVar()
        props_entry = tk.Text(additional_grid, wrap=tk.WORD, height=3, width=40, bg=self.accent_color, fg=self.text_color)
        props_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Connect text widget with StringVar
        def update_props_var(event=None):
            self.props_var.set(props_entry.get("1.0", "end-1c"))
        
        props_entry.bind("<KeyRelease>", update_props_var)
        
        # VFX
        ttk.Label(additional_grid, text="VFX:", style="Dark.TLabel").grid(row=2, column=0, sticky="nw", padx=5, pady=5)
        self.vfx_var = tk.StringVar()
        vfx_entry = tk.Text(additional_grid, wrap=tk.WORD, height=3, width=40, bg=self.accent_color, fg=self.text_color)
        vfx_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        # Connect text widget with StringVar
        def update_vfx_var(event=None):
            self.vfx_var.set(vfx_entry.get("1.0", "end-1c"))
        
        vfx_entry.bind("<KeyRelease>", update_vfx_var)
        
        # Configure grid columns
        additional_grid.columnconfigure(1, weight=1)
        
        # Store text widgets for later access
        self.hair_makeup_entry = hair_makeup_entry
        self.props_entry = props_entry
        self.vfx_entry = vfx_entry
        
        # Save changes button
        save_button = ttk.Button(additional_frame, text="Save Changes", command=self._save_changes, style="Dark.TButton")
        save_button.pack(pady=10)
    
    def _on_scene_number_change(self, event=None):
        """Update full shot number when scene number changes."""
        self._update_full_shot_number()
    
    def _update_full_shot_number(self):
        """Update the full shot number display."""
        scene = self.scene_number_var.get() or "1"
        shot = self.shot_number_var.get() or ""
        self.full_shot_var.set(f"{scene}{shot}")
    
    def _toggle_bgd_notes(self):
        """Show/hide background notes field based on bgd selection."""
        if self.bgd_var.get() == "Yes":
            # Show background notes field
            self.bgd_notes_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
            self.bgd_notes_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        else:
            # Hide background notes field
            self.bgd_notes_label.grid_forget()
            self.bgd_notes_entry.grid_forget()
    
    def _add_custom_value(self, field, value):
        """Add a custom value to the dropdown if it's not already there."""
        if value and value not in self.custom_values[field]:
            self.custom_values[field].add(value)
            self.tech_combos[field]['values'] = tuple(self.custom_values[field])
    
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
                image_label = ttk.Label(self.image_container, image=display_image, style="Dark.TLabel")
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
        self.current_panel.scene_number = self.scene_number_var.get() or "1"
        self.current_panel.camera = self.camera_var.get()
        self.current_panel.lens = self.lens_var.get()
        self.current_panel.size = self.size_var.get()
        self.current_panel.type = self.type_var.get()
        self.current_panel.move = self.move_var.get()
        self.current_panel.equip = self.equip_var.get()
        self.current_panel.action = self.action_var.get()
        self.current_panel.bgd = self.bgd_var.get()
        
        # Get values for new fields
        if self.bgd_var.get() == "Yes":
            self.current_panel.bgd_notes = self.bgd_notes_var.get()
        else:
            self.current_panel.bgd_notes = ""
        
        # Get text from Text widgets
        self.current_panel.description = self.description_entry.get("1.0", "end-1c")
        self.current_panel.notes = self.notes_entry.get("1.0", "end-1c")
        self.current_panel.hair_makeup = self.hair_makeup_entry.get("1.0", "end-1c")
        self.current_panel.props = self.props_entry.get("1.0", "end-1c")
        self.current_panel.vfx = self.vfx_entry.get("1.0", "end-1c")
        
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
        self._update_full_shot_number()
        
        self.camera_var.set(panel.camera)
        self.lens_var.set(panel.lens)
        self.size_var.set(panel.size)
        self.type_var.set(panel.type)
        self.move_var.set(panel.move)
        self.equip_var.set(panel.equip)
        self.action_var.set(panel.action)
        self.bgd_var.set(panel.bgd)
        self.bgd_notes_var.set(panel.bgd_notes)
        
        # Toggle background notes visibility
        self._toggle_bgd_notes()
        
        # Set text in Text widgets
        self.description_entry.delete("1.0", "end")
        self.description_entry.insert("1.0", panel.description)
        
        self.notes_entry.delete("1.0", "end")
        self.notes_entry.insert("1.0", panel.notes)
        
        # Set text for new fields
        self.hair_makeup_entry.delete("1.0", "end")
        self.hair_makeup_entry.insert("1.0", panel.hair_makeup)
        
        self.props_entry.delete("1.0", "end")
        self.props_entry.insert("1.0", panel.props)
        
        self.vfx_entry.delete("1.0", "end")
        self.vfx_entry.insert("1.0", panel.vfx)
        
        # Update image display
        self._update_image_display()
