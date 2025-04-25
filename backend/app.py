from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import pandas as pd
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io
import base64
import os
import json
import re
from dotenv import load_dotenv
from werkzeug.exceptions import BadRequest
import logging
from functools import wraps
import random
import datetime
import squarify
from dateutil import parser as date_parser
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Validate API key exists
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.error("GEMINI_API_KEY environment variable not set")
    raise ValueError("GEMINI_API_KEY environment variable not set")

# Configure Gemini API 
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

app = Flask(__name__)
CORS(app, 
     origins=["https://plott.hitanshu.tech", "http://plott.hitanshu.tech"],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "Accept"],
     methods=["GET", "POST", "OPTIONS"])

# Initialize rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per day", "20 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

# Custom error class
class DiagramError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

# Decorator for error handling
def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except DiagramError as e:
            logger.error(f"DiagramError: {e.message}")
            return jsonify({"error": e.message}), e.status_code
        except json.JSONDecodeError:
            logger.error("Invalid JSON response from Gemini API")
            return jsonify({"error": "Failed to parse AI response"}), 500
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return jsonify({"error": "An unexpected error occurred"}), 500
    return decorated_function

def parse_gemini_json(text):
    """Extract JSON from Gemini response text which might include markdown code blocks"""
    # Try to extract JSON from code blocks
    code_block_match = re.search(r'```(?:json)?\s*([\s\S]+?)\s*```', text)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try the whole text as JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Last resort: look for anything that resembles JSON
        json_like_match = re.search(r'({[\s\S]+})', text)
        if json_like_match:
            try:
                return json.loads(json_like_match.group(1))
            except json.JSONDecodeError:
                pass
    
    raise DiagramError("Could not extract valid JSON from AI response")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/cors-test', methods=['GET', 'OPTIONS'])
def cors_test():
    return jsonify({
        "status": "success",
        "message": "CORS is properly configured",
        "cors_config": {
            "allowed_origins": ["https://plott.hitanshu.tech", "http://plott.hitanshu.tech"],
            "allowed_methods": ["GET", "POST", "OPTIONS"],
            "allowed_headers": ["Content-Type", "Authorization", "Accept"],
            "supports_credentials": True
        }
    }), 200

