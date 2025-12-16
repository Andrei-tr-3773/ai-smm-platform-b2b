# Week 2: Custom Templates & Multi-tenancy (REVISED)

**Duration:** 4 days (28 hours)
**Goal:** Enable clients to create and manage custom templates - our KILLER FEATURE

---

## 🎯 Что мы делаем на этой неделе

**KILLER FEATURE:** Каждый клиент может создавать свои собственные шаблоны!

### Why This Matters (Почему это важно)

**Competitors (Jasper, Copy.ai, ChatGPT):**
- ❌ Generic templates for everyone
- ❌ Can't customize
- ❌ One size fits all

**WE:**
- ✅ Each client creates templates specific to THEIR business
- ✅ Edit templates anytime
- ✅ Share templates across team
- ✅ This is our **#1 competitive advantage**

---

## Что уже готово из Week 1 ✅

- ✅ Multi-tenancy design (`docs/MULTI_TENANCY_DESIGN.md`)
- ✅ B2B personas defined (3 personas)
- ✅ Example businesses (FitZone, CloudFlow, ShopStyle)
- ✅ Monitoring & API cost tracking working
- ✅ Getting Started page deployed
- ✅ Production deployment on http://34.165.81.129:8501
- ✅ GitHub repo: https://github.com/Andrei-tr-3773/ai-smm-platform-b2b

---

## День 1: Template Management UI (8 часов)

### Утро (4 часа)

#### Task 2.1.1: Create Template Management Page (2 часа)

**Создать:** `pages/03_Templates.py`

**Features:**
```python
import streamlit as st

st.set_page_config(page_title="Templates", page_icon="📝", layout="wide")

st.title("📝 Content Templates")

# Tabs: My Templates | Global Templates | Create New
tab1, tab2, tab3 = st.tabs(["My Templates", "Global Templates", "Create New"])

with tab1:
    # List user's custom templates
    # Show: name, description, category, usage_count, last_used
    # Actions: Edit, Delete, Duplicate, Preview

with tab2:
    # Global templates (provided by platform)
    # Filter by industry: fitness, ecommerce, saas, generic
    # Action: Copy to My Templates (customize)

with tab3:
    # Create new template wizard
    # Step 1: Template name & description
    # Step 2: Define fields
    # Step 3: Liquid template editor
    # Step 4: Preview & save
```

**UI Components:**
- Search templates
- Filter by category (fitness, ecommerce, saas, generic)
- Sort by: name, usage, date
- Grid view / List view toggle
- Template card with preview image

**Deliverables:**
- [ ] `pages/03_Templates.py` created
- [ ] List custom templates from MongoDB
- [ ] Filter & search working
- [ ] Create/Edit/Delete buttons functional

---

#### Task 2.1.2: Template Repository (2 часа)

**Create:** `repositories/template_repository.py`

```python
class TemplateRepository:
    def __init__(self):
        self.collection = get_mongodb_collection("content_templates")

    def create_template(self, workspace_id: str, template_data: dict):
        """Create new custom template"""
        pass

    def get_templates_by_workspace(self, workspace_id: str):
        """Get all templates for workspace"""
        pass

    def get_global_templates(self):
        """Get platform templates (workspace_id = null)"""
        pass

    def update_template(self, template_id: str, updates: dict):
        """Update existing template"""
        pass

    def delete_template(self, template_id: str):
        """Delete template"""
        pass

    def duplicate_template(self, template_id: str, workspace_id: str):
        """Copy global template to workspace"""
        pass

    def increment_usage_count(self, template_id: str):
        """Track template usage"""
        pass
```

**Deliverables:**
- [ ] `repositories/template_repository.py` created
- [ ] CRUD operations working
- [ ] Unit tests (optional)

---

### День (4 часа)

#### Task 2.1.3: Template Models (1 час)

**Update:** `campaign.py` → add `ContentTemplate` model

