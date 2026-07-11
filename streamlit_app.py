"""
=============================================================================
 streamlit_app.py  —  Streamlit UI for the "Second Brain" Knowledge Manager
=============================================================================
 This file recreates every feature from the CLI-based app.py as a modern,
 interactive web application using Streamlit.

 WHAT IS STREAMLIT?
 ------------------
 Streamlit is a Python library that turns plain Python scripts into
 interactive web apps. You write normal Python — no HTML, CSS, or JS needed.
 Every time you interact with a widget (button, text box, slider, etc.),
 Streamlit RE-RUNS the entire script from top to bottom. This is called the
 "execution model". To survive re-runs you use:
   • st.session_state   → a dictionary that persists across re-runs
   • @st.cache_resource  → caches expensive objects (DB connections, models)

 HOW TO RUN THIS FILE:
 ---------------------
   streamlit run streamlit_app.py
"""

# ─── IMPORTS ────────────────────────────────────────────────────────────────────
import streamlit as st            # The main Streamlit library
import mysql.connector            # MySQL database connector for Python
import os                         # For reading environment variables
import json                       # For parsing AI responses (JSON format)
from openai import OpenAI         # OpenAI-compatible client (used via OpenRouter)
from dotenv import load_dotenv    # Loads variables from a .env file into os.environ

# Load environment variables from the .env file in the project root.
# This reads PASSWORD, API_KEY, and Model so we don't hard-code secrets.
load_dotenv()


# ─── CONSTANTS ──────────────────────────────────────────────────────────────────
# Predefined categories — same as in app.py.
# Used in dropdowns and multi-selects throughout the app.
CATEGORIES = ["AI Resources", "Business Ideas", "DSA Concepts", "Motivation", "Personal Growth"]

# Column names the user is allowed to update (whitelist for SQL safety).
ALLOWED_FIELDS = {"title", "category", "short_description", "link"}


# ─── PAGE CONFIGURATION ────────────────────────────────────────────────────────
# st.set_page_config() MUST be the first Streamlit command in the script.
# It configures the browser tab title, icon, and default layout width.
st.set_page_config(
    page_title="Second Brain 🧠",       # Text shown on the browser tab
    page_icon="🧠",                      # Favicon shown on the browser tab
    layout="wide",                        # "wide" uses the full browser width; "centered" is narrower
    initial_sidebar_state="expanded"      # Sidebar starts open; can also be "collapsed"
)


# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────────
# st.markdown() renders Markdown (and raw HTML when unsafe_allow_html=True).
# We inject a <style> block to customize the look of the app beyond Streamlit's
# built-in theming. This is the ONLY way to add custom CSS in Streamlit.
st.markdown("""
<style>
    /* ── Import a modern Google Font ──────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Apply the font to the entire app ─────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Style the main header with a gradient ────────────────────────── */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    .main-header h1 {
        font-size: 2.4rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        font-size: 1.05rem;
        opacity: 0.9;
        margin-top: 0.4rem;
    }

    /* ── Resource cards shown in Browse / Search results ───────────────── */
    .resource-card {
        background: linear-gradient(145deg, #1e1e2e, #2a2a3d);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 1.5rem 1.6rem;
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    .resource-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
    }
    .resource-card h3 {
        color: #a78bfa;
        margin: 0 0 0.5rem 0;
        font-weight: 700;
    }
    .resource-card .meta {
        color: #94a3b8;
        font-size: 0.82rem;
        margin-bottom: 0.6rem;
    }
    .resource-card .desc {
        color: #e2e8f0;
        line-height: 1.6;
    }
    .resource-card a {
        color: #60a5fa;
        text-decoration: none;
        font-weight: 500;
    }
    .resource-card a:hover {
        text-decoration: underline;
    }

    /* ── Category badges (colored chips) ──────────────────────────────── */
    .category-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .cat-ai       { background: rgba(99, 102, 241, 0.2); color: #818cf8; }
    .cat-business { background: rgba(16, 185, 129, 0.2); color: #34d399; }
    .cat-dsa      { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
    .cat-motivation { background: rgba(239, 68, 68, 0.2); color: #f87171; }
    .cat-personal { background: rgba(236, 72, 153, 0.2); color: #f472b6; }

    /* ── Stat / metric boxes on the Browse page ───────────────────────── */
    .stat-box {
        background: linear-gradient(145deg, #1e1e2e, #252540);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
    }
    .stat-box .number {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-box .label {
        color: #94a3b8;
        font-size: 0.85rem;
        margin-top: 0.3rem;
    }

    /* ── Sidebar navigation styling ───────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
    }
    .sidebar-header {
        text-align: center;
        padding: 1rem 0 1.5rem 0;
    }
    .sidebar-header .emoji {
        font-size: 3rem;
    }
    .sidebar-header h2 {
        color: #e2e8f0;
        margin: 0.5rem 0 0 0;
        font-weight: 700;
    }
    .sidebar-header p {
        color: #64748b;
        font-size: 0.85rem;
    }

    /* ── Success / info banners ────────────────────────────────────────── */
    .success-banner {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(52, 211, 153, 0.1));
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        color: #34d399;
        font-weight: 500;
    }

    /* ── Hide Streamlit's default top-right hamburger menu and footer ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
# 📝 LEARNING NOTE:
# unsafe_allow_html=True is needed whenever you include raw HTML/CSS.
# Without it, Streamlit strips out all HTML tags for security.


# ─── DATABASE CONNECTION ────────────────────────────────────────────────────────
# @st.cache_resource tells Streamlit to run this function ONCE and cache the
# returned object. On every subsequent re-run, the cached connection is reused
# instead of opening a new one. This is essential for expensive objects like
# database connections, ML models, etc.
@st.cache_resource
def get_connection():
    """Create and cache a MySQL database connection."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("PASSWORD"),     # Read from .env file
        database="second_brain"
    )

