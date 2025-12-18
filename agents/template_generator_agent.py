# template_generator_agent.py
import json
import logging
import re
from typing import TypedDict, Dict, List
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from liquid import Template, Environment
from utils.api_cost_tracker import track_openai_request
from utils.template_utils import render_template_preview
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TemplateGeneratorState(TypedDict):
    """State schema for Template Generator workflow."""
    description: str  # User's plain English description
    parsed_intent: Dict  # Parsed template requirements
    field_schema: List[Dict]  # Generated field definitions
    liquid_template: str  # Generated Liquid HTML
    validation_result: Dict  # Syntax & security validation
    preview_html: str  # Rendered preview with sample data
    error: str  # Error message if any


class TemplateGeneratorAgent:
    """
    AI Template Generator Agent

    Generates HTML/Liquid templates from plain English descriptions.

    Workflow:
    1. analyze_description: Parse user's description into structured intent
    2. generate_schema: Create field definitions based on intent
    3. generate_liquid: Generate HTML with Liquid template syntax
    4. validate_template: Validate syntax, security, and consistency
    """

    def __init__(self, model):
        self.model = model
        self.graph = self._initialize_graph()
        logger.info("TemplateGeneratorAgent initialized.")

    def _extract_json_from_response(self, response_content: str) -> str:
        """
        Robustly extract JSON from OpenAI response that may contain explanatory text.

        Handles cases like:
        - "Here's the JSON:\n```json\n{...}\n```"
        - "Sure! Here it is:\n{...}"
        - "{...}" (pure JSON)
        """
        # Remove markdown code fences
        content = response_content.replace("```json", "").replace("```", "").strip()

        # Try to find JSON object {...} or array [...]
        # Look for first { or [ and last } or ]
        start_brace = content.find('{')
        start_bracket = content.find('[')

        # Determine which comes first (or if only one exists)
        if start_brace == -1 and start_bracket == -1:
            # No JSON found
            return content

        if start_brace == -1:
            start = start_bracket
            end_char = ']'
        elif start_bracket == -1:
            start = start_brace
            end_char = '}'
        else:
            # Both exist, use whichever comes first
            if start_brace < start_bracket:
                start = start_brace
                end_char = '}'
            else:
                start = start_bracket
                end_char = ']'

        # Find matching closing brace/bracket
        end = content.rfind(end_char)

        if start >= 0 and end > start:
            json_str = content[start:end+1]
            return json_str

        # Fallback: return cleaned content
        return content

    def _initialize_graph(self):
        """Initialize LangGraph state machine with 4-node workflow."""
        try:
            graph = StateGraph(TemplateGeneratorState)

            # Add nodes
            graph.add_node("analyze_description", self.analyze_description)
            graph.add_node("generate_schema", self.generate_schema)
            graph.add_node("generate_liquid", self.generate_liquid)
            graph.add_node("validate_template", self.validate_template)

            # Connect nodes sequentially
            graph.add_edge("analyze_description", "generate_schema")
            graph.add_edge("generate_schema", "generate_liquid")
            graph.add_edge("generate_liquid", "validate_template")
            graph.add_edge("validate_template", END)

            # Set entry point
            graph.set_entry_point("analyze_description")

            logger.info("TemplateGeneratorAgent StateGraph initialized and compiled.")
            return graph.compile()
        except Exception as e:
            logger.error(f"Error initializing TemplateGeneratorAgent StateGraph: {e}")
            raise

    def analyze_description(self, state: TemplateGeneratorState) -> TemplateGeneratorState:
        """
        Node 1: Analyze user's description and extract structured intent.

        Example:
        Input: "I need template for gym class announcement with instructor photo"
        Output: {
            "content_type": "announcement",
            "industry": "fitness",
            "key_elements": ["class_name", "instructor_name", "instructor_photo", "date_time", "benefits"],
            "layout": "visual-focused",
            "cta": "registration"
        }
        """
        try:
            description = state['description']
            logger.info(f"Analyzing template description: {description[:100]}...")

            prompt = f"""Analyze this template request and extract structured intent.

Request: "{description}"

Return JSON with:
{{
    "content_type": "announcement|promotion|update|story|tutorial|testimonial|event|sale",
    "industry": "fitness|ecommerce|saas|consulting|education|food|generic",
    "key_elements": ["field names that should be included"],
    "layout": "visual-focused|text-focused|balanced",
    "cta": "buy|register|learn|share|contact|none",
    "tone": "professional|casual|energetic|inspirational|urgent"
}}

IMPORTANT: Be specific about key_elements. Include fields like:
- Text fields: title, description, name, tagline
- Media fields: image, photo, logo, video
- Data fields: date, time, price, location
- Rich content: benefits, features, testimonials

Return ONLY the JSON object.
"""

            # Use JSON mode to force pure JSON output
            response = self.model.invoke(
                [HumanMessage(content=prompt)],
                response_format={"type": "json_object"}
            )

            # Track API usage
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            track_openai_request(
                model=model_name,
                response=response,
                metadata={"agent": "template_generator", "step": "analyze_description"}
            )

            # Parse JSON response
            json_str = self._extract_json_from_response(response.content)
            parsed_intent = json.loads(json_str)
            logger.info(f"Intent parsed: content_type={parsed_intent.get('content_type')}, industry={parsed_intent.get('industry')}")

            return {
                'description': description,
                'parsed_intent': parsed_intent,
                'field_schema': [],
                'liquid_template': '',
                'validation_result': {},
                'preview_html': '',
                'error': ''
            }
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON during description analysis: {e}")
            return {'error': f"Failed to parse intent: {str(e)}"}
        except Exception as e:
            logger.error(f"Error analyzing description: {e}")
            return {'error': f"Analysis failed: {str(e)}"}

    def generate_schema(self, state: TemplateGeneratorState) -> TemplateGeneratorState:
        """
        Node 2: Generate field schema based on parsed intent.

        Example output:
        [
            {"name": "class_name", "type": "text", "label": "Class Name", "required": true},
            {"name": "instructor_name", "type": "text", "label": "Instructor Name", "required": true},
            {"name": "instructor_photo", "type": "url", "label": "Instructor Photo URL", "required": false},
            {"name": "date_time", "type": "datetime", "label": "Class Date & Time", "required": true},
            {"name": "benefits", "type": "rich_text", "label": "Class Benefits", "required": true},
            {"name": "cta_button", "type": "text", "label": "Call-to-Action Button Text", "required": false}
        ]
        """
        try:
            parsed_intent = state['parsed_intent']
            logger.info("Generating field schema from parsed intent...")

            prompt = f"""Based on this template intent, generate a JSON schema for fields.

Intent:
{json.dumps(parsed_intent, indent=2)}

Generate a JSON object with a "fields" array containing field definitions:
{{
    "fields": [
        {{
            "name": "field_name_lowercase_underscore",
            "type": "text|url|number|datetime|rich_text|boolean",
            "label": "Human-readable Label",
            "required": true|false,
            "placeholder": "Example value or hint"
        }}
    ]
}}

Field type guidelines:
- "text": Short text (names, titles, taglines)
- "url": Images, photos, logos, links
- "number": Prices, quantities, ratings
- "datetime": Dates, times, timestamps
- "rich_text": Long formatted text (descriptions, benefits, features)
- "boolean": Yes/no flags

IMPORTANT:
1. Include 5-10 fields based on key_elements
2. Always include a title/name field
3. Add description/body field for rich content
4. Include CTA button text if cta is not "none"
5. Use descriptive labels and helpful placeholders

Return ONLY the JSON object with fields array.
"""

            # Use JSON mode to force pure JSON output
            response = self.model.invoke(
                [HumanMessage(content=prompt)],
                response_format={"type": "json_object"}
            )

            # Track API usage
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            track_openai_request(
                model=model_name,
                response=response,
                metadata={"agent": "template_generator", "step": "generate_schema"}
            )

            # Parse JSON response
            json_str = self._extract_json_from_response(response.content)
            response_obj = json.loads(json_str)
            # Extract fields array from response object
            field_schema = response_obj.get('fields', response_obj if isinstance(response_obj, list) else [])
            logger.info(f"Field schema generated with {len(field_schema)} fields")

            return {
                'field_schema': field_schema
            }
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON during schema generation: {e}")
            return {'error': f"Failed to generate schema: {str(e)}"}
        except Exception as e:
            logger.error(f"Error generating schema: {e}")
            return {'error': f"Schema generation failed: {str(e)}"}

    def generate_liquid(self, state: TemplateGeneratorState) -> TemplateGeneratorState:
        """
        Node 3: Generate HTML template with Liquid syntax.

        Example output:
        <div class="campaign-card">
            <h1>{{ items.class_name }}</h1>
            {% if items.instructor_photo %}
                <img src="{{ items.instructor_photo }}" alt="{{ items.instructor_name }}">
            {% endif %}
            <p class="instructor">Instructor: {{ items.instructor_name }}</p>
            <p class="datetime">{{ items.date_time }}</p>
            <div class="benefits">{{ items.benefits }}</div>
            {% if items.cta_button %}
                <button>{{ items.cta_button }}</button>
            {% endif %}
        </div>
        """
        try:
            parsed_intent = state['parsed_intent']
            field_schema = state['field_schema']
            logger.info("Generating Liquid template from field schema...")

            prompt = f"""Generate an HTML template with Liquid syntax for this template.

Intent:
{json.dumps(parsed_intent, indent=2)}

Field Schema:
{json.dumps(field_schema, indent=2)}

Generate a complete HTML template using Liquid syntax:

LIQUID SYNTAX RULES:
1. Variables: {{{{ field_name }}}} - renders field value (use exact field name from schema)
2. Conditionals: {{% if field_name %}} ... {{% endif %}} - for optional fields
3. Rich text: Use <div>{{{{ rich_text_field }}}}</div> for rich_text fields
4. Images: <img src="{{{{ image_url_field }}}}" alt="{{{{ image_alt_field }}}}">
5. Dates: {{{{ date_field }}}} (formatted as-is)

IMPORTANT: Do NOT use "items." prefix - just use field names directly from schema!

HTML STRUCTURE:
- Use semantic HTML5 (section, article, header, footer)
- Add CSS classes for styling (.campaign-card, .title, .description, etc.)
- Make layout responsive (use flexbox/grid concepts in class names)
- Include accessibility attributes (alt, aria-label)
- INCLUDE <style> tag with complete CSS styling (colors, fonts, spacing, layout)

LAYOUT GUIDELINES:
- visual-focused: Large image at top, minimal text
- text-focused: Headline-first, smaller images
- balanced: Equal weight to images and text

TONE STYLING (with CSS):
- professional: Clean sans-serif fonts, minimal colors (#2c3e50, #ecf0f1), subtle borders
- casual: Rounded corners (8px+), warm colors (#ff6b6b, #4ecdc4), playful fonts
- energetic: Bold colors (#ff5722, #ffc107), large headings, dynamic shadows
- inspirational: Large fonts, hero images, elegant colors (#6c5ce7, #a29bfe)
- urgent: Strong CTAs (red/orange), countdown timers, bold text

CSS REQUIREMENTS:
- Add embedded <style> block at the top with all necessary styles
- Style all classes used in HTML (.title, .description, .cta-button, etc.)
- Include responsive design (max-width, padding, margins)
- Style buttons with :hover pseudo-class for hover effects
- Use proper typography (font-family, line-height, letter-spacing)

SECURITY REQUIREMENTS:
- DO NOT use inline event handlers (onclick, onload, onmouseover, etc.)
- DO NOT use javascript: protocol in links
- DO NOT use <script> tags
- Use CSS :hover pseudo-classes instead of inline events
- Example: .button:hover {{ background: #357ABD; }} (GOOD)
- Example: <button onclick="..."> (BAD - DO NOT USE)

Return complete HTML with embedded <style> block and Liquid syntax. NO explanations.
"""

            message = HumanMessage(content=prompt)
            response = self.model.invoke([message])

            # Track API usage
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            track_openai_request(
                model=model_name,
                response=response,
                metadata={"agent": "template_generator", "step": "generate_liquid"}
            )

            # Extract template (remove code fences if present)
            liquid_template = response.content.replace("```html", "").replace("```liquid", "").replace("```", "").strip()
            logger.info(f"Liquid template generated ({len(liquid_template)} characters)")

            return {
                'liquid_template': liquid_template
            }
        except Exception as e:
            logger.error(f"Error generating Liquid template: {e}")
            return {'error': f"Template generation failed: {str(e)}"}

    def validate_template(self, state: TemplateGeneratorState) -> TemplateGeneratorState:
        """
        Node 4: Validate Liquid template for syntax, security, and field consistency.

        Checks:
        1. Liquid syntax validity
        2. Security (no <script> tags, no inline JS)
        3. All schema fields are used in template
        4. No undefined fields in template
        """
        try:
            liquid_template = state['liquid_template']
            field_schema = state['field_schema']
            logger.info("Validating Liquid template...")

            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'security_pass': True,
                'syntax_pass': True,
                'consistency_pass': True
            }

            # 1. Syntax validation - try to parse with Liquid
            try:
                env = Environment()
                template = env.from_string(liquid_template)
                logger.info("✓ Liquid syntax is valid")
            except Exception as e:
                validation_result['valid'] = False
                validation_result['syntax_pass'] = False
                validation_result['errors'].append(f"Liquid syntax error: {str(e)}")
                logger.error(f"Liquid syntax validation failed: {e}")

            # 2. Security validation - check for dangerous patterns
            dangerous_patterns = [
                (r'<script', 'Found <script> tag (XSS risk)'),
                (r'javascript:', 'Found javascript: protocol (XSS risk)'),
                (r'<[^>]+\s+on\w+\s*=', 'Found inline event handler (onclick, onload, etc.)'),  # Only catch in HTML tags
                (r'eval\(', 'Found eval() function (code injection risk)'),
            ]

            for pattern, message in dangerous_patterns:
                if re.search(pattern, liquid_template, re.IGNORECASE):
                    validation_result['valid'] = False
                    validation_result['security_pass'] = False
                    validation_result['errors'].append(message)
                    logger.error(f"Security validation failed: {message}")

            if validation_result['security_pass']:
                logger.info("✓ Security validation passed")

            # 3. Field consistency validation
            # Extract all field references from template (now without 'items.' prefix)
            field_pattern = r'{{\s*(\w+)\s*}}|{%\s*if\s+(\w+)\s*%}'
            matches = re.findall(field_pattern, liquid_template)
            used_fields = set()
            for match in matches:
                # Each match is a tuple (group1, group2) - one will be empty
                field_name = match[0] if match[0] else match[1]
                used_fields.add(field_name)

            # Check if all schema fields are used
            schema_fields = {field['name'] for field in field_schema}
            unused_fields = schema_fields - used_fields
            if unused_fields:
                validation_result['warnings'].append(f"Unused fields in schema: {', '.join(unused_fields)}")
                logger.warning(f"Unused fields: {unused_fields}")

            # Check if template uses undefined fields
            undefined_fields = used_fields - schema_fields
            if undefined_fields:
                validation_result['valid'] = False
                validation_result['consistency_pass'] = False
                validation_result['errors'].append(f"Template uses undefined fields: {', '.join(undefined_fields)}")
                logger.error(f"Undefined fields: {undefined_fields}")

            if validation_result['consistency_pass']:
                logger.info("✓ Field consistency validation passed")

            # 4. Generate preview with sample data
            if validation_result['valid']:
                # Get industry from parsed_intent for realistic sample data
                parsed_intent = state.get('parsed_intent', {})
                industry = parsed_intent.get('industry', 'generic')

                try:
                    preview_html = render_template_preview(liquid_template, field_schema, industry)
                except Exception as e:
                    logger.warning(f"Enhanced preview failed, falling back to basic preview: {e}")
                    preview_html = self._generate_preview(liquid_template, field_schema)
            else:
                preview_html = ""

            logger.info(f"Validation complete: valid={validation_result['valid']}, errors={len(validation_result['errors'])}, warnings={len(validation_result['warnings'])}")

            return {
                'validation_result': validation_result,
                'preview_html': preview_html
            }
        except Exception as e:
            logger.error(f"Error during template validation: {e}")
            return {
                'validation_result': {
                    'valid': False,
                    'errors': [f"Validation exception: {str(e)}"],
                    'warnings': [],
                    'security_pass': False,
                    'syntax_pass': False,
                    'consistency_pass': False
                },
                'preview_html': ''
            }

    def _generate_preview(self, liquid_template: str, field_schema: List[Dict]) -> str:
        """Generate preview HTML with sample data."""
        try:
            # Create sample data based on field types
            sample_data = {}
            for field in field_schema:
                field_name = field['name']
                field_type = field['type']

                if field_type == 'text':
                    sample_data[field_name] = field.get('placeholder', f"Sample {field['label']}")
                elif field_type == 'url':
                    sample_data[field_name] = "https://placehold.co/400x300"
                elif field_type == 'number':
                    sample_data[field_name] = "99"
                elif field_type == 'datetime':
                    sample_data[field_name] = "2025-01-15 10:00 AM"
                elif field_type == 'rich_text':
                    sample_data[field_name] = f"<p>Sample {field['label']}: This is example rich text content with <strong>formatting</strong>.</p>"
                elif field_type == 'boolean':
                    sample_data[field_name] = True

            # Render template with sample data
            env = Environment()
            template = env.from_string(liquid_template)
            preview_html = template.render(**sample_data)

            logger.info("Preview HTML generated successfully")
            return preview_html
        except Exception as e:
            logger.error(f"Error generating preview: {e}")
            return f"<p>Error generating preview: {str(e)}</p>"

    def generate_template_from_description(self, description: str) -> Dict:
        """
        Main entry point: Generate template from plain English description.

        Args:
            description: User's plain English description of desired template

        Returns:
            Dict with:
            - liquid_template: Generated Liquid HTML template
            - field_schema: List of field definitions
            - validation_result: Validation results
            - parsed_intent: Extracted intent
            - preview_html: Rendered preview
            - error: Error message if any
        """
        try:
            logger.info(f"Starting template generation from description: {description[:100]}...")

            # Initialize state
            initial_state = {
                'description': description,
                'parsed_intent': {},
                'field_schema': [],
                'liquid_template': '',
                'validation_result': {},
                'preview_html': '',
                'error': ''
            }

            # Run workflow
            final_state = self.graph.invoke(initial_state)

            # Check for errors
            if final_state.get('error'):
                logger.error(f"Template generation failed: {final_state['error']}")
                return final_state

            # Return results
            result = {
                'liquid_template': final_state['liquid_template'],
                'field_schema': final_state['field_schema'],
                'validation_result': final_state['validation_result'],
                'parsed_intent': final_state['parsed_intent'],
                'preview_html': final_state['preview_html'],
                'error': final_state.get('error', '')
            }

            logger.info(f"Template generation complete: valid={result['validation_result'].get('valid', False)}")
            return result
        except Exception as e:
            logger.error(f"Error in generate_template_from_description: {e}", exc_info=True)
            return {
                'liquid_template': '',
                'field_schema': [],
                'validation_result': {'valid': False, 'errors': [str(e)]},
                'parsed_intent': {},
                'preview_html': '',
                'error': f"Template generation failed: {str(e)}"
            }
