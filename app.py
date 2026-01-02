"""Streamlit chatbot application using OpenAI API.

To run this app:
    1. Navigate to the directory containing this file
    2. Run: python -m streamlit run app.py
    3. Open the provided local URL (typically http://localhost:8501) in your browser
"""

# Import necessary libraries
import json  # For saving/loading conversation data
import os  # For file system operations
from datetime import datetime  # For timestamping saved conversations
from pathlib import Path  # For cross-platform file path handling
from openai import OpenAI
import streamlit as st
from streamlit_js_eval import streamlit_js_eval  # For page reload functionality

# Set up the Streamlit app configuration
st.set_page_config(page_title="Streamlit Chat", page_icon=":speech_balloon:", layout="wide")
st.title("Chatbot")

# Create directory for saved conversations
# All interview conversations will be automatically saved here as JSON files
SAVED_CONVERSATIONS_DIR = Path("saved_conversations")
SAVED_CONVERSATIONS_DIR.mkdir(exist_ok=True)  # Create if doesn't exist

# Initialize session state variables
if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0
if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False

# Define functions for saving and loading conversations
def save_conversation(conv_data, filename=None):
    """Save conversation to a JSON file.

    Args:
        conv_data: Dictionary containing session state data to save
        filename: Optional custom filename, auto-generated with timestamp if None

    Returns:
        Path object pointing to the saved file
    """
    # Generate filename with timestamp if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"interview_{timestamp}.json"

    # Save conversation data as formatted JSON
    save_path = SAVED_CONVERSATIONS_DIR / filename
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(conv_data, f, indent=2, ensure_ascii=False)
    return save_path

def load_conversation(filename):
    """Load conversation from a JSON file.

    Args:
        filename: Name of the JSON file to load

    Returns:
        Dictionary containing the saved session state data
    """
    load_path = SAVED_CONVERSATIONS_DIR / filename
    with open(load_path, 'r', encoding='utf-8') as f:
        return json.load(f)  # Parse JSON and return as dictionary

def get_saved_conversations():
    """Get list of saved conversation files.

    Returns:
        List of filenames sorted by modification time (newest first)
    """
    if not SAVED_CONVERSATIONS_DIR.exists():
        return []
    # Find all JSON files and sort by modification time (newest first)
    files = sorted(SAVED_CONVERSATIONS_DIR.glob("*.json"),
                   key=os.path.getmtime, reverse=True)
    return [f.name for f in files]

def format_conversation_for_export():
    """Format conversation as readable text for TXT export.

    Returns:
        Formatted string with header and all conversation messages
    """
    output = []
    # Add header with interview details
    output.append("=" * 50)
    output.append("INTERVIEW CONVERSATION")
    output.append("=" * 50)
    output.append(f"Name: {st.session_state.get('name', 'N/A')}")
    # Split long line for readability
    level = st.session_state.get('level', 'N/A')
    position = st.session_state.get('position', 'N/A')
    output.append(f"Position: {level} {position}")
    output.append(f"Company: {st.session_state.get('company', 'N/A')}")
    output.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("=" * 50)
    output.append("")

    # Add all conversation messages (exclude system prompt)
    for msg in st.session_state.messages:
        if msg['role'] != 'system':
            output.append(f"{msg['role'].upper()}: {msg['content']}")
            output.append("")

    return "\n".join(output)

# Define functions for setup completion and feedback display
def complete_setup():
    """
    Mark the setup process as complete by setting the session state flag.

    This function updates the Streamlit session state to indicate that the initial
    setup has been completed. It is typically called after necessary configuration
    steps are finished.

    Returns:
        None
    """
    st.session_state.setup_complete = True

# Display feedback form after a certain number of messages
def show_feedback():
    """
    Display a feedback form to the user after a certain number of messages.

    This function checks if the user has sent a specified number of messages
    and whether the feedback form has already been shown. If both conditions
    are met, it displays a feedback form for the user to fill out.

    Returns:
        None
    """
    st.session_state.feedback_shown = True

