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
        """Generate a potential mistake for a word"""
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
            # Use the single-stroke font (SL) for actual plotting
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
                        
                        if current_path:
                            paths.append(current_path)
                        
                        logger.debug(f"Extracted {len(paths)} raw paths for '{char_str}'")
                        
                        # Scale paths to our coordinate system
                        scaled_paths = []
                        for path in paths:
                            scaled_path = []
                            for x, y in path:
                                # Scale paths to fit within normalized coordinate system
                                scale_factor = 8 / units_per_em  # Further reduced scale for more compact paths
                                scaled_x = round((x * scale_factor), 1)  # Round to 1 decimal place
                                scaled_y = round(8 - (y * scale_factor * 0.8), 1)  # Further reduced y-range and scale
                                # Only add point if it's significantly different from the last one
                                if not scaled_path or abs(scaled_path[-1][0] - scaled_x) > 0.1 or abs(scaled_path[-1][1] - scaled_y) > 0.1:
                                    scaled_path.append((scaled_x, scaled_y))
                                    logger.debug(f"Scaled point ({x}, {y}) to ({scaled_x:.2f}, {scaled_y:.2f})")
                            
                            # Validate path points and deduplicate
                            if len(scaled_path) >= 2:
                                valid_path = True
                                last_point = None
                                deduped_path = []
                                
                                for point in scaled_path:
                                    # Validate coordinate range
                                    if not (0 <= point[0] <= 30 and 0 <= point[1] <= 30):
                                        logger.warning(f"Invalid coordinates in path for '{char_str}': {point}")
                                        valid_path = False
                                        break
                                        
                                    # Deduplicate consecutive identical points
                                    if last_point is None or point != last_point:
                                        deduped_path.append(point)
                                        last_point = point
                                
                                if valid_path and len(deduped_path) >= 2:
                                    # Only add if path is not already present
                                    path_str = str(deduped_path)
                                    if path_str not in set(str(p) for p in scaled_paths):
                                        scaled_paths.append(deduped_path)
                                        logger.debug(f"Added unique path for '{char_str}' with {len(deduped_path)} points")
                        
                        logger.debug(f"Converted {len(scaled_paths)} scaled paths for '{char_str}'")
                        self.font_data[char_str] = scaled_paths
                        
                except Exception as e:
                    logger.error(f"Error processing character '{char_str}': {e}")
            
            logger.info(f"Created font with {len(self.font_data)} characters")
            
        except Exception as e:
            logger.error(f"Error loading font: {str(e)}")
            # Provide minimal fallback in case of complete failure
            self.font_data = {' ': []}
            raise

    def get_text_paths(self, text: str, font_size: int) -> List[Dict[str, float]]:
        """Convert text to plottable paths
        
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
        margin = 20  # Margin from edges in preview units
        x_pos = margin
        y_pos = margin + (font_size * 0.4)  # Initial vertical position
        
        logger.debug(f"Starting text layout at position ({x_pos}, {y_pos})")
        
        # Calculate scale and dimensions for preview canvas
        base_size = 5  # Base size for characters
        scale = (font_size / 12) * (base_size / 8)  # Scale relative to base size
        char_width = base_size * scale  # Individual character width
        char_height = base_size * scale * 1.2  # Line height with spacing
        word_spacing = (base_size / 4) * scale  # Space between words
        letter_spacing = (base_size / 8) * scale  # Space between letters
        
        # Available width for text (in preview coordinate system)
        preview_width = 600  # Preview canvas width
        max_width = preview_width - (margin * 2)  # Account for margins
        
        logger.debug(f"Text layout parameters: scale={scale}, char_width={char_width}, word_spacing={word_spacing}, letter_spacing={letter_spacing}, max_width={max_width}")
        
        # Track mistakes for strike-through
        mistakes_to_strike = []
        
        # Process each line from input text
        lines = text.split('\n')
        for line_text in lines:
            # Reset x position for new line
            current_x = x_pos
            line_start_x = x_pos
            current_line = []
            
            # Process words in current line
            words = line_text.split()
            for word in words:
                # Generate potential mistake
                modified_word, is_mistake = self.generate_mistake(word)
                
                # Calculate total width needed for this word including spacing
                word_width = len(modified_word) * (char_width + letter_spacing)
                total_width = word_width + (word_spacing if current_line else 0)
                
                # Check if word fits on current line
                if current_x + total_width > max_width and current_line:
                    # Render current line before starting new one
                    render_x = line_start_x
                    for w in current_line:
                        # Add word spacing if not first word
                        if render_x > line_start_x:
                            render_x += word_spacing
                        
                        # Render each character
                        for char in w:
                            char_paths = self.font_data.get(char, [[(0, 15), (15, 15), (15, 30), (0, 30), (0, 15)]])
                            for stroke in char_paths:
                                path = []
                                for x, y in stroke:
                                    scaled_x = render_x + (x * scale)
                                    scaled_y = y_pos + (y * scale)
                                    path.append({'x': scaled_x, 'y': scaled_y})
                                if len(path) >= 2:
                                    paths.append(path)
                            render_x += char_width + letter_spacing
                    
                    # Start new line
                    y_pos += char_height * 1.2
                    current_x = x_pos
                    current_line = [modified_word]
                    logger.debug(f"Word wrap: moving to new line at y={y_pos}")
                else:
                    # Add word to current line
                    current_line.append(modified_word)
                
                # Track mistake if generated
                if is_mistake:
                    logger.debug(f"Tracking mistake: '{modified_word}' at x={current_x}, y={y_pos}")
                    mistakes_to_strike.append({
                        'x': current_x,
                        'y': y_pos,
                        'width': word_width
                    })
                
                # Update position for next word
                current_x += word_width + word_spacing
            
            # Render final line
            if current_line:
                render_x = line_start_x
                for w in current_line:
                    # Add word spacing if not first word
                    if render_x > line_start_x:
                        render_x += word_spacing
                    
                    # Render each character
                    for char in w:
                        char_paths = self.font_data.get(char, [[(0, 15), (15, 15), (15, 30), (0, 30), (0, 15)]])
                        for stroke in char_paths:
                            path = []
                            for x, y in stroke:
                                scaled_x = render_x + (x * scale)
                                scaled_y = y_pos + (y * scale)
                                path.append({'x': scaled_x, 'y': scaled_y})
                            if len(path) >= 2:
                                paths.append(path)
                        render_x += char_width + letter_spacing
            
            # Move to next line for manual line breaks
            y_pos += char_height * 1.2
        
        # Add strike-through for mistakes
        for mistake in mistakes_to_strike:
            strike_y = mistake['y'] + (char_height * 0.5)
            strike_path = [
                {'x': mistake['x'], 'y': strike_y},
                {'x': mistake['x'] + mistake['width'], 'y': strike_y + (char_height * 0.1)}
            ]
            paths.append(strike_path)
        
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