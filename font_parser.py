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
            word: The word to modify
            
        Returns:
            Tuple of (word, was_modified)
        """
        import random
        
        # Skip words with capitals, punctuation, or if too short
        if (len(word) <= 2 or 
            not word.islower() or 
            not word.isalpha()):
            logger.debug(f"Skipping word '{word}' - not eligible for mistakes")
            return word, False
            
        # Check if we should generate a mistake based on frequency
        if random.random() >= self.mistake_frequency:
            logger.debug(f"Skipping word '{word}' - random check failed")
            return word, False
            
        # Find vowels in the word
        vowel_positions = [i for i, char in enumerate(word) if char in self.vowels]
        if not vowel_positions:
            logger.debug(f"Skipping word '{word}' - no vowels found")
            return word, False
            
        # Select a random vowel position and replacement
        pos = random.choice(vowel_positions)
        current_vowel = word[pos]
        replacement = random.choice([v for v in self.vowels if v != current_vowel])
        
        modified = word[:pos] + replacement + word[pos+1:]
        logger.debug(f"Created mistake: '{word}' -> '{modified}'")
        return modified, True
    
    def load_font(self):
        """Initialize with basic character shapes for testing"""
        try:
            logger.debug("Loading development font")
            
            # Initialize font data dictionary
            self.font_data = {}
            
            # Create simple character shapes
            # Each character is represented by a series of paths that form its shape
            # All characters use a 40-unit height
            
            # Uppercase Letters
            # Letter 'A'
            self.font_data['A'] = [
                [(0, 40), (20, 0), (40, 40)],  # Outer lines
                [(10, 25), (30, 25)]  # Cross bar
            ]
            
            # Letter 'B'
            self.font_data['B'] = [
                [(0, 0), (0, 40)],  # Vertical
                [(0, 0), (20, 0), (25, 5), (25, 15), (20, 20)],  # Top loop
                [(0, 20), (20, 20), (30, 25), (30, 35), (20, 40), (0, 40)]  # Bottom loop
            ]
            
            # Letter 'C'
            self.font_data['C'] = [
                [(30, 5), (20, 0), (10, 0), (0, 10), (0, 30), (10, 40), (20, 40), (30, 35)]
            ]
            
            # Letter 'D'
            self.font_data['D'] = [
                [(0, 0), (0, 40)],  # Vertical
                [(0, 0), (20, 0), (30, 10), (30, 30), (20, 40), (0, 40)]  # Curve
            ]
            
            # Letter 'E'
            self.font_data['E'] = [
                [(30, 0), (0, 0), (0, 40), (30, 40)],  # Outline
                [(0, 20), (20, 20)]  # Middle bar
            ]
            
            # Letter 'F'
            self.font_data['F'] = [
                [(0, 40), (0, 0), (30, 0)],  # Vertical and top
                [(0, 20), (20, 20)]  # Middle bar
            ]
            
            # Letter 'G'
            self.font_data['G'] = [
                [(30, 5), (20, 0), (10, 0), (0, 10), (0, 30), (10, 40), (20, 40), (30, 35), (30, 20), (15, 20)]
            ]
            
            # Letter 'H'
            self.font_data['H'] = [
                [(0, 0), (0, 40)],  # Left vertical
                [(0, 20), (30, 20)],  # Middle bar
                [(30, 0), (30, 40)]  # Right vertical
            ]
            
            # Letter 'I'
            self.font_data['I'] = [
                [(0, 0), (20, 0)],  # Top bar
                [(10, 0), (10, 40)],  # Vertical line
                [(0, 40), (20, 40)]  # Bottom bar
            ]
            
            # Letter 'J'
            self.font_data['J'] = [
                [(20, 0), (20, 30), (15, 38), (5, 38), (0, 30)]
            ]
            
            # Letter 'K'
            self.font_data['K'] = [
                [(0, 0), (0, 40)],  # Vertical
                [(0, 20), (30, 0)],  # Upper diagonal
                [(0, 20), (30, 40)]  # Lower diagonal
            ]
            
            # Letter 'L'
            self.font_data['L'] = [
                [(0, 0), (0, 40), (30, 40)]
            ]
            
            # Letter 'M'
            self.font_data['M'] = [
                [(0, 40), (0, 0), (20, 20), (40, 0), (40, 40)]
            ]
            
            # Letter 'N'
            self.font_data['N'] = [
                [(0, 40), (0, 0), (30, 40), (30, 0)]
            ]
            
            # Letter 'O'
            self.font_data['O'] = [
                [(10, 0), (20, 0), (30, 10), (30, 30), (20, 40), (10, 40), (0, 30), (0, 10), (10, 0)]
            ]
            
            # Letter 'P'
            self.font_data['P'] = [
                [(0, 40), (0, 0), (20, 0), (30, 5), (30, 15), (20, 20), (0, 20)]
            ]
            
            # Letter 'Q'
            self.font_data['Q'] = [
                [(10, 0), (20, 0), (30, 10), (30, 30), (20, 40), (10, 40), (0, 30), (0, 10), (10, 0)],
                [(15, 25), (35, 45)]  # Tail
            ]
            
            # Letter 'R'
            self.font_data['R'] = [
                [(0, 40), (0, 0), (20, 0), (30, 5), (30, 15), (20, 20), (0, 20)],
                [(15, 20), (30, 40)]  # Leg
            ]
            
            # Letter 'S'
            self.font_data['S'] = [
                [(30, 5), (20, 0), (10, 0), (0, 5), (0, 15), (30, 25), (30, 35), (20, 40), (10, 40), (0, 35)]
            ]
            
            # Letter 'T'
            self.font_data['T'] = [
                [(0, 0), (40, 0)],  # Top bar
                [(20, 0), (20, 40)]  # Vertical line
            ]
            
            # Letter 'U'
            self.font_data['U'] = [
                [(0, 0), (0, 30), (10, 40), (20, 40), (30, 30), (30, 0)]
            ]
            
            # Letter 'V'
            self.font_data['V'] = [
                [(0, 0), (15, 40), (30, 0)]
            ]
            
            # Letter 'W'
            self.font_data['W'] = [
                [(0, 0), (10, 40), (20, 20), (30, 40), (40, 0)]
            ]
            
            # Letter 'X'
            self.font_data['X'] = [
                [(0, 0), (30, 40)],
                [(0, 40), (30, 0)]
            ]
            
            # Letter 'Y'
            self.font_data['Y'] = [
                [(0, 0), (15, 20), (30, 0)],
                [(15, 20), (15, 40)]
            ]
            
            # Letter 'Z'
            self.font_data['Z'] = [
                [(0, 0), (30, 0), (0, 40), (30, 40)]
            ]
            
            # Lowercase Letters (smaller height: 30 units)
            # Letter 'a'
            self.font_data['a'] = [
                [(20, 30), (10, 30), (0, 25), (0, 20), (5, 15), (25, 15)],
                [(25, 15), (25, 30)]
            ]
            
            # Letter 'b'
            self.font_data['b'] = [
                [(0, 0), (0, 30)],  # Vertical
                [(0, 20), (10, 15), (20, 20), (20, 25), (10, 30), (0, 25)]  # Bowl
            ]
            
            # Letter 'c'
            self.font_data['c'] = [
                [(20, 17), (10, 15), (0, 20), (0, 25), (10, 30), (20, 28)]
            ]
            
            # Letter 'd'
            self.font_data['d'] = [
                [(20, 0), (20, 30)],  # Vertical
                [(20, 25), (10, 30), (0, 25), (0, 20), (10, 15), (20, 20)]  # Bowl
            ]
            
            # Letter 'e'
            self.font_data['e'] = [
                [(0, 23), (20, 23), (20, 20), (10, 15), (0, 20), (0, 25), (10, 30), (20, 28)]
            ]
            
            # Letter 'f'
            self.font_data['f'] = [
                [(10, 30), (10, 5), (15, 0), (20, 0)],
                [(5, 15), (15, 15)]
            ]
            
            # Letter 'g'
            self.font_data['g'] = [
                [(20, 15), (20, 35), (15, 40), (5, 40), (0, 35)],
                [(20, 25), (10, 30), (0, 25), (0, 20), (10, 15), (20, 20)]
            ]
            
            # Letter 'h'
            self.font_data['h'] = [
                [(0, 0), (0, 30)],  # Vertical
                [(0, 20), (10, 15), (20, 20), (20, 30)]  # Arch
            ]
            
            # Letter 'i'
            self.font_data['i'] = [
                [(10, 15), (10, 30)],  # Main stroke
                [(10, 5), (10, 7)]  # Dot
            ]
            
            # Letter 'j'
            self.font_data['j'] = [
                [(10, 15), (10, 35), (5, 40), (0, 35)],  # Hook
                [(10, 5), (10, 7)]  # Dot
            ]
            
            # Common punctuation and numbers
            # Period
            self.font_data['.'] = [
                [(0, 38), (0, 40)]
            ]
            
            # Comma
            self.font_data[','] = [
                [(0, 38), (0, 42), (-2, 44)]
            ]
            
            # Space (empty path)
            self.font_data[' '] = []
            
            # Question mark
            self.font_data['?'] = [
                [(0, 10), (0, 5), (5, 0), (15, 0), (20, 5), (20, 10), (10, 20), (10, 25)],
                [(10, 35), (10, 37)]  # Dot
            ]
            
            # Exclamation mark
            self.font_data['!'] = [
                [(10, 0), (10, 25)],  # Main stroke
                [(10, 35), (10, 37)]  # Dot
            ]
            
            # Default shape for unimplemented characters (small rectangle)
            for char in range(32, 127):  # ASCII printable chars
                if chr(char) not in self.font_data:
                    char_str = chr(char)
                    # Simple box shape instead of vertical line
                    self.font_data[char_str] = [
                        [(0, 15), (15, 15), (15, 30), (0, 30), (0, 15)]
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
        if not text:
            logger.debug("Empty text received, returning empty paths list")
            return []
            
        paths = []
        margin = 50  # 0.5-inch margin at 100 DPI
        x_pos = margin
        y_pos = margin + font_size  # Start y position at margin plus font size
        
        logger.debug(f"Starting text layout at position ({x_pos}, {y_pos})")
        
        # Base size is 40 units, scale everything relative to requested font size
        scale = font_size / 12  # Increase base size for better visibility
        char_width = 40 * scale  # Wider character width
        char_height = 40 * scale
        spacing = 15 * scale  # Increase spacing between characters
        max_width = 600 - (margin * 2)  # Max width with margins
        
        logger.debug(f"Text layout parameters: scale={scale}, char_width={char_width}, spacing={spacing}")
        
        logger.debug(f"Converting text: '{text}' at font size {font_size}")
        logger.debug(f"Scale: {scale}, Mistake frequency: {self.mistake_frequency}")
        
        # Split text into words
        words = text.split()
        current_line = []
        line_start_x = x_pos
        current_x = x_pos
        
        # Track mistakes for strike-through
        mistakes_to_strike = []
        
        for word in words:
            # Generate potential mistake
            modified_word, is_mistake = self.generate_mistake(word)
            word_width = len(modified_word) * char_width * 1.2
            
            # Check if we need to wrap to next line
            if current_x + word_width > max_width + margin and current_line:
                # Render current line
                render_x = line_start_x
                for w in current_line:
                    # Add word spacing
                    if render_x > line_start_x:
                        render_x += spacing * 2  # Double spacing between words

                    for char in w:
                        # Get character paths, fallback to box shape if not found
                        char_paths = self.font_data.get(char, [[(0, 15), (15, 15), (15, 30), (0, 30), (0, 15)]])

                        # Draw each stroke in the character
                        for stroke in char_paths:
                            path = []
                            for x, y in stroke:
                                # Scale and position the point
                                scaled_x = render_x + (x * scale)
                                scaled_y = y_pos + (y * scale)
                                path.append({
                                    'x': scaled_x,
                                    'y': scaled_y
                                })
                            if len(path) >= 2:  # Only add valid paths
                                paths.append(path)

                        # Move to next character position
                        render_x += char_width + (spacing * 0.5)  # Add spacing between characters
                
                # Move to next line
                y_pos += char_height * 1.5
                current_line = []
                line_start_x = x_pos
                current_x = x_pos
            
            # Add word to current line
            current_line.append(modified_word)
            
            # If this is a mistake, track it for strike-through
            if is_mistake:
                logger.debug(f"Tracking mistake: '{modified_word}' at x={current_x}, y={y_pos}")
                mistakes_to_strike.append({
                    'x': current_x,
                    'y': y_pos,
                    'width': word_width
                })
            
            current_x += word_width + (char_width * 0.2)
        
        # Render remaining line if any
        if current_line:
            render_x = line_start_x
            for w in current_line:
                # Add word spacing
                if render_x > line_start_x:
                    render_x += spacing * 2  # Double spacing between words
                
                for char in w:
                    # Get character paths, fallback to box shape if not found
                    char_paths = self.font_data.get(char, [[(0, 15), (15, 15), (15, 30), (0, 30), (0, 15)]])
                    
                    # Draw each stroke in the character
                    for stroke in char_paths:
                        path = []
                        for x, y in stroke:
                            # Scale and position the point
                            scaled_x = render_x + (x * scale)
                            scaled_y = y_pos + (y * scale)
                            path.append({
                                'x': scaled_x,
                                'y': scaled_y
                            })
                        if len(path) >= 2:  # Only add valid paths
                            paths.append(path)
                    
                    # Move to next character position
                    render_x += char_width + (spacing * 0.5)  # Add spacing between characters
        
        # Add strike-through for mistakes
        for mistake in mistakes_to_strike:
            strike_y = mistake['y'] + (char_height * 0.5)
            strike_path = [
                {'x': mistake['x'], 'y': strike_y},
                {'x': mistake['x'] + mistake['width'], 'y': strike_y + (char_height * 0.1)}
            ]
            paths.append(strike_path)
            logger.debug(f"Added strike-through at ({mistake['x']}, {strike_y})")
        
        logger.debug(f"Generated {len(paths)} paths with {len(mistakes_to_strike)} mistakes")
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