# Sidebar for viewing past conversations and exporting current chat
with st.sidebar:
    st.header("📚 Past Conversations")

    # Get list of all saved conversation files
    saved_files = get_saved_conversations()

    if saved_files:
        st.write(f"Total saved: {len(saved_files)}")

        # Dropdown to select a conversation to load
        selected_file = st.selectbox(
            "Select a conversation to view:",
            options=["-- Select --"] + saved_files,
            key="conversation_selector"
        )

        # Load button - restores entire session state from saved file
        if selected_file != "-- Select --":
            if st.button("Load Selected Conversation"):
                try:
                    loaded_data = load_conversation(selected_file)
                    # Restore all session state variables from saved conversation
                    for key, value in loaded_data.items():
                        st.session_state[key] = value
                    st.success(f"Loaded: {selected_file}")
                    st.rerun()  # Refresh page to show loaded conversation
                except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
                    st.error(f"Error loading conversation: {e}")

        st.divider()

        # Option to delete saved conversations
        if st.checkbox("Show delete options"):
            file_to_delete = st.selectbox(
                "Select file to delete:",
                options=saved_files,
                key="delete_selector"
            )
            if st.button("🗑️ Delete", type="secondary"):
                try:
                    # Permanently delete the selected file
                    (SAVED_CONVERSATIONS_DIR / file_to_delete).unlink()
                    st.success(f"Deleted: {file_to_delete}")
                    st.rerun()  # Refresh to update file list
                except (FileNotFoundError, OSError) as e:
                    st.error(f"Error deleting file: {e}")
    else:
        st.info("No saved conversations yet.")

    st.divider()

    # Export current conversation section
    # Only show if there's an active conversation
    if st.session_state.get('messages') and len(st.session_state.messages) > 1:
        st.header("💾 Export Current Chat")

        # Format conversation as readable text
        export_text: str = format_conversation_for_export()

        # Download button for TXT format (human-readable)
        st.download_button(
            label="📥 Download as TXT",
            data=export_text,
            file_name=f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )

        # Download button for JSON format (complete session data)
        export_json = json.dumps(dict(st.session_state), indent=2, default=str)
        st.download_button(
            label="📥 Download as JSON",
            data=export_json,
            file_name=f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

# Main application logic
if not st.session_state.setup_complete:

    st.subheader("Personal Information", divider="rainbow")

    # Initialize personal information fields in session state
    if "name" not in st.session_state:
        st.session_state["name"] = ""
    if "experience" not in st.session_state:
        st.session_state["experience"] = ""
    if "skills" not in st.session_state:
        st.session_state["skills"] = ""

    # Input fields for personal information
    st.session_state["name"] = st.text_input(
        label = "Name",
        max_chars = 40,
        value = st.session_state["name"],
        placeholder = "Enter your name"
    )

    # Text area for experience
    st.session_state["experience"] = st.text_area(
        label = "Experience",
        value = st.session_state["experience"],
        height = None,
        max_chars = 200,
        placeholder = "Describe your experience"
    )

    # Text area for skills
    st.session_state["skills"] = st.text_area(
        label = "Skills",
        value = st.session_state["skills"],
        height = None,
        max_chars = 200,
        placeholder = "List your skills"
    )

    st.subheader("Company and Position", divider="rainbow")

    # Initialize company and position fields in session state
    if "level" not in st.session_state:
        st.session_state["level"] = "Junior"
    if "position" not in st.session_state:
        st.session_state["position"] = "Data Scientist"
    if "company" not in st.session_state:
        st.session_state["company"] = "Amazon"

    # Input fields for company and position
    col1, col2 = st.columns(2)
    with col1:
        st.session_state["level"] = st.radio(
            "Choose level",
            key = "visibility",
            options = ["Intern", "Junior", "Mid-level", "Senior", "Lead"],
        )

    with col2:
        st.session_state["position"] = st.selectbox(
            "Choose a position",
            ("Data Scientist", "Data Engineer", "ML Engineer",
             "BI Analyst", "Financial Analyst"
            )
        )

    # Company selection
    st.session_state["company"] = st.selectbox(
        "Choose a company",
        ("Google", "Microsoft", "Apple", "Amazon", "Meta", "365 Company")
    )

    # Display entered company and position information
    st.write(f"**Your information**: {st.session_state['level']} {st.session_state['position']} "
             f"at {st.session_state['company']}")

    # Button to complete setup
    if st.button("Start Interview", on_click=complete_setup):
        st.write("Setup complete! Starting interview...")

# Chat interface after setup is complete, but not yet showing feedback nor completed chat
if (st.session_state.setup_complete and not st.session_state.feedback_shown
        and not st.session_state.chat_complete):
    st.info(
        """
        Start by introducing yourself.
        """,
        icon="💡"
    )

    # Initialize OpenAI client
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"

    # Check if messages are empty and initialize with system prompt
    if not st.session_state.messages:
        st.session_state.messages = [
            {"role": "system",
            "content":
            f"You are an HR executive who is interviewing applicant {st.session_state['name']} "
            f"with {st.session_state['experience']} experience"
            f"and {st.session_state['skills']} skills"
            f"for the position {st.session_state['level']} {st.session_state['position']}"
            f"at {st.session_state['company']}."
            }
        ]

    # Display chat messages from session state
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Accept user input and generate assistant response if messages under limit of 5
    if st.session_state.user_message_count < 5:
        if prompt := st.chat_input("Your answer.", max_chars=1000):
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            if st.session_state.user_message_count < 4:
                with st.chat_message("assistant"):
                    stream = client.chat.completions.create(
                        model=st.session_state["openai_model"],
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        stream=True,
                    )
                    response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})

            st.session_state.user_message_count += 1

    # Check if interview is complete (5 user messages sent)
    if st.session_state.user_message_count >= 5:
        st.session_state.chat_complete = True
        # Auto-save conversation when interview is complete (before feedback)
        try:
            # Convert entire session state to dictionary for saving
            conv_state_data = dict(st.session_state)
            saved_filepath = save_conversation(conv_state_data)
            st.success("💾 Conversation auto-saved!")
        except (OSError, IOError) as e:
            # Show warning but don't stop the app if save fails
            st.warning(f"Could not auto-save: {e}")

