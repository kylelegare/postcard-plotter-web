import logging
from typing import List, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class WorkspaceBounds:
    """Physical workspace dimensions for AxiDraw Mini"""
    MIN_X: float = 10.0  # mm from left edge
    MAX_X: float = 95.0  # mm (105mm total width - margins)
    MIN_Y: float = 10.0  # mm from bottom edge
    MAX_Y: float = 50.0  # mm (60mm total height - margins)
    WIDTH: float = MAX_X - MIN_X  # Effective width
    HEIGHT: float = MAX_Y - MIN_Y  # Effective height

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
        self.workspace = WorkspaceBounds()

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

    def validate_point(self, x: float, y: float) -> bool:
        """Check if a point is within the safe workspace bounds"""
        return (self.workspace.MIN_X <= x <= self.workspace.MAX_X and 
                self.workspace.MIN_Y <= y <= self.workspace.MAX_Y)

    def connect(self) -> Dict[str, any]:
        """Connect to AxiDraw device"""
        try:
            logger.info("Starting AxiDraw connection process...")

            if self.connected:
                logger.info("Already connected to AxiDraw")
                return {'success': True, 'message': 'Already connected to AxiDraw'}

            if not AXIDRAW_AVAILABLE:
                logger.error("AxiDraw Python module not available")
                return {
                    'success': False,
                    'error': 'AxiDraw Python module not installed. Please install the module first using:\n'
                            'python -m pip install https://cdn.evilmadscientist.com/dl/ad/public/AxiDraw_API.zip'
                }

            if not self.dev_mode:
                try:
                    logger.info("Attempting to connect to physical AxiDraw device...")

                    self.ad = axidraw.AxiDraw()
                    logger.debug("AxiDraw object created successfully")

                    logger.debug("Enabling interactive mode...")
                    self.ad.interactive()
                    logger.debug("Interactive mode enabled successfully")

                    logger.debug("Attempting USB connection...")
                    self.ad.connect()
                    logger.info("Successfully established USB connection to AxiDraw device")

                    logger.debug("Testing device communication...")
                    self.ad.penup()
                    logger.debug("Pen up command successful")

                    self.connected = True
                    logger.info("Physical AxiDraw device fully connected and responsive")
                    return {'success': True, 'message': 'Successfully connected to physical AxiDraw device'}

                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Failed to connect to physical AxiDraw: {error_msg}")

                    if "no module named" in error_msg.lower():
                        return {
                            'success': False,
                            'error': 'AxiDraw Python module not properly installed. Please run:\n'
                                    'python -m pip install https://cdn.evilmadscientist.com/dl/ad/public/AxiDraw_API.zip'
                        }
                    elif "could not open" in error_msg.lower() or "failed to open" in error_msg.lower():
                        return {
                            'success': False,
                            'error': 'Could not open USB connection. Please check:\n'
                                    '1. USB cable is properly connected\n'
                                    '2. AxiDraw is powered on\n'
                                    '3. No other software is currently using the device'
                        }
                    else:
                        return {
                            'success': False,
                            'error': f'Connection failed: {error_msg}\n'
                                    'Please ensure:\n'
                                    '1. USB connection is secure\n'
                                    '2. Device is powered on\n'
                                    '3. Correct drivers are installed'
                        }

            if self.dev_mode:
                logger.info("Running in development mode as explicitly requested")
                self.connected = True
                return {'success': True, 'message': 'Connected in development mode (simulation only)'}

            return {'success': False, 'error': 'Unexpected error during connection attempt'}

        except Exception as e:
            logger.error(f"Error connecting to AxiDraw: {str(e)}")
            return {'success': False, 'error': f'Failed to connect: {str(e)}'}

    def disconnect(self) -> Dict[str, any]:
        """Disconnect from AxiDraw device"""
        try:
            if not self.connected:
                return {'success': True, 'message': 'Already disconnected'}

            if self.dev_mode:
                self.connected = False
                logger.info("Development mode: Simulated disconnect from AxiDraw")
                return {'success': True, 'message': 'Disconnected from AxiDraw (Development Mode)'}

            if self.ad:
                try:
                    self.ad.disconnect()
                    self.connected = False
                    logger.info("Disconnected from AxiDraw")
                    return {'success': True, 'message': 'Disconnected from AxiDraw'}
                except Exception as e:
                    logger.error(f"Error disconnecting AxiDraw: {str(e)}")
                    return {'success': False, 'error': f'Failed to disconnect: {str(e)}'}
            else:
                self.connected = False
                return {'success': True, 'message': 'Disconnected (no device was initialized)'}

        except Exception as e:
            logger.error(f"Error disconnecting from AxiDraw: {str(e)}")
            return {'success': False, 'error': f'Failed to disconnect: {str(e)}'}

    def _home_axes(self) -> bool:
        """Home the AxiDraw axes to establish origin"""
        try:
            logger.info("Homing AxiDraw axes...")

            # First ensure pen is up with extra delay
            self.ad.penup()
            self.ad.delay(500)

            # Move to 0,0 with proper delays
            logger.debug("Moving to origin...")
            self.ad.moveto(0, 0)
            self.ad.delay(500)

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
                invalid_points = 0

                for i, path in enumerate(paths):
                    # Skip empty paths
                    if not path or len(path) < 2:
                        simulation_logs.append(f"   • Skipping empty path {i}")
                        continue

                    # Validate path points
                    valid_points = []
                    for point in path:
                        if self.validate_point(point['x'], point['y']):
                            valid_points.append(point)
                        else:
                            invalid_points += 1

                    if len(valid_points) < 2:
                        simulation_logs.append(f"   • Skipping path {i} - insufficient valid points")
                        continue

                    # Log movement simulation
                    first_point = valid_points[0]
                    simulation_logs.append(f"\n   Path {i + 1}:")
                    simulation_logs.append(f"   • Moving to start position ({first_point['x']:.1f}, {first_point['y']:.1f})")
                    simulation_logs.append("   • Lowering pen DOWN")
                    total_pen_movements += 1

                    # Calculate path distance
                    total_distance = 0
                    prev_point = first_point
                    for point in valid_points[1:]:
                        dx = point['x'] - prev_point['x']
                        dy = point['y'] - prev_point['y']
                        distance = (dx * dx + dy * dy) ** 0.5
                        total_distance += distance
                        simulation_logs.append(f"   • Drawing line to ({point['x']:.1f}, {point['y']:.1f})")
                        prev_point = point

                    total_path_distance += total_distance
                    simulation_logs.append(f"   • Path distance: {total_distance:.1f}mm")
                    simulation_logs.append("   • Raising pen UP")
                    total_pen_movements += 1

                if invalid_points > 0:
                    simulation_logs.append(f"\nWarning: {invalid_points} points were outside the safe workspace bounds")

                # Calculate estimated plotting time
                est_time = (total_path_distance / 10) + (total_pen_movements * 0.5)  # Rough estimate

                simulation_logs.append("\n3. Plot Statistics:")
                simulation_logs.append(f"• Valid paths plotted: {len(paths)}")
                simulation_logs.append(f"• Total drawing distance: {total_path_distance:.1f}mm")
                simulation_logs.append(f"• Total pen movements: {total_pen_movements}")
                simulation_logs.append(f"• Estimated plotting time: {est_time:.1f} seconds")
                simulation_logs.append("\n=== Plot Complete ===")

                return {
                    'success': True,
                    'simulation_logs': simulation_logs,
                    'statistics': {
                        'total_paths': len(paths),
                        'total_distance': total_path_distance,
                        'pen_movements': total_pen_movements,
                        'estimated_time': est_time,
                        'invalid_points': invalid_points
                    }
                }

            # Hardware mode
            if not self.ad:
                return {'success': False, 'error': 'AxiDraw device not initialized'}

            logger.info("Configuring AxiDraw plotting parameters")
            try:
                # Configure movement parameters
                self.ad.options.speed_pendown = 25     # Slower for precise writing
                self.ad.options.speed_penup = 75       # Faster between strokes
                self.ad.options.accel = 50             # Moderate acceleration
                self.ad.options.pen_pos_down = 40      # Light touch for writing
                self.ad.options.pen_pos_up = 75        # Full up position
                self.ad.options.pen_delay_down = 400   # Delay for pen down
                self.ad.options.pen_delay_up = 400     # Delay for pen up

                # Configure AxiDraw Mini specific settings
                self.ad.options.model = 3              # AxiDraw Mini model
                self.ad.options.port = None            # Auto-detect USB port
                self.ad.options.units = 1              # Use mm units
                self.ad.options.const_speed = True     # Enable constant speed

                # Home axes before starting plot
                if not self._home_axes():
                    return {'success': False, 'error': 'Failed to home AxiDraw axes'}

            except Exception as e:
                logger.error(f"Error configuring AxiDraw options: {str(e)}")
                return {'success': False, 'error': f'Failed to configure AxiDraw: {str(e)}'}

            try:
                # Ensure we start with pen up
                self.ad.penup()
                self.ad.delay(500)

                paths_plotted = 0
                invalid_points = 0

                # Plot each path
                for i, path in enumerate(paths):
                    # Skip empty paths
                    if not path or len(path) < 2:
                        logger.debug(f"Skipping empty path {i}")
                        continue

                    # Validate and filter points
                    valid_points = []
                    for point in path:
                        if self.validate_point(point['x'], point['y']):
                            valid_points.append(point)
                        else:
                            invalid_points += 1
                            logger.debug(f"Point ({point['x']:.1f}, {point['y']:.1f}) outside workspace bounds")

                    if len(valid_points) < 2:
                        logger.debug(f"Skipping path {i} - insufficient valid points")
                        continue

                    # Initialize new path sequence
                    logger.debug(f"Starting path {i + 1}")
                    first_point = valid_points[0]

                    # Move to start position with pen up
                    self.ad.penup()
                    self.ad.delay(400)
                    self.ad.moveto(first_point['x'], first_point['y'])
                    self.ad.delay(400)

# Lower pen and draw
            self.ad.pendown()
            self.ad.delay(400)

            # Draw each line segment
            for point in valid_points[1:]:
                self.ad.lineto(point['x'], point['y'])
                self.ad.delay(100)  # Small delay between segments

            # Lift pen after path
            self.ad.penup()
            self.ad.delay(400)
            paths_plotted += 1

        # Return to home position when done
        logger.info("Plotting complete, returning to home")
        if not self._home_axes():
            logger.warning("Failed to return to home position")

        return {
            'success': True,
            'message': 'Plotting completed successfully',
            'statistics': {
                'paths_plotted': paths_plotted,
                'invalid_points': invalid_points
            }
        }

    except Exception as e:
        logger.error(f"Error during plotting: {str(e)}")
        # Try to recover by homing
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