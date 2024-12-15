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
        """Load font from TTF file and extract glyph paths"""
        try:
            from fontTools.ttLib import TTFont
            from fontTools.pens.recordingPen import RecordingPen
            
            logger.debug("Loading PremiumUltra font")
            font_path = "static/fonts/PremiumUltra54SL.ttf"
            
            # Load the font file
            logger.debug(f"Attempting to load font from: {font_path}")
            ttfont = TTFont(font_path)
            
            # Get required tables
            glyf = ttfont.get('glyf')
            if glyf is None:
                logger.error("Font is missing required 'glyf' table")
                raise ValueError("Invalid font file: missing glyph data")
                
            # Initialize font data dictionary
            self.font_data = {}
            
            # Get the cmap table for character to glyph mapping
            cmap = ttfont.getBestCmap()
            if cmap is None:
                logger.error("Could not find suitable cmap table in font")
                raise ValueError("Invalid font file: no character mapping found")
                
            units_per_em = ttfont['head'].unitsPerEm
            logger.debug(f"Font loaded successfully. Units per em: {units_per_em}")
            
            # Extract paths for each printable character
            for char in range(32, 127):  # ASCII printable chars
                char_str = chr(char)
                
                try:
                    # Get glyph name for this character
                    glyph_id = cmap.get(ord(char_str))
                    if glyph_id is None:
                        logger.debug(f"No glyph mapping found for character '{char_str}' (ord={ord(char_str)})")
                        continue
                    
                    glyph = glyf[glyph_id]
                    if glyph is None:
                        logger.debug(f"Null glyph for character '{char_str}' (id={glyph_id})")
                        continue
                    
                    logger.debug(f"Processing glyph for '{char_str}' (id={glyph_id}, contours={glyph.numberOfContours})")
                    
                    # Use RecordingPen to capture the glyph's path
                    pen = RecordingPen()
                    if glyph.numberOfContours > 0:  # Skip empty glyphs
                        glyph.draw(pen, glyf)
                        logger.debug(f"Captured {len(pen.value)} path commands for '{char_str}'")
                    
                    # Convert pen recordings to our path format
                        paths = []
                        current_path = []
                        
                        for cmd, args in pen.value:
                            try:
                                if cmd == 'moveTo':
                                    if current_path:
                                        paths.append(current_path)
                                    current_path = [tuple(args[0])]
                                elif cmd == 'lineTo':
                                    current_path.append(tuple(args[0]))
                                elif cmd == 'closePath':
                                    if current_path and current_path[0] != current_path[-1]:
                                        current_path.append(current_path[0])
                                    if current_path:
                                        paths.append(current_path)
                                    current_path = []
                                elif cmd == 'qCurveTo':
                                    # Handle quadratic curves by approximating with line segments
                                    if len(args) >= 2:  # Need at least start and end points
                                        start = current_path[-1] if current_path else (0, 0)
                                        for i in range(0, len(args)-1):
                                            t = i / (len(args)-1)
                                            x = (1-t)*start[0] + t*args[-1][0]
                                            y = (1-t)*start[1] + t*args[-1][1]
                                            current_path.append((x, y))
                            except Exception as e:
                                logger.error(f"Error processing path command {cmd} for '{char_str}': {e}")
                        
                        if current_path:
                            paths.append(current_path)
                        
                        logger.debug(f"Extracted {len(paths)} raw paths for '{char_str}'")
                        
                        # Scale paths to our coordinate system
                        scaled_paths = []
                        try:
                            for path_idx, path in enumerate(paths):
                                scaled_path = []
                                for x, y in path:
                                    # For single-line font, maintain exact path proportions
                                    # Scale to fit within 40x40 units, maintaining stroke precision
                                    # Scale paths to fit within standard postcard size
                                    # Use consistent 40-unit base size for both preview and plotting
                                    scale_factor = 40 / units_per_em
                                    scaled_x = (x * scale_factor)
                                    scaled_y = 40 - (y * scale_factor)  # Flip y-coordinate for correct orientation
                                    scaled_path.append((scaled_x, scaled_y))
                                    logger.debug(f"Scaled point ({x}, {y}) to ({scaled_x:.2f}, {scaled_y:.2f})")
                                # Validate path points are within bounds and properly formatted
                                    if len(scaled_path) >= 2:
                                        # Ensure all coordinates are within valid range (0-40)
                                        valid_path = True
                                        for point in scaled_path:
                                            if not (0 <= point[0] <= 40 and 0 <= point[1] <= 40):
                                                logger.warning(f"Invalid coordinates in path for '{char_str}': {point}")
                                                valid_path = False
                                                break
                                        
                                        if valid_path:
                                            scaled_paths.append(scaled_path)
                                            logger.debug(f"Added valid path for '{char_str}' with {len(scaled_path)} points")
                                    
                            logger.debug(f"Converted {len(scaled_paths)} scaled paths for '{char_str}'")
                            self.font_data[char_str] = scaled_paths
                            
                        except Exception as e:
                            logger.error(f"Error scaling paths for '{char_str}': {e}")
                            
                except Exception as e:
                    logger.error(f"Error processing character '{char_str}': {e}")
            
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