import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

class FontParser:
    def __init__(self):
        """Initialize font parser with the custom single-stroke font"""
        self.font_data = {}  # Will store parsed font data
        self.vowels = 'aeiou'  # Vowels for mistake generation
        self.mistake_frequency = 0  # Default: no mistakes
        self.load_font()
        
    def set_mistake_frequency(self, frequency: float):
        """Set the frequency of intentional mistakes (0.0 to 1.0)"""
        self.mistake_frequency = max(0.0, min(1.0, frequency))
        
    def generate_mistake(self, word: str) -> tuple[str, bool]:
        """Generate a potential mistake for a word
        
        Args:
            word: The word to potentially modify
            
        Returns:
            Tuple of (word, was_modified)
        """
        import random
        
        # Skip words with capitals, punctuation, or if too short
        if (len(word) <= 2 or 
            not word.islower() or 
            not word.isalpha()):
            return word, False
            
        # Check if we should generate a mistake based on frequency
        if random.random() > self.mistake_frequency:
            return word, False
            
        # Find vowels in the word
        vowel_positions = [i for i, char in enumerate(word) if char in self.vowels]
        if not vowel_positions:
            return word, False
            
        # Select a random vowel position and replacement
        pos = random.choice(vowel_positions)
        current_vowel = word[pos]
        replacement = random.choice([v for v in self.vowels if v != current_vowel])
        
        # Create the mistake
        return (word[:pos] + replacement + word[pos+1:]), True
    
    def load_font(self):
        """Initialize with basic character shapes for testing"""
        try:
            logger.debug("Loading development font")
            
            # Initialize font data dictionary
            self.font_data = {}
            
            # Create simple character shapes
            # Each character is represented by a series of paths that form its shape
            
            # Basic single-stroke letters
            # Letter 'A'
            self.font_data['A'] = [
                [(0, 40), (20, 0), (40, 40)],  # Outer lines
                [(10, 20), (30, 20)]  # Cross bar
            ]
            
            # Letter 'H'
            self.font_data['H'] = [
                [(0, 0), (0, 40)],  # Left vertical
                [(0, 20), (30, 20)],  # Middle bar
                [(30, 0), (30, 40)]  # Right vertical
            ]
            
            # Letter 'I'
            self.font_data['I'] = [
                [(15, 0), (15, 40)]  # Single vertical line
            ]
            
            # Letter 'T'
            self.font_data['T'] = [
                [(0, 0), (30, 0)],  # Top bar
                [(15, 0), (15, 40)]  # Vertical line
            ]
            
            # Default simple single-stroke shapes for other characters
            for char in range(32, 127):  # ASCII printable chars
                if chr(char) not in self.font_data:
                    char_str = chr(char)
                    if char_str == ' ':
                        self.font_data[char_str] = []  # Empty path for space
                    else:
                        # Simple vertical line for unimplemented characters
                        self.font_data[char_str] = [
                            [(15, 0), (15, 40)]
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
        
        # Track mistake positions for strike-through
        mistake_positions = []  # List of (x, y, width) for mistakes
        
        # Base size is 40 units, scale everything relative to requested font size
        scale = font_size / 40
        char_width = 30 * scale
        char_height = 40 * scale
        max_width = 600 - (margin * 2)  # Max width with margins
        
        logger.debug(f"Converting text: '{text}' at font size {font_size} (scale: {scale})")
        logger.debug(f"Mistake frequency set to: {self.mistake_frequency}")
        
        # Split text into words for wrapping
        words = text.split()
        current_line = []
        current_width = 0
        line_x = x_pos
        
        for word in words:
            # Generate potential mistake
            modified_word, is_mistake = self.generate_mistake(word)
            logger.debug(f"Word: {word}, Modified: {modified_word}, Is mistake: {is_mistake}")
            
            # Calculate word width
            word_width = len(modified_word) * char_width * 1.2
            
            # Add word to current line
            test_line = (current_line + [modified_word]) if current_line else [modified_word]
            test_width = sum(len(w) * char_width * 1.2 for w in test_line)
            
            if test_width > max_width and current_line:
                # Process current line
                line_x = x_pos
                for word_to_render in current_line:
                    if word_to_render != ' ':
                        word_start_x = line_x
                        # Get character's stroke paths
                        for char in word_to_render:
                            char_paths = self.font_data.get(char, self.font_data['I'])
                            
                            # Transform and scale each path
                            for stroke in char_paths:
                                path = []
                                for x, y in stroke:
                                    path.append({
                                        'x': line_x + (x * scale),
                                        'y': y_pos + (y * scale)
                                    })
                                paths.append(path)
                            line_x += char_width * 1.2
                        
                        # If this word was a mistake, record its position
                        if word_to_render == modified_word and is_mistake:
                            mistake_positions.append({
                                'x': word_start_x,
                                'y': y_pos,
                                'width': word_width
                            })
                            logger.debug(f"Added mistake position for word: {word_to_render}")
                    
                    line_x += char_width * 0.5  # Space between words
                
                # Move to next line
                y_pos += char_height * 1.5
                current_line = [modified_word]
                current_width = len(modified_word) * char_width * 1.2
            else:
                current_line.append(modified_word)
                current_width = test_width

        # Process remaining line if any
        if current_line:
            line_x = x_pos
            for word_to_render in current_line:
                if word_to_render != ' ':
                    for char in word_to_render:
                        char_paths = self.font_data.get(char, self.font_data['I'])
                        for stroke in char_paths:
                            path = []
                            for x, y in stroke:
                                path.append({
                                    'x': line_x + (x * scale),
                                    'y': y_pos + (y * scale)
                                })
                            paths.append(path)
                        line_x += char_width * 1.2
                line_x += char_width * 0.5  # Space between words


        # Add strike-through paths for mistakes
        for mistake in mistake_positions:
            # Create strike-through line (slightly diagonal for natural look)
            strike_y = mistake['y'] + (char_height * 0.4)  # Strike through middle of text
            strike_path = [
                {'x': mistake['x'], 'y': strike_y},
                {'x': mistake['x'] + mistake['width'], 'y': strike_y + (char_height * 0.2)}
            ]
            paths.append(strike_path)
            logger.debug(f"Added strike-through at y={strike_y} with width={mistake['width']}")
        
        logger.debug(f"Generated {len(paths)} paths ({len(mistake_positions)} mistakes)")
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