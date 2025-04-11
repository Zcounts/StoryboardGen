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
        self.input_bg_color = "#3E3E42"  # Darker input background for better contrast
        self.highlight_color = "#007ACC"  # Blue highlight
        
        # Configure the frame
        self.configure(style="TFrame")
        
        # Main container with scrollbar
        self.canvas = tk.Canvas(self, background=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="TFrame")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add mouse wheel scrolling for the canvas
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Add enter/leave binding to control when mousewheel scrolls this pane
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        # Create sections with nice margins and spacing
        section_padding = 10
        
        # Image section
        self._create_section("Panel Image", self._create_image_section, section_padding)
        
        # Scene and shot info section
        self._create_section("Scene Information", self._create_scene_info_section, section_padding)
        
        # Setup and Camera section
        self._create_section("Setup and Camera Information", self._create_setup_camera_section, section_padding)
        
        # Technical info section
        self._create_section("Technical Information", self._create_technical_info_section, section_padding)
        
        # Action info section
        self._create_section("Action Information", self._create_action_info_section, section_padding)
        
        # Shot list specific section
        self._create_section("Shot List Information", self._create_shot_list_section, section_padding)
        
        # Additional info section
        self._create_section("Additional Information", self._create_additional_info_section, section_padding)
    
    def _create_section(self, title, content_function, padding):
        """Create a collapsible section with a title and content."""
        # Create a frame for this section
        section_frame = ttk.LabelFrame(self.scrollable_frame, text=title)
        section_frame.pack(fill="x", padx=padding, pady=padding)
        
        # Call the content creation function with the section frame
        content_function(section_frame)
    
    def _on_enter(self, event):
        """Track when mouse enters this widget."""
        # Set a flag that can be checked by the mousewheel handler
        self.active_scroll = True
        
    def _on_leave(self, event):
        """Track when mouse leaves this widget."""
        self.active_scroll = False
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling when in this pane."""
        if hasattr(self, 'active_scroll') and self.active_scroll:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _create_image_section(self, parent_frame):
        """Create the image display and upload section."""
        # Image display area
        self.image_container = ttk.Frame(parent_frame, width=400, height=300)
        self.image_container.pack(padx=10, pady=10)
        self.image_container.pack_propagate(False)  # Keep the frame at fixed size
        
        # "No image" label
        self.no_image_label = ttk.Label(self.image_container, text="No image selected")
        self.no_image_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Upload button with modern styling
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        upload_button = ttk.Button(
            button_frame, 
            text="Upload Image", 
            command=self._upload_image,
            style="Accent.TButton"  # Custom style for accent buttons
        )
        upload_button.pack(side=tk.LEFT, padx=5)
    
    def _create_scene_info_section(self, parent_frame):
        """Create the scene and shot info section."""
        # Grid for labels and inputs
        info_grid = ttk.Frame(parent_frame)
        info_grid.pack(fill="x", padx=10, pady=10)
        
        # Scene Number
        ttk.Label(info_grid, text="Scene Number:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.scene_number_var = tk.StringVar(value="1")
        scene_entry = ttk.Entry(info_grid, textvariable=self.scene_number_var)
        scene_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        scene_entry.bind("<FocusOut>", self._on_field_change)
        scene_entry.bind("<KeyRelease>", self._on_field_change)
        
        # Shot Number (letter)
        ttk.Label(info_grid, text="Shot Letter:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.shot_number_var = tk.StringVar()
        shot_entry = ttk.Entry(info_grid,
        shot_entry.bind("<KeyRelease>", self._on_field_change)
        
        # Full Shot Number Preview (read-only)
        ttk.Label(info_grid, text="Full Shot Number:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.full_shot_var = tk.StringVar()
        full_shot_entry = ttk.Entry(info_grid, textvariable=self.full_shot_var, state="readonly")
        full_shot_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        # Lens
        ttk.Label(info_grid, text="Lens:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.lens_var = tk.StringVar()
        lens_entry = ttk.Entry(info_grid, textvariable=self.lens_var)
        lens_entry.grid(row=0, column=3, sticky="ew", padx=5, pady=5)
        lens_entry.bind("<FocusOut>", self._on_field_change)
        lens_entry.bind("<KeyRelease>", self._on_field_change)
        
        # Configure grid columns to expand
        info_grid.columnconfigure(1, weight=1)
        info_grid.columnconfigure(3, weight=1)
    
    def _create_setup_camera_section(self, parent_frame):
        """Create the setup and camera section."""
        # Grid for setup info
        setup_grid = ttk.Frame(parent_frame)
        setup_grid.pack(fill="x", padx=10, pady=10)
        
        # Setup Number
        ttk.Label(setup_grid, text="Setup Number:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.setup_number_var = tk.StringVar(value="1")
        setup_entry = ttk.Entry(setup_grid, textvariable=self.setup_number_var)
        setup_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        setup_entry.bind("<FocusOut>", self._on_field_change)
        setup_entry.bind("<KeyRelease>", self._on_field_change)
        
        # Camera (dropdown)
        ttk.Label(setup_grid, text="Camera:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.camera_var = tk.StringVar(value="Camera 1")
        camera_combo = ttk.Combobox(setup_grid, textvariable=self.camera_var)
        camera_combo['values'] = ("Camera 1", "Camera 2", "Camera 3", "Camera 4", "Camera 5", "Camera 6")
        camera_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        camera_combo.bind("<<ComboboxSelected>>", self._on_field_change)
        
        # Camera Name
        ttk.Label(setup_grid, text="Camera Name:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.camera_name_var = tk.StringVar()
        camera_name_entry = ttk.Entry(setup_grid, textvariable=self.camera_name_var)
        camera_name_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        camera_name_entry.bind("<FocusOut>", self._on_field_change)
        camera_name_entry.bind("<KeyRelease>", self._on_field_change)
        
        # Help text
        ttk.Label(
            setup_grid, 
            text="Camera Name is for identifying specific equipment (e.g., 'fx30')",
            font=("Arial", 8, "italic"),
            foreground="#888888"
        ).grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        # Configure grid columns to expand
        setup_grid.columnconfigure(1, weight=1)
    
    def _create_technical_info_section(self, parent_frame):
        """Create the technical info section with Size, Type, Move, Equip."""
        # Grid for the technical info
        tech_grid = ttk.Frame(parent_frame)
        tech_grid.pack(fill="x", padx=10, pady=10)
        
        # SIZE
        ttk.Label(tech_grid, text="SIZE").grid(row=0, column=0, padx=10, pady=5)
        self.size_var = tk.StringVar()
        size_combo = ttk.Combobox(tech_grid, textvariable=self.size_var)
        size_combo['values'] = tuple(sorted(self.custom_values['size']))
        size_combo.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        size_combo.bind("<KeyRelease>", lambda e: self._add_custom_value_and_save('size', self.size_var.get()))
        size_combo.bind("<<ComboboxSelected>>", self._on_field_change)
        
        # TYPE
        ttk.Label(tech_grid, text="TYPE").grid(row=0, column=1, padx=10, pady=5)
        self.type_var = tk.StringVar()
        type_combo = ttk.Combobox(tech_grid, textvariable=self.type_var)
        type_combo['values'] = tuple(sorted(self.custom_values['type']))
        type_combo.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        type_combo.bind("<KeyRelease>", lambda e: self._add_custom_value_and_save('type', self.type_var.get()))
        type_combo.bind("<<ComboboxSelected>>", self._on_field_change)
        
        # MOVE
        ttk.Label(tech_grid, text="MOVE").grid(row=0, column=2, padx=10, pady=5)
        self.move_var = tk.StringVar(value="STATIC")
        move_combo = ttk.Combobox(tech_grid, textvariable=self.move_var)
        move_combo['values'] = tuple(sorted(self.custom_values['move']))
        move_combo.grid(row=1, column=2, padx=10, pady=5, sticky="ew")
        move_combo.bind("<KeyRelease>", lambda e: self._add_custom_value_and_save('move', self.move_var.get()))
        move_combo.bind("<<ComboboxSelected>>", self._on_field_change)
        
        # EQUIP
        ttk.Label(tech_grid, text="EQUIP").grid(row=0, column=3, padx=10, pady=5)
        self.equip_var = tk.StringVar(value="STICKS")
        equip_combo = ttk.Combobox(tech_grid, textvariable=self.equip_var)
        equip_combo['values'] = tuple(sorted(self.custom_values['equip']))
        equip_combo.grid(row=1, column=3, padx=10, pady=5, sticky="ew")
        equip_combo.bind("<KeyRelease>", lambda e: self._add_custom_value_and_save('equip', self.equip_var.get()))
        equip_combo.bind("<<ComboboxSelected>>", self._on_field_change)
        
        # Help text
        help_text = ttk.Label(
            tech_grid, 
            text="You can type custom values in these fields to add them to the dropdown list.",
            font=("Arial", 8, "italic"),
            foreground="#888888"
        )
        help_text.grid(row=2, column=0, columnspan=4, sticky="w", padx=10, pady=5)
        
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
    
    def _create_shot_list_section(self, parent_frame):
        """Create the section for shot list specific information."""
        # Grid for shot list info
        shot_list_grid = ttk.Frame(parent_frame)
        shot_list_grid.pack(fill="x", padx=10, pady=10)
        
        # Shot Time
        ttk.Label(shot_list_grid, text="Shot Time (min/hrs):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.shot_time_var = tk.StringVar()
        shot_time_entry = ttk.Entry(shot_list_grid, textvariable=self.shot_time_var)
        shot_time_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        shot_time_entry.bind("<FocusOut>", self._on_field_change)
        shot_time_entry.bind("<KeyRelease>", self._on_field_change)
        
        # Subject
        ttk.Label(shot_list_grid, text="Subject:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.subject_var = tk.StringVar()
        subject_entry = ttk.Entry(shot_list_grid, textvariable=self.subject_var)
        subject_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        subject_entry.bind("<FocusOut>", self._on_field_change)
        subject_entry.bind("<KeyRelease>", self._on_field_change)
        
        # Help text
        help_text = ttk.Label(
            shot_list_grid,
            text="Subject refers to who is on screen (e.g., 'John, Mary')",
            font=("Arial", 8, "italic"),
            foreground="#888888"
        )
        help_text.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        # Audio Notes
        ttk.Label(shot_list_grid, text="Audio Notes:").grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        
        # Custom styled text widget for audio notes
        self.audio_notes_entry = tk.Text(
            shot_list_grid, 
            wrap=tk.WORD, 
            height=3, 
            width=40, 
            bg=self.input_bg_color, 
            fg=self.text_color, 
            insertbackground=self.text_color
        )
        self.audio_notes_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        self.audio_notes_entry.bind("<KeyRelease>", self._on_text_change)
        self.audio_notes_entry.bind("<FocusOut>", self._on_text_change)
        
        # Audio notes explanation
        help_text = ttk.Label(
            shot_list_grid,
            text="Use this for sound design notes, dialogue cues, or music direction",
            font=("Arial", 8, "italic"),
            foreground="#888888"
        )
        help_text.grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        # Configure grid columns to expand
        shot_list_grid.columnconfigure(1, weight=1)
    
    def _create_action_info_section(self, parent_frame):
        """Create the action information section."""
        # Grid for action info
        action_grid = ttk.Frame(parent_frame)
        action_grid.pack(fill="x", padx=10, pady=10)
        
        # Action
        ttk.Label(action_grid, text="Action:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.action_var = tk.StringVar()
        action_entry = ttk.Entry(action_grid, textvariable=self.action_var)
        action_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        action_entry.bind("<FocusOut>", self._on_field_change)
        action_entry.bind("<KeyRelease>", self._on_field_change)
        
        # Background
        ttk.Label(action_grid, text="Background:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.bgd_var = tk.StringVar(value="No")
        bgd_frame = ttk.Frame(action_grid)
        bgd_frame.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Radiobutton(bgd_frame, text="Yes", variable=self.bgd_var, value="Yes", 
                       command=lambda: self._toggle_bgd_notes(True)).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(bgd_frame, text="No", variable=self.bgd_var, value="No", 
                       command=lambda: self._toggle_bgd_notes(False)).pack(side=tk.LEFT, padx=5)
        
        # Background notes (initially hidden)
        self.bgd_notes_label = ttk.Label(action_grid, text="Background Notes:")
        self.bgd_notes_var = tk.StringVar()
        self.bgd_notes_entry = ttk.Entry(action_grid, textvariable=self.bgd_notes_var)
        self.bgd_notes_entry.bind("<FocusOut>", self._on_field_change)
        self.bgd_notes_entry.bind("<KeyRelease>", self._on_field_change)
        
        # Description
        ttk.Label(action_grid, text="Description:").grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        self.description_var = tk.StringVar()
        
        # Custom text widget with improved styling
        self.description_entry = tk.Text(
            action_grid, 
            wrap=tk.WORD, 
            height=4, 
            width=40, 
            bg=self.input_bg_color, 
            fg=self.text_color, 
            insertbackground=self.text_color
        )
        self.description_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        self.description_entry.bind("<KeyRelease>", self._on_text_change)
        self.description_entry.bind("<FocusOut>", self._on_text_change)
        
        # Notes
        ttk.Label(action_grid, text="Notes:").grid(row=4, column=0, sticky="nw", padx=5, pady=5)
        self.notes_var = tk.StringVar()
        
        # Custom styled text widget
        self.notes_entry = tk.Text(
            action_grid, 
            wrap=tk.WORD, 
            height=4, 
            width=40, 
            bg=self.input_bg_color, 
            fg=self.text_color, 
            insertbackground=self.text_color
        )
        self.notes_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        self.notes_entry.bind("<KeyRelease>", self._on_text_change)
        self.notes_entry.bind("<FocusOut>", self._on_text_change)
        
        # Configure grid columns
        action_grid.columnconfigure(1, weight=1)
    
    def _create_additional_info_section(self, parent_frame):
        """Create the section for hair/makeup, props, and VFX."""
        # Grid for additional info
        additional_grid = ttk.Frame(parent_frame)
        additional_grid.pack(fill="x", padx=10, pady=10)
        
        # Hair/Makeup with Yes/No toggle
        ttk.Label(additional_grid, text="Hair/Makeup/Wardrobe:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.hair_makeup_enabled_var = tk.StringVar(value="No")
        hair_makeup_frame = ttk.Frame(additional_grid)
        hair_makeup_frame.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Radiobutton(
            hair_makeup_frame, 
            text="Yes", 
            variable=self.hair_makeup_enabled_var, 
            value="Yes", 
            command=lambda: self._toggle_hair_makeup_notes(True)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            hair_makeup_frame, 
            text="No", 
            variable=self.hair_makeup_enabled_var, 
            value="No", 
            command=lambda: self._toggle_hair_makeup_notes(False)
        ).pack(side=tk.LEFT, padx=5)
        
        # Hair/Makeup notes (initially hidden)
        self.hair_makeup_notes_label = ttk.Label(additional_grid, text="H/M/W Notes:")
        self.hair_makeup_var = tk.StringVar()
        
        # Custom styled text widget
        self.hair_makeup_entry = tk.Text(
            additional_grid, 
            wrap=tk.WORD, 
            height=3, 
            width=40, 
            bg=self.input_bg_color, 
            fg=self.text_color, 
            insertbackground=self.text_color
        )
        self.hair_makeup_entry.bind("<KeyRelease>", self._on_text_change)
        self.hair_makeup_entry.bind("<FocusOut>", self._on_text_change)
        
        # Props with Yes/No toggle
        ttk.Label(additional_grid, text="Props:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.props_enabled_var = tk.StringVar(value="No")
        props_frame = ttk.Frame(additional_grid)
        props_frame.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Radiobutton(
            props_frame, 
            text="Yes", 
            variable=self.props_enabled_var, 
            value="Yes", 
            command=lambda: self._toggle_props_notes(True)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            props_frame, 
            text="No", 
            variable=self.props_enabled_var, 
            value="No", 
            command=lambda: self._toggle_props_notes(False)
        ).pack(side=tk.LEFT, padx=5)
        
        # Props notes (initially hidden)
        self.props_notes_label = ttk.Label(additional_grid, text="Props Notes:")
        self.props_var = tk.StringVar()
        
        # Custom styled text widget
        self.props_entry = tk.Text(
            additional_grid, 
            wrap=tk.WORD, 
            height=3, 
            width=40, 
            bg=self.input_bg_color, 
            fg=self.text_color, 
            insertbackground=self.text_color
        )
        self.props_entry.bind("<KeyRelease>", self._on_text_change)
        self.props_entry.bind("<FocusOut>", self._on_text_change)
        
        # VFX with Yes/No toggle
        ttk.Label(additional_grid, text="VFX:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.vfx_enabled_var = tk.StringVar(value="No")
        vfx_frame = ttk.Frame(additional_grid)
        vfx_frame.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Radiobutton(
            vfx_frame, 
            text="Yes", 
            variable=self.vfx_enabled_var, 
            value="Yes", 
            command=lambda: self._toggle_vfx_notes(True)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            vfx_frame, 
            text="No", 
            variable=self.vfx_enabled_var, 
            value="No", 
            command=lambda: self._toggle_vfx_notes(False)
        ).pack(side=tk.LEFT, padx=5)
        
        # VFX notes (initially hidden)
        self.vfx_notes_label = ttk.Label(additional_grid, text="VFX Notes:")
        self.vfx_var = tk.StringVar()
        
        # Custom styled text widget
        self.vfx_entry = tk.Text(
            additional_grid, 
            wrap=tk.WORD, 
            height=3, 
            width=40, 
            bg=self.input_bg_color, 
            fg=self.text_color, 
            insertbackground=self.text_color
        )
        self.vfx_entry.bind("<KeyRelease>", self._on_text_change)
        self.vfx_entry.bind("<FocusOut>", self._on_text_change)
        
        # Configure grid columns
        additional_grid.columnconfigure(1, weight=1)
        
        # Status label instead of save button
        self.status_label = ttk.Label(
            parent_frame, 
            text="Changes are saved automatically",
            font=("Arial", 8, "italic"),
            foreground="#888888"
        )
        self.status_label.pack(side=tk.RIGHT, padx=10, pady=10)
    
    def _on_field_change(self, event=None):
        """Handle field changes for auto-save."""
        self._update_full_shot_number()
        self._auto_save()
    
    def _on_text_change(self, event=None):
        """Handle text widget changes for auto-save."""
        # Delay auto-save slightly to avoid excessive updates during typing
        if hasattr(self, "_text_change_timer") and self._text_change_timer:
            self.after_cancel(self._text_change_timer)
        
        self._text_change_timer = self.after(500, self._auto_save)
    
    def _update_full_shot_number(self):
        """Update the full shot number display."""
        scene = self.scene_number_var.get() or "1"
        shot = self.shot_number_var.get() or ""
        self.full_shot_var.set(f"{scene}{shot}")
    
    def _add_custom_value_and_save(self, field, value):
        """Add a custom value to the dropdown if it's not already there and save."""
        # Add the value to the dropdown
        self._add_custom_value(field, value)
        
        # Auto-save the panel
        self._on_text_change()
    
    def _add_custom_value(self, field, value):
        """Add a custom value to the dropdown if it's not already there."""
        if value and value not in self.custom_values[field]:
            self.custom_values[field].add(value)
            self.tech_combos[field]['values'] = tuple(sorted(self.custom_values[field]))
    
    def _toggle_bgd_notes(self, show):
        """Show/hide background notes field based on bgd selection."""
        if show:
            # Show background notes field
            self.bgd_notes_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
            self.bgd_notes_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        else:
            # Hide background notes field
            self.bgd_notes_label.grid_forget()
            self.bgd_notes_entry.grid_forget()
            # Clear the notes
            self.bgd_notes_var.set("")
        
        # Save the changes
        self._auto_save()

    def _toggle_hair_makeup_notes(self, show):
        """Show/hide hair/makeup notes field based on selection."""
        if show:
            # Show hair/makeup notes field
            self.hair_makeup_notes_label.grid(row=1, column=0, sticky="nw", padx=5, pady=5)
            self.hair_makeup_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        else:
            # Hide hair/makeup notes field
            self.hair_makeup_notes_label.grid_forget()
            self.hair_makeup_entry.grid_forget()
            # Clear the text
            self.hair_makeup_entry.delete("1.0", "end")
            self.hair_makeup_var.set("")
        
        # Save the changes
        self._auto_save()

    def _toggle_props_notes(self, show):
        """Show/hide props notes field based on selection."""
        if show:
            # Show props notes field
            self.props_notes_label.grid(row=3, column=0, sticky="nw", padx=5, pady=5)
            self.props_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        else:
            # Hide props notes field
            self.props_notes_label.grid_forget()
            self.props_entry.grid_forget()
            # Clear the text
            self.props_entry.delete("1.0", "end")
            self.props_var.set("")
        
        # Save the changes
        self._auto_save()

    def _toggle_vfx_notes(self, show):
        """Show/hide VFX notes field based on selection."""
        if show:
            # Show VFX notes field
            self.vfx_notes_label.grid(row=5, column=0, sticky="nw", padx=5, pady=5)
            self.vfx_entry.grid(row=5, column=1, sticky="ew", padx=5, pady=5)
        else:
            # Hide VFX notes field
            self.vfx_notes_label.grid_forget()
            self.vfx_entry.grid_forget()
            # Clear the text
            self.vfx_entry.delete("1.0", "end")
            self.vfx_var.set("")
        
        # Save the changes
        self._auto_save()
    
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
                
                # Auto-save
                self._auto_save()
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
    
    def _auto_save(self):
        """Auto-save changes to the current panel."""
        if not self.current_panel:
            return
        
        # Update status label
        self.status_label.config(text="Saving changes...")
        
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
        
        # Get values for additional fields using the Yes/No toggles
        self.current_panel.hair_makeup_enabled = self.hair_makeup_enabled_var.get()
        if self.hair_makeup_enabled_var.get() == "Yes":
            self.current_panel.hair_makeup = self.hair_makeup_entry.get("1.0", "end-1c")
        else:
            self.current_panel.hair_makeup = ""
            
        self.current_panel.props_enabled = self.props_enabled_var.get()
        if self.props_enabled_var.get() == "Yes":
            self.current_panel.props = self.props_entry.get("1.0", "end-1c")
        else:
            self.current_panel.props = ""
            
        self.current_panel.vfx_enabled = self.vfx_enabled_var.get()
        if self.vfx_enabled_var.get() == "Yes":
            self.current_panel.vfx = self.vfx_entry.get("1.0", "end-1c")
        else:
            self.current_panel.vfx = ""
        # Set new shot list fields
        self.current_panel.setup_number = self.setup_number_var.get() or "1"
        self.current_panel.camera_name = self.camera_name_var.get()
        self.current_panel.shot_time = self.shot_time_var.get()
        self.current_panel.subject = self.subject_var.get()
        self.current_panel.audio_notes = self.audio_notes_entry.get("1.0", "end-1c")
        
        # Notify about the update
        if self.on_panel_update:
            self.on_panel_update(self.current_panel)
        
        # Update status label
        self.status_label.config(text="Changes saved automatically")
        # Reset after a delay
        self.after(2000, lambda: self.status_label.config(text="Changes are saved automatically"))
    
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
        
        # Set new shot list fields
        self.setup_number_var.set(panel.setup_number if hasattr(panel, 'setup_number') else "1")
        self.camera_name_var.set(panel.camera_name if hasattr(panel, 'camera_name') else "")
        self.shot_time_var.set(panel.shot_time if hasattr(panel, 'shot_time') else "")
        self.subject_var.set(panel.subject if hasattr(panel, 'subject') else "")
        
        # Set audio notes
        self.audio_notes_entry.delete("1.0", "end")
        if hasattr(panel, 'audio_notes') and panel.audio_notes:
            self.audio_notes_entry.insert("1.0", panel.audio_notes)
        
        # Toggle background notes visibility
        self._toggle_bgd_notes(panel.bgd == "Yes")
        
        # Set text in Text widgets
        self.description_entry.delete("1.0", "end")
        self.description_entry.insert("1.0", panel.description)
        
        self.notes_entry.delete("1.0", "end")
        self.notes_entry.insert("1.0", panel.notes)
        
        # Handle additional fields with Yes/No toggles
        
        # Hair/makeup
        if hasattr(panel, 'hair_makeup_enabled'):
            self.hair_makeup_enabled_var.set(panel.hair_makeup_enabled)
        else:
            # If the panel doesn't have this attribute yet, set based on content
            self.hair_makeup_enabled_var.set("Yes" if panel.hair_makeup else "No")
            
        self.hair_makeup_entry.delete("1.0", "end")
        self.hair_makeup_entry.insert("1.0", panel.hair_makeup)
        self._toggle_hair_makeup_notes(self.hair_makeup_enabled_var.get() == "Yes")
        
        # Props
        if hasattr(panel, 'props_enabled'):
            self.props_enabled_var.set(panel.props_enabled)
        else:
            # If the panel doesn't have this attribute yet, set based on content
            self.props_enabled_var.set("Yes" if panel.props else "No")
            
        self.props_entry.delete("1.0", "end")
        self.props_entry.insert("1.0", panel.props)
        self._toggle_props_notes(self.props_enabled_var.get() == "Yes")
        
        # VFX
        if hasattr(panel, 'vfx_enabled'):
            self.vfx_enabled_var.set(panel.vfx_enabled)
        else:
            # If the panel doesn't have this attribute yet, set based on content
            self.vfx_enabled_var.set("Yes" if panel.vfx else "No")
            
        self.vfx_entry.delete("1.0", "end")
        self.vfx_entry.insert("1.0", panel.vfx)
        self._toggle_vfx_notes(self.vfx_enabled_var.get() == "Yes")
        
        # Update image display
        self._update_image_display()
