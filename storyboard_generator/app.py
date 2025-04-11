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
