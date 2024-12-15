import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# First try to import the module
try:
    from pyaxidraw import axidraw
    AXIDRAW_AVAILABLE = True
    logger.info("Successfully imported pyaxidraw module")
except ImportError as e:
    logger.error(f"Failed to import pyaxidraw module: {str(e)}")
    logger.error("Please install using: python -m pip install https://cdn.evilmadscientist.com/dl/ad/public/AxiDraw_API.zip")
    AXIDRAW_AVAILABLE = False

class AxiDrawController:
    def __init__(self, dev_mode=None):
        """Initialize AxiDraw controller
        
        Args:
            dev_mode (bool): If True, force development mode. If None, auto-detect hardware.
        """
        self.ad = None
        self.connected = False
        
        # Auto-detect if dev_mode not specified
        if dev_mode is None:
            try:
                from pyaxidraw import axidraw
                self.ad = axidraw.AxiDraw()
                self.dev_mode = False
                logger.info("Hardware detected, initializing in hardware mode")
            except (ImportError, Exception) as e:
                logger.info(f"No hardware detected ({str(e)}), falling back to development mode")
                self.dev_mode = True
        else:
            self.dev_mode = dev_mode
            logger.info(f"Explicitly set to {'development' if dev_mode else 'hardware'} mode")
    
    def connect(self) -> Dict[str, any]:
        """Connect to AxiDraw device
        
        Returns:
            Dict with success status and error message if any
        """
        try:
            logger.info("Starting AxiDraw connection process...")
            
            if self.connected:
                logger.info("Already connected to AxiDraw")
                return {
                    'success': True,
                    'message': 'Already connected to AxiDraw'
                }
            
            # Check if module is available
            if not AXIDRAW_AVAILABLE:
                logger.error("AxiDraw Python module not available")
                return {
                    'success': False,
                    'error': 'AxiDraw Python module not installed. Please install the module first using:\npython -m pip install https://cdn.evilmadscientist.com/dl/ad/public/AxiDraw_API.zip'
                }
            
            # In hardware mode, we'll keep trying to connect to the physical device
            if not self.dev_mode:
                try:
                    logger.info("Attempting to connect to physical AxiDraw device...")
                    
                    # Create AxiDraw object
                    self.ad = axidraw.AxiDraw()
                    logger.debug("AxiDraw object created successfully")
                    
                    # Enable interactive mode
                    logger.debug("Enabling interactive mode...")
                    self.ad.interactive()
                    logger.debug("Interactive mode enabled successfully")
                    
                    # Connect to the device
                    logger.debug("Attempting USB connection...")
                    self.ad.connect()
                    logger.info("Successfully established USB connection to AxiDraw device")
                    
                    # Test if we can access basic device functions
                    logger.debug("Testing device communication...")
                    self.ad.penup()
                    logger.debug("Pen up command successful")
                    
                    # Connection successful, set status
                    self.connected = True
                    logger.info("Physical AxiDraw device fully connected and responsive")
                    return {
                        'success': True,
                        'message': 'Successfully connected to physical AxiDraw device'
                    }
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Failed to connect to physical AxiDraw: {error_msg}")
                    
                    if "no module named" in error_msg.lower():
                        return {
                            'success': False,
                            'error': 'AxiDraw Python module not properly installed. Please run:\npython -m pip install https://cdn.evilmadscientist.com/dl/ad/public/AxiDraw_API.zip'
                        }
                    elif "could not open" in error_msg.lower() or "failed to open" in error_msg.lower():
                        return {
                            'success': False,
                            'error': 'Could not open USB connection. Please check:\n1. USB cable is properly connected\n2. AxiDraw is powered on\n3. No other software is currently using the device'
                        }
                    else:
                        return {
                            'success': False,
                            'error': f'Connection failed: {error_msg}\nPlease ensure:\n1. USB connection is secure\n2. Device is powered on\n3. Correct drivers are installed'
                        }
            
            # Only use development mode if explicitly requested
            if self.dev_mode:
                logger.info("Running in development mode as explicitly requested")
                self.connected = True
                return {
                    'success': True,
                    'message': 'Connected in development mode (simulation only)'
                }
            
            # If we get here, something unexpected happened
            return {
                'success': False,
                'error': 'Unexpected error during connection attempt'
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
    
    def _home_axes(self) -> bool:
        """Home the AxiDraw axes to establish origin
        Returns:
            bool: True if homing successful
        """
        try:
            logger.info("Homing AxiDraw axes...")
            # First ensure pen is up with extra delay
            self.ad.penup()
            self.ad.delay(500)  # Longer delay for pen up
            
            # Move to 0,0 in steps
            logger.debug("Moving to origin...")
            self.ad.moveto(0, 0)
            self.ad.delay(500)  # Wait for movement
            
            # Double check pen is up
            self.ad.penup()
            self.ad.delay(200)
            
            logger.info("Successfully homed AxiDraw")
            return True
        except Exception as e:
            logger.error(f"Error homing AxiDraw: {str(e)}")
            return False

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
                simulation_logs.append("=== Starting Plot Simulation ===")
                simulation_logs.append("1. Initial Position Setup:")
                simulation_logs.append("   • Moving to home position (0, 0)")
                simulation_logs.append("   • Ensuring pen is UP")
                simulation_logs.append("\n2. Beginning Plot Sequence:")
                
                total_path_distance = 0
                total_pen_movements = 0
                
                for i, path in enumerate(paths):
                    # Validate path structure
                    if not path:
                        simulation_logs.append(f"   • Warning: Path {i} is empty, skipping")
                        continue
                        
                    # Log movement simulation
                    first_point = path[0]
                    simulation_logs.append(f"\n   Path {i + 1}:")
                    simulation_logs.append(f"   • Moving to start position ({first_point['x']:.1f}, {first_point['y']:.1f})")
                    simulation_logs.append("   • Lowering pen DOWN")
                    total_pen_movements += 1
                    
                    # Calculate total distance for this path
                    total_distance = 0
                    prev_point = first_point
                    for point in path[1:]:
                        dx = point['x'] - prev_point['x']
                        dy = point['y'] - prev_point['y']
                        distance = (dx * dx + dy * dy) ** 0.5
                        total_distance += distance
                        simulation_logs.append(f"   • Drawing line to ({point['x']:.1f}, {point['y']:.1f})")
                        prev_point = point
                    
                    total_path_distance += total_distance
                    simulation_logs.append(f"   • Total drawing distance: {total_distance:.1f} units")
                    simulation_logs.append("   • Raising pen UP")
                    total_pen_movements += 1
                
                # Calculate estimated plotting time and stats
                est_time = len(paths) * 2  # Rough estimate: 2 seconds per path
                simulation_logs.append("\n3. Completing Plot:")
                simulation_logs.append("   • Ensuring pen is UP")
                simulation_logs.append("   • Returning to home position (0, 0)")
                simulation_logs.append("\n=== Plot Statistics ===")
                simulation_logs.append(f"• Total paths plotted: {len(paths)}")
                simulation_logs.append(f"• Total drawing distance: {total_path_distance:.1f} units")
                simulation_logs.append(f"• Total pen up/down movements: {total_pen_movements}")
                simulation_logs.append(f"• Estimated plotting time: {est_time} seconds")
                simulation_logs.append("\n=== Final Position ===")
                simulation_logs.append("• Pen: UP")
                simulation_logs.append("• Location: Home position (0, 0)")
                
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
                # Configure movement parameters specifically for AxiDraw Mini postcard writing
                self.ad.options.speed_pendown = 10    # Very slow for precise writing
                self.ad.options.speed_penup = 25      # Conservative speed for safety
                self.ad.options.accel = 20           # Lower acceleration for smooth writing
                self.ad.options.pen_pos_down = 40    # Light touch for writing
                self.ad.options.pen_pos_up = 75      # Full up position
                self.ad.options.pen_delay_down = 500  # Extra delay for consistent writing
                self.ad.options.pen_delay_up = 400    # Standard delay for pen up
                
                # Configure AxiDraw Mini specific settings
                self.ad.options.model = 3           # AxiDraw Mini model
                self.ad.options.port = None         # Auto-detect USB port
                self.ad.options.units = 1           # Use mm units
                self.ad.options.const_speed = True  # Enable constant speed for better writing
                
                # Define workspace limits for postcard
                self.WORKSPACE_MIN_X = 10   # mm from left edge
                self.WORKSPACE_MAX_X = 95   # mm (105mm total width - margins)
                self.WORKSPACE_MIN_Y = 10   # mm from bottom edge
                self.WORKSPACE_MAX_Y = 50   # mm (60mm total height - margins)
                
                # Home axes before starting plot
                if not self._home_axes():
                    return {
                        'success': False,
                        'error': 'Failed to home AxiDraw axes'
                    }
                
            except AttributeError as e:
                logger.error(f"Error configuring AxiDraw options: {str(e)}")
                return {
                    'success': False,
                    'error': f'Failed to configure AxiDraw: {str(e)}'
                }
            
            try:
                # Ensure we start with pen up
                self.ad.penup()
                
                # Plot each path
                for i, path in enumerate(paths):
                    if not path:
                        logger.warning(f"Path {i} is empty, skipping")
                        continue
                    
                    # Validate and move to start of path with pen up
                    first_point = path[0]
                    # Validate point is within postcard workspace bounds
                    if not (self.WORKSPACE_MIN_X <= first_point['x'] <= self.WORKSPACE_MAX_X and 
                           self.WORKSPACE_MIN_Y <= first_point['y'] <= self.WORKSPACE_MAX_Y):
                        logger.warning(
                            f"Path {i}: Point ({first_point['x']:.1f}, {first_point['y']:.1f}) outside "
                            f"safe workspace bounds ({self.WORKSPACE_MIN_X}-{self.WORKSPACE_MAX_X}, "
                            f"{self.WORKSPACE_MIN_Y}-{self.WORKSPACE_MAX_Y})"
                        )
                        continue
                    
                    # Always start from home position for each path
                    logger.info("Initializing new path sequence...")
                    if not self._home_axes():
                        logger.error("Failed to home axes before path")
                        continue
                        
                    # Ensure pen is fully up with extended delay
                    self.ad.penup()
                    self.ad.delay(800)  # Extra long delay for safety
                    
                    # Move to start position in two steps for smoother movement
                    logger.debug(f"Moving to start position ({first_point['x']:.1f}, {first_point['y']:.1f})")
                    # First move Y coordinate
                    self.ad.moveto(0, first_point['y'])
                    self.ad.delay(500)
                    # Then move X coordinate
                    self.ad.moveto(first_point['x'], first_point['y'])
                    self.ad.delay(800)  # Extended delay for precise positioning
                    
                    # Lower pen with extended delay
                    logger.debug("Lowering pen...")
                    self.ad.pendown()
                    self.ad.delay(500)  # Extended delay for pen down
                    
                    # Draw path with delays between points
                    for point in path[1:]:
                        logger.debug(f"Drawing line to ({point['x']:.1f}, {point['y']:.1f})")
                        self.ad.lineto(point['x'], point['y'])
                        self.ad.delay(100)  # Small delay between line segments
                    
                    # Lift pen and wait
                    self.ad.penup()
                    self.ad.delay(500)
                    
                    # Return to home position in two steps
                    logger.debug("Returning to home position...")
                    # First move X to 0
                    self.ad.moveto(0, path[-1]['y'])
                    self.ad.delay(500)
                    # Then move Y to 0
                    self.ad.moveto(0, 0)
                    self.ad.delay(500)
                
                # Final home position check after all paths
                logger.info("Plotting complete, ensuring home position")
                if not self._home_axes():
                    logger.warning("Final home position check failed")
                
                return {
                    'success': True,
                    'message': 'Plotting completed successfully'
                }
                
            except Exception as e:
                logger.error(f"Error during plotting: {str(e)}")
                # Try to home axes and lift pen in case of error
                try:
                    self.ad.penup()
                    self._home_axes()
                except:
                    pass
                return {
                    'success': False,
                    'error': f'Failed to plot: {str(e)}'
                }
            
        except Exception as e:
            logger.error(f"Error plotting paths: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to plot: {str(e)}'
            }