# Get the cached connection and create a cursor.
mydb = get_connection()
my_cursor = mydb.cursor()


# ─── HELPER FUNCTIONS ──────────────────────────────────────────────────────────
def get_category_badge(category):
    """
    Return an HTML snippet for a colored category badge.
    Maps each category to a specific CSS class for unique coloring.
    """
    # Dictionary mapping category names to CSS class suffixes
    class_map = {
        "AI Resources": "cat-ai",
        "Business Ideas": "cat-business",
        "DSA Concepts": "cat-dsa",
        "Motivation": "cat-motivation",
        "Personal Growth": "cat-personal"
    }
    css_class = class_map.get(category, "cat-ai")      # Default to "cat-ai" if unknown
    return f'<span class="category-badge {css_class}">{category}</span>'


def render_resource_card(row):
    """
    Render a single resource as a styled HTML card.
    `row` is a tuple: (id, title, category, description, link, created_at, updated_at)
    """
    res_id, title, category, description, link, created_at, updated_at = row
    badge = get_category_badge(category)

    # Build the link HTML — only show if the resource has a link
    link_html = ""
    if link and link.strip():
        link_html = f'<p style="margin-top:0.8rem;"><a href="{link}" target="_blank">🔗 Open Resource →</a></p>'

    # st.markdown() with unsafe_allow_html renders our custom HTML card
    st.markdown(f"""
    <div class="resource-card">
        <h3>📌 {title}</h3>
        <div class="meta">
            {badge} &nbsp;·&nbsp; ID: {res_id} &nbsp;·&nbsp; 📅 {created_at}
        </div>
        <p class="desc">{description}</p>
        {link_html}
    </div>
    """, unsafe_allow_html=True)


def fetch_all_resources():
    """Fetch all resources from the database."""
    my_cursor.execute("SELECT * FROM resources")
    return my_cursor.fetchall()


def fetch_by_category(category):
    """Fetch resources filtered by a specific category."""
    query = "SELECT * FROM resources WHERE category = %s"
    my_cursor.execute(query, (category,))
    return my_cursor.fetchall()


def insert_resource(title, category, description, link):
    """Insert a new resource into the database."""
    query = "INSERT INTO resources (title, category, short_description, link) VALUES (%s, %s, %s, %s)"
    my_cursor.execute(query, (title, category, description, link))
    mydb.commit()


def update_resource(resource_id, field, new_value):
    """Update a single field of a resource. Only whitelisted fields are allowed."""
    if field not in ALLOWED_FIELDS:
        return False
    query = f"UPDATE resources SET {field} = %s WHERE id = %s"
    my_cursor.execute(query, (new_value, resource_id))
    mydb.commit()
    return True


def delete_resources(id_list):
    """Delete one or more resources by their IDs."""
    placeholders = ", ".join(["%s"] * len(id_list))
    query = f"DELETE FROM resources WHERE id IN ({placeholders})"
    my_cursor.execute(query, tuple(id_list))
    mydb.commit()


