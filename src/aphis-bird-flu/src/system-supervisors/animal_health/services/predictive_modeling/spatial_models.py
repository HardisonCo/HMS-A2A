"""
Spatial models for avian influenza spread prediction.

This module implements spatial modeling techniques for predicting the spread
of avian influenza outbreaks across geographic regions. It includes:
- Spatial auto-regressive models
- Network-based spread models
- Environmental factor analysis
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import geopandas as gpd
from scipy import stats
from scipy.spatial import distance
from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel

from ...models.base import GeoLocation, GeoRegion
from ...models.case import Case, VirusSubtype
from ...models.surveillance import SurveillanceSite


class SpatialSpreadModel:
    """Base class for spatial spread models."""
    
    def __init__(self):
        """Initialize the spatial spread model."""
        self.name = "Base Spatial Model"
        self.description = "Abstract base class for spatial spread models"
        
    def fit(self, cases: List[Case], regions: List[GeoRegion], **kwargs) -> None:
        """
        Fit the model using historical case data and region information.
        
        Args:
            cases: List of historical cases
            regions: List of geographic regions
            **kwargs: Additional model-specific parameters
        """
        raise NotImplementedError("Subclasses must implement fit()")
    
    def predict(self, 
               current_cases: List[Case], 
               regions: List[GeoRegion], 
               days_ahead: int = 7,
               **kwargs) -> Dict[str, Any]:
        """
        Predict the spread of avian influenza over the specified time period.
        
        Args:
            current_cases: Current active cases
            regions: List of geographic regions
            days_ahead: Number of days to predict ahead
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dictionary containing predictions:
                - predicted_cases: List of predicted new cases
                - risk_by_region: Dictionary mapping region IDs to risk scores
                - confidence_intervals: Dictionary of confidence intervals
        """
        raise NotImplementedError("Subclasses must implement predict()")


class DistanceBasedSpreadModel(SpatialSpreadModel):
    """
    A model that predicts spread based on distance to existing cases,
    similar to gravity models in epidemiology.
    """
    
    def __init__(self, 
                distance_decay: float = 2.0, 
                transmission_threshold: float = 100.0,  # km
                time_window: int = 14):  # days
        """
        Initialize the distance-based spread model.
        
        Args:
            distance_decay: Power parameter for distance decay function
            transmission_threshold: Maximum distance (km) for transmission consideration
            time_window: Time window (days) for considering active cases
        """
        super().__init__()
        self.name = "Distance-Based Spread Model"
        self.description = "Predicts spread based on proximity to active cases"
        self.distance_decay = distance_decay
        self.transmission_threshold = transmission_threshold
        self.time_window = time_window
        self.fitted = False
        
        # Parameters to be estimated during fitting
        self.base_transmission_rate = None
        self.subtype_factors = {}
        self.environmental_factors = {}
        
    def fit(self, cases: List[Case], regions: List[GeoRegion], **kwargs) -> None:
        """
        Fit the model using historical case data.
        
        Args:
            cases: List of historical cases with timestamps and locations
            regions: List of geographic regions
            **kwargs: Additional parameters:
                - environmental_data: Optional environmental data by region
        """
        # Sort cases by date
        sorted_cases = sorted(cases, key=lambda c: datetime.fromisoformat(c.detection_date))
        
        # Group cases by day
        cases_by_day = {}
        for case in sorted_cases:
            day = datetime.fromisoformat(case.detection_date).date()
            if day not in cases_by_day:
                cases_by_day[day] = []
            cases_by_day[day].append(case)
        
        # Calculate transmission rates based on case proximity
        transmission_events = []
        for i, day in enumerate(sorted(cases_by_day.keys())[1:]):
            prev_window_start = day - timedelta(days=self.time_window)
            potential_source_cases = []
            
            # Collect potential source cases from the previous time window
            for prev_day in sorted(cases_by_day.keys()):
                if prev_window_start <= prev_day < day:
                    potential_source_cases.extend(cases_by_day[prev_day])
            
            # For each new case on this day, find potential transmission events
            for new_case in cases_by_day[day]:
                for source_case in potential_source_cases:
                    # Skip if same case or location
                    if new_case.id == source_case.id:
                        continue
                    
                    # Calculate distance between cases
                    dist_km = self._calculate_distance(
                        source_case.location.latitude, 
                        source_case.location.longitude,
                        new_case.location.latitude,
                        new_case.location.longitude
                    )
                    
                    # Only consider cases within threshold distance
                    if dist_km <= self.transmission_threshold:
                        transmission_events.append({
                            'source_case': source_case,
                            'target_case': new_case,
                            'distance_km': dist_km,
                            'time_days': (datetime.fromisoformat(new_case.detection_date) - 
                                         datetime.fromisoformat(source_case.detection_date)).days,
                            'source_subtype': source_case.virus_subtype,
                            'target_subtype': new_case.virus_subtype
                        })
        
        # Estimate base transmission rate
        if transmission_events:
            distances = np.array([event['distance_km'] for event in transmission_events])
            decay_factor = distances ** (-self.distance_decay)
            self.base_transmission_rate = len(transmission_events) / np.sum(decay_factor)
        else:
            # Default if no transmission events found
            self.base_transmission_rate = 0.1
        
        # Estimate subtype-specific factors
        subtype_counts = {}
        for event in transmission_events:
            subtype = event['source_subtype']
            if subtype not in subtype_counts:
                subtype_counts[subtype] = 0
            subtype_counts[subtype] += 1
            
        total_events = len(transmission_events)
        if total_events > 0:
            for subtype, count in subtype_counts.items():
                self.subtype_factors[subtype] = count / total_events
        
        # Set default for subtypes not observed
        for subtype in VirusSubtype:
            if subtype not in self.subtype_factors:
                self.subtype_factors[subtype] = 0.5  # default factor
        
        self.fitted = True
    
    def predict(self, 
               current_cases: List[Case], 
               regions: List[GeoRegion], 
               days_ahead: int = 7,
               **kwargs) -> Dict[str, Any]:
        """
        Predict the spread of avian influenza over the specified time period.
        
        Args:
            current_cases: Current active cases
            regions: List of geographic regions
            days_ahead: Number of days to predict ahead
            **kwargs: Additional parameters:
                - environmental_factors: Optional environmental data by region
                
        Returns:
            Dictionary containing predictions:
                - risk_by_region: Dictionary mapping region IDs to risk scores
                - predicted_case_count: Estimated number of new cases by region
                - confidence_intervals: 95% confidence intervals for predictions
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Filter for recently active cases within time window
        now = datetime.now()
        active_cases = [
            case for case in current_cases 
            if (now - datetime.fromisoformat(case.detection_date)).days <= self.time_window
        ]
        
        # Calculate risk for each region
        risk_by_region = {}
        predicted_cases_by_region = {}
        confidence_intervals = {}
        
        for region in regions:
            # Calculate region centroid for distance calculation
            region_lat = region.centroid.latitude
            region_long = region.centroid.longitude
            
            # Calculate risk contribution from each active case
            risk_contributions = []
            
            for case in active_cases:
                # Calculate distance between case and region centroid
                dist_km = self._calculate_distance(
                    case.location.latitude,
                    case.location.longitude,
                    region_lat,
                    region_long
                )
                
                # Skip if beyond transmission threshold
                if dist_km > self.transmission_threshold:
                    continue
                
                # Calculate distance-based transmission probability
                if dist_km > 0:
                    transmission_prob = self.base_transmission_rate * (dist_km ** (-self.distance_decay))
                else:
                    # Handle case where distance is 0 (same location)
                    transmission_prob = self.base_transmission_rate
                
                # Adjust for virus subtype
                subtype_factor = self.subtype_factors.get(case.virus_subtype, 0.5)
                transmission_prob *= subtype_factor
                
                # Apply environmental adjustment if provided
                env_factors = kwargs.get('environmental_factors', {})
                if region.id in env_factors:
                    # Adjust based on environmental suitability (0.5-2.0 multiplier)
                    env_adjustment = 0.5 + 1.5 * env_factors[region.id]
                    transmission_prob *= env_adjustment
                
                risk_contributions.append(transmission_prob)
            
            # Total risk is sum of contributions from all relevant cases
            total_risk = sum(risk_contributions) if risk_contributions else 0
            
            # Scale to account for multiple days ahead
            scaled_risk = 1 - (1 - total_risk) ** days_ahead
            
            # Ensure risk is between 0 and 1
            scaled_risk = min(max(scaled_risk, 0), 1)
            
            # Calculate expected number of cases using region population/farm density
            region_density_factor = getattr(region, 'farm_density', 1.0)
            expected_cases = scaled_risk * region_density_factor * days_ahead
            
            # Generate confidence interval (simplistic approach)
            if expected_cases > 0:
                # Using Poisson distribution for count data
                lower_ci = max(0, stats.poisson.ppf(0.025, expected_cases))
                upper_ci = stats.poisson.ppf(0.975, expected_cases)
            else:
                lower_ci = 0
                upper_ci = 0
                
            risk_by_region[region.id] = scaled_risk
            predicted_cases_by_region[region.id] = expected_cases
            confidence_intervals[region.id] = (lower_ci, upper_ci)
        
        return {
            'risk_by_region': risk_by_region,
            'predicted_case_count': predicted_cases_by_region,
            'confidence_intervals': confidence_intervals
        }
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2) -> float:
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        """
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return c * r


class NetworkBasedSpreadModel(SpatialSpreadModel):
    """
    A model that predicts spread based on network connections between locations,
    such as bird migration routes, farm supply chains, or transportation networks.
    """
    
    def __init__(self, network_type="migration"):
        """
        Initialize the network-based spread model.
        
        Args:
            network_type: Type of network to model (migration, trade, transport)
        """
        super().__init__()
        self.name = f"Network-Based Spread Model ({network_type})"
        self.description = f"Predicts spread based on {network_type} networks"
        self.network_type = network_type
        self.network_weights = {}
        self.fitted = False
        
    def fit(self, cases: List[Case], regions: List[GeoRegion], **kwargs) -> None:
        """
        Fit the model using historical case data and network information.
        
        Args:
            cases: List of historical cases
            regions: List of geographic regions
            **kwargs: Additional parameters:
                - network_data: Dictionary containing network connection weights
                - migration_routes: Optional bird migration route data
                - trade_data: Optional poultry trade data
        """
        network_data = kwargs.get('network_data')
        if network_data is None:
            raise ValueError("Network data is required for NetworkBasedSpreadModel")
            
        # Store network weights
        self.network_weights = network_data
        
        # Process historical transmission along network
        sorted_cases = sorted(cases, key=lambda c: datetime.fromisoformat(c.detection_date))
        
        # Define temporal windows for analysis (e.g., weekly)
        time_windows = []
        if sorted_cases:
            start_date = datetime.fromisoformat(sorted_cases[0].detection_date).date()
            end_date = datetime.fromisoformat(sorted_cases[-1].detection_date).date()
            
            current_window = start_date
            while current_window <= end_date:
                window_end = current_window + timedelta(days=7)
                time_windows.append((current_window, window_end))
                current_window = window_end
        
        # Analyze transmission patterns along network edges
        transmission_counts = {}
        total_transmissions = 0
        
        for i, (window_start, window_end) in enumerate(time_windows[:-1]):
            # Cases in current window
            current_window_cases = [c for c in sorted_cases 
                                    if window_start <= datetime.fromisoformat(c.detection_date).date() < window_end]
            
            # Cases in next window
            next_window_cases = [c for c in sorted_cases 
                                if window_end <= datetime.fromisoformat(c.detection_date).date() < window_end + timedelta(days=7)]
            
            # Map cases to regions
            current_regions = set(c.region_id for c in current_window_cases if hasattr(c, 'region_id'))
            
            # Check for potential transmissions to connected regions
            for next_case in next_window_cases:
                if not hasattr(next_case, 'region_id'):
                    continue
                    
                next_region = next_case.region_id
                
                # Check if any current regions could have transmitted to this region
                for current_region in current_regions:
                    # Check if network connection exists
                    network_key = f"{current_region}:{next_region}"
                    if network_key in self.network_weights and self.network_weights[network_key] > 0:
                        # Record transmission along this network edge
                        if network_key not in transmission_counts:
                            transmission_counts[network_key] = 0
                        transmission_counts[network_key] += 1
                        total_transmissions += 1
        
        # Calculate transmission probabilities based on observed patterns
        self.transmission_probs = {}
        if total_transmissions > 0:
            for network_key, count in transmission_counts.items():
                self.transmission_probs[network_key] = count / total_transmissions
        
        self.fitted = True
    
    def predict(self, 
               current_cases: List[Case], 
               regions: List[GeoRegion], 
               days_ahead: int = 7,
               **kwargs) -> Dict[str, Any]:
        """
        Predict the spread of avian influenza over the specified time period.
        
        Args:
            current_cases: Current active cases
            regions: List of geographic regions
            days_ahead: Number of days to predict ahead
            **kwargs: Additional parameters:
                - seasonal_factor: Adjustment for seasonal migration patterns
                - trade_volume: Current trade volume data
                
        Returns:
            Dictionary containing predictions:
                - risk_by_region: Dictionary mapping region IDs to risk scores
                - predicted_case_count: Estimated number of new cases by region
                - transmission_paths: Likely transmission paths
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Get current active regions with cases
        active_regions = set(case.region_id for case in current_cases 
                           if hasattr(case, 'region_id'))
        
        # Calculate risk for each region based on network connections
        risk_by_region = {}
        predicted_cases = {}
        transmission_paths = []
        
        for region in regions:
            region_id = region.id
            
            # Skip if this is already an active region
            if region_id in active_regions:
                risk_by_region[region_id] = 1.0  # Maximum risk
                # Estimate additional cases in already affected regions
                existing_cases = len([c for c in current_cases 
                                    if hasattr(c, 'region_id') and c.region_id == region_id])
                predicted_cases[region_id] = existing_cases * 0.5  # Simplified estimate
                continue
            
            # Calculate risk from connected regions with active cases
            risk = 0
            for active_region in active_regions:
                network_key = f"{active_region}:{region_id}"
                if network_key in self.network_weights:
                    connection_strength = self.network_weights[network_key]
                    # Get transmission probability, default to a small value if not observed
                    trans_prob = self.transmission_probs.get(network_key, 0.01)
                    
                    # Apply seasonal adjustment if provided
                    seasonal_factor = kwargs.get('seasonal_factor', 1.0)
                    if self.network_type == 'migration':
                        trans_prob *= seasonal_factor
                    
                    # Apply trade volume adjustment if provided
                    if self.network_type == 'trade' and 'trade_volume' in kwargs:
                        trade_data = kwargs['trade_volume']
                        if network_key in trade_data:
                            volume_factor = trade_data[network_key] / trade_data.get('baseline', 1.0)
                            trans_prob *= volume_factor
                    
                    path_risk = connection_strength * trans_prob
                    risk += path_risk
                    
                    # Record significant transmission paths
                    if path_risk > 0.05:
                        transmission_paths.append({
                            'source': active_region,
                            'target': region_id,
                            'risk': path_risk
                        })
            
            # Account for multiple time steps (days ahead)
            # Using a simplified cumulative risk model
            cumulative_risk = 1 - (1 - risk) ** days_ahead
            risk_by_region[region_id] = min(cumulative_risk, 1.0)  # Cap at 1.0
            
            # Estimate case count based on risk and region properties
            farm_count = getattr(region, 'farm_count', 10)  # Default if not available
            susceptible = farm_count * 0.8  # Assume 80% susceptible
            attack_rate = 0.2  # Basic attack rate
            expected_cases = risk_by_region[region_id] * susceptible * attack_rate
            predicted_cases[region_id] = expected_cases
        
        return {
            'risk_by_region': risk_by_region,
            'predicted_case_count': predicted_cases,
            'transmission_paths': transmission_paths
        }


