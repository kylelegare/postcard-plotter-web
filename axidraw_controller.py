import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

try:
    from pyaxidraw import axidraw
    AXIDRAW_AVAILABLE = True
except ImportError:
    logger.warning("pyaxidraw module not found - running in development mode")
    AXIDRAW_AVAILABLE = False

class AxiDrawController:
    def __init__(self):
        """Initialize AxiDraw controller"""
        self.ad = None if not AXIDRAW_AVAILABLE else axidraw.AxiDraw()
        self.connected = False
        self.dev_mode = not AXIDRAW_AVAILABLE
    
    def connect(self) -> bool:
        """Connect to AxiDraw device
        
        Returns:
            bool: True if connection successful
        """
        try:
            if not self.connected:
                if self.dev_mode:
                    logger.info("Development mode: Simulating AxiDraw connection")
                    self.connected = True
                    return True
                    
                if self.ad is None:
                    raise Exception("AxiDraw not initialized")
                    
                self.ad.interactive()
                self.ad.connect()
                self.connected = True
                logger.info("Connected to AxiDraw")
            return True
        except Exception as e:
            logger.error(f"Error connecting to AxiDraw: {str(e)}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from AxiDraw device
        
        Returns:
            bool: True if disconnection successful
        """
        try:
            if self.connected:
                self.ad.disconnect()
                self.connected = False
                logger.info("Disconnected from AxiDraw")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from AxiDraw: {str(e)}")
            return False
    
    def plot_paths(self, paths: List[List[Dict[str, float]]]) -> bool:
        """Plot the given paths using AxiDraw
        
        Args:
            paths: List of paths, where each path is a list of points
        
        Returns:
            bool: True if plotting successful
        """
        try:
            if not self.connected:
                raise Exception("AxiDraw not connected")
            
            if self.dev_mode:
                # Simulate plotting in development mode
                logger.info("Development mode: Simulating AxiDraw plotting")
                logger.info("Validating paths and simulating movements...")
                
                for i, path in enumerate(paths):
                    # Validate path structure
                    if not path:
                        logger.warning(f"Path {i} is empty, skipping")
                        continue
                        
                    # Log movement simulation
                    first_point = path[0]
                    logger.info(f"Path {i}: Moving to start position ({first_point['x']:.1f}, {first_point['y']:.1f})")
                    logger.info("Lowering pen")
                    
                    # Calculate total distance for this path
                    total_distance = 0
                    prev_point = first_point
                    for point in path[1:]:
                        dx = point['x'] - prev_point['x']
                        dy = point['y'] - prev_point['y']
                        distance = (dx * dx + dy * dy) ** 0.5
                        total_distance += distance
                        logger.debug(f"Drawing line to ({point['x']:.1f}, {point['y']:.1f})")
                        prev_point = point
                    
                    logger.info(f"Path {i}: Total drawing distance: {total_distance:.1f} units")
                    logger.info("Raising pen")
                
                # Estimate total plotting time
                est_time = len(paths) * 2  # Rough estimate: 2 seconds per path
                logger.info(f"Estimated plotting time: {est_time} seconds")
                return True
            
            # Real hardware mode
            logger.info("Configuring AxiDraw plotting parameters")
            self.ad.options.speed_pendown = 25  # Adjust based on needs
            self.ad.options.speed_penup = 75
            self.ad.options.accel = 75
            self.ad.options.pen_pos_down = 40
            self.ad.options.pen_pos_up = 60
            
            # Plot each path
            for i, path in enumerate(paths):
                if not path:
                    logger.warning(f"Path {i} is empty, skipping")
                    continue
                    
                # Move to start of path
                first_point = path[0]
                logger.debug(f"Path {i}: Moving to ({first_point['x']:.1f}, {first_point['y']:.1f})")
                self.ad.moveto(first_point['x'], first_point['y'])
                self.ad.pendown()
                
                # Draw path
                for point in path[1:]:
                    logger.debug(f"Drawing line to ({point['x']:.1f}, {point['y']:.1f})")
                    self.ad.lineto(point['x'], point['y'])
                
                self.ad.penup()
            
            logger.info("Plotting completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error plotting paths: {str(e)}")
            return False
