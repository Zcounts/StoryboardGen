# storyboard_generator/panel.py
import os
import uuid
from PIL import Image, ImageTk
from datetime import datetime

class Panel:
    """
    Represents a single storyboard panel with an image and associated metadata.
    """
    
    def __init__(self):
        """Initialize a new panel with default values."""
        # Unique identifier for the panel
        self.id = str(uuid.uuid4())
        
        # Basic panel information
        self.shot_number = ""  # Will be a letter (A, B, C, etc.)
        self.scene_number = "1"  # Default to scene 1
        self.description = ""
        self.notes = ""
        
        # Additional metadata
        self.camera = "Camera 1"
        self.lens = ""  # e.g., 85mm
        self.size = ""  # e.g., CLOSE UP, WIDE, MEDIUM
        self.type = ""  # e.g., OTS, BAR LVL, EYE LVL
        self.move = "STATIC"  # e.g., STATIC, PUSH
        self.equip = "STICKS"  # e.g., STICKS, GIMBAL
        self.action = ""
        
        # Background info
        self.bgd = "No"  # Yes/No
        self.bgd_notes = ""  # Only used when bgd is "Yes"
        
        # Additional fields (original)
        self.hair_makeup = ""  # Hair and makeup notes
        self.props = ""  # Props notes
        self.vfx = ""  # VFX notes
        
        # New fields for shot list
        self.setup_number = "1"  # Setup grouping number
        self.camera_name = ""    # Custom camera name (e.g. "fx30")
        self.shot_time = ""      # Time to shoot (minutes/hours)
        self.audio_notes = ""    # Audio notes
        self.subject = ""        # Who's on screen
        
        # Image properties
        self.image_path = None
        self.image = None
        self.thumbnail = None
        
        # Order in storyboard
        self.order = 0
    
    def set_image(self, image_path, project_dir=None):
        """
        Set the image for this panel.
        
        Args:
            image_path (str): Path to the image file
            project_dir (str, optional): Project directory for relative path storage
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Store the original path
        self.original_image_path = image_path
        
        # If we have a project directory, copy the image to it and store the relative path
        if project_dir:
            # Create images directory if it doesn't exist
            images_dir = os.path.join(project_dir, "images")
            os.makedirs(images_dir, exist_ok=True)
            
            # Generate a filename based on the panel ID
            filename = f"{self.id}_{os.path.basename(image_path)}"
            dest_path = os.path.join(images_dir, filename)
            
            # Copy the image file
            import shutil
            shutil.copy2(image_path, dest_path)
            
            # Store the relative path
            self.image_path = os.path.join("images", filename)
        else:
            # Store the absolute path if no project directory
            self.image_path = image_path
        
        # Load the image
        self._load_image()
        
        # Clear any existing thumbnail so it will be regenerated
        self.thumbnail = None
    
    def _load_image(self):
        """Load the image from the saved path."""
        if not self.image_path or not os.path.exists(self.image_path):
            return
        
        try:
            # Load the full image
            self.image = Image.open(self.image_path)
            
            # Create a thumbnail for display in the UI
            thumbnail_size = (200, 150)  # Adjust size as needed
            self.thumbnail = self.image.copy()
            self.thumbnail.thumbnail(thumbnail_size)
        except Exception as e:
            print(f"Error loading image: {e}")
    
    def get_display_image(self, size=None):
        """
        Get the panel image resized for display.
        
        Args:
            size (tuple, optional): Width and height to resize to
        
        Returns:
            ImageTk.PhotoImage: The image ready for display in Tkinter
        """
        if not self.image:
            return None
        
        if size:
            # Resize the image while keeping the aspect ratio
            img_copy = self.image.copy()
            img_copy.thumbnail(size)
            return ImageTk.PhotoImage(img_copy)
        else:
            return ImageTk.PhotoImage(self.image)
    
    def get_thumbnail(self):
        """
        Get the panel thumbnail for display in the panel list.
        
        Returns:
            ImageTk.PhotoImage: The thumbnail image
        """
        if not self.thumbnail:
            return None
        
        # Create a thumbnail if we don't have one already
        if not self.image:
            return None
        
        # Create a thumbnail if we don't have one already
        if not self.thumbnail:
            thumbnail_size = (100, 75)  # Adjust size as needed
            self.thumbnail = self.image.copy()
            self.thumbnail.thumbnail(thumbnail_size)
        
        return ImageTk.PhotoImage(self.thumbnail)
    
    def get_full_shot_number(self):
        """
        Get the full shot number in format: sceneN-letter (e.g., 1A, 2B)
        
        Returns:
            str: The formatted shot number
        """
        if not self.shot_number:
            return f"{self.scene_number}"
        return f"{self.scene_number}{self.shot_number}"
    
    def to_dict(self):
        """
        Convert the panel to a dictionary for serialization.
        
        Returns:
            dict: The panel data as a dictionary
        """
        return {
            'id': self.id,
            'shot_number': self.shot_number,
            'scene_number': self.scene_number,
            'description': self.description,
            'notes': self.notes,
            'camera': self.camera,
            'lens': self.lens,
            'size': self.size,
            'type': self.type,
            'move': self.move,
            'equip': self.equip,
            'action': self.action,
            'bgd': self.bgd,
            'bgd_notes': self.bgd_notes,
            'hair_makeup': self.hair_makeup,
            'props': self.props,
            'vfx': self.vfx,
            'setup_number': self.setup_number,
            'camera_name': self.camera_name,
            'shot_time': self.shot_time,
            'audio_notes': self.audio_notes,
            'subject': self.subject,
            'image_path': self.image_path,
            'order': self.order,
            'last_modified': datetime.now().isoformat()
        }
    
    @classmethod
    def from_dict(cls, data, project_dir=None):
        """
        Create a panel from a dictionary.
        
        Args:
            data (dict): The panel data
            project_dir (str, optional): Project directory for resolving relative paths
        
        Returns:
            Panel: A new Panel instance
        """
        panel = cls()
        
        # Set basic properties
        panel.id = data.get('id', panel.id)
        panel.shot_number = data.get('shot_number', '')
        panel.scene_number = data.get('scene_number', '1')
        panel.description = data.get('description', '')
        panel.notes = data.get('notes', '')
        
        # Set additional metadata
        panel.camera = data.get('camera', 'Camera 1')
        panel.lens = data.get('lens', '')
        panel.size = data.get('size', '')
        panel.type = data.get('type', '')
        panel.move = data.get('move', 'STATIC')
        panel.equip = data.get('equip', 'STICKS')
        panel.action = data.get('action', '')
        panel.bgd = data.get('bgd', 'No')
        
        # Original additional fields
        panel.bgd_notes = data.get('bgd_notes', '')
        panel.hair_makeup = data.get('hair_makeup', '')
        panel.props = data.get('props', '')
        panel.vfx = data.get('vfx', '')
        
        # New fields for shot list
        panel.setup_number = data.get('setup_number', '1')
        panel.camera_name = data.get('camera_name', '')
        panel.shot_time = data.get('shot_time', '')
        panel.audio_notes = data.get('audio_notes', '')
        panel.subject = data.get('subject', '')
        
        # Set order
        panel.order = data.get('order', 0)
        
        # Handle image path
        image_path = data.get('image_path')
        if image_path and project_dir:
            # Convert relative path to absolute
            abs_path = os.path.join(project_dir, image_path)
            if os.path.exists(abs_path):
                panel.image_path = abs_path
                panel._load_image()
        elif image_path and os.path.exists(image_path):
            panel.image_path = image_path
            panel._load_image()
        
        return panel
