"""
Notification Channel Manager

Manages the various notification channels available in the system.
"""

import logging
from typing import Dict, List, Any, Optional
import importlib

logger = logging.getLogger(__name__)


class NotificationChannelManager:
    """
    Manages notification channels for sending alerts through various mediums
    like email, SMS, and webhooks.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the notification channel manager.
        
        Args:
            config: Configuration for notification channels
        """
        self.config = config
        self.channels = {}
        self.channel_configs = {}
        
        # Store channel configs by name
        for channel_name, channel_config in config.items():
            self.channel_configs[channel_name] = channel_config
    
    async def initialize(self) -> bool:
        """
        Initialize all configured notification channels.
        
        Returns:
            bool: True if all channels initialized successfully
        """
        success = True
        
        for channel_name, channel_config in self.channel_configs.items():
            try:
                # Skip disabled channels
                if channel_config.get("enabled", True) is False:
                    logger.info(f"Channel {channel_name} is disabled, skipping")
                    continue
                
                # Get channel type
                channel_type = channel_config.get("type", channel_name)
                
                # Import the channel class
                try:
                    # First try to import from notification channels extension points
                    module_path = f"foundation.extension_points.notification_channels.{channel_type}"
                    module = importlib.import_module(module_path)
                    
                    # Get channel class (assume it ends with NotificationChannel)
                    class_name = next((
                        name for name in dir(module)
                        if name.endswith("NotificationChannel") and not name.startswith("_")
                    ), None)
                    
                    if not class_name:
                        raise ImportError(f"No NotificationChannel class found in {module_path}")
                        
                    channel_class = getattr(module, class_name)
                    
                except ImportError:
                    # Fallback to local channels directory
                    try:
                        module_path = f"..channels.{channel_type}_channel"
                        module = importlib.import_module(module_path, package=__name__)
                        channel_class = getattr(module, f"{channel_type.capitalize()}Channel")
                    except (ImportError, AttributeError) as e:
                        logger.error(f"Error importing channel class for {channel_name}: {e}")
                        success = False
                        continue
                
                # Create and initialize channel
                channel = channel_class()
                channel_initialized = await channel.initialize(channel_config)
                
                if channel_initialized:
                    self.channels[channel_name] = channel
                    logger.info(f"Initialized channel {channel_name}")
                else:
                    logger.error(f"Failed to initialize channel {channel_name}")
                    success = False
                    
            except Exception as e:
                logger.error(f"Error initializing channel {channel_name}: {e}")
                success = False
        
        return success
    
    async def shutdown(self) -> None:
        """Shutdown all notification channels."""
        for channel_name, channel in self.channels.items():
            try:
                await channel.shutdown()
                logger.info(f"Shutdown channel {channel_name}")
            except Exception as e:
                logger.error(f"Error shutting down channel {channel_name}: {e}")
    
    def get_channel(self, channel_name: str) -> Optional[Any]:
        """
        Get a notification channel by name.
        
        Args:
            channel_name: Name of the channel to get
            
        Returns:
            The channel object or None if not found
        """
        return self.channels.get(channel_name)
    
    def get_available_channels(self) -> List[str]:
        """
        Get list of available channel names.
        
        Returns:
            List of channel names
        """
        return list(self.channels.keys())
    
    def get_channel_info(self, channel_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific channel.
        
        Args:
            channel_name: Name of the channel
            
        Returns:
            Dict with channel information or None if not found
        """
        channel = self.get_channel(channel_name)
        if not channel:
            return None
            
        try:
            return channel.get_channel_info()
        except Exception as e:
            logger.error(f"Error getting info for channel {channel_name}: {e}")
            return None