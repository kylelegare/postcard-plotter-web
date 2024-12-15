import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

class FontParser:
    def __init__(self):
        """Initialize font parser with the custom single-stroke font"""
        self.font_data = {}  # Will store parsed font data
        self.load_font()
    
    def load_font(self):
        """Load and parse the custom single-stroke font file"""
        try:
            logger.debug("Loading font file")
            logger.info("Using development fallback for font paths")
            
            # Initialize font data dictionary
            self.font_data = {}
            
            # Create simple line patterns for testing
            # Uppercase letters (A-Z) - vertical strokes
            for char in range(65, 91):
                char_str = chr(char)
                # Create an "L" shape for each uppercase letter
                self.font_data[char_str] = [
                    [(0, 0), (0, 40)],  # Vertical line
                    [(0, 40), (20, 40)]  # Horizontal line at top
                ]
            
            # Lowercase letters (a-z) - horizontal strokes
            for char in range(97, 123):
                char_str = chr(char)
                # Create a simple horizontal line with a small vertical at start
                self.font_data[char_str] = [
                    [(0, 10), (0, 25)],  # Small vertical line
                    [(0, 25), (20, 25)]  # Horizontal line
                ]
            
            # Numbers (0-9) - box shapes
            for char in range(48, 58):
                char_str = chr(char)
                self.font_data[char_str] = [
                    [(0, 0), (20, 0), (20, 40), (0, 40), (0, 0)]  # Box shape
                ]
            
            # Special characters
            self.font_data[' '] = []  # Space - empty path
            self.font_data['.'] = [[(0, 0), (0, 2)]]  # Period - tiny vertical line
            self.font_data[','] = [[(0, -5), (0, 2)]]  # Comma - tiny vertical line with tail
            self.font_data['!'] = [[(0, 0), (0, 30)], [(0, 35), (0, 40)]]  # Exclamation mark
            self.font_data['?'] = [[(0, 40), (20, 40), (20, 20), (10, 20)], [(10, 0), (10, 5)]]  # Question mark
            
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