```python
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

class FieldSchema(BaseModel):
    """Schema for template field"""
    type: str  # text, number, url, date, rich_text
    required: bool = True
    default_value: Optional[str] = None
    max_length: Optional[int] = None
    description: Optional[str] = None

class ContentTemplate(BaseModel):
    """Content template model"""
    id: Optional[str] = None
    workspace_id: Optional[str] = None  # null = global template
    name: str
    description: str
    liquid_template: str  # HTML with Liquid variables
    items: Dict[str, FieldSchema]  # field_name → schema
    example_query: str
    category: str  # fitness, ecommerce, saas, generic
    tags: List[str] = []
    is_shared: bool = False  # global or workspace-specific
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    usage_count: int = 0
```

**Deliverables:**
- [ ] `ContentTemplate` model added
- [ ] `FieldSchema` model added
- [ ] Validation working

---

#### Task 2.1.4: Template Gallery UI (3 часа)

**Design Template Cards:**

```markdown
┌─────────────────────────────────────┐
│ 📝 New Class Announcement          │
│ Category: Fitness                   │
│                                     │
│ Announce new fitness classes with   │
│ instructor, schedule, benefits      │
│                                     │
│ Fields: 5 | Used: 24 times         │
│ Last used: 2 hours ago             │
│                                     │
│ [Preview] [Use] [Edit] [Delete]    │
└─────────────────────────────────────┘
```

**Features:**
- Template thumbnail (auto-generated from first render)
- Hover preview (larger view)
- Quick actions (Use, Edit, Duplicate, Delete)
- Usage statistics
- "Popular" badge (>50 uses)
- "New" badge (<7 days old)

**Deliverables:**
- [ ] Template card component styled
- [ ] Gallery grid layout working
- [ ] Thumbnail generation (screenshot or placeholder)
- [ ] Quick actions functional

---

## День 2: Liquid Template Editor (8 часов)

### Утро (4 часа)

#### Task 2.2.1: Monaco Editor Integration (3 часа)

**Install Monaco Editor:**
```bash
cd static/
npm init -y
npm install monaco-editor
```

**Create:** `components/monaco_liquid_editor.py`

```python
import streamlit as st
import streamlit.components.v1 as components

def liquid_editor(template_code: str, height: int = 400):
    """Monaco editor with Liquid syntax highlighting"""

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs/editor/editor.main.css">
    </head>
    <body>
        <div id="editor" style="height: {height}px"></div>

        <script src="https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs/loader.js"></script>
        <script>
            require.config({{ paths: {{ 'vs': 'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs' }} }});
            require(['vs/editor/editor.main'], function() {{
                // Register Liquid language
                monaco.languages.register({{ id: 'liquid' }});

                // Define Liquid syntax
                monaco.languages.setMonarchTokensProvider('liquid', {{
                    tokenizer: {{
                        root: [
                            [/\{{\\{{/, 'delimiter.liquid'],
                            [/\\}}\\}}/, 'delimiter.liquid'],
                            [/\{{%/, 'delimiter.liquid'],
                            [/%\\}}/, 'delimiter.liquid'],
                            [/<[^>]+>/, 'tag'],
                        ]
                    }}
                }});

                var editor = monaco.editor.create(document.getElementById('editor'), {{
                    value: `{template_code}`,
                    language: 'liquid',
                    theme: 'vs-dark',
                    automaticLayout: true,
                    minimap: {{ enabled: false }},
                    lineNumbers: 'on',
                    fontSize: 14
                }});

                // Send changes back to Streamlit
                editor.onDidChangeModelContent(function() {{
                    var code = editor.getValue();
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        value: code
                    }}, '*');
                }});
            }});
        </script>
    </body>
    </html>
    """

    return components.html(html, height=height + 50)
```

**Deliverables:**
- [ ] Monaco editor embedded in Streamlit
- [ ] Liquid syntax highlighting working
- [ ] Code changes sent back to Streamlit
- [ ] Dark theme enabled

---

#### Task 2.2.2: Auto-complete for Liquid Variables (1 час)