@app.route('/api/generate-diagram', methods=['POST'])
@handle_errors
@limiter.limit("8 per minute")
def generate_diagram():
    data = request.json
    if not data:
        raise DiagramError("No data provided")
    
    user_prompt = data.get('prompt')
    if not user_prompt:
        raise DiagramError("No prompt provided")
    
    logger.info(f"Processing diagram request: {user_prompt[:50]}...")
    
    # Step 1: Ask Gemini for recommended chart types (multiple)
    recommendation_prompt = f"""
    You are a data visualization expert tasked with recommending the most appropriate chart types.

    USER REQUEST: {user_prompt}

    CRITICAL INSTRUCTIONS:
    1. CAREFULLY ANALYZE what the user is trying to visualize, what data they've provided, and the relationships they want to show
    2. Consider the exact data structure mentioned (if any) in the user's request
    3. Recommend the 3 MOST APPROPRIATE chart types from this list:
       - bar: For comparing values across categories
       - line: For showing trends over time or ordered categories
       - pie: For showing proportions of a whole
       - scatter: For showing relationship between two variables
       - histogram: For showing distribution of a single variable
       - heatmap: For showing patterns in a matrix of values
       - boxplot: For showing distribution statistics with quartiles
       - violin: For showing distribution density across categories
       - area: For showing cumulative totals over time
       - stacked_bar: For showing part-to-whole relationships across categories
       - bubble: For showing relationships between three variables
       - radar: For showing multivariate data on axes radiating from center
       - treemap: For showing hierarchical data as nested rectangles
       - funnel: For showing stages in a process with decreasing quantities

    4. Your ENTIRE response must be ONLY valid JSON with this exact format:
    {{
        "recommended_chart_types": [
            {{
                "chart_type": "first_type",
                "reason": "Specific reason why this chart type is optimal for the requested data"
            }},
            {{
                "chart_type": "second_type",
                "reason": "Specific reason why this chart type is optimal for the requested data"
            }},
            {{
                "chart_type": "third_type",
                "reason": "Specific reason why this chart type is optimal for the requested data"
            }}
        ]
    }}

    REQUIREMENTS:
    - Recommend EXACTLY 3 different chart types, most appropriate first
    - Do NOT add any explanations, text, or markdown outside the JSON
    - Ensure that your suggestions match the user's data structure and visualization goals
    - Provide specific reasons tailored to the user's exact request, not generic descriptions
    """
    
    try:
        recommendation_response = model.generate_content(recommendation_prompt)
        recommendation = parse_gemini_json(recommendation_response.text)
        recommended_chart_types = recommendation.get("recommended_chart_types", [])
        
        # Validate we have at least 3 recommendations
        if len(recommended_chart_types) < 3:
            # Add default recommendations if needed
            default_types = [
                {"chart_type": "bar", "reason": "Default recommendation for comparing values"},
                {"chart_type": "line", "reason": "Default recommendation for showing trends"},
                {"chart_type": "pie", "reason": "Default recommendation for showing proportions"}
            ]
            
            # Add only the needed ones
            for i in range(3 - len(recommended_chart_types)):
                # Find a default type that isn't already recommended
                for default in default_types:
                    if not any(r.get("chart_type") == default["chart_type"] for r in recommended_chart_types):
                        recommended_chart_types.append(default)
                        break
        
        # Ensure we have exactly 3 chart types
        recommended_chart_types = recommended_chart_types[:3]
        
        logger.info(f"Recommended chart types: {[r.get('chart_type') for r in recommended_chart_types]}")
    except Exception as e:
        logger.error(f"Error getting chart recommendations: {str(e)}")
        # Default recommendations if the API call fails
        recommended_chart_types = [
            {"chart_type": "bar", "reason": "Default recommendation for comparing values"},
            {"chart_type": "line", "reason": "Default recommendation for showing trends"},
            {"chart_type": "pie", "reason": "Default recommendation for showing proportions"}
        ]
    
    # Step 2: Parse the user prompt for general information
    parsing_prompt = f"""
    You are a data specification parser responsible for extracting GENERAL visualization requirements.

    USER REQUEST: {user_prompt}

    CRITICAL INSTRUCTIONS:
    Extract the following general information. Focus on high-level details. Defer detailed data point extraction.

    1. data_description: General description of what the user wants to visualize.
    2. x_axis: Suggested label for the x-axis (e.g., "Categories", "Time", "Value"). Use null if unclear.
    3. y_axis: Suggested label for the y-axis (e.g., "Count", "Sales", "Measurement"). Use null if unclear.
    4. title: Suggested clear, descriptive title. Use null if unclear.
    5. subtitle: Optional subtitle providing additional context. Use null if none suggested.
    6. palette: Color palette suggestion if mentioned (e.g., 'viridis', 'Blues'). Use null if not mentioned.

    RESPONSE FORMAT:
    Return ONLY a valid JSON object with these exact fields. No explanation text, no markdown formatting.

    STRICT REQUIREMENTS:
    - Every field MUST be present (use null for truly unknown values).
    - Do NOT extract specific data points or detailed data structures yet.
    - Keep descriptions concise.
    """
    
    parsing_response = model.generate_content(parsing_prompt)
    general_parsed_info = parse_gemini_json(parsing_response.text)
    
    # Add default values if necessary
    default_fields = {'title': 'Generated Chart', 'x_axis': 'X-Axis', 'y_axis': 'Y-Axis', 'data_description': user_prompt, 'subtitle': None, 'palette': 'viridis'}
    for field, default_value in default_fields.items():
        if field not in general_parsed_info or general_parsed_info[field] is None:
            general_parsed_info[field] = default_value
            logger.warning(f"Missing or null general info field: '{field}', using default: '{default_value}'")

    logger.info(f"General Parsed Info: {json.dumps(general_parsed_info, indent=2)}")
    
    # Step 3 & 4: Iterate through recommendations, extract/generate data, and create chart images
    chart_results = []
    error_messages = []
    
    for recommendation in recommended_chart_types:
        chart_type = recommendation.get("chart_type", "bar").lower()
        reason = recommendation.get("reason", "")
        
        try:
            logger.info(f"--- Processing chart type: {chart_type} ---")
            
            # --- Chart-Specific Extraction ---
            chart_specific_extraction_prompt = f"""
            You are a data extraction expert focused on the '{chart_type}' chart type.
            Analyze the user's request and general info provided below.

            USER REQUEST: {user_prompt}
            GENERAL INFO: {json.dumps(general_parsed_info)}
            TARGET CHART TYPE: {chart_type}

            CRITICAL INSTRUCTIONS:
            1. Determine if the USER REQUEST contains specific data points/values suitable for a '{chart_type}' chart.
            2. If YES (specific data found):
               - Extract the EXACT data points relevant for the '{chart_type}' chart.
               - Format them correctly into the appropriate structure for a '{chart_type}' chart.
               - For standard charts: Use `x_values`, `y_values` for basic data.
               - For pie chart: Use `labels` and `sizes`.
               - For heatmap: Use `x_values` (column labels), `y_values` (row labels), and `z_values` (2D matrix).
               - For boxplot/violin: Use `x_values` (categories) and `distributions` (list of lists).
               - For radar chart: Use `categories` (axis labels) and `values` (data points).
               - For treemap: Use `labels` (rectangle labels), `parents` (hierarchy), and `sizes` (rectangle sizes).
               - For funnel: Use `stages` (stage names) and `values` (values for each stage).
               - Set `exact_data_provided` to true.
               - Set `data_specifications` to null.
            3. If NO (no specific data found):
               - Describe the data needed for a '{chart_type}' chart based on the request in `data_specifications`.
               - Set `exact_data_provided` to false.
               - Include the EXACT field names required for this chart type in your response.
            4. Refine `x_axis` and `y_axis` labels specifically for this '{chart_type}' based on the extracted/specified data.
            5. Refine `title` and `subtitle` if the user request gives more specific context for this chart type.

            RESPONSE FORMAT:
            Return ONLY a valid JSON object with these exact fields:
            {{
                "exact_data_provided": boolean,
                // Include ONLY the appropriate fields for this chart type below:
                "x_values": list | null,
                "y_values": list | null,
                "labels": list | null, // For pie, treemap
                "sizes": list | null, // For pie, bubble, treemap
                "categories": list | null, // For radar
                "values": list | null, // For radar
                "z_values": list[list] | null, // For heatmap
                "distributions": list[list] | list | null, // For box/violin
                "groups": list | null, // For stacked_bar, boxplot, violin
                "stages": list | null, // For funnel
                "values": list | null, // For funnel
                "parents": list | null, // For treemap
                // --- End chart-specific keys ---
                "data_specifications": string | null, // Description for AI generation if no exact data
                "x_axis": string, // Refined X-axis label
                "y_axis": string, // Refined Y-axis label
                "title": string, // Refined title
                "subtitle": string | null // Refined subtitle
            }}

            REQUIREMENTS:
            - Adhere strictly to the JSON format. No extra text.
            - Include ONLY the fields relevant to this chart type.
            - Preserve user's exact wording and values when `exact_data_provided` is true.
            """
            
            extraction_response = model.generate_content(chart_specific_extraction_prompt)
            specific_info = parse_gemini_json(extraction_response.text)
            logger.info(f"[{chart_type}] Specific Info Extracted: {json.dumps(specific_info, indent=2)}")

            # --- Chart-Specific Data Generation ---
            specific_chart_data = None
            if specific_info.get("exact_data_provided"):
                logger.info(f"[{chart_type}] Using user-specified data.")
                # Use extracted data directly, validate basic structure
                extracted_data = {
                    "data_source": "user_specified"
                }
                
                # Add only the relevant keys for this chart type
                for key in ["x_values", "y_values", "labels", "sizes", "categories", "values", 
                           "z_values", "distributions", "groups", "stages", "parents"]:
                    if specific_info.get(key) is not None:
                        extracted_data[key] = specific_info[key]

                # Validate that we have the necessary data for this chart type
                if chart_type == 'radar' and 'categories' not in extracted_data and 'values' not in extracted_data:
                    if 'x_values' in extracted_data and 'y_values' in extracted_data:
                        extracted_data['categories'] = extracted_data['x_values']
                        extracted_data['values'] = extracted_data['y_values']
                    else:
                        raise DiagramError(f"[{chart_type}] Missing required fields: categories and values")
                        
                elif chart_type == 'treemap' and 'labels' not in extracted_data and 'sizes' not in extracted_data:
                    if 'x_values' in extracted_data and 'y_values' in extracted_data:
                        extracted_data['labels'] = extracted_data['x_values']
                        extracted_data['sizes'] = extracted_data['y_values']
                    else:
                        raise DiagramError(f"[{chart_type}] Missing required fields: labels and sizes")
                        
                elif chart_type == 'funnel' and 'stages' not in extracted_data and 'values' not in extracted_data:
                    if 'x_values' in extracted_data and 'y_values' in extracted_data:
                        extracted_data['stages'] = extracted_data['x_values']
                        extracted_data['values'] = extracted_data['y_values']
                    else:
                        raise DiagramError(f"[{chart_type}] Missing required fields: stages and values")
                
                specific_chart_data = extracted_data
            else:
                logger.info(f"[{chart_type}] Generating AI data based on specifications.")
                chart_specific_data_generation_prompt = f"""
                You are a data generation expert for '{chart_type}' charts.
                Generate data based ONLY on the specifications below.

                TARGET CHART TYPE: {chart_type}
                DATA SPECIFICATIONS: {specific_info.get("data_specifications", general_parsed_info["data_description"])}
                X-AXIS HINT: {specific_info.get("x_axis")}
                Y-AXIS HINT: {specific_info.get("y_axis")}

                CRITICAL INSTRUCTIONS:
                1. Generate realistic data points (aim for 8-12 points unless specifications dictate otherwise) suitable for a '{chart_type}' chart.
                2. Structure the output based on the TARGET CHART TYPE:
                   - Bar/Line: Include `x_values` and `y_values`.
                   - Pie/Treemap: Include `labels` and `sizes`.
                   - Radar: Include `categories` and `values`.
                   - Heatmap: Include `x_values`, `y_values`, and `z_values` (2D matrix).
                   - Box/Violin: Include `x_values` (group labels) and `distributions` (list of lists).
                   - Funnel: Include `stages` and `values`.
                3. ONLY include fields relevant to this chart type.
                4. Ensure data structures have compatible lengths for the chart type.

                RETURN FORMAT:
                Return ONLY a valid JSON object containing the generated data. Include `data_source` set to "ai_generated".
                """
                data_gen_response = model.generate_content(chart_specific_data_generation_prompt)
                specific_chart_data = parse_gemini_json(data_gen_response.text)
                
                # Add data_source if missing
                if "data_source" not in specific_chart_data:
                    specific_chart_data["data_source"] = "ai_generated"

                # Chart-specific validations and corrections
                if chart_type == 'radar':
                    # If radar chart data is missing categories/values, try to use x_values/y_values
                    if 'categories' not in specific_chart_data and 'values' not in specific_chart_data:
                        if 'x_values' in specific_chart_data and 'y_values' in specific_chart_data:
                            logger.warning(f"[{chart_type}] Converting x_values/y_values to categories/values")
                            specific_chart_data['categories'] = specific_chart_data['x_values']
                            specific_chart_data['values'] = specific_chart_data['y_values']
                        else:
                            # Generate default radar data
                            logger.warning(f"[{chart_type}] Generating default radar data")
                            specific_chart_data['categories'] = ["Category 1", "Category 2", "Category 3", "Category 4", "Category 5"]
                            specific_chart_data['values'] = [4, 7, 5, 8, 6]
                            
                elif chart_type == 'treemap':
                    # If treemap data is missing labels/sizes, try to use x_values/y_values
                    if 'labels' not in specific_chart_data and 'sizes' not in specific_chart_data:
                        if 'x_values' in specific_chart_data and 'y_values' in specific_chart_data:
                            logger.warning(f"[{chart_type}] Converting x_values/y_values to labels/sizes")
                            specific_chart_data['labels'] = specific_chart_data['x_values']
                            specific_chart_data['sizes'] = specific_chart_data['y_values']
                        else:
                            # Generate default treemap data
                            logger.warning(f"[{chart_type}] Generating default treemap data")
                            specific_chart_data['labels'] = ["Category A", "Category B", "Category C", "Category D"]
                            specific_chart_data['sizes'] = [15, 30, 45, 10]
                            
                elif chart_type == 'funnel':
                    # If funnel data is missing stages/values, try to use x_values/y_values
                    if 'stages' not in specific_chart_data and 'values' not in specific_chart_data:
                        if 'x_values' in specific_chart_data and 'y_values' in specific_chart_data:
                            logger.warning(f"[{chart_type}] Converting x_values/y_values to stages/values")
                            specific_chart_data['stages'] = specific_chart_data['x_values']
                            specific_chart_data['values'] = specific_chart_data['y_values']
                        else:
                            # Generate default funnel data
                            logger.warning(f"[{chart_type}] Generating default funnel data")
                            specific_chart_data['stages'] = ["Awareness", "Interest", "Consideration", "Intent", "Purchase"]
                            specific_chart_data['values'] = [100, 70, 50, 30, 15]

                logger.info(f"[{chart_type}] AI-generated data: {json.dumps(specific_chart_data)}")

            # --- Prepare final info for chart generation ---
            chart_parsed_info = general_parsed_info.copy() # Start with general info
            chart_parsed_info.update(specific_info) # Override with specific info (title, axes etc)
            chart_parsed_info["chart_type"] = chart_type # Ensure chart_type is set
            # Remove fields that don't belong in final parsed info for the image function
            for key in ["exact_data_provided", "data_specifications", "x_values", "y_values", "labels", "sizes", "categories", "z_values", "distributions", "groups", "stages", "parents"]:
                 chart_parsed_info.pop(key, None) 

            logger.info(f"[{chart_type}] Final chart info for generation: {json.dumps(chart_parsed_info)}")
            logger.info(f"[{chart_type}] Final chart data for generation: {json.dumps(specific_chart_data)}")

            # --- Generate Chart Image ---
            chart_image = generate_chart_image(chart_type, specific_chart_data, chart_parsed_info)
            
            chart_results.append({
                "chart_type": chart_type,
                "reason": reason,
                "image": chart_image,
                "parsed_info": chart_parsed_info, # Pass the refined info
                "chart_data": specific_chart_data # Also return the specific data used
            })
            
            logger.info(f"Generated {chart_type} chart successfully")
            
        except DiagramError as e: # Catch DiagramErrors specifically to report them
             error_msg = f"Error generating {chart_type} chart: {e.message}"
             logger.error(error_msg)
             error_messages.append({"chart_type": chart_type, "error": e.message})
        except Exception as e: # Catch unexpected errors
            error_msg = f"Unexpected error generating {chart_type} chart: {str(e)}"
            logger.exception(error_msg) # Log stack trace for unexpected errors
            error_messages.append({"chart_type": chart_type, "error": f"An unexpected error occurred: {str(e)}"})
            # Continue with other chart types even if one fails
    
    # If all charts failed, try to generate a simple bar chart as fallback
    if len(chart_results) == 0:
        logger.warning("All recommended charts failed, attempting fallback bar chart")
        try:
             # Simplified extraction/generation for fallback bar chart
             fallback_chart_type = "bar"
             logger.info(f"--- Processing fallback: {fallback_chart_type} ---")
             
             # Minimal info extraction for fallback
             fallback_specific_info = {
                 "exact_data_provided": False, # Assume AI generation for fallback
                 "data_specifications": f"Create a simple bar chart based on the user request: {user_prompt}. Use generic categories and values if necessary.",
                 "x_axis": general_parsed_info['x_axis'],
                 "y_axis": general_parsed_info['y_axis'],
                 "title": f"{general_parsed_info['title']} (Fallback Bar Chart)",
                 "subtitle": general_parsed_info['subtitle']
             }
             
             # Minimal data generation for fallback
             fallback_data_gen_prompt = f"""
             Generate simple data for a fallback 'bar' chart.
             SPECIFICATIONS: {fallback_specific_info['data_specifications']}
             Return JSON: {{"x_values": ["Cat1", "Cat2", "Cat3"], "y_values": [5, 8, 3], "data_source": "ai_generated_fallback"}}
             """
             fallback_data_response = model.generate_content(fallback_data_gen_prompt)
             fallback_chart_data = parse_gemini_json(fallback_data_response.text)
             if "data_source" not in fallback_chart_data: fallback_chart_data["data_source"] = "ai_generated_fallback"
             if 'x_values' not in fallback_chart_data or 'y_values' not in fallback_chart_data:
                  fallback_chart_data = {"x_values": ["FB_Cat1", "FB_Cat2", "FB_Cat3"], "y_values": [5, 8, 3], "data_source": "ai_generated_fallback_hardcoded"} # Hardcoded fallback

             fallback_parsed_info = general_parsed_info.copy()
             fallback_parsed_info.update({k: v for k, v in fallback_specific_info.items() if k in ['x_axis', 'y_axis', 'title', 'subtitle', 'palette']})
             fallback_parsed_info["chart_type"] = fallback_chart_type

             logger.info(f"[Fallback] Final chart info: {json.dumps(fallback_parsed_info)}")
             logger.info(f"[Fallback] Final chart data: {json.dumps(fallback_chart_data)}")
             
             fallback_image = generate_chart_image(fallback_chart_type, fallback_chart_data, fallback_parsed_info)
            
             chart_results.append({
                "chart_type": fallback_chart_type,
                "reason": "Fallback chart type when others failed",
                "image": fallback_image,
                "parsed_info": fallback_parsed_info,
                "chart_data": fallback_chart_data
            })
             logger.info("Generated fallback bar chart successfully")

        except Exception as e:
            logger.error(f"Even fallback chart failed: {str(e)}")
            # If even the fallback fails, report the original errors if any, or a generic message
            if error_messages:
                 failure_reason = f"Failed to generate any charts. Errors encountered: {json.dumps(error_messages)}"
            else:
                 failure_reason = f"Failed to generate fallback chart: {str(e)}"
            raise DiagramError(failure_reason)

    # Return all chart results
    return jsonify({
        "charts": chart_results,
        # "chart_data": chart_data, # Remove generic chart_data
        "error_messages": error_messages if error_messages else None # Keep error messages
    })

