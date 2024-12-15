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
        margin = 100  # 1-inch margin at 100 DPI
        x_pos = margin
        y_pos = margin
        
        # Base size is 40 units, scale everything relative to requested font size
        scale = font_size / 40
        char_width = 30 * scale
        char_height = 40 * scale
        max_width = 600 - (margin * 2)  # Max width with margins
        
        logger.debug(f"Converting text: '{text}' at font size {font_size} (scale: {scale})")
        
        # Split text into words for wrapping
        words = text.split()
        current_line = []
        current_width = 0
        
        for word in words:
            word_width = len(word) * char_width * 1.2  # Include character spacing
            
            # Check if adding this word would exceed max width
            if current_width + word_width > max_width and current_line:
                # Process current line
                line_x = x_pos
                for char in ' '.join(current_line):
                    if char != ' ':
                        # Create character path
                        char_path = [
                            {'x': line_x, 'y': y_pos},  # Top left
                            {'x': line_x + char_width, 'y': y_pos},  # Top right
                            {'x': line_x + char_width, 'y': y_pos + char_height},  # Bottom right
                            {'x': line_x, 'y': y_pos + char_height},  # Bottom left
                            {'x': line_x, 'y': y_pos}  # Back to start
                        ]
                        paths.append(char_path)
                    line_x += char_width * 1.2
                
                # Move to next line
                y_pos += char_height * 1.5
                current_line = [word]
                current_width = word_width
            else:
                current_line.append(word)
                current_width += word_width
        
        # Process remaining line if any
        if current_line:
            line_x = x_pos
            for char in ' '.join(current_line):
                if char != ' ':
                    char_path = [
                        {'x': line_x, 'y': y_pos},  # Top left
                        {'x': line_x + char_width, 'y': y_pos},  # Top right
                        {'x': line_x + char_width, 'y': y_pos + char_height},  # Bottom right
                        {'x': line_x, 'y': y_pos + char_height},  # Bottom left
                        {'x': line_x, 'y': y_pos}  # Back to start
                    ]
                    paths.append(char_path)
                line_x += char_width * 1.2
        
        logger.debug(f"Generated {len(paths)} character paths")
        return paths
        
        logger.debug(f"Generated {len(paths)} paths")
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