**Features:**
- Type `{{` → show available variables
- Type `{%` → show Liquid tags (if, for, etc.)
- Hover over variable → show field description
- Error highlighting for undefined variables

**Liquid Tags to Support:**
```liquid
{{ variable_name }}
{% if condition %} ... {% endif %}
{% for item in items %} ... {% endfor %}
{% else %}
{{ variable | filter }}
```

**Deliverables:**
- [ ] Auto-complete working for variables
- [ ] Liquid tag suggestions
- [ ] Error detection for undefined vars

---

### День (4 часа)

#### Task 2.2.3: Live Preview Panel (2 часа)

**Create:** Split view: Editor (left) | Preview (right)

```python
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Liquid Template Editor")
    template_code = liquid_editor(current_template, height=500)

with col2:
    st.subheader("👁️ Live Preview")

    # Sample data for preview
    sample_data = {
        "class_name": "HIIT Blast",
        "instructor": "Sarah",
        "date": "Saturday, Dec 16",
        "time": "10:00 AM",
        "benefits": "Burn 500 calories in 45 minutes!"
    }

    # Render Liquid template with sample data
    try:
        from liquid import Template
        template = Template(template_code)
        rendered_html = template.render(**sample_data)
        st.components.v1.html(rendered_html, height=500, scrolling=True)
    except Exception as e:
        st.error(f"Template Error: {e}")
```

**Features:**
- Real-time preview (update as you type)
- Editable sample data (JSON editor)
- Responsive preview (desktop, tablet, mobile views)
- Error messages with line numbers

**Deliverables:**
- [ ] Split-pane layout working
- [ ] Live preview updates on code change
- [ ] Sample data editable
- [ ] Error handling with helpful messages

---

#### Task 2.2.4: Template Validation (2 часа)

**Validation Rules:**

```python
def validate_liquid_template(template_code: str, fields_schema: Dict) -> List[str]:
    """Validate Liquid template"""
    errors = []

    # 1. Check Liquid syntax is valid
    try:
        Template(template_code)
    except Exception as e:
        errors.append(f"Syntax Error: {e}")

    # 2. Check all variables are defined in fields_schema
    import re
    variables = re.findall(r'\{\{\s*(\w+)', template_code)
    undefined_vars = set(variables) - set(fields_schema.keys())
    if undefined_vars:
        errors.append(f"Undefined variables: {', '.join(undefined_vars)}")

    # 3. Check all required fields are used in template
    required_fields = [k for k, v in fields_schema.items() if v['required']]
    unused_required = set(required_fields) - set(variables)
    if unused_required:
        errors.append(f"Required fields not used: {', '.join(unused_required)}")

    # 4. Check HTML is valid (basic check)
    from html.parser import HTMLParser
    try:
        HTMLParser().feed(template_code)
    except Exception as e:
        errors.append(f"HTML Error: {e}")

    return errors
```

**UI:**
- Show validation errors in sidebar
- Green checkmark if valid
- Red X with error count if invalid
- Click error → jump to line in editor

**Deliverables:**
- [ ] Template validation function working
- [ ] Errors displayed in UI
- [ ] Prevent saving invalid templates
- [ ] Helpful error messages

---

## День 3: Field Schema Builder (8 часов)

### Утро (4 часа)

#### Task 2.3.1: Field Definition UI (3 часа)

**Create:** Field builder interface

