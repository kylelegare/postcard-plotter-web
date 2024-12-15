import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

class FontParser:
    def __init__(self):
        """Initialize font parser with the custom single-stroke font"""
        self.font_data = {}  # Will store parsed font data
        self.load_font()
    
    def load_font(self):
        """Initialize with basic character shapes for testing"""
        try:
            logger.debug("Loading development font")
            
            # Initialize font data dictionary
            self.font_data = {}
            
            # Create simple character shapes
            # Each character is represented by a series of paths that form its shape
            
            # Letter 'A'
            self.font_data['A'] = [
                [(0, 40), (20, 0), (40, 40)],  # Outer lines
                [(10, 20), (30, 20)]  # Cross bar
            ]
            
            # Default shape for other characters - simple rectangle
            for char in range(32, 127):  # ASCII printable chars
                if chr(char) not in self.font_data:
                    char_str = chr(char)
                    if char_str.isalnum():  # Letters and numbers
                        self.font_data[char_str] = [
                            [(0, 0), (30, 0), (30, 40), (0, 40), (0, 0)]  # Rectangle
                        ]
                    elif char_str == ' ':
                        self.font_data[char_str] = []  # Empty path for space
                    else:
                        self.font_data[char_str] = [
                            [(0, 0), (20, 0), (20, 20), (0, 20), (0, 0)]  # Smaller rectangle for symbols
                        ]
            
            logger.info(f"Created development font with {len(self.font_data)} characters")
            
        except Exception as e:
            logger.error(f"Error loading font: {str(e)}")
            # Provide minimal fallback in case of complete failure
            self.font_data = {' ': []}
            raise
            
        except Exception as e:
            logger.error(f"Error loading font file: {str(e)}")
            raise
    
    def get_text_paths(self, text: str, font_size: int) -> List[List[Dict[str, float]]]:
        """Convert text to plottable paths using the loaded font
        
        Args:
            text: The text to convert
            font_size: Font size in points
        
        Returns:
            List of paths, where each path is a list of points
        """
        paths = []
        x_pos = 0  # Starting at origin, canvas will handle margins
        y_pos = 0  # Starting at origin, canvas will handle centering
        
        scale = font_size / 40  # Scale relative to base font size
        
        for char in text:
            if char == '\n':
                x_pos = 0
                y_pos += font_size * 1.5
                continue
                
            if char in self.font_data:
                char_paths = self.font_data[char]
                for stroke in char_paths:
                    path = []
                    for x, y in stroke:
                        path.append({
                            'x': x_pos + x * scale,
                            'y': y_pos + y * scale
                        })
                    paths.append(path)
                x_pos += (self.get_char_width(char) + 5) * scale  # Add consistent spacing
            else:
                # For unsupported characters, add space
                x_pos += 15 * scale
        
        return paths
    
    def get_char_width(self, char: str) -> float:
        """Get the width of a character in font units"""
        # This is a placeholder - implement based on actual font metrics
        return 30
    
    def get_text_bounds(self, text: str, font_size: int) -> Dict[str, float]:
        """Calculate the bounding box of the text
        
        Args:
            text: The text to measure
            font_size: Font size in points
        
        Returns:
            Dictionary with width and height of text bounds
        """
        scale = font_size / 72
        
        # Split text into lines
        lines = text.split('\n')
        max_width = 0
        total_height = 0
        
        for line in lines:
            width = sum(self.get_char_width(c) * scale for c in line)
            width += (len(line) - 1) * 2 * scale  # Add character spacing
            max_width = max(max_width, width)
            total_height += font_size * 1.5
        
        return {
            'width': max_width,
            'height': total_height
        }