class GaussianProcessSpatioTemporalModel(SpatialSpreadModel):
    """
    A Gaussian Process model for spatiotemporal prediction of avian influenza spread,
    accounting for both spatial correlation and temporal trends.
    """
    
    def __init__(self, 
                spatial_length_scale=50.0,  # km
                temporal_length_scale=7.0,  # days
                nugget=0.05):
        """
        Initialize the Gaussian Process model.
        
        Args:
            spatial_length_scale: Length scale for spatial correlation (km)
            temporal_length_scale: Length scale for temporal correlation (days)
            nugget: Noise level in observations
        """
        super().__init__()
        self.name = "Gaussian Process Spatiotemporal Model"
        self.description = "Predicts spread using GP regression with spatiotemporal kernel"
        
        # Model parameters
        self.spatial_length_scale = spatial_length_scale
        self.temporal_length_scale = temporal_length_scale
        self.nugget = nugget
        
        # Model objects
        self.gp_model = None
        self.X_train = None
        self.y_train = None
        self.fitted = False
    
    def fit(self, cases: List[Case], regions: List[GeoRegion], **kwargs) -> None:
        """
        Fit the Gaussian Process model using historical case data.
        
        Args:
            cases: List of historical cases
            regions: List of geographic regions
            **kwargs: Additional parameters:
                - covariates: Optional additional covariates by region/time
        """
        if not cases:
            raise ValueError("Need at least one case for training")
        
        # Prepare training data
        X = []  # Features: [lat, lon, time, covariates...]
        y = []  # Target: case count or presence
        
        # Get unique dates from cases
        dates = sorted(set(datetime.fromisoformat(case.detection_date).date() 
                          for case in cases))
        date_to_day = {date: i for i, date in enumerate(dates)}
        
        # Group cases by region and day
        case_counts = {}
        for case in cases:
            case_date = datetime.fromisoformat(case.detection_date).date()
            day_idx = date_to_day[case_date]
            
            # Get region info
            region_id = getattr(case, 'region_id', None)
            if not region_id:
                # If no region_id, use case location directly
                loc_key = (case.location.latitude, case.location.longitude)
                region_info = {'centroid': case.location, 'id': f"loc:{loc_key}"}
            else:
                # Find matching region
                matching_regions = [r for r in regions if r.id == region_id]
                if not matching_regions:
                    continue
                region_info = matching_regions[0]
            
            # Create space-time key
            if hasattr(region_info, 'centroid'):
                centroid = region_info.centroid
                space_time_key = (centroid.latitude, centroid.longitude, day_idx)
            else:
                # Fallback if no centroid
                space_time_key = (0, 0, day_idx)
            
            # Count cases
            if space_time_key not in case_counts:
                case_counts[space_time_key] = 0
            case_counts[space_time_key] += 1
        
        # Convert to training data
        covariates = kwargs.get('covariates', {})
        for (lat, lon, day), count in case_counts.items():
            # Basic spatiotemporal features
            features = [lat, lon, day]
            
            # Add any covariates if available
            region_key = next((k for k, v in case_counts.keys() if k[0] == lat and k[1] == lon), None)
            if region_key and region_key in covariates:
                features.extend(covariates[region_key])
            
            X.append(features)
            y.append(count)
        
        # Convert to numpy arrays
        self.X_train = np.array(X)
        self.y_train = np.array(y)
        
        # Normalize coordinates to improve GP performance
        if self.X_train.shape[0] > 0:
            self.lat_mean = np.mean(self.X_train[:, 0])
            self.lat_std = np.std(self.X_train[:, 0]) or 1.0
            self.lon_mean = np.mean(self.X_train[:, 1])
            self.lon_std = np.std(self.X_train[:, 1]) or 1.0
            self.time_mean = np.mean(self.X_train[:, 2])
            self.time_std = np.std(self.X_train[:, 2]) or 1.0
            
            # Normalize
            self.X_train_norm = self.X_train.copy()
            self.X_train_norm[:, 0] = (self.X_train[:, 0] - self.lat_mean) / self.lat_std
            self.X_train_norm[:, 1] = (self.X_train[:, 1] - self.lon_mean) / self.lon_std
            self.X_train_norm[:, 2] = (self.X_train[:, 2] - self.time_mean) / self.time_std
            
            # Create kernel: combination of spatial and temporal components
            spatial_kernel = ConstantKernel() * RBF(
                length_scale=[self.spatial_length_scale/self.lat_std, 
                             self.spatial_length_scale/self.lon_std], 
                length_scale_bounds=(1e-1, 1e3)
            )
            temporal_kernel = ConstantKernel() * RBF(
                length_scale=self.temporal_length_scale/self.time_std,
                length_scale_bounds=(1e-1, 1e3)
            )
            kernel = spatial_kernel * temporal_kernel
            
            # Create and fit GP model
            self.gp_model = GaussianProcessRegressor(
                kernel=kernel,
                alpha=self.nugget,
                normalize_y=True,
                n_restarts_optimizer=3
            )
            self.gp_model.fit(self.X_train_norm, self.y_train)
            self.fitted = True
        else:
            raise ValueError("No valid training data could be extracted from cases")
    
    def predict(self, 
               current_cases: List[Case], 
               regions: List[GeoRegion], 
               days_ahead: int = 7,
               **kwargs) -> Dict[str, Any]:
        """
        Predict the spread of avian influenza over the specified time period.
        
        Args:
            current_cases: Current active cases
            regions: List of geographic regions
            days_ahead: Number of days to predict ahead
            **kwargs: Additional parameters:
                - covariates: Optional additional covariates by region/time
                - prediction_grid: Optional custom prediction grid points
                
        Returns:
            Dictionary containing predictions:
                - risk_by_region: Dictionary mapping region IDs to risk scores
                - predicted_case_count: Estimated number of new cases by region
                - confidence_intervals: 95% confidence intervals for predictions
                - prediction_grid: Optional grid of prediction points with values
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Get latest day from training data
        latest_day = int(np.max(self.X_train[:, 2]))
        
        # Create prediction points for each region for future days
        X_pred = []
        region_indices = {}  # Map prediction indices to regions
        covariates = kwargs.get('covariates', {})
        
        # For each region, predict for each day in the forecast period
        for region_idx, region in enumerate(regions):
            if hasattr(region, 'centroid'):
                centroid = region.centroid
                for day_offset in range(1, days_ahead + 1):
                    pred_day = latest_day + day_offset
                    
                    # Basic spatiotemporal features
                    features = [centroid.latitude, centroid.longitude, pred_day]
                    
                    # Add covariates if available
                    if region.id in covariates:
                        features.extend(covariates[region.id])
                    
                    X_pred.append(features)
                    pred_idx = len(X_pred) - 1
                    region_indices[(region.id, day_offset)] = pred_idx
        
        if not X_pred:
            return {
                'risk_by_region': {},
                'predicted_case_count': {},
                'confidence_intervals': {}
            }
        
        # Convert to numpy array and normalize
        X_pred = np.array(X_pred)
        X_pred_norm = X_pred.copy()
        X_pred_norm[:, 0] = (X_pred[:, 0] - self.lat_mean) / self.lat_std
        X_pred_norm[:, 1] = (X_pred[:, 1] - self.lon_mean) / self.lon_std
        X_pred_norm[:, 2] = (X_pred[:, 2] - self.time_mean) / self.time_std
        
        # Make predictions
        y_pred, y_std = self.gp_model.predict(X_pred_norm, return_std=True)
        
        # Create prediction output by region
        risk_by_region = {}
        predicted_cases = {}
        confidence_intervals = {}
        
        for region in regions:
            region_id = region.id
            
            # Aggregate predictions across forecast days
            region_predictions = []
            region_std = []
            
            for day_offset in range(1, days_ahead + 1):
                key = (region_id, day_offset)
                if key in region_indices:
                    pred_idx = region_indices[key]
                    region_predictions.append(max(0, y_pred[pred_idx]))  # Ensure non-negative
                    region_std.append(y_std[pred_idx])
            
            if region_predictions:
                # Calculate cumulative cases over the forecast period
                total_predicted = sum(region_predictions)
                
                # Calculate average standard deviation
                avg_std = np.mean(region_std) if region_std else 0
                
                # Compute risk score (normalized predicted cases)
                max_possible = 10 * days_ahead  # Arbitrary scaling factor
                risk = min(total_predicted / max_possible, 1.0)
                
                # Calculate confidence intervals
                lower_ci = max(0, total_predicted - 1.96 * avg_std * np.sqrt(days_ahead))
                upper_ci = total_predicted + 1.96 * avg_std * np.sqrt(days_ahead)
                
                risk_by_region[region_id] = risk
                predicted_cases[region_id] = total_predicted
                confidence_intervals[region_id] = (lower_ci, upper_ci)
        
        # Optional: create grid prediction if requested
        prediction_grid = None
        if 'prediction_grid' in kwargs and kwargs['prediction_grid']:
            grid_points = kwargs['prediction_grid']
            grid_pred = []
            
            for point in grid_points:
                lat, lon = point[:2]
                features = [lat, lon, latest_day + days_ahead]
                
                # Normalize
                norm_features = features.copy()
                norm_features[0] = (features[0] - self.lat_mean) / self.lat_std
                norm_features[1] = (features[1] - self.lon_mean) / self.lon_std
                norm_features[2] = (features[2] - self.time_mean) / self.time_std
                
                # Predict
                val, std = self.gp_model.predict(np.array([norm_features]), return_std=True)
                grid_pred.append((lat, lon, max(0, val[0]), std[0]))
            
            prediction_grid = grid_pred
        
        return {
            'risk_by_region': risk_by_region,
            'predicted_case_count': predicted_cases,
            'confidence_intervals': confidence_intervals,
            'prediction_grid': prediction_grid
        }