def ai_search(user_question):
    """
    Perform an AI-powered semantic search over all resources.
    Sends resource metadata + user question to an LLM via OpenRouter,
    which returns matching IDs.
    """
    # Fetch lightweight metadata (no full rows) for the prompt
    my_cursor.execute("SELECT id, title, category, short_description FROM resources")
    result = my_cursor.fetchall()

    # Build a text block listing every resource for the AI
    col = ("ID", "Title", "Category", "Description")
    resource_text = ""
    for row in result:
        resource_text += ", ".join(f"{label}: {value}" for label, value in zip(col, row)) + "\n"

    # Construct the prompt (same logic as app.py's prompt() function)
    prompt_text = f'''
    You are the retrieval engine for a personal "Second Brain" knowledge system. Your task is to analyze a list of saved resources and identify which ones are conceptually relevant to the user's query.

    Each resource in the dataset contains four fields: "ID", "Title", "Category", and "Description".

    Retrieval Rules:
    Match based on underlying concepts and intent, not just exact keywords.
    If you find relevant resources, add their exact IDs to the matching_ids list and leave the message field empty.
    If no resources match the query, leave the matching_ids list empty and provide a polite, well-written response in the message field stating that no relevant notes were found in the archive.

    Saved Resources:
    {resource_text}

    User Query:
    {user_question}

    Output Constraints:
    You must output your response as raw, valid JSON.
    Do not include any explanations, greetings, or conversational text outside the JSON object.
    Do not wrap the JSON in Markdown formatting or code blocks.
    Use this exact schema:
    {{"matching_ids": [list of integers], "message": "String or null"}}'''

    try:
        # Create the OpenAI-compatible client pointed at OpenRouter
        client = OpenAI(
            api_key=os.getenv("API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )
        model = os.getenv("Model", "tencent/hy3:free")

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt_text}],
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        return data                       # {"matching_ids": [...], "message": "..."}
    except Exception as e:
        return {"matching_ids": [], "message": f"AI search failed: {e}"}


def fetch_by_ids(id_list):
    """Fetch full resource rows for a list of IDs."""
    placeholders = ", ".join(["%s"] * len(id_list))
    query = f"SELECT * FROM resources WHERE id IN ({placeholders})"
    my_cursor.execute(query, tuple(id_list))
    return my_cursor.fetchall()


# ─── SIDEBAR NAVIGATION ────────────────────────────────────────────────────────
# st.sidebar creates a collapsible side panel. Anything placed inside
# st.sidebar.* will appear there instead of in the main content area.

# Sidebar header with branding
st.sidebar.markdown("""
<div class="sidebar-header">
    <div class="emoji">🧠</div>
    <h2>Second Brain</h2>
    <p>Your Knowledge Vault</p>
</div>
""", unsafe_allow_html=True)

# st.sidebar.divider() draws a thin horizontal line in the sidebar.
st.sidebar.divider()

# st.sidebar.radio() creates a radio-button group. The user picks ONE option.
# The selected value is returned and stored in `page`.
# Every time the user clicks a different option, the script re-runs.
page = st.sidebar.radio(
    "📍 Navigate",                                       # Label shown above the radio buttons
    [
        "🏠 Home",
        "➕ Add Resource",
        "🤖 AI Search",
        "📂 Browse",
        "✏️ Update Resource",
        "🗑️ Delete Resource"
    ],
    label_visibility="collapsed"                          # Hides the label text, keeps the radio buttons
)
# 📝 LEARNING NOTE:
# label_visibility can be:
#   "visible"   → normal label (default)
#   "hidden"    → label hidden but space reserved
#   "collapsed" → label hidden and space removed

# Sidebar footer
st.sidebar.divider()
st.sidebar.markdown(
    "<p style='text-align:center; color:#64748b; font-size:0.8rem;'>"
    "Built with ❤️ & Streamlit</p>",
    unsafe_allow_html=True
)


# ─── MAIN HEADER ───────────────────────────────────────────────────────────────
# This gradient header appears at the top of every page.
st.markdown("""
<div class="main-header">
    <h1>🧠 Second Brain</h1>
    <p>Your personal AI-powered knowledge manager</p>
</div>
""", unsafe_allow_html=True)


