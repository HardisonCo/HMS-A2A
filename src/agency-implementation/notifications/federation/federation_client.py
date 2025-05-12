"""
Federation Client

Connects to federation components to collect alerts and stakeholder information.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Set
import aiohttp
import json
from datetime import datetime
import jwt
import time

from ..models.alert import Alert
from ..models.stakeholder import Stakeholder, StakeholderGroup

logger = logging.getLogger(__name__)


class FederationClient:
    """
    Client for interacting with federation services that provide access to
    CDC, EPA, and FEMA data and systems.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the federation client.
        
        Args:
            config: Configuration for federation client
        """
        self.config = config
        self.base_url = config.get("base_url", "http://localhost:8000/api")
        self.api_key = config.get("api_key", "")
        self.jwt_secret = config.get("jwt_secret", "")
        self.timeout = config.get("timeout", 30)
        self.retry_count = config.get("retry_count", 3)
        self.retry_delay = config.get("retry_delay", 1.0)
        self.session = None
        self.is_initialized = False
        
        # Cache settings
        self.use_cache = config.get("use_cache", True)
        self.cache_ttl = config.get("cache_ttl", 300)  # 5 minutes
        self.cache = {}
        
    async def initialize(self) -> bool:
        """
        Initialize the federation client.
        
        Returns:
            bool: True if initialization was successful
        """
        try:
            # Create HTTP session
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                headers=self._get_default_headers(),
                timeout=timeout,
            )
            
            # Test connection to federation service
            if self.config.get("test_connection", True):
                try:
                    resp = await self.session.get(f"{self.base_url}/health")
                    if resp.status != 200:
                        logger.error(f"Federation health check failed: {resp.status}")
                        return False
                except Exception as e:
                    logger.error(f"Federation connection test failed: {e}")
                    return False
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Error initializing federation client: {e}")
            if self.session:
                await self.session.close()
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the federation client."""
        if self.session:
            await self.session.close()
        self.is_initialized = False
    
    async def get_alerts(self) -> List[Alert]:
        """
        Get alerts from federated agencies.
        
        Returns:
            List of alerts
        """
        if not self.is_initialized:
            raise RuntimeError("Federation client not initialized")
            
        alerts = []
        agencies = ["cdc", "epa", "fema"]
        
        for agency in agencies:
            try:
                agency_alerts = await self._get_agency_alerts(agency)
                alerts.extend(agency_alerts)
            except Exception as e:
                logger.error(f"Error getting alerts from {agency}: {e}")
        
        return alerts
    
    async def get_stakeholder(self, stakeholder_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a stakeholder by ID.
        
        Args:
            stakeholder_id: ID of the stakeholder to fetch
            
        Returns:
            Stakeholder information or None if not found
        """
        if not self.is_initialized:
            raise RuntimeError("Federation client not initialized")
            
        cache_key = f"stakeholder:{stakeholder_id}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
            
        try:
            async with self.session.get(
                f"{self.base_url}/stakeholders/{stakeholder_id}",
                headers=self._get_auth_headers()
            ) as response:
                if response.status == 404:
                    return None
                elif response.status != 200:
                    logger.error(f"Error fetching stakeholder {stakeholder_id}: {response.status}")
                    return None
                    
                stakeholder_data = await response.json()
                self._add_to_cache(cache_key, stakeholder_data)
                return stakeholder_data
                
        except Exception as e:
            logger.error(f"Error fetching stakeholder {stakeholder_id}: {e}")
            return None
    
    async def get_stakeholders_by_group(self, group: StakeholderGroup) -> List[Stakeholder]:
        """
        Get stakeholders by group.
        
        Args:
            group: The stakeholder group to filter by
            
        Returns:
            List of stakeholders in the specified group
        """
        if not self.is_initialized:
            raise RuntimeError("Federation client not initialized")
            
        cache_key = f"stakeholders_group:{group.value}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return [Stakeholder.from_dict(s) for s in cached]
            
        stakeholders = []
        try:
            async with self.session.get(
                f"{self.base_url}/stakeholders",
                params={"group": group.value},
                headers=self._get_auth_headers()
            ) as response:
                if response.status != 200:
                    logger.error(f"Error fetching stakeholders by group {group.value}: {response.status}")
                    return []
                    
                stakeholders_data = await response.json()
                self._add_to_cache(cache_key, stakeholders_data)
                
                for data in stakeholders_data:
                    try:
                        stakeholders.append(Stakeholder.from_dict(data))
                    except Exception as e:
                        logger.warning(f"Error parsing stakeholder data: {e}")
                        
        except Exception as e:
            logger.error(f"Error fetching stakeholders by group {group.value}: {e}")
            
        return stakeholders
    
    async def get_stakeholders_by_region(self, region: str) -> List[Stakeholder]:
        """
        Get stakeholders by region.
        
        Args:
            region: The region code to filter by
            
        Returns:
            List of stakeholders in the specified region
        """
        if not self.is_initialized:
            raise RuntimeError("Federation client not initialized")
            
        cache_key = f"stakeholders_region:{region}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return [Stakeholder.from_dict(s) for s in cached]
            
        stakeholders = []
        try:
            async with self.session.get(
                f"{self.base_url}/stakeholders",
                params={"region": region},
                headers=self._get_auth_headers()
            ) as response:
                if response.status != 200:
                    logger.error(f"Error fetching stakeholders by region {region}: {response.status}")
                    return []
                    
                stakeholders_data = await response.json()
                self._add_to_cache(cache_key, stakeholders_data)
                
                for data in stakeholders_data:
                    try:
                        stakeholders.append(Stakeholder.from_dict(data))
                    except Exception as e:
                        logger.warning(f"Error parsing stakeholder data: {e}")
                        
        except Exception as e:
            logger.error(f"Error fetching stakeholders by region {region}: {e}")
            
        return stakeholders
    
    async def get_subscriptions(self) -> List[Dict[str, Any]]:
        """
        Get stakeholder alert subscriptions.
        
        Returns:
            List of subscription records
        """
        if not self.is_initialized:
            raise RuntimeError("Federation client not initialized")
            
        cache_key = "subscriptions"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
            
        try:
            async with self.session.get(
                f"{self.base_url}/subscriptions",
                headers=self._get_auth_headers()
            ) as response:
                if response.status != 200:
                    logger.error(f"Error fetching subscriptions: {response.status}")
                    return []
                    
                subscriptions = await response.json()
                self._add_to_cache(cache_key, subscriptions)
                return subscriptions
                
        except Exception as e:
            logger.error(f"Error fetching subscriptions: {e}")
            return []
    
    async def update_subscriptions(self, subscriptions: List[Dict[str, Any]]) -> bool:
        """
        Update stakeholder alert subscriptions.
        
        Args:
            subscriptions: List of subscription records to update
            
        Returns:
            bool: True if update was successful
        """
        if not self.is_initialized:
            raise RuntimeError("Federation client not initialized")
            
        try:
            async with self.session.put(
                f"{self.base_url}/subscriptions",
                json=subscriptions,
                headers=self._get_auth_headers()
            ) as response:
                if response.status != 200:
                    logger.error(f"Error updating subscriptions: {response.status}")
                    return False
                    
                # Clear cache
                if "subscriptions" in self.cache:
                    del self.cache["subscriptions"]
                    
                return True
                
        except Exception as e:
            logger.error(f"Error updating subscriptions: {e}")
            return False
    
    async def _get_agency_alerts(self, agency: str) -> List[Alert]:
        """
        Get alerts from a specific agency.
        
        Args:
            agency: Agency code (cdc, epa, fema)
            
        Returns:
            List of alerts from the agency
        """
        alerts = []
        retry_count = 0
        
        while retry_count <= self.retry_count:
            try:
                async with self.session.get(
                    f"{self.base_url}/agencies/{agency}/alerts",
                    headers=self._get_auth_headers()
                ) as response:
                    if response.status == 200:
                        alerts_data = await response.json()
                        
                        for alert_data in alerts_data:
                            try:
                                # Ensure the source is set
                                if "source" not in alert_data:
                                    alert_data["source"] = agency.upper()
                                    
                                alert = Alert.from_dict(alert_data)
                                alerts.append(alert)
                            except Exception as e:
                                logger.warning(f"Error parsing alert data from {agency}: {e}")
                        
                        break  # Success, exit retry loop
                    elif response.status == 429:  # Rate limited
                        retry_count += 1
                        if retry_count <= self.retry_count:
                            # Get retry-after if available
                            retry_after = int(response.headers.get("Retry-After", self.retry_delay))
                            await asyncio.sleep(retry_after)
                        else:
                            logger.error(f"Rate limited when fetching alerts from {agency}")
                            break
                    elif response.status >= 500:  # Server error, retry
                        retry_count += 1
                        if retry_count <= self.retry_count:
                            await asyncio.sleep(self.retry_delay * (2 ** (retry_count - 1)))
                        else:
                            logger.error(f"Server error when fetching alerts from {agency}: {response.status}")
                            break
                    else:  # Other error, don't retry
                        logger.error(f"Error fetching alerts from {agency}: {response.status}")
                        break
                        
            except asyncio.TimeoutError:
                retry_count += 1
                if retry_count <= self.retry_count:
                    await asyncio.sleep(self.retry_delay * (2 ** (retry_count - 1)))
                else:
                    logger.error(f"Timeout when fetching alerts from {agency}")
                    break
                    
            except Exception as e:
                logger.error(f"Error fetching alerts from {agency}: {e}")
                break
                
        return alerts
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default HTTP headers."""
        return {
            "Content-Type": "application/json",
            "User-Agent": "FederationClient/1.0",
        }
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get headers with authentication."""
        headers = self._get_default_headers()
        
        if self.jwt_secret:
            # Generate JWT token
            payload = {
                "iss": "notification-system",
                "exp": int(time.time()) + 300,  # 5 minutes
                "iat": int(time.time()),
            }
            token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
            headers["Authorization"] = f"Bearer {token}"
        elif self.api_key:
            headers["X-API-Key"] = self.api_key
            
        return headers
    
    def _get_from_cache(self, key: str) -> Any:
        """
        Get item from cache if valid.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        if not self.use_cache or key not in self.cache:
            return None
            
        cache_entry = self.cache[key]
        if time.time() > cache_entry["expires"]:
            del self.cache[key]
            return None
            
        return cache_entry["data"]
    
    def _add_to_cache(self, key: str, data: Any) -> None:
        """
        Add item to cache.
        
        Args:
            key: Cache key
            data: Data to cache
        """
        if not self.use_cache:
            return
            
        self.cache[key] = {
            "data": data,
            "expires": time.time() + self.cache_ttl
        }
        
        # Clean expired cache entries occasionally
        if len(self.cache) > 100:  # Arbitrary threshold for cleanup
            self._cleanup_cache()
    
    def _cleanup_cache(self) -> None:
        """Remove expired cache entries."""
        now = time.time()
        expired_keys = [k for k, v in self.cache.items() if v["expires"] < now]
        for key in expired_keys:
            del self.cache[key]