```python
st.subheader("📋 Define Template Fields")

# Add field button
if st.button("➕ Add Field"):
    st.session_state.fields.append({
        "name": "",
        "type": "text",
        "required": True,
        "default_value": "",
        "description": ""
    })

# List existing fields
for i, field in enumerate(st.session_state.fields):
    with st.expander(f"Field {i+1}: {field.get('name', 'Unnamed')}", expanded=True):
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            field['name'] = st.text_input(
                "Field Name",
                value=field['name'],
                key=f"field_name_{i}",
                placeholder="e.g., class_name, product_price"
            )

        with col2:
            field['type'] = st.selectbox(
                "Type",
                ["text", "number", "url", "date", "rich_text"],
                key=f"field_type_{i}"
            )

        with col3:
            field['required'] = st.checkbox(
                "Required",
                value=field['required'],
                key=f"field_required_{i}"
            )

        # Type-specific options
        if field['type'] == 'text':
            field['max_length'] = st.number_input(
                "Max Length",
                min_value=1,
                max_value=1000,
                value=100,
                key=f"field_maxlen_{i}"
            )

        field['default_value'] = st.text_input(
            "Default Value (optional)",
            value=field.get('default_value', ''),
            key=f"field_default_{i}"
        )

        field['description'] = st.text_area(
            "Description (for users)",
            value=field.get('description', ''),
            key=f"field_desc_{i}",
            placeholder="e.g., Name of the fitness class"
        )

        # Delete button
        if st.button("🗑️ Delete Field", key=f"delete_{i}"):
            st.session_state.fields.pop(i)
            st.rerun()
```

**Field Types Supported:**
- **text**: Short text (max_length)
- **number**: Integer or decimal
- **url**: Valid URL (with validation)
- **date**: Date picker
- **rich_text**: Multi-line text with formatting

**Deliverables:**
- [ ] Field builder UI created
- [ ] Add/Edit/Delete fields working
- [ ] Field types supported
- [ ] Validation for field names (no spaces, lowercase)

---

#### Task 2.3.2: Field Schema Validation (1 час)

**Validation Rules:**

```python
def validate_field_schema(fields: List[Dict]) -> List[str]:
    """Validate field schema"""
    errors = []

    # Check field names are unique
    names = [f['name'] for f in fields]
    if len(names) != len(set(names)):
        errors.append("Field names must be unique")

    # Check field names are valid (lowercase, no spaces)
    for field in fields:
        name = field['name']
        if not name:
            errors.append("Field name cannot be empty")
        elif not re.match(r'^[a-z_][a-z0-9_]*$', name):
            errors.append(f"Invalid field name '{name}' (use lowercase, underscores only)")

    # Check required fields have descriptions
    for field in fields:
        if field['required'] and not field.get('description'):
            errors.append(f"Required field '{field['name']}' needs a description")

    return errors
```

**Deliverables:**
- [ ] Field validation working
- [ ] Errors shown in UI
- [ ] Prevent saving invalid schema

---

### День (4 часа)

#### Task 2.3.3: Template Preview with Real Data (2 часа)

**Features:**
- Generate sample data based on field types
- User can edit sample data
- Preview updates in real-time
- Multiple preview scenarios (empty fields, full fields)

```python
def generate_sample_data(fields_schema: Dict) -> Dict:
    """Generate realistic sample data"""
    sample = {}

    for field_name, field_info in fields_schema.items():
        if field_info['type'] == 'text':
            sample[field_name] = f"Sample {field_name.replace('_', ' ').title()}"
        elif field_info['type'] == 'number':
            sample[field_name] = 42
        elif field_info['type'] == 'url':
            sample[field_name] = "https://example.com/image.jpg"
        elif field_info['type'] == 'date':
            sample[field_name] = "Saturday, Dec 16, 2024"
        elif field_info['type'] == 'rich_text':
            sample[field_name] = "This is a longer sample text with multiple sentences. It demonstrates how rich text fields look in the template."

    return sample
```

**Deliverables:**
- [ ] Sample data generation working
- [ ] User can edit sample data (JSON editor)
- [ ] Preview updates correctly
- [ ] Multiple preview scenarios (desktop, mobile)

---

#### Task 2.3.4: Save & Test Template (2 часа)

**Save Flow:**
1. Validate template code
2. Validate field schema
3. Generate preview thumbnail
4. Save to MongoDB
5. Show success message
6. Redirect to template detail page

