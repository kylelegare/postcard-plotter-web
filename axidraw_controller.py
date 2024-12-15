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
        self.ad = None
        self.connected = False
        self.dev_mode = False  # Default to attempting hardware connection
    
    def connect(self) -> Dict[str, any]:
        """Connect to AxiDraw device
        
        Returns:
            Dict with success status and error message if any
        """
        try:
            if self.connected:
                return {
                    'success': True,
                    'message': 'Already connected to AxiDraw'
                }
            
            if not AXIDRAW_AVAILABLE:
                logger.error("AxiDraw Python module not available. Please install using:")
                logger.error("python -m pip install https://cdn.evilmadscientist.com/dl/ad/public/AxiDraw_API.zip")
                return {
                    'success': False,
                    'error': 'AxiDraw Python module not installed. Please install the module first.'
                }
            
            try:
                self.ad = axidraw.AxiDraw()
                self.ad.interactive()
                self.ad.connect()
                self.connected = True
                logger.info("Successfully connected to physical AxiDraw device")
                return {
                    'success': True,
                    'message': 'Connected to physical AxiDraw device'
                }
            except Exception as e:
                logger.warning(f"Could not connect to physical AxiDraw: {str(e)}")
                logger.info("Falling back to development mode")
                self.dev_mode = True
                self.connected = True
                return {
                    'success': True,
                    'message': 'Connected in development mode - no physical device found'
                }
                
        except Exception as e:
            logger.error(f"Error connecting to AxiDraw: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to connect: {str(e)}'
            }
    
    def disconnect(self) -> Dict[str, any]:
        """Disconnect from AxiDraw device
        
        Returns:
            Dict with success status and error message if any
        """
        try:
            if not self.connected:
                return {
                    'success': True,
                    'message': 'Already disconnected'
                }
            
            if self.dev_mode:
                self.connected = False
                logger.info("Development mode: Simulated disconnect from AxiDraw")
                return {
                    'success': True,
                    'message': 'Disconnected from AxiDraw (Development Mode)'
                }
            
            if self.ad:
                try:
                    self.ad.disconnect()
                    self.connected = False
                    logger.info("Disconnected from AxiDraw")
                    return {
                        'success': True,
                        'message': 'Disconnected from AxiDraw'
                    }
                except AttributeError as e:
                    logger.error(f"Error disconnecting AxiDraw: {str(e)}")
                    return {
                        'success': False,
                        'error': f'Failed to disconnect: {str(e)}'
                    }
            else:
                self.connected = False
                return {
                    'success': True,
                    'message': 'Disconnected (no device was initialized)'
                }
                
        except Exception as e:
            logger.error(f"Error disconnecting from AxiDraw: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to disconnect: {str(e)}'
            }
    
    def plot_paths(self, paths: List[List[Dict[str, float]]]) -> Dict[str, any]:
        """Plot the given paths using AxiDraw
        
        Args:
            paths: List of paths, where each path is a list of points
        
        Returns:
            Dict with success status and simulation details
        """
        try:
            if not self.connected:
                raise Exception("AxiDraw not connected")
            
            if self.dev_mode:
                # Simulate plotting in development mode
                simulation_logs = []
                simulation_logs.append("Development mode: Simulating AxiDraw plotting")
                simulation_logs.append("Validating paths and simulating movements...")
                
                total_path_distance = 0
                total_pen_movements = 0
                
                for i, path in enumerate(paths):
                    # Validate path structure
                    if not path:
                        simulation_logs.append(f"Warning: Path {i} is empty, skipping")
                        continue
                        
                    # Log movement simulation
                    first_point = path[0]
                    simulation_logs.append(f"Path {i}: Moving to start position ({first_point['x']:.1f}, {first_point['y']:.1f})")
                    simulation_logs.append("Lowering pen")
                    total_pen_movements += 1
                    
                    # Calculate total distance for this path
                    total_distance = 0
                    prev_point = first_point
                    for point in path[1:]:
                        dx = point['x'] - prev_point['x']
                        dy = point['y'] - prev_point['y']
                        distance = (dx * dx + dy * dy) ** 0.5
                        total_distance += distance
                        simulation_logs.append(f"Drawing line to ({point['x']:.1f}, {point['y']:.1f})")
                        prev_point = point
                    
                    total_path_distance += total_distance
                    simulation_logs.append(f"Path {i}: Total drawing distance: {total_distance:.1f} units")
                    simulation_logs.append("Raising pen")
                    total_pen_movements += 1
                
                # Calculate estimated plotting time and stats
                est_time = len(paths) * 2  # Rough estimate: 2 seconds per path
                simulation_logs.append("-------------------")
                simulation_logs.append("Plotting Statistics:")
                simulation_logs.append(f"Total paths: {len(paths)}")
                simulation_logs.append(f"Total drawing distance: {total_path_distance:.1f} units")
                simulation_logs.append(f"Total pen movements: {total_pen_movements}")
                simulation_logs.append(f"Estimated plotting time: {est_time} seconds")
                
                return {
                    'success': True,
                    'simulation_logs': simulation_logs,
                    'statistics': {
                        'total_paths': len(paths),
                        'total_distance': total_path_distance,
                        'pen_movements': total_pen_movements,
                        'estimated_time': est_time
                    }
                }
            
            if not self.ad:
                return {
                    'success': False,
                    'error': 'AxiDraw device not initialized'
                }
            
            # Real hardware mode
            logger.info("Configuring AxiDraw plotting parameters")
            try:
                self.ad.options.speed_pendown = 25  # Adjust based on needs
                self.ad.options.speed_penup = 75
                self.ad.options.accel = 75
                self.ad.options.pen_pos_down = 40
                self.ad.options.pen_pos_up = 60
            except AttributeError as e:
                logger.error(f"Error configuring AxiDraw options: {str(e)}")
                return {
                    'success': False,
                    'error': f'Failed to configure AxiDraw: {str(e)}'
                }
            
            # Plot each path
            for i, path in enumerate(paths):
                if not path:
                    logger.warning(f"Path {i} is empty, skipping")
                    continue
                    
                try:
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
                except Exception as e:
                    logger.error(f"Error plotting path {i}: {str(e)}")
                    return {
                        'success': False,
                        'error': f'Failed to plot path {i}: {str(e)}'
                    }
            
            logger.info("Plotting completed successfully")
            return {
                'success': True,
                'message': 'Plotting completed successfully'
            }
            
        except Exception as e:
            logger.error(f"Error plotting paths: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to plot: {str(e)}'
            }