def generate_chart_image(chart_type, chart_data, parsed_info):
    """Generate a chart image and return its base64 encoding"""
    plt_fig = None
    buffer = None
    try:
        # Create figure
        plt_fig = plt.figure(figsize=(12, 7))
        
        # Set the style and palette
        sns.set_style("whitegrid")
        # Ensure we use a valid matplotlib palette
        valid_palettes = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 
                          'Blues', 'Greens', 'Reds', 'Oranges', 'Purples', 
                          'GnBu', 'PuRd', 'YlGn', 'YlOrRd', 'YlOrBr', 'RdPu']
        
        if isinstance(parsed_info.get('palette'), list):
            parsed_info['palette'] = 'viridis'  # Default if palette is a list
        
        palette = parsed_info.get('palette', 'viridis')
        if palette not in valid_palettes:
            logger.warning(f"Invalid palette '{palette}', defaulting to 'viridis'")
            palette = 'viridis'  # Default to a safe option
                
        # Generate the appropriate chart type
        if chart_type == 'bar':
            # Convert any non-string x_values to strings to prevent unhashable errors
            x_values = [str(x) for x in chart_data['x_values']]
            y_values = [float(y) if not isinstance(y, (int, float)) else y for y in chart_data['y_values']]
            
            # Create plot using direct lists, not the original data
            ax = sns.barplot(x=list(range(len(x_values))), y=y_values)
            plt.xticks(range(len(x_values)), x_values, rotation=45 if len(max(x_values, key=len)) > 5 else 0)
            
            # Add data labels
            for i, v in enumerate(y_values):
                ax.text(i, v + 0.1, f"{v:.1f}", ha='center')
                
        elif chart_type == 'line':
            # Convert to numeric values if possible
            try:
                # Process x and y values ensuring they're primitive types
                x_vals = []
                y_vals = []
                pairs = []  # For storing (x,y) pairs that will be sorted
                
                # First, try to parse all values as numeric
                for i, (x, y) in enumerate(zip(chart_data['x_values'], chart_data['y_values'])):
                    try:
                        # Try to convert to numeric if possible
                        if isinstance(x, (int, float)):
                            x_val = x
                        elif isinstance(x, str):
                            # Try to parse as number or date
                            try:
                                # First try as simple float
                                x_val = float(x)
                            except ValueError:
                                # If that fails, check if it looks like a date/month
                                if x.lower() in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                                                'jul', 'aug', 'sep', 'oct', 'nov', 'dec']:
                                    # Use month number for sorting
                                    months = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
                                            'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
                                            'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
                                    x_val = months.get(x.lower(), i)
                                else:
                                    # Try to parse as a date
                                    try:
                                        # Try to parse the string as a date
                                        parsed_date = date_parser.parse(x, fuzzy=True)
                                        # Use the timestamp as the numerical value for sorting
                                        x_val = datetime.datetime.timestamp(parsed_date)
                                    except (ValueError, TypeError):
                                        # Use position as a fallback
                                        x_val = i
                        else:
                            # For other types, use position index
                            x_val = i
                        
                        # Convert y to float if possible
                        if isinstance(y, (int, float)):
                            y_val = y
                        else:
                            y_val = float(y) if isinstance(y, str) else 0
                        
                        # Store the (x,y) pair for sorting
                        pairs.append((x_val, y_val, x))  # Include original x for labels
                    except (ValueError, TypeError):
                        logger.warning(f"Could not convert line data point {i} to numeric: x={x}, y={y}")
                        # Try to use the index as x value
                        pairs.append((i, 0 if not isinstance(y, (int, float)) else y, x))
                
                # Sort pairs by x value for proper line plotting
                pairs.sort(key=lambda pair: pair[0])
                
                # Extract sorted values and original labels
                x_numeric = [pair[0] for pair in pairs]
                y_values = [pair[1] for pair in pairs]
                x_labels = [pair[2] for pair in pairs]
                
                # Create the plot
                if len(pairs) > 1:
                    # Plot with numeric x values for correct line placement
                    fig, ax = plt.subplots(figsize=(12, 7))  # Get axis for more control
                    
                    # Create a better looking line chart
                    line = ax.plot(x_numeric, y_values, marker='o', linewidth=2.5)[0]
                    
                    # Add marker points with contrasting color
                    ax.scatter(x_numeric, y_values, color=line.get_color(), s=80, zorder=5, 
                               edgecolor='white', linewidth=1.5)
                    
                    # Add grid but only on the y-axis
                    ax.grid(axis='y', linestyle='--', alpha=0.7)
                    
                    # Add value labels above points
                    for i, (x, y) in enumerate(zip(x_numeric, y_values)):
                        ax.annotate(f'{y:.1f}', (x, y), textcoords="offset points", 
                                   xytext=(0, 10), ha='center')
                    
                    # But use original labels for the x-axis
                    ax.set_xticks(x_numeric)
                    ax.set_xticklabels(x_labels, rotation=45 if any(len(str(x)) > 5 for x in x_labels) else 0)
                    
                    # Set y-axis to start at 0 unless all values are negative
                    if any(y < 0 for y in y_values):
                        # If we have negative values, add some padding
                        y_min = min(y_values) * 1.1
                    else:
                        y_min = 0
                        
                    # Add some headroom above the highest point
                    y_max = max(y_values) * 1.15
                    
                    # Set the y limits
                    ax.set_ylim(y_min, y_max)
                    
                    # Remove the previous figure to avoid duplicate plots
                    plt.close(plt_fig)
                    plt_fig = fig
                else:
                    # Fallback if we don't have enough points
                    logger.warning("Not enough valid points for line chart, creating sample")
                    x_vals = list(range(5))
                    y_vals = [random.randint(1, 10) for _ in range(5)]
                    plt.plot(x_vals, y_vals, marker='o', linewidth=2.5)
            except Exception as e:
                logger.error(f"Error in line chart: {str(e)}")
                # Create a simple fallback line chart with random data
                x_vals = list(range(5))
                y_vals = [random.randint(1, 10) for _ in range(5)]
                plt.plot(x_vals, y_vals, marker='o', linewidth=2.5)
                
        elif chart_type == 'pie':
            # Get labels and sizes, ensuring they're primitive types
            try:
                labels = [str(label) for label in chart_data.get('labels', chart_data['x_values'])]
                
                # Handle y_values that might be dictionaries or other unhashable types
                sizes = []
                for size in chart_data.get('sizes', chart_data['y_values']):
                    if isinstance(size, (int, float)):
                        sizes.append(max(0, size))  # Ensure positive
                    else:
                        try:
                            sizes.append(max(0, float(size)))  # Try to convert to float
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid size value for pie chart: {size}")
                            sizes.append(0)  # Default to zero for invalid values
                
                # Only plot if we have valid data
                if sum(sizes) > 0:
                    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, shadow=True)
                    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
                else:
                    raise DiagramError("Cannot create pie chart with non-positive values")
            except Exception as e:
                logger.error(f"Error in pie chart: {str(e)}")
                raise DiagramError(f"Could not generate pie chart: {str(e)}")
            
        elif chart_type == 'scatter':
            try:
                # Extract and convert x and y values to numeric when possible
                x_vals = []
                y_vals = []
                
                # First try to convert everything to numeric
                for i, (x, y) in enumerate(zip(chart_data['x_values'], chart_data['y_values'])):
                    try:
                        x_val = float(x) if not isinstance(x, (int, float)) else x
                        y_val = float(y) if not isinstance(y, (int, float)) else y
                        x_vals.append(x_val)
                        y_vals.append(y_val)
                    except (ValueError, TypeError):
                        logger.warning(f"Could not convert scatter point {i} to numeric")
                        # Skip this point
                        continue
                
                # If we couldn't convert any points, try a different approach
                if len(x_vals) == 0:
                    logger.warning("No numeric points for scatter plot, using indices as x values")
                    # Use indices for x and original values for y
                    for i, y in enumerate(chart_data['y_values']):
                        try:
                            y_val = float(y) if not isinstance(y, (int, float)) else y
                            x_vals.append(i)  # Use index as x value
                            y_vals.append(y_val)
                        except (ValueError, TypeError):
                            # If y can't be converted either, use a default
                            x_vals.append(i)
                            y_vals.append(i)  # Use index as default y value
                
                # Handle categories if present
                if len(x_vals) > 0:
                    categories = chart_data.get('categories')
                    if categories and len(categories) > 0:
                        if len(categories) != len(x_vals):
                            logger.warning(f"Categories length {len(categories)} doesn't match data length {len(x_vals)}")
                            categories = categories[:len(x_vals)] if len(categories) > len(x_vals) else categories + [categories[-1]] * (len(x_vals) - len(categories))
                        
                        # Ensure categories are hashable
                        cat_vals = [str(cat) for cat in categories]
                        sns.scatterplot(x=x_vals, y=y_vals, hue=cat_vals, palette=palette, s=80)
                    else:
                        sns.scatterplot(x=x_vals, y=y_vals, palette=palette, s=80)
                else:
                    # If all else fails, create a sample scatter plot
                    logger.warning("Creating sample scatter plot with random data")
                    x = np.random.rand(10)
                    y = np.random.rand(10)
                    sns.scatterplot(x=x, y=y, palette=palette, s=80)
            except Exception as e:
                logger.error(f"Error in scatter plot: {str(e)}")
                raise DiagramError(f"Could not generate scatter plot: {str(e)}")
            
        elif chart_type == 'histogram':
            try:
                # Convert to numeric values, skipping non-numeric
                values = []
                for y in chart_data['y_values']:
                    try:
                        values.append(float(y) if not isinstance(y, (int, float)) else y)
                    except (ValueError, TypeError):
                        logger.warning(f"Skipping non-numeric histogram value: {y}")
                        # Skip non-numeric values
                        continue
                
                if len(values) > 0:
                    sns.histplot(values, bins=min(10, len(values)), kde=True)
                else:
                    raise DiagramError("No valid numeric data for histogram")
            except Exception as e:
                logger.error(f"Error in histogram: {str(e)}")
                raise DiagramError(f"Could not generate histogram: {str(e)}")
            
        elif chart_type == 'heatmap':
            try:
                data_source = chart_data.get('data_source', 'unknown')
                
                # Check if z_values are present
                z_values = chart_data.get('z_values')
                
                # If z_values are missing and data is user-specified, it's likely unsuitable
                if not z_values and data_source == 'user_specified':
                    raise DiagramError("User-provided data does not contain the required 'z_values' (2D array) for a heatmap.")
                
                # If z_values are missing and AI generated, the AI should have generated them. If not, raise error.
                elif not z_values and data_source == 'ai_generated':
                     # Attempt to create a simple 2D array based on x_values and y_values as a fallback for AI data
                    logger.warning("AI-generated data missing 'z_values' for heatmap, attempting fallback generation.")
                    x_len = min(5, len(chart_data['x_values']))
                    y_len = min(5, len(chart_data['y_values']))
                    
                    # Check if y_values is empty or too short
                    if not chart_data['y_values']:
                         raise DiagramError("Cannot generate heatmap fallback: 'y_values' is empty.")

                    new_z_values = []
                    for i in range(y_len):
                        row = []
                        for j in range(x_len):
                            y_idx = (i * x_len + j) % len(chart_data['y_values']) # Use modulo
                            try:
                                val = float(chart_data['y_values'][y_idx])
                            except (ValueError, TypeError):
                                val = i + j  # Fallback value
                            row.append(val)
                        new_z_values.append(row)
                    z_values = new_z_values # Assign the generated fallback
                    logger.info(f"Generated fallback z_values for heatmap: {json.dumps(z_values)}")

                elif not z_values:
                     raise DiagramError("Heatmap requires 'z_values' data (2D array), which was not found or generated.")

                if z_values and isinstance(z_values, list):
                    # Ensure z_values is a proper 2D array of numeric values
                    processed_z = []
                    for row in z_values:
                        if not isinstance(row, list):
                            # Convert non-list rows to a list with a single item
                            processed_row = [float(row) if isinstance(row, (int, float)) else 0]
                        else:
                            # Process each cell in the row
                            processed_row = [float(cell) if isinstance(cell, (int, float)) else 0 for cell in row]
                        processed_z.append(processed_row)
                    
                    # Make sure all rows have the same length
                    max_len = max(len(row) for row in processed_z)
                    for i, row in enumerate(processed_z):
                        if len(row) < max_len:
                            processed_z[i] = row + [0] * (max_len - len(row))
                    
                    # Convert labels to strings
                    x_labels = [str(x) for x in chart_data['x_values']]
                    y_labels = [str(y) for y in chart_data.get('y_labels', chart_data['y_values'])]
                    
                    # Limit labels to the actual data dimensions
                    x_labels = x_labels[:len(processed_z[0])]
                    y_labels = y_labels[:len(processed_z)]
                    
                    # If we have too few labels, add placeholders
                    if len(x_labels) < len(processed_z[0]):
                        x_labels += [f"Col {i+1}" for i in range(len(x_labels), len(processed_z[0]))]
                    if len(y_labels) < len(processed_z):
                        y_labels += [f"Row {i+1}" for i in range(len(y_labels), len(processed_z))]
                    
                    # Create the heatmap with our processed data
                    sns.heatmap(processed_z, annot=True, cmap=palette, 
                                xticklabels=x_labels, yticklabels=y_labels)
                else:
                    raise DiagramError("Heatmap requires z_values data as a 2D array")
            except Exception as e:
                logger.error(f"Error in heatmap: {str(e)}")
                raise DiagramError(f"Could not generate heatmap: {str(e)}")
                
        elif chart_type == 'boxplot':
            try:
                data_source = chart_data.get('data_source', 'unknown')
                distributions = chart_data.get('distributions')

                # If distributions are missing and data is user-specified, it's likely unsuitable
                if not distributions and data_source == 'user_specified':
                    # Check if y_values look like they could be treated as a single distribution
                    if 'y_values' in chart_data and isinstance(chart_data['y_values'], list) and chart_data['y_values']:
                        logger.warning("User-specified data missing 'distributions' for boxplot. Attempting to use 'y_values' as a single distribution.")
                        distributions = chart_data['y_values'] # Treat y_values as the distribution
                        # Ensure groups reflect this single distribution if needed
                        if 'groups' not in chart_data or not chart_data['groups']:
                             chart_data['groups'] = [parsed_info.get('y_axis', 'Values')] # Use y-axis label or default
                    else:
                        raise DiagramError("User-provided data does not contain the required 'distributions' (list of lists or list of values) for a boxplot.")

                # If distributions are missing and AI generated, the AI should have generated them.
                elif not distributions and data_source == 'ai_generated':
                     # Attempt to generate fallback distributions for AI data
                    logger.warning("AI-generated data missing 'distributions' for boxplot, attempting fallback generation.")
                    new_distributions = []
                    if not chart_data.get('y_values'):
                         raise DiagramError("Cannot generate boxplot fallback: 'y_values' is empty.")
                         
                    for y in chart_data['y_values']:
                        try:
                            base = float(y) if not isinstance(y, (int, float)) else y
                            dist = np.random.normal(base, base * 0.2 + 1, 20).tolist()
                            new_distributions.append(dist)
                        except (ValueError, TypeError):
                            new_distributions.append(np.random.normal(5, 2, 20).tolist())
                    distributions = new_distributions
                    logger.info("Generated fallback distributions for boxplot.")

                elif not distributions:
                     raise DiagramError("Boxplot requires 'distributions' data, which was not found or generated.")

                # Get groups and ensure they're strings
                groups = [str(g) for g in chart_data.get('groups', chart_data['x_values'])]
                
                if isinstance(distributions, list) and len(distributions) > 0:
                    # Check if it's a list of lists (multiple distributions) or just a list (single distribution)
                    if isinstance(distributions[0], list):
                        # Multiple distributions case
                        # Process each distribution to ensure numeric values
                        processed_dists = []
                        for dist in distributions:
                            processed_dist = []
                            for val in dist:
                                try:
                                    processed_dist.append(float(val) if not isinstance(val, (int, float)) else val)
                                except (ValueError, TypeError):
                                    logger.warning(f"Skipping non-numeric boxplot value: {val}")
                                    # Skip non-numeric
                                    continue
                            if processed_dist:  # Only add if not empty
                                processed_dists.append(processed_dist)
                        
                        if processed_dists:
                            # Create a dataframe for the plot
                            import pandas as pd
                            # Ensure we don't have more distributions than groups
                            valid_groups = groups[:len(processed_dists)]
                            data_dict = {group: dist for group, dist in zip(valid_groups, processed_dists)}
                            df = pd.DataFrame(data_dict)
                            sns.boxplot(data=df, palette=palette)
                        else:
                            raise DiagramError("No valid numeric data for boxplot")
                    else:
                        # Single distribution case - convert to numeric
                        y_vals = []
                        valid_groups = []
                        for i, (g, y) in enumerate(zip(groups, distributions)):
                            try:
                                y_val = float(y) if not isinstance(y, (int, float)) else y
                                y_vals.append(y_val)
                                valid_groups.append(g)
                            except (ValueError, TypeError):
                                logger.warning(f"Skipping non-numeric boxplot value: {y}")
                                # Skip non-numeric
                                continue
                        
                        if len(y_vals) > 0:
                            sns.boxplot(x=valid_groups, y=y_vals, palette=palette)
                        else:
                            raise DiagramError("No valid numeric data for boxplot")
                else:
                    raise DiagramError("Invalid distribution data for boxplot")
            except Exception as e:
                logger.error(f"Error in boxplot: {str(e)}")
                raise DiagramError(f"Could not generate boxplot: {str(e)}")
            
        elif chart_type == 'violin':
            try:
                # Similar logic to boxplot for handling missing 'distributions'
                data_source = chart_data.get('data_source', 'unknown')
                distributions = chart_data.get('distributions')

                if not distributions and data_source == 'user_specified':
                     if 'y_values' in chart_data and isinstance(chart_data['y_values'], list) and chart_data['y_values']:
                        logger.warning("User-specified data missing 'distributions' for violin plot. Attempting to use 'y_values' as a single distribution.")
                        distributions = chart_data['y_values']
                        if 'groups' not in chart_data or not chart_data['groups']:
                             chart_data['groups'] = [parsed_info.get('y_axis', 'Values')]
                     else:
                         raise DiagramError("User-provided data does not contain the required 'distributions' (list of lists or list of values) for a violin plot.")

                elif not distributions and data_source == 'ai_generated':
                    logger.warning("AI-generated data missing 'distributions' for violin plot, attempting fallback generation.")
                    new_distributions = []
                    if not chart_data.get('y_values'):
                         raise DiagramError("Cannot generate violin plot fallback: 'y_values' is empty.")

                    for y in chart_data['y_values']:
                        try:
                            base = float(y) if not isinstance(y, (int, float)) else y
                            dist = np.random.normal(base, base * 0.2 + 1, 20).tolist()
                            new_distributions.append(dist)
                        except (ValueError, TypeError):
                            new_distributions.append(np.random.normal(5, 2, 20).tolist())
                    distributions = new_distributions
                    logger.info("Generated fallback distributions for violin plot.")

                elif not distributions:
                    raise DiagramError("Violin plot requires 'distributions' data, which was not found or generated.")

                # Similar approach as boxplot
                groups = [str(g) for g in chart_data.get('groups', chart_data['x_values'])]
                
                if isinstance(distributions, list) and len(distributions) > 0:
                     # Check if it's a list of lists (multiple distributions) or just a list (single distribution)
                    if isinstance(distributions[0], list):
                        # Multiple distributions case
                        processed_dists = []
                        for dist in distributions:
                            processed_dist = []
                            for val in dist:
                                try:
                                    processed_dist.append(float(val) if not isinstance(val, (int, float)) else val)
                                except (ValueError, TypeError):
                                    # Skip non-numeric
                                    continue
                            if processed_dist:  # Only add if not empty
                                processed_dists.append(processed_dist)
                        
                        if processed_dists:
                            # Create a dataframe for the plot
                            import pandas as pd
                            # Ensure we don't have more distributions than groups
                            valid_groups = groups[:len(processed_dists)]
                            data_dict = {group: dist for group, dist in zip(valid_groups, processed_dists)}
                            df = pd.DataFrame(data_dict)
                            sns.violinplot(data=df, palette=palette)
                        else:
                            raise DiagramError("No valid numeric data for violin plot")
                    else:
                        # Single distribution case
                        y_vals = []
                        valid_groups = []
                        for i, (g, y) in enumerate(zip(groups, distributions)):
                            try:
                                y_val = float(y) if not isinstance(y, (int, float)) else y
                                y_vals.append(y_val)
                                valid_groups.append(g)
                            except (ValueError, TypeError):
                                # Skip non-numeric
                                continue
                        
                        if len(y_vals) > 0:
                            sns.violinplot(x=valid_groups, y=y_vals, palette=palette)
                        else:
                            raise DiagramError("No valid numeric data for violin plot")
                else:
                    raise DiagramError("Invalid distribution data for violin plot")
            except Exception as e:
                logger.error(f"Error in violin plot: {str(e)}")
                raise DiagramError(f"Could not generate violin plot: {str(e)}")

        elif chart_type == 'area':
            try:
                # Similar to line chart but with filled area
                x_vals = []
                y_vals = []
                pairs = []
                
                for i, (x, y) in enumerate(zip(chart_data['x_values'], chart_data['y_values'])):
                    try:
                        # Convert x to numeric if possible
                        if isinstance(x, (int, float)):
                            x_val = x
                        elif isinstance(x, str):
                            try:
                                x_val = float(x)
                            except ValueError:
                                # Try to parse as date
                                try:
                                    parsed_date = date_parser.parse(x, fuzzy=True)
                                    x_val = datetime.datetime.timestamp(parsed_date)
                                except (ValueError, TypeError):
                                    x_val = i
                        else:
                            x_val = i
                        
                        # Convert y to float
                        y_val = float(y) if not isinstance(y, (int, float)) else y
                        
                        pairs.append((x_val, y_val, x))  # Keep original x for labels
                    except (ValueError, TypeError):
                        pairs.append((i, 0 if not isinstance(y, (int, float)) else y, x))
                
                # Sort by x value
                pairs.sort(key=lambda pair: pair[0])
                
                # Extract sorted values
                x_numeric = [pair[0] for pair in pairs]
                y_values = [pair[1] for pair in pairs]
                x_labels = [pair[2] for pair in pairs]
                
                if len(pairs) > 1:
                    fig, ax = plt.subplots(figsize=(12, 7))
                    ax.fill_between(x_numeric, y_values, alpha=0.4)
                    ax.plot(x_numeric, y_values, linewidth=2.5)
                    
                    # Add markers
                    ax.scatter(x_numeric, y_values, s=80, zorder=5, edgecolor='white', linewidth=1.5)
                    
                    # Add grid
                    ax.grid(axis='y', linestyle='--', alpha=0.7)
                    
                    # Add value labels
                    for i, (x, y) in enumerate(zip(x_numeric, y_values)):
                        ax.annotate(f'{y:.1f}', (x, y), textcoords="offset points", 
                                   xytext=(0, 10), ha='center')
                    
                    # Set x-axis labels
                    ax.set_xticks(x_numeric)
                    ax.set_xticklabels(x_labels, rotation=45 if any(len(str(x)) > 5 for x in x_labels) else 0)
                    
                    # Set y limits
                    y_min = min(y_values) * 1.1 if any(y < 0 for y in y_values) else 0
                    y_max = max(y_values) * 1.15
                    ax.set_ylim(y_min, y_max)
                    
                    plt.close(plt_fig)
                    plt_fig = fig
                else:
                    # Fallback if not enough points
                    logger.warning("Not enough valid points for area chart, creating sample")
                    x_vals = list(range(5))
                    y_vals = [random.randint(1, 10) for _ in range(5)]
                    plt.fill_between(x_vals, y_vals, alpha=0.4)
                    plt.plot(x_vals, y_vals, linewidth=2.5)
            except Exception as e:
                logger.error(f"Error in area chart: {str(e)}")
                raise DiagramError(f"Could not generate area chart: {str(e)}")

        elif chart_type == 'stacked_bar':
            try:
                # Need x_values, groups, and y_values
                x_values = [str(x) for x in chart_data['x_values']]
                groups = [str(g) for g in chart_data.get('groups', ['Group'] * len(x_values))]
                
                # Validate y_values structure
                if not isinstance(chart_data['y_values'], list):
                    raise DiagramError("y_values must be a list for stacked bar chart")
                
                # Create DataFrame for plotting
                df = pd.DataFrame({
                    'x': x_values,
                    'y': chart_data['y_values'],
                    'group': groups[:len(x_values)]
                })
                
                # Pivot for stacked bar
                pivot_df = df.pivot(index='x', columns='group', values='y')
                
                # Plot
                pivot_df.plot(kind='bar', stacked=True, figsize=(12, 7))
            except Exception as e:
                logger.error(f"Error in stacked bar chart: {str(e)}")
                raise DiagramError(f"Could not generate stacked bar chart: {str(e)}")

        elif chart_type == 'bubble':
            try:
                # Need x_values, y_values, and sizes
                x_vals = []
                y_vals = []
                sizes = []
                
                for i, (x, y) in enumerate(zip(chart_data['x_values'], chart_data['y_values'])):
                    try:
                        x_val = float(x) if not isinstance(x, (int, float)) else x
                        y_val = float(y) if not isinstance(y, (int, float)) else y
                        x_vals.append(x_val)
                        y_vals.append(y_val)
                        
                        # Get size if available, otherwise use default
                        if 'sizes' in chart_data and i < len(chart_data['sizes']):
                            try:
                                sizes.append(float(chart_data['sizes'][i]) * 100)  # Scale for visibility
                            except (ValueError, TypeError):
                                sizes.append(100)  # Default size
                        else:
                            sizes.append(100)  # Default size
                    except (ValueError, TypeError):
                        continue
                
                if len(x_vals) > 0:
                    plt.scatter(x=x_vals, y=y_vals, s=sizes, alpha=0.6)
                else:
                    raise DiagramError("No valid data points for bubble chart")
            except Exception as e:
                logger.error(f"Error in bubble chart: {str(e)}")
                raise DiagramError(f"Could not generate bubble chart: {str(e)}")

        elif chart_type == 'radar':
            try:
                # Need categories and values - check all possible places they could be
                categories = None
                values = None
                
                # First check for explicit categories/values format
                if 'categories' in chart_data and 'values' in chart_data:
                    categories = chart_data['categories']
                    values = chart_data['values']
                # Then check if they're using x_values/y_values as categories/values
                elif 'x_values' in chart_data and 'y_values' in chart_data:
                    categories = chart_data['x_values']
                    values = chart_data['y_values']
                else:
                    raise DiagramError(f"Radar chart requires categories/values or x_values/y_values")
                
                # Ensure categories and values are lists
                if not isinstance(categories, list) or not isinstance(values, list):
                    raise DiagramError(f"Radar chart categories and values must be lists")
                
                # Convert to strings and floats
                categories = [str(cat) for cat in categories]
                values_numeric = []
                
                for val in values:
                    try:
                        values_numeric.append(float(val) if not isinstance(val, (int, float)) else val)
                    except (ValueError, TypeError):
                        values_numeric.append(0)  # Default value
                
                # Ensure equal lengths
                if len(categories) != len(values_numeric):
                    logger.warning("Mismatched lengths in radar chart data, truncating")
                    min_len = min(len(categories), len(values_numeric))
                    categories = categories[:min_len]
                    values_numeric = values_numeric[:min_len]
                
                if len(categories) >= 3:  # Radar needs at least 3 categories
                    # Close the plot
                    values_closed = values_numeric + values_numeric[:1]
                    categories_closed = categories + categories[:1]
                    
                    # Calculate angles
                    angles = np.linspace(0, 2*np.pi, len(categories_closed), endpoint=True)
                    
                    # Make the plot
                    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
                    ax.fill(angles, values_closed, alpha=0.25)
                    ax.plot(angles, values_closed, linewidth=2)
                    
                    # Fix axis to go in the right order and start at 12 o'clock
                    ax.set_theta_offset(np.pi / 2)
                    ax.set_theta_direction(-1)
                    
                    # Draw axis lines for each angle and label
                    ax.set_thetagrids(np.degrees(angles[:-1]), categories)
                    
                    # Set y-axis limits
                    ax.set_ylim(0, max(values_numeric) * 1.1)
                    
                    plt.close(plt_fig)
                    plt_fig = fig
                else:
                    raise DiagramError("Radar chart requires at least 3 categories")
            except Exception as e:
                logger.error(f"Error in radar chart: {str(e)}", exc_info=True)
                raise DiagramError(f"Could not generate radar chart: {str(e)}")

        elif chart_type == 'treemap':
            try:
                # For treemap, we need labels and sizes
                labels = None
                sizes = None
                parents = None
                
                # Try to find the data in different possible formats
                if 'labels' in chart_data and 'sizes' in chart_data:
                    labels = chart_data['labels']
                    sizes = chart_data['sizes']
                elif 'x_values' in chart_data and 'y_values' in chart_data:
                    labels = chart_data['x_values']
                    sizes = chart_data['y_values']
                else:
                    raise DiagramError("Treemap requires labels/sizes or x_values/y_values")
                
                # Check for parents if present
                if 'parents' in chart_data:
                    parents = chart_data['parents']
                
                # Convert to proper types
                labels = [str(label) for label in labels]
                sizes_numeric = []
                
                for size in sizes:
                    try:
                        size_val = float(size) if not isinstance(size, (int, float)) else size
                        # Ensure positive values for sizes
                        sizes_numeric.append(max(0.1, size_val))
                    except (ValueError, TypeError):
                        sizes_numeric.append(1)  # Default size
                
                if len(labels) != len(sizes_numeric):
                    logger.warning("Mismatched lengths in treemap data, truncating")
                    min_len = min(len(labels), len(sizes_numeric))
                    labels = labels[:min_len]
                    sizes_numeric = sizes_numeric[:min_len]
                
                if len(labels) > 0:
                    # Normalize sizes if needed
                    if max(sizes_numeric) > 1000:  # If values are very large
                        max_size = max(sizes_numeric)
                        sizes_normalized = [s / max_size * 100 for s in sizes_numeric]
                    else:
                        sizes_normalized = sizes_numeric
                    
                    # Create colors using the specified palette
                    cmap = plt.cm.get_cmap(palette)
                    colors = [cmap(i / len(labels)) for i in range(len(labels))]
                    
                    # Plot the treemap
                    squarify.plot(sizes=sizes_normalized, label=labels, color=colors, alpha=0.7, pad=True)
                    plt.axis('off')
                else:
                    raise DiagramError("No valid data for treemap")
            except Exception as e:
                logger.error(f"Error in treemap: {str(e)}", exc_info=True)
                raise DiagramError(f"Could not generate treemap: {str(e)}")

        elif chart_type == 'funnel':
            try:
                # Need stages and values
                stages = None
                values = None
                
                # Try different possible formats
                if 'stages' in chart_data and 'values' in chart_data:
                    stages = chart_data['stages']
                    values = chart_data['values']
                elif 'x_values' in chart_data and 'y_values' in chart_data:
                    stages = chart_data['x_values']
                    values = chart_data['y_values']
                else:
                    raise DiagramError("Funnel chart requires stages/values or x_values/y_values")
                
                # Convert to strings and floats
                stages = [str(stage) for stage in stages]
                values_numeric = []
                
                for val in values:
                    try:
                        values_numeric.append(float(val) if not isinstance(val, (int, float)) else val)
                    except (ValueError, TypeError):
                        values_numeric.append(0)  # Default value
                
                if len(stages) != len(values_numeric):
                    logger.warning("Mismatched lengths in funnel chart data, truncating")
                    min_len = min(len(stages), len(values_numeric))
                    stages = stages[:min_len]
                    values_numeric = values_numeric[:min_len]
                
                if len(stages) > 1:
                    # Ensure values are in descending order for a proper funnel
                    combined = sorted(zip(stages, values_numeric), key=lambda x: x[1], reverse=True)
                    stages = [item[0] for item in combined]
                    values_numeric = [item[1] for item in combined]
                    
                    # Create funnel
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    # Calculate bar widths and positions
                    bar_width = 0.8
                    bar_positions = range(len(stages))
                    
                    # Get colormap from palette
                    cmap = plt.cm.get_cmap(palette)
                    colors = cmap(np.linspace(0, 1, len(stages)))
                    
                    # Plot bars with different widths to create funnel effect
                    max_width = max(values_numeric)
                    widths = [v for v in values_numeric]  # Use actual values for width
                    
                    bars = ax.barh(bar_positions, widths, height=bar_width, color=colors)
                    
                    # Add value labels
                    for i, (bar, value) in enumerate(zip(bars, values_numeric)):
                        ax.text(bar.get_width() / 2, bar.get_y() + bar.get_height() / 2,
                                f"{value:.1f}", ha='center', va='center', color='white', fontweight='bold')
                    
                    # Set y-axis labels
                    ax.set_yticks(bar_positions)
                    ax.set_yticklabels(stages)
                    ax.invert_yaxis()  # Top to bottom
                    
                    # Remove top and right spines
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    
                    plt.close(plt_fig)
                    plt_fig = fig
                else:
                    raise DiagramError("Funnel chart requires at least 2 stages")
            except Exception as e:
                logger.error(f"Error in funnel chart: {str(e)}", exc_info=True)
                raise DiagramError(f"Could not generate funnel chart: {str(e)}")
        else:
            # Default to a simple bar chart for any unrecognized type
            try:
                # Convert x to strings and y to floats
                x_values = [str(x) for x in chart_data['x_values']]
                y_values = []
                for y in chart_data['y_values']:
                    try:
                        y_values.append(float(y) if not isinstance(y, (int, float)) else y)
                    except (ValueError, TypeError):
                        y_values.append(0)  # Default to zero for invalid values
                
                # Create plot using index for x-axis position
                ax = sns.barplot(x=list(range(len(x_values))), y=y_values)
                plt.xticks(range(len(x_values)), x_values, rotation=45 if len(max(x_values, key=len)) > 5 else 0)
                
                # Add data labels
                for i, v in enumerate(y_values):
                    ax.text(i, v + 0.1, f"{v:.1f}", ha='center')
            except Exception as e:
                logger.error(f"Error in default bar chart: {str(e)}")
                raise DiagramError(f"Could not generate chart: {str(e)}")
            
        # Add title and subtitle
        plt.title(parsed_info['title'], fontsize=16, fontweight='bold')
        if 'subtitle' in parsed_info:
            plt.suptitle(parsed_info['subtitle'], fontsize=12)
            
        plt.xlabel(parsed_info['x_axis'], fontsize=12)
        plt.ylabel(parsed_info['y_axis'], fontsize=12)
        plt.tight_layout()
        
        # Save the plot to a bytes buffer
        buffer = io.BytesIO()
        plt_fig.savefig(buffer, format='png', dpi=150)
        buffer.seek(0)
        
        # Encode the image to base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return image_base64
        
    except Exception as e:
        logger.error(f"Error generating {chart_type} chart: {str(e)}", exc_info=True)
        raise DiagramError(f"Failed to generate {chart_type} chart: {str(e)}")
    finally:
        # Clean up resources to prevent memory leaks
        if buffer:
            buffer.close()
        if plt_fig:
            plt.close(plt_fig)
        # Extra cleanup to be safe
        plt.close('all')