```python
if st.button("💾 Save Template"):
    # Validate
    code_errors = validate_liquid_template(template_code, fields_schema)
    schema_errors = validate_field_schema(fields)

    if code_errors or schema_errors:
        st.error("Cannot save: template has errors")
        for err in code_errors + schema_errors:
            st.error(f"• {err}")
    else:
        # Save
        template_data = {
            "name": template_name,
            "description": template_description,
            "liquid_template": template_code,
            "items": fields_schema,
            "category": category,
            "workspace_id": current_workspace_id,
            "created_by": current_user_id,
        }

        template_id = template_repo.create_template(template_data)

        st.success(f"✅ Template '{template_name}' saved successfully!")
        st.balloons()

        # Redirect
        st.switch_page(f"pages/03_Templates.py?template_id={template_id}")
```

**Test Flow:**
- "Test Template" button
- User enters test data (form auto-generated from fields)
- Generate content using ContentGenerationAgent
- Show rendered result
- If good → Save, if bad → go back and edit

**Deliverables:**
- [ ] Save template working
- [ ] Test template flow functional
- [ ] Success/error messages shown
- [ ] Redirect to template detail page

---

## День 4: Integration & Testing (4 часа)

### Утро (2 часа)

#### Task 2.4.1: Integrate Templates with Content Generation (2 часа)

**Update:** `Home.py` → use custom templates

```python
# In Create Campaign tab
st.subheader("📝 Select Template")

template_source = st.radio(
    "Template Source",
    ["Global Templates", "My Custom Templates"],
    horizontal=True
)

if template_source == "My Custom Templates":
    custom_templates = template_repo.get_templates_by_workspace(workspace_id)
    if not custom_templates:
        st.info("You haven't created any custom templates yet. [Create one now](pages/03_Templates.py)")
    else:
        template_names = [t['name'] for t in custom_templates]
        selected_name = st.selectbox("Choose Template", template_names)
        selected_template = next(t for t in custom_templates if t['name'] == selected_name)
else:
    # Use global templates (existing flow)
    pass

# Generate form based on template fields
for field_name, field_info in selected_template['items'].items():
    if field_info['type'] == 'text':
        user_input[field_name] = st.text_input(
            field_info.get('description', field_name),
            value=field_info.get('default_value', ''),
            max_chars=field_info.get('max_length', 100)
        )
    elif field_info['type'] == 'number':
        user_input[field_name] = st.number_input(
            field_info.get('description', field_name),
            value=field_info.get('default_value', 0)
        )
    # ... other types
```

**Deliverables:**
- [ ] Custom templates selectable in Home.py
- [ ] Form auto-generated from field schema
- [ ] Content generation works with custom templates
- [ ] Usage count incremented on use

---

### День (2 часа)

#### Task 2.4.2: End-to-End Testing (1 час)

**Test Scenarios:**

**Scenario 1: Create Custom Template**
1. Go to Templates page
2. Click "Create New"
3. Enter name: "Product Launch"
4. Add fields: product_name (text), price (number), image_url (url)
5. Write Liquid template
6. Preview with sample data
7. Save template
8. ✅ Template appears in "My Templates"

**Scenario 2: Use Custom Template**
1. Go to Home → Create Campaign
2. Select "My Custom Templates"
3. Choose "Product Launch"
4. Fill in form (auto-generated)
5. Generate content
6. ✅ Content rendered correctly using custom template

**Scenario 3: Edit Template**
1. Go to Templates → My Templates
2. Click "Edit" on "Product Launch"
3. Change liquid template
4. Save
5. Generate new campaign
6. ✅ New template version used

**Test Checklist:**
- [ ] Create template works
- [ ] Edit template works
- [ ] Delete template works
- [ ] Use template in campaign works
- [ ] Template validation catches errors
- [ ] Sample data preview accurate
- [ ] Usage count increments

**Deliverables:**
- [ ] All test scenarios pass
- [ ] Bug list created
- [ ] Critical bugs fixed

---

#### Task 2.4.3: Documentation & Cleanup (1 час)

**Create:** `docs/CUSTOM_TEMPLATES_GUIDE.md`