# =============================================================================
#  PAGE: HOME
# =============================================================================
if page == "🏠 Home":
    # Fetch all resources to compute stats
    all_resources = fetch_all_resources()
    total = len(all_resources)

    # Count resources per category using a simple dictionary
    cat_counts = {}
    for row in all_resources:
        cat = row[2]                                  # Category is at index 2
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    # ── Stat boxes row ──────────────────────────────────────────────────
    # st.columns(N) creates N equal-width columns. Returns a list of
    # column objects. Use `with col:` to place widgets inside that column.
    cols = st.columns(len(CATEGORIES) + 1)            # +1 for the "Total" box

    # First column: total count
    with cols[0]:
        st.markdown(f"""
        <div class="stat-box">
            <div class="number">{total}</div>
            <div class="label">Total Resources</div>
        </div>
        """, unsafe_allow_html=True)

    # Remaining columns: one per category
    for i, cat in enumerate(CATEGORIES):
        with cols[i + 1]:
            count = cat_counts.get(cat, 0)
            st.markdown(f"""
            <div class="stat-box">
                <div class="number">{count}</div>
                <div class="label">{cat}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Recent resources ────────────────────────────────────────────────
    # st.subheader() renders a smaller heading (like <h2>).
    st.subheader("📋 Recent Resources")

    if all_resources:
        # Show the last 5 resources (most recent at top by assuming ascending IDs)
        for row in reversed(all_resources[-5:]):
            render_resource_card(row)
    else:
        # st.info() shows a blue info banner — great for empty-state messages.
        st.info("No resources yet. Head over to **➕ Add Resource** to get started!")


# =============================================================================
#  PAGE: ADD RESOURCE
# =============================================================================
elif page == "➕ Add Resource":
    st.subheader("➕ Add a New Resource")

    # st.markdown() also renders normal text/paragraphs.
    st.markdown("Fill in the details below to save a new resource to your knowledge vault.")

    # ── Form ────────────────────────────────────────────────────────────
    # st.form() groups multiple input widgets together so the script does
    # NOT re-run after every keystroke. Instead, it waits until the user
    # clicks the submit button. This is ideal for data-entry forms.
    with st.form(key="add_resource_form", clear_on_submit=True):
        # clear_on_submit=True resets all inputs inside the form after submission.

        # st.text_input() creates a single-line text field.
        # The first argument is the label, placeholder sets ghost text.
        title = st.text_input(
            "📝 Title *",                               # Label (the * hints it's required)
            placeholder="e.g. Transformer Architecture Explained"
        )
        # 📝 LEARNING NOTE:
        # The value typed by the user is returned as a string and stored
        # in the variable `title`. If the user hasn't typed anything, it's "".

        # st.selectbox() creates a dropdown menu. The user picks exactly one option.
        # `index=0` means the first item is pre-selected.
        category = st.selectbox(
            "📂 Category *",                            # Label
            CATEGORIES,                                  # List of options
            index=0                                      # Default selection (first item)
        )

        # st.text_area() creates a multi-line text box (like <textarea> in HTML).
        # `height` controls how tall it is in pixels.
        description = st.text_area(
            "📄 Description *",
            placeholder="Write a brief summary of this resource...",
            height=120
        )

        # Another text_input for an optional field (link).
        link = st.text_input(
            "🔗 Link (optional)",
            placeholder="https://example.com/article"
        )

        # st.form_submit_button() creates the submit button inside the form.
        # It returns True when clicked, False otherwise.
        submitted = st.form_submit_button(
            "💾 Save Resource",
            use_container_width=True                     # Button spans full form width
        )
        # 📝 LEARNING NOTE:
        # use_container_width=True makes the button stretch to fill its container.
        # This creates a more prominent, easier-to-click button.

    # ── Handle form submission ──────────────────────────────────────────
    # This code runs AFTER the form is submitted (when submitted == True).
    if submitted:
        # Validate required fields
        if not title.strip():
            # st.error() shows a red error banner.
            st.error("⚠️ Title is required!")
        elif not description.strip():
            st.error("⚠️ Description is required!")
        else:
            insert_resource(title.strip(), category, description.strip(), link.strip())
            # st.success() shows a green success banner.
            st.success(f"✅ **{title}** has been added to your Second Brain!")
            # st.balloons() triggers a fun balloon animation across the screen.
            st.balloons()


# =============================================================================
#  PAGE: AI SEARCH
# =============================================================================
elif page == "🤖 AI Search":
    st.subheader("🤖 AI-Powered Semantic Search")
    st.markdown(
        "Ask a natural-language question and the AI will find the most relevant "
        "resources from your knowledge vault."
    )

    # ── Search input ────────────────────────────────────────────────────
    # st.text_input with a unique key so it doesn't collide with other text_inputs.
    # Every widget needs a unique key if you have multiple of the same type.
    search_query = st.text_input(
        "🔍 What are you looking for?",
        placeholder="e.g. How do neural networks learn?",
        key="ai_search_input"                            # Unique key for this widget
    )

    # st.button() creates a clickable button. Returns True when clicked.
    search_clicked = st.button(
        "🚀 Search",
        use_container_width=True,
        type="primary"                                   # "primary" gives it the accent color
    )
    # 📝 LEARNING NOTE:
    # type="primary" makes the button use the app's primary accent color
    # (usually blue/purple). type="secondary" (default) is more subtle.

    if search_clicked and search_query.strip():
        # st.spinner() shows a loading spinner while the code inside runs.
        # The message is displayed next to the spinner.
        with st.spinner("🧠 Thinking... Searching your knowledge vault..."):
            result = ai_search(search_query.strip())

        if result["matching_ids"]:
            matching = fetch_by_ids(result["matching_ids"])
            st.markdown(f"### 🎯 Found {len(matching)} matching resource(s)")
            for row in matching:
                render_resource_card(row)
        else:
            # st.warning() shows an orange/yellow warning banner.
            message = result.get("message") or "No matching resources found."
            st.warning(f"🔍 {message}")

    elif search_clicked and not search_query.strip():
        st.error("⚠️ Please enter a search query first!")


# =============================================================================
#  PAGE: BROWSE
# =============================================================================
elif page == "📂 Browse":
    st.subheader("📂 Browse Resources")

    # ── Category filter ─────────────────────────────────────────────────
    # st.multiselect() creates a multi-select dropdown where the user can
    # pick ZERO or MORE items from the list. Returns a list of selected items.
    selected_categories = st.multiselect(
        "Filter by categories:",                         # Label
        CATEGORIES,                                      # Available options
        default=CATEGORIES,                              # Pre-select all by default
        key="browse_categories"
    )
    # 📝 LEARNING NOTE:
    # st.multiselect returns a LIST, e.g. ["AI Resources", "DSA Concepts"].
    # Unlike st.selectbox (single choice), this allows multiple selections.
    # The `default` parameter sets which options are pre-selected on first load.

    if selected_categories:
        results = []
        for cat in selected_categories:
            results.extend(fetch_by_category(cat))

        if results:
            st.markdown(f"**Showing {len(results)} resource(s)**")

            # st.divider() renders a horizontal line to visually separate sections.
            st.divider()

            for row in results:
                render_resource_card(row)
        else:
            st.info("No resources found in the selected categories.")
    else:
        st.info("👆 Select at least one category to browse resources.")


# =============================================================================
#  PAGE: UPDATE RESOURCE
# =============================================================================
elif page == "✏️ Update Resource":
    st.subheader("✏️ Update a Resource")
    st.markdown("Select a resource and the fields you want to edit.")

    # ── Pick the resource to edit ───────────────────────────────────────
    all_resources = fetch_all_resources()

    if not all_resources:
        st.info("No resources to update. Add some first!")
    else:
        # Build a dictionary mapping "ID: Title" → resource row for easy lookup.
        resource_options = {f"{row[0]}: {row[1]}": row for row in all_resources}

        # st.selectbox with a dictionary's keys as options — user picks by label.
        selected_label = st.selectbox(
            "🔎 Select Resource to Edit",
            options=list(resource_options.keys()),
            key="update_resource_select"
        )

        selected_row = resource_options[selected_label]
        res_id = selected_row[0]

        # Show the current state of the selected resource
        # st.expander() creates a collapsible section. The user clicks to expand.
        with st.expander("📄 Current Resource Details", expanded=True):
            # expanded=True means it starts open (not collapsed).
            render_resource_card(selected_row)
        # 📝 LEARNING NOTE:
        # st.expander is perfect for showing additional details that the user
        # might not always need. It keeps the UI clean and uncluttered.

        st.divider()

        # ── Choose which fields to edit ─────────────────────────────────
        # st.checkbox() creates a single checkbox. Returns True if checked.
        # We use individual checkboxes to let the user pick which fields to edit.
        st.markdown("**Select fields to update:**")

        # st.columns() again — here 4 equal columns for the checkboxes.
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            edit_title = st.checkbox("📝 Title", key="edit_title")
        with col2:
            edit_category = st.checkbox("📂 Category", key="edit_category")
        with col3:
            edit_desc = st.checkbox("📄 Description", key="edit_desc")
        with col4:
            edit_link = st.checkbox("🔗 Link", key="edit_link")
        # 📝 LEARNING NOTE:
        # Each checkbox needs a unique `key` so Streamlit can track its state
        # independently. Without unique keys, widgets with the same label
        # would conflict.

        # ── Show input fields for selected edits ────────────────────────
        # We collect all edits into a list and apply them together.
        edits_to_apply = []

        if edit_title:
            new_title = st.text_input(
                "New Title",
                value=selected_row[1],                    # Pre-fill with current value
                key="new_title_input"
            )
            edits_to_apply.append(("title", new_title))

        if edit_category:
            # For category, use a selectbox (dropdown) — no free-text typing needed.
            current_cat_index = CATEGORIES.index(selected_row[2]) if selected_row[2] in CATEGORIES else 0
            new_category = st.selectbox(
                "New Category",
                CATEGORIES,
                index=current_cat_index,                  # Pre-select the current category
                key="new_category_select"
            )
            edits_to_apply.append(("category", new_category))

        if edit_desc:
            new_desc = st.text_area(
                "New Description",
                value=selected_row[3],                    # Pre-fill with current value
                height=120,
                key="new_desc_input"
            )
            edits_to_apply.append(("short_description", new_desc))

        if edit_link:
            new_link = st.text_input(
                "New Link",
                value=selected_row[4] or "",              # Pre-fill; handle None
                key="new_link_input"
            )
            edits_to_apply.append(("link", new_link))

        # ── Apply updates ───────────────────────────────────────────────
        if edits_to_apply:
            if st.button("💾 Apply Changes", type="primary", use_container_width=True):
                for field, value in edits_to_apply:
                    update_resource(res_id, field, value)
                st.success(f"✅ Resource **#{res_id}** updated successfully!")
                # st.rerun() forces the entire script to re-run immediately.
                # We use it here so the displayed resource card refreshes
                # with the updated data.
                st.rerun()
                # 📝 LEARNING NOTE:
                # st.rerun() is like hitting "Refresh" — the script runs again
                # from top to bottom, and the database query fetches fresh data.


# =============================================================================
#  PAGE: DELETE RESOURCE
# =============================================================================
elif page == "🗑️ Delete Resource":
    st.subheader("🗑️ Delete Resources")
    st.markdown("Select the resources you want to permanently remove.")

    all_resources = fetch_all_resources()

    if not all_resources:
        st.info("No resources to delete.")
    else:
        # ── Show resources with checkboxes ──────────────────────────────
        # We use st.session_state to track which resources the user checked.
        # st.session_state is a dictionary that PERSISTS across re-runs.
        if "delete_ids" not in st.session_state:
            st.session_state.delete_ids = set()
        # 📝 LEARNING NOTE:
        # st.session_state survives script re-runs. Normal Python variables
        # get reset every re-run. Use session_state for anything that needs
        # to persist: form data, counters, toggle states, shopping carts, etc.

        # "Select All" toggle using a checkbox
        select_all = st.checkbox("Select All", key="select_all_delete")

        st.divider()

        for row in all_resources:
            res_id = row[0]
            # Each resource gets its own checkbox.
            # The default value is True if "Select All" is checked OR if
            # the user previously checked this specific resource.
            checked = st.checkbox(
                f"**#{res_id}** — {row[1]}  ({row[2]})",     # Label shows ID, title, category
                value=select_all,                              # Controlled by "Select All"
                key=f"del_{res_id}"                            # Unique key per resource
            )
            if checked:
                st.session_state.delete_ids.add(res_id)
            else:
                st.session_state.delete_ids.discard(res_id)

        st.divider()

        # Show how many are selected
        selected_count = len(st.session_state.delete_ids)
        if selected_count > 0:
            # st.error() used here as a "danger zone" indicator
            st.error(f"⚠️ **{selected_count}** resource(s) selected for deletion.")

            # Confirmation button
            if st.button(
                f"🗑️ Permanently Delete {selected_count} Resource(s)",
                type="primary",
                use_container_width=True
            ):
                delete_resources(list(st.session_state.delete_ids))
                st.session_state.delete_ids = set()       # Clear the selection
                st.success("✅ Resources deleted successfully!")
                st.rerun()                                 # Refresh to show updated list
        else:
            st.info("☝️ Check the resources you want to delete.")
