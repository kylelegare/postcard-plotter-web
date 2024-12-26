import logging
from typing import List, Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class WorkspaceBounds:
    """Physical workspace dimensions for AxiDraw Mini"""
    MIN_X: float = 10.0  # mm from left edge (safe margin)
    MAX_X: float = 140.0  # mm (150mm total width - margins)
    MIN_Y: float = 10.0  # mm from bottom edge (safe margin)
    MAX_Y: float = 90.0  # mm (100mm total height - margins)
    WIDTH: float = MAX_X - MIN_X  # Effective width
    HEIGHT: float = MAX_Y - MIN_Y  # Effective height

class FontParser:
    def __init__(self):
        """Initialize font parser with the custom single-stroke font"""
        self.font_data = {}  # Will store parsed font data
        self.vowels = 'aeiou'  # Vowels for mistake generation
        self.mistake_frequency = 0  # Default: no mistakes
        self.workspace = WorkspaceBounds()
        self.preview_width = 600  # Preview canvas width
        self.preview_height = 400  # Preview canvas height
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

    def scale_to_physical(self, x: float, y: float, preview_bounds: Dict[str, float]) -> Tuple[float, float]:
        """Scale preview coordinates to physical AxiDraw coordinates"""
        # First normalize the coordinates (0-1)
        norm_x = (x - preview_bounds['min_x']) / (preview_bounds['max_x'] - preview_bounds['min_x'])
        norm_y = (y - preview_bounds['min_y']) / (preview_bounds['max_y'] - preview_bounds['min_y'])

        # Clamp normalized values to 0-1 range
        norm_x = max(0.0, min(1.0, norm_x))
        norm_y = max(0.0, min(1.0, norm_y))

        # Then scale to physical space, ensuring we stay within bounds
        physical_x = self.workspace.MIN_X + (norm_x * self.workspace.WIDTH)
        physical_y = self.workspace.MIN_Y + ((1.0 - norm_y) * self.workspace.HEIGHT)  # Invert Y coordinate

        # Double-check bounds before returning
        physical_x = max(self.workspace.MIN_X, min(self.workspace.MAX_X, physical_x))
        physical_y = max(self.workspace.MIN_Y, min(self.workspace.MAX_Y, physical_y))

        return round(physical_x, 3), round(physical_y, 3)

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

            # Get the cmap table for character to glyph mapping
            cmap = ttfont.getBestCmap()
            if cmap is None:
                logger.error("Could not find suitable cmap table in font")
                raise ValueError("Invalid font file: no character mapping found")

            units_per_em = ttfont['head'].unitsPerEm
            logger.debug(f"Font loaded successfully. Units per em: {units_per_em}")

            # Store the units_per_em for later scaling calculations
            self.units_per_em = units_per_em

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

                    # Use RecordingPen to capture the glyph's path
                    pen = RecordingPen()
                    if glyph.numberOfContours > 0:
                        glyph.draw(pen, glyf)

                        # Convert pen recordings to normalized paths (0-1 range)
                        paths = []
                        current_path = []

                        for cmd, args in pen.value:
                            if cmd == 'moveTo':
                                if current_path:
                                    paths.append(current_path)
                                current_path = [self.normalize_point(args[0], units_per_em)]
                            elif cmd == 'lineTo':
                                current_path.append(self.normalize_point(args[0], units_per_em))
                            elif cmd == 'qCurveTo':
                                # Approximate curves with line segments
                                if current_path and len(args) >= 2:
                                    start = current_path[-1]
                                    end = self.normalize_point(args[-1], units_per_em)
                                    # Add intermediate points
                                    for i in range(1, 5):  # Use 4 segments for curves
                                        t = i / 5
                                        x = start[0] * (1-t) + end[0] * t
                                        y = start[1] * (1-t) + end[1] * t
                                        current_path.append((x, y))
                            elif cmd == 'closePath':
                                if current_path and current_path[0] != current_path[-1]:
                                    current_path.append(current_path[0])
                                if current_path:
                                    paths.append(current_path)
                                current_path = []

                        if current_path:
                            paths.append(current_path)

                        # Store normalized paths
                        if paths:
                            self.font_data[char_str] = paths

                except Exception as e:
                    logger.error(f"Error processing character '{char_str}': {e}")

            logger.info(f"Created font with {len(self.font_data)} characters")

        except Exception as e:
            logger.error(f"Error loading font: {str(e)}")
            self.font_data = {' ': []}  # Minimal fallback
            raise

    def normalize_point(self, point: Tuple[float, float], units_per_em: int) -> Tuple[float, float]:
        """Convert font units to normalized coordinates (0-1 range)"""
        return (
            point[0] / units_per_em,
            point[1] / units_per_em
        )

    def get_text_paths(self, text: str, font_size: int, for_preview: bool = True) -> List[Dict[str, float]]:
        """Convert text to plottable paths

        Args:
            text: The text to convert
            font_size: Font size in points
            for_preview: If True, generate preview coordinates, else physical coordinates

        Returns:
            List of paths, where each path is a list of points
        """
        if not text:
            return []

        # Calculate base scaling and spacing
        points_to_mm = 0.352778  # 1 point = 0.352778mm
        base_scale = font_size * points_to_mm  # Convert font size to mm

        # Preview dimensions (in preview units)
        preview_margin = 20
        preview_bounds = {
            'min_x': preview_margin,
            'max_x': self.preview_width - preview_margin,
            'min_y': preview_margin,
            'max_y': self.preview_height - preview_margin
        }

        # Calculate maximum allowed width based on workspace or preview
        max_allowed_width = self.workspace.WIDTH if not for_preview else (self.preview_width - 2 * preview_margin)

        # Calculate how much we need to scale down to fit
        total_text_width = len(text) * font_size * points_to_mm * 0.6  # 0.6 is approximate character width ratio
        scale_factor = min(1.0, max_allowed_width / total_text_width)

        # Adjust layout parameters based on scale
        line_height = font_size * 1.2 * scale_factor
        word_spacing = font_size * 0.3 * scale_factor
        char_spacing = font_size * 0.1 * scale_factor

        # Start position - ensure we stay within bounds
        x = self.workspace.MIN_X if not for_preview else preview_margin
        y = self.workspace.MIN_Y + (font_size * scale_factor) if not for_preview else preview_margin + (font_size * scale_factor)

        paths = []
        current_x = x
        current_y = y

        logger.debug(f"Starting text layout: preview={for_preview}, scale_factor={scale_factor:.3f}")
        logger.debug(f"Initial position: x={current_x:.1f}, y={current_y:.1f}")

        # Process each line
        for line in text.split('\n'):
            current_x = x  # Reset X position for new line
            words = line.split()

            for word_idx, word in enumerate(words):
                # Generate potential mistake
                modified_word, is_mistake = self.generate_mistake(word)

                # Process each character
                for char_idx, char in enumerate(modified_word):
                    if char in self.font_data:
                        for glyph_path in self.font_data[char]:
                            path = []

                            for norm_x, norm_y in glyph_path:
                                # Scale normalized coordinates
                                if for_preview:
                                    # Preview coordinates - can exceed workspace bounds
                                    point_x = current_x + (norm_x * base_scale * scale_factor * self.preview_width / 100)
                                    point_y = current_y + (norm_y * base_scale * scale_factor * self.preview_height / 100)
                                    point = {'x': point_x, 'y': point_y}
                                else:
                                    # Physical coordinates - must stay within workspace bounds
                                    phys_x = current_x + (norm_x * base_scale * scale_factor)
                                    phys_y = current_y + (norm_y * base_scale * scale_factor)

                                    # Strict bounds checking for physical coordinates
                                    phys_x = max(self.workspace.MIN_X, min(self.workspace.MAX_X, phys_x))
                                    phys_y = max(self.workspace.MIN_Y, min(self.workspace.MAX_Y, phys_y))

                                    if (phys_x != current_x + (norm_x * base_scale * scale_factor) or 
                                        phys_y != current_y + (norm_y * base_scale * scale_factor)):
                                        logger.warning(f"Coordinate clamped: ({phys_x:.1f}, {phys_y:.1f})")

                                    point = {'x': phys_x, 'y': phys_y}

                                path.append(point)

                            if len(path) >= 2:  # Only add paths with at least 2 points
                                paths.append(path)

                    # Move to next character position
                    current_x += char_spacing

                # Add word spacing after each word (except last)
                if word_idx < len(words) - 1:
                    current_x += word_spacing

            # Move to next line
            current_y += line_height

            if not for_preview:
                logger.debug(f"Line position - x: {x:.1f}, y: {current_y:.1f}")

        return paths

    def get_char_width(self, char: str) -> float:
        """Get the width of a character in normalized units"""
        if char not in self.font_data or not self.font_data[char]:
            return 0.5  # Default width for unknown characters

        # Calculate width from the actual glyph paths
        paths = self.font_data[char]
        if not paths:
            return 0.5

        # Find the maximum x coordinate
        max_x = max(point[0] for path in paths for point in path)
        return max_x