```markdown
# Custom Templates Guide

## What are Custom Templates?

Custom templates allow you to create content templates specific to YOUR business.

## Creating a Template

### Step 1: Define Fields
- Name your fields (e.g., `product_name`, `price`)
- Choose field type (text, number, url, date)
- Mark required fields
- Add descriptions for users

### Step 2: Write Liquid Template
- Use {{ field_name }} for variables
- Use {% if %} for conditions
- Use {% for %} for loops

### Step 3: Preview
- Test with sample data
- Check on desktop & mobile
- Verify all fields render correctly

### Step 4: Save & Use
- Save to your workspace
- Use in Create Campaign

## Best Practices

- Keep field names lowercase with underscores
- Provide clear descriptions
- Test template before saving
- Use semantic HTML
- Optimize for mobile

## Examples

See `docs/LIQUID_TEMPLATES.md` for detailed examples.
```

**Code Cleanup:**
- Remove debug print statements
- Add docstrings to all functions
- Fix linting errors
- Update type hints

**Deliverables:**
- [ ] User guide created
- [ ] Code cleaned up
- [ ] Comments added
- [ ] Ready for next week

---

## Week 2 Checklist

### Day 1 ✅
- [ ] Template Management page created
- [ ] Template repository CRUD working
- [ ] Template models defined
- [ ] Template gallery UI styled

### Day 2 ✅
- [ ] Monaco editor integrated
- [ ] Liquid syntax highlighting working
- [ ] Live preview panel functional
- [ ] Template validation working

### Day 3 ✅
- [ ] Field builder UI created
- [ ] Field schema validation working
- [ ] Sample data generation working
- [ ] Save & test flow functional

### Day 4 ✅
- [ ] Custom templates integrated with Home.py
- [ ] End-to-end tests passing
- [ ] Documentation created
- [ ] Code cleaned up

---

## Success Metrics (Week 2)

**Technical:**
- ✅ Users can create custom templates
- ✅ Templates saved to MongoDB
- ✅ Live preview works
- ✅ Validation prevents errors

**User Experience:**
- ✅ Create template in <10 minutes
- ✅ No code knowledge required
- ✅ Preview matches final output
- ✅ Clear error messages

**Business Value:**
- ✅ Killer feature functional
- ✅ Competitive advantage validated
- ✅ Ready for beta user testing
- ✅ Foundation for Week 3 (Analytics)

---

## Risks & Mitigation

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Monaco editor too complex | Medium | Use simpler textarea if needed, add Monaco later |
| Liquid template learning curve | High | Provide examples, auto-complete, documentation |
| Template validation edge cases | Medium | Start simple, add more rules iteratively |
| Preview rendering issues | Medium | Test on multiple browsers, add fallback |

---

## Next Week Preview (Week 3)

**Focus:** Analytics & Insights - explain WHAT worked and WHY

**Tasks:**
- Mock analytics generator
- Analytics agent (LangGraph)
- Dashboard UI with charts
- "Why It Worked" explanations
- Next month recommendations

---

## GitHub & Deployment

**Branch Strategy:**
- Create branch: `week-2-custom-templates`
- Daily commits with meaningful messages
- PR review before merging to main
- Deploy to production after testing

**Commit Message Format:**
```bash
git commit -m "Add template management UI

- Create pages/03_Templates.py
- List user templates with filter/search
- Add template card component
- Connect to template repository"
```

---

## Questions for Week 2 Kickoff

1. **Monaco Editor:** Use CDN or npm install locally?
2. **Template Storage:** MongoDB only or also cache in Redis?
3. **Preview:** Server-side render or client-side?
4. **Field Types:** Start with 5 types or add more?
5. **Workspace:** Implement multi-tenancy now or later?

---

**Status:** 📋 **READY TO START**
**Duration:** 28 hours (4 days)
**Start Date:** Week 2, Day 1
**End Date:** Week 2, Day 4

**Let's build the killer feature! 🚀**