@app.route('/api/chart-types', methods=['GET'])
@limiter.limit("12 per minute")
def get_chart_types():
    return jsonify({
        "chart_types": [
            {
                "id": "bar",
                "name": "Bar Chart",
                "description": "Compares values across categories"
            },
            {
                "id": "line",
                "name": "Line Chart", 
                "description": "Shows trends over time or ordered categories"
            },
            {
                "id": "pie",
                "name": "Pie Chart",
                "description": "Shows proportions of a whole"
            },
            {
                "id": "scatter",
                "name": "Scatter Plot",
                "description": "Shows relationship between two variables"
            },
            {
                "id": "histogram",
                "name": "Histogram",
                "description": "Shows distribution of a single variable"
            },
            {
                "id": "heatmap",
                "name": "Heat Map",
                "description": "Shows patterns in a matrix of values"
            },
            {
                "id": "boxplot",
                "name": "Box Plot",
                "description": "Shows distribution statistics with quartiles"
            },
            {
                "id": "violin",
                "name": "Violin Plot",
                "description": "Shows distribution density across categories"
            },
            {
                "id": "area",
                "name": "Area Chart",
                "description": "Shows cumulative totals over time"
            },
            {
                "id": "stacked_bar",
                "name": "Stacked Bar Chart",
                "description": "Shows part-to-whole relationships across categories"
            },
            {
                "id": "bubble",
                "name": "Bubble Chart",
                "description": "Shows relationships between three variables"
            },
            {
                "id": "radar",
                "name": "Radar Chart",
                "description": "Shows multivariate data on axes radiating from center"
            },
            {
                "id": "treemap",
                "name": "Treemap",
                "description": "Shows hierarchical data as nested rectangles"
            },
            {
                "id": "funnel",
                "name": "Funnel Chart",
                "description": "Shows stages in a process with decreasing quantities"
            }
        ]
    })