# Show feedback button if chat is complete and feedback not yet shown
if st.session_state.chat_complete and not st.session_state.feedback_shown:
    if st.button("Get feedback", on_click=show_feedback):
        st.write("Fetching feedback...")

# Display feedback form and generate feedback using OpenAI API
if st.session_state.feedback_shown:
    st.subheader("Feedback", divider="rainbow")

    # Compile conversation history
    conversation_history: str = "\n".join(f"{msg['role']}: {msg['content']}"
                                    for msg in st.session_state.messages)

    # Initialize OpenAI client for feedback
    feedback_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # Generate feedback completion
    feedback_completion = feedback_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content":
                    """You are a helpful tool that provides feedback on interview performance.
                    Before the feedback, give a score from 1 to 10 (10 being the best).
                    Follow this format:
                    Overall Score: //Your score
                    Feedback: //Your feedback here
                    Give only your feedback without additional questions."""
            },
            {
                "role": "user",
                "content":
                    f"""This is the interview you need to evaluate.
                    Keep in mind that you are only a tool and shouldn't engage in conversation:
                    {conversation_history}."""
            },
        ],
    )

    # Display the AI-generated feedback
    feedback_text = feedback_completion.choices[0].message.content
    st.write(feedback_text)

    # Save feedback to session state and persist to file
    if "feedback_text" not in st.session_state:
        # Store feedback in session state
        st.session_state.feedback_text = feedback_text
        # Save complete conversation with feedback included
        try:
            conv_final_data = dict(st.session_state)
            final_filepath = save_conversation(conv_final_data)
            st.info("💾 Conversation with feedback saved!")
        except (OSError, IOError) as e:
            st.warning(f"Could not save: {e}")

    # Button to restart the interview
    if st.button("Restart Interview", type="primary"):
        streamlit_js_eval(js_expressions="parent.window.location.reload()")
