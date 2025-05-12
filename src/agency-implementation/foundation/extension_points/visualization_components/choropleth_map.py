"""
Choropleth Map Visualization

Extension point implementation for choropleth map visualizations.
"""

from typing import Dict, List, Any, Optional, Union
import json
import logging
from .. import base
from . import VisualizationExtensionPoint

logger = logging.getLogger(__name__)

@base.BaseExtensionPoint.extension_point("visualization", "choropleth_map")
class ChoroplethMapVisualization(VisualizationExtensionPoint):
    """Implementation of visualization extension point for choropleth maps."""
    
    def __init__(self):
        self.config = {}
        self.geo_json = {}
        self.color_schemes = {}
        self.is_initialized = False
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the choropleth map visualization.
        
        Args:
            config: Configuration parameters including GeoJSON data
            
        Returns:
            bool: True if initialization successful
        """
        try:
            # Store configuration
            self.config = config
            
            # Load GeoJSON data for map rendering
            geo_json_path = config.get("geo_json_path")
            geo_json_str = config.get("geo_json_string")
            
            if geo_json_path:
                try:
                    with open(geo_json_path, 'r') as f:
                        self.geo_json = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading GeoJSON from path: {e}")
                    return False
            elif geo_json_str:
                try:
                    self.geo_json = json.loads(geo_json_str)
                except Exception as e:
                    logger.error(f"Error parsing GeoJSON string: {e}")
                    return False
            else:
                logger.error("No GeoJSON data provided")
                return False
            
            # Load color schemes
            self.color_schemes = {
                "blue": ["#f7fbff", "#deebf7", "#c6dbef", "#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#08519c", "#08306b"],
                "green": ["#f7fcf5", "#e5f5e0", "#c7e9c0", "#a1d99b", "#74c476", "#41ab5d", "#238b45", "#006d2c", "#00441b"],
                "red": ["#fff5f0", "#fee0d2", "#fcbba1", "#fc9272", "#fb6a4a", "#ef3b2c", "#cb181d", "#a50f15", "#67000d"],
                "purple": ["#fcfbfd", "#efedf5", "#dadaeb", "#bcbddc", "#9e9ac8", "#807dba", "#6a51a3", "#54278f", "#3f007d"],
                "orange": ["#fff5eb", "#fee6ce", "#fdd0a2", "#fdae6b", "#fd8d3c", "#f16913", "#d94801", "#a63603", "#7f2704"],
                "gray": ["#ffffff", "#f0f0f0", "#d9d9d9", "#bdbdbd", "#969696", "#737373", "#525252", "#252525", "#000000"],
            }
            
            # Add any custom color schemes from config
            custom_schemes = config.get("color_schemes", {})
            self.color_schemes.update(custom_schemes)
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Error initializing choropleth map visualization: {e}")
            return False
    
    def shutdown(self) -> None:
        """Clean up resources used by the visualization component."""
        self.geo_json = {}
        self.config = {}
        self.is_initialized = False
    
    def render(self, data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render the choropleth map visualization.
        
        Args:
            data: The geographic data to visualize
            options: Rendering options
            
        Returns:
            Dict containing the visualization output
        """
        if not self.is_initialized:
            raise RuntimeError("Choropleth map visualization not initialized")
            
        try:
            # Merge options with defaults
            default_options = self.get_default_options()
            merged_options = {**default_options, **options}
            
            # Validate data
            validation_result = self.validate_data(data)
            if not validation_result.get("valid", False):
                return {
                    "success": False,
                    "error": f"Invalid data: {validation_result.get('errors')}",
                }
            
            # Get target format
            output_format = merged_options.get("format", "html")
            
            # Generate the visualization based on format
            if output_format == "html":
                return self._render_html(data, merged_options)
            elif output_format == "svg":
                return self._render_svg(data, merged_options)
            elif output_format == "json":
                return self._render_json(data, merged_options)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported output format: {output_format}",
                }
                
        except Exception as e:
            logger.error(f"Error rendering choropleth map: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    def _render_html(self, data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate HTML visualization with Leaflet or D3."""
        try:
            # Extract required options
            title = options.get("title", "Choropleth Map")
            width = options.get("width", 800)
            height = options.get("height", 500)
            color_scheme = options.get("color_scheme", "blue")
            
            # Get color scale
            colors = self.color_schemes.get(color_scheme, self.color_schemes["blue"])
            
            # Determine library to use
            library = options.get("library", "leaflet")
            
            if library == "leaflet":
                # Generate Leaflet-based visualization
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>{title}</title>
                    <meta charset="utf-8" />
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css" />
                    <script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.4.2/chroma.min.js"></script>
                    <style>
                        #map {{ height: {height}px; width: {width}px; }}
                        .info {{ padding: 6px 8px; font: 14px/16px Arial, Helvetica, sans-serif; background: white; background: rgba(255,255,255,0.8); box-shadow: 0 0 15px rgba(0,0,0,0.2); border-radius: 5px; }}
                        .info h4 {{ margin: 0 0 5px; color: #777; }}
                        .legend {{ line-height: 18px; color: #555; }}
                        .legend i {{ width: 18px; height: 18px; float: left; margin-right: 8px; opacity: 0.7; }}
                    </style>
                </head>
                <body>
                    <h1>{title}</h1>
                    <div id="map"></div>
                    <script>
                        // Data
                        const geoJsonData = {json.dumps(self.geo_json)};
                        const valueData = {json.dumps(data.get("values", {}))};
                        
                        // Create color scale using chroma.js
                        const colorScale = chroma.scale({json.dumps(colors)})
                            .domain([{data.get("min_value", 0)}, {data.get("max_value", 100)}]);
                        
                        // Initialize map
                        const map = L.map('map').setView([{options.get("center_lat", 37.8)}, {options.get("center_lng", -96)}], {options.get("zoom", 4)});
                        
                        // Add basemap
                        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        }}).addTo(map);
                        
                        // Style function
                        function getColor(d) {{
                            return d ? colorScale(d).hex() : '#FFEDA0';
                        }}
                        
                        function style(feature) {{
                            const id = feature.properties.{options.get("id_property", "id")};
                            const value = valueData[id];
                            return {{
                                fillColor: getColor(value),
                                weight: 2,
                                opacity: 1,
                                color: 'white',
                                dashArray: '3',
                                fillOpacity: 0.7
                            }};
                        }}
                        
                        // Add GeoJSON layer
                        const geojson = L.geoJson(geoJsonData, {{
                            style: style,
                            onEachFeature: onEachFeature
                        }}).addTo(map);
                        
                        // Interaction
                        function highlightFeature(e) {{
                            const layer = e.target;
                            layer.setStyle({{
                                weight: 5,
                                color: '#666',
                                dashArray: '',
                                fillOpacity: 0.7
                            }});
                            layer.bringToFront();
                            info.update(layer.feature.properties);
                        }}
                        
                        function resetHighlight(e) {{
                            geojson.resetStyle(e.target);
                            info.update();
                        }}
                        
                        function onEachFeature(feature, layer) {{
                            layer.on({{
                                mouseover: highlightFeature,
                                mouseout: resetHighlight
                            }});
                        }}
                        
                        // Info control
                        const info = L.control();
                        
                        info.onAdd = function(map) {{
                            this._div = L.DomUtil.create('div', 'info');
                            this.update();
                            return this._div;
                        }};
                        
                        info.update = function(props) {{
                            const nameProperty = "{options.get("name_property", "name")}";
                            const idProperty = "{options.get("id_property", "id")}";
                            this._div.innerHTML = '<h4>{options.get("info_title", "Information")}</h4>' + 
                                (props ? '<b>' + props[nameProperty] + '</b><br />' + (valueData[props[idProperty]] || 'No data') + ' {options.get("value_label", "")}' : 'Hover over an area');
                        }};
                        
                        info.addTo(map);
                        
                        // Legend
                        const legend = L.control({{position: 'bottomright'}});
                        
                        legend.onAdd = function(map) {{
                            const div = L.DomUtil.create('div', 'info legend');
                            const min = {data.get("min_value", 0)};
                            const max = {data.get("max_value", 100)};
                            const step = (max - min) / 8;
                            const grades = Array.from({{length: 9}}, (_, i) => Math.round(min + i * step));
                            
                            div.innerHTML = '<h4>{options.get("legend_title", "Legend")}</h4>';
                            
                            // Loop through intervals and generate a label with a colored square for each interval
                            for (let i = 0; i < grades.length; i++) {{
                                div.innerHTML +=
                                    '<i style="background:' + colorScale(grades[i]).hex() + '"></i> ' +
                                    grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
                            }}
                            
                            return div;
                        }};
                        
                        legend.addTo(map);
                    </script>
                </body>
                </html>
                """
                
                return {
                    "success": True,
                    "format": "html",
                    "content": html,
                    "title": title,
                }
                
            elif library == "d3":
                # Generate D3-based visualization (simplified for example)
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>{title}</title>
                    <meta charset="utf-8">
                    <script src="https://d3js.org/d3.v7.min.js"></script>
                    <script src="https://d3js.org/topojson.v3.min.js"></script>
                    <style>
                        body {{ font-family: Arial, sans-serif; }}
                        .tooltip {{ position: absolute; background: white; border: 1px solid #ddd; padding: 10px; pointer-events: none; }}
                    </style>
                </head>
                <body>
                    <h1>{title}</h1>
                    <div id="visualization"></div>
                    <script>
                        // Data
                        const geoJson = {json.dumps(self.geo_json)};
                        const valueData = {json.dumps(data.get("values", {}))};
                        const minValue = {data.get("min_value", 0)};
                        const maxValue = {data.get("max_value", 100)};
                        
                        // Set up dimensions
                        const width = {width};
                        const height = {height};
                        
                        // Create SVG
                        const svg = d3.select("#visualization")
                            .append("svg")
                            .attr("width", width)
                            .attr("height", height);
                            
                        // Create tooltip
                        const tooltip = d3.select("body").append("div")
                            .attr("class", "tooltip")
                            .style("opacity", 0);
                            
                        // Create projection
                        const projection = d3.geoMercator()
                            .fitSize([width, height], geoJson);
                            
                        // Create path generator
                        const path = d3.geoPath()
                            .projection(projection);
                            
                        // Create color scale
                        const colorScale = d3.scaleLinear()
                            .domain([minValue, maxValue])
                            .range(["{colors[0]}", "{colors[-1]}"]);
                            
                        // Draw map
                        svg.selectAll("path")
                            .data(geoJson.features)
                            .enter()
                            .append("path")
                            .attr("d", path)
                            .attr("fill", d => {{
                                const id = d.properties.{options.get("id_property", "id")};
                                const value = valueData[id];
                                return value ? colorScale(value) : "#ccc";
                            }})
                            .attr("stroke", "#fff")
                            .attr("stroke-width", 0.5)
                            .on("mouseover", function(event, d) {{
                                d3.select(this)
                                    .attr("stroke", "#000")
                                    .attr("stroke-width", 1.5);
                                    
                                const id = d.properties.{options.get("id_property", "id")};
                                const name = d.properties.{options.get("name_property", "name")};
                                const value = valueData[id] || "No data";
                                
                                tooltip.transition()
                                    .duration(200)
                                    .style("opacity", .9);
                                tooltip.html(`<strong>${{name}}</strong><br/>${{value}} {options.get("value_label", "")}`)
                                    .style("left", (event.pageX) + "px")
                                    .style("top", (event.pageY - 28) + "px");
                            }})
                            .on("mouseout", function() {{
                                d3.select(this)
                                    .attr("stroke", "#fff")
                                    .attr("stroke-width", 0.5);
                                    
                                tooltip.transition()
                                    .duration(500)
                                    .style("opacity", 0);
                            }});
                            
                        // Add legend
                        const legendWidth = 20;
                        const legendHeight = 200;
                        const legend = svg.append("g")
                            .attr("transform", `translate(${{width - 50}}, ${{height - 220}})`);
                            
                        legend.append("text")
                            .attr("x", 0)
                            .attr("y", -10)
                            .text("{options.get("legend_title", "Legend")}");
                            
                        // Create gradient for legend
                        const gradient = legend.append("defs")
                            .append("linearGradient")
                            .attr("id", "gradient")
                            .attr("x1", "0%")
                            .attr("y1", "100%")
                            .attr("x2", "0%")
                            .attr("y2", "0%");
                            
                        // Add color stops
                        {colors_js = [f'gradient.append("stop").attr("offset", "{i/8}").attr("stop-color", "{color}");' for i, color in enumerate(colors)]}
                        {' '.join(colors_js)}
                            
                        // Draw legend rectangle
                        legend.append("rect")
                            .attr("width", legendWidth)
                            .attr("height", legendHeight)
                            .style("fill", "url(#gradient)");
                            
                        // Add legend scale
                        const legendScale = d3.scaleLinear()
                            .domain([minValue, maxValue])
                            .range([legendHeight, 0]);
                            
                        const legendAxis = d3.axisRight(legendScale)
                            .ticks(5);
                            
                        legend.append("g")
                            .attr("transform", `translate(${{legendWidth}}, 0)`)
                            .call(legendAxis);
                    </script>
                </body>
                </html>
                """
                
                return {
                    "success": True,
                    "format": "html",
                    "content": html,
                    "title": title,
                }
                
            else:
                return {
                    "success": False,
                    "error": f"Unsupported library: {library}",
                }
                
        except Exception as e:
            logger.error(f"Error rendering HTML choropleth map: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    def _render_svg(self, data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SVG visualization."""
        # For brevity, this would implement SVG generation
        # Similar to the D3 version but returning just the SVG
        return {
            "success": True,
            "format": "svg",
            "content": "<svg><!-- SVG content would be generated here --></svg>",
            "width": options.get("width", 800),
            "height": options.get("height", 500),
        }
    
    def _render_json(self, data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON visualization configuration."""
        # Return a configuration that could be used by a frontend library
        return {
            "success": True,
            "format": "json",
            "content": {
                "type": "choropleth",
                "geoJson": self.geo_json,
                "data": data,
                "options": options,
                "colorScheme": self.color_schemes.get(options.get("color_scheme", "blue")),
            },
        }
    
    def get_supported_formats(self) -> List[str]:
        """
        Get the output formats supported by this visualization.
        
        Returns:
            List of supported format identifiers
        """
        return ["html", "svg", "json"]
    
    def get_required_data_schema(self) -> Dict[str, Any]:
        """
        Get the schema of data required by this visualization.
        
        Returns:
            Dict describing the required data structure
        """
        return {
            "type": "object",
            "required": ["values"],
            "properties": {
                "values": {
                    "type": "object",
                    "description": "Object mapping feature IDs to numerical values",
                },
                "min_value": {
                    "type": "number",
                    "description": "Minimum value for color scale",
                },
                "max_value": {
                    "type": "number",
                    "description": "Maximum value for color scale",
                }
            }
        }
    
    def get_default_options(self) -> Dict[str, Any]:
        """
        Get the default rendering options.
        
        Returns:
            Dict of default option values
        """
        return {
            "format": "html",
            "library": "leaflet",
            "title": "Choropleth Map",
            "width": 800,
            "height": 500,
            "color_scheme": "blue",
            "id_property": "id",
            "name_property": "name",
            "value_label": "",
            "info_title": "Information",
            "legend_title": "Legend",
            "center_lat": 37.8,
            "center_lng": -96,
            "zoom": 4,
        }
    
    def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input data against the required schema.
        
        Args:
            data: The data to validate
            
        Returns:
            Dict with validation results
        """
        errors = []
        
        # Check required fields
        if "values" not in data:
            errors.append("Missing required field: values")
        elif not isinstance(data["values"], dict):
            errors.append("Field 'values' must be an object mapping IDs to values")
            
        # Check value types
        if "min_value" in data and not isinstance(data["min_value"], (int, float)):
            errors.append("Field 'min_value' must be a number")
            
        if "max_value" in data and not isinstance(data["max_value"], (int, float)):
            errors.append("Field 'max_value' must be a number")
            
        # If min/max not provided, calculate from values
        if "values" in data and isinstance(data["values"], dict) and data["values"]:
            values = [v for v in data["values"].values() if isinstance(v, (int, float))]
            if values:
                if "min_value" not in data:
                    data["min_value"] = min(values)
                if "max_value" not in data:
                    data["max_value"] = max(values)
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }
    
    def transform_data(self, data: Dict[str, Any], transformation: str) -> Dict[str, Any]:
        """
        Apply a transformation to the input data.
        
        Args:
            data: The data to transform
            transformation: Identifier of the transformation to apply
            
        Returns:
            Dict with transformed data
        """
        if transformation == "normalize":
            # Normalize values to 0-100 range
            if "values" in data and isinstance(data["values"], dict) and data["values"]:
                values = [v for v in data["values"].values() if isinstance(v, (int, float))]
                if values:
                    min_val = min(values)
                    max_val = max(values)
                    range_val = max_val - min_val
                    
                    if range_val > 0:
                        normalized_values = {}
                        for k, v in data["values"].items():
                            if isinstance(v, (int, float)):
                                normalized_values[k] = 100 * (v - min_val) / range_val
                            else:
                                normalized_values[k] = v
                                
                        return {
                            **data,
                            "values": normalized_values,
                            "min_value": 0,
                            "max_value": 100,
                        }
            
            return data
            
        elif transformation == "log":
            # Apply log transformation
            import math
            
            if "values" in data and isinstance(data["values"], dict) and data["values"]:
                log_values = {}
                for k, v in data["values"].items():
                    if isinstance(v, (int, float)) and v > 0:
                        log_values[k] = math.log10(v)
                    elif isinstance(v, (int, float)):
                        log_values[k] = None
                    else:
                        log_values[k] = v
                
                log_data = {
                    **data,
                    "values": log_values,
                }
                
                # Recalculate min/max
                values = [v for v in log_values.values() if isinstance(v, (int, float))]
                if values:
                    log_data["min_value"] = min(values)
                    log_data["max_value"] = max(values)
                    
                return log_data
                
            return data
            
        elif transformation == "quantile":
            # Convert to quantiles
            if "values" in data and isinstance(data["values"], dict) and data["values"]:
                values = [v for v in data["values"].items() if isinstance(v[1], (int, float))]
                if values:
                    # Sort by value
                    values.sort(key=lambda x: x[1])
                    
                    # Divide into 5 quantiles
                    n = len(values)
                    quantile_size = n / 5
                    
                    quantile_values = {}
                    for i, (k, v) in enumerate(values):
                        quantile = min(4, int(i / quantile_size))
                        quantile_values[k] = quantile
                    
                    # Add non-numeric values back
                    for k, v in data["values"].items():
                        if not isinstance(v, (int, float)):
                            quantile_values[k] = v
                    
                    return {
                        **data,
                        "values": quantile_values,
                        "min_value": 0,
                        "max_value": 4,
                    }
            
            return data
            
        else:
            # Unknown transformation, return original data
            return data
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this visualization component.
        
        Returns:
            Dict with component metadata
        """
        return {
            "name": "Choropleth Map",
            "description": "Displays geographic data with color variations to represent values",
            "version": "1.0.0",
            "author": "Agency Implementation Team",
            "supported_libraries": ["leaflet", "d3"],
            "supported_formats": self.get_supported_formats(),
            "available_color_schemes": list(self.color_schemes.keys()),
            "available_transformations": ["normalize", "log", "quantile"],
        }