@app.route('/api/enhance-prompt', methods=['POST'])
@handle_errors
@limiter.limit("15 per minute")
def enhance_prompt():
    data = request.json
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    
    try:
        # Use Gemini model to enhance the prompt
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        enhancement_prompt = f"""
        You are an expert data visualization consultant that helps users create precise, accurate chart prompts.
        
        ORIGINAL USER REQUEST: "{prompt}"
        
        Your task is to enhance this request to ensure it produces EXACTLY the visualization the user wants.
        
        ENHANCEMENT REQUIREMENTS:
        1. Maintain the user's original intent and data requirements
        2. If the user specified exact data values or series, HIGHLIGHT and PRESERVE those specifications
        3. Add precise details about:
           - Axis labels with proper units
           - Title/subtitle that clearly explains the visualization
           - Data ranges or distributions if relevant
           - Color schemes or styling preferences if appropriate
        4. Clarify ambiguities in the original request
        5. Ensure the enhanced prompt will produce a chart that accurately represents the user's data
        
        IMPORTANT FORMAT RULES:
        - Keep your response concise and only 150 WORDS (max 3-4 sentences)
        - Maintain the user's tone and terminology
        - Return ONLY the enhanced prompt with no explanations or additional text
        - DO NOT add "Chart showing..." or similar phrases unless part of the original prompt
        - DO NOT add placeholder data unless the user explicitly asks for examples
        """
        
        response = model.generate_content(enhancement_prompt)
        enhanced_prompt = response.text.strip()
        
        # Ensure we're not getting a response that includes markdown formatting or explanations
        if "```" in enhanced_prompt or "Here's an enhanced prompt:" in enhanced_prompt:
            # Extract just the prompt part
            pattern = r'```(?:.*?)\n(.*?)```|Here\'s an enhanced prompt:(.*?)$'
            match = re.search(pattern, enhanced_prompt, re.DOTALL)
            if match:
                if match.group(1):  # If found in code block
                    enhanced_prompt = match.group(1).strip()
                elif match.group(2):  # If found after "Here's an enhanced prompt:"
                    enhanced_prompt = match.group(2).strip()
        
        logger.info(f"Enhanced prompt: {enhanced_prompt}")
        return jsonify({"enhanced_prompt": enhanced_prompt})
        
    except Exception as e:
        logger.error(f"Error enhancing prompt: {str(e)}")
        return jsonify({"error": f"Failed to enhance prompt: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', debug=os.environ.get("DEBUG", "True").lower() == "true", port=port)