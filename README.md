# AI Interview Chatbot 🤖💼

An interactive Streamlit application that simulates job interviews using OpenAI's GPT-4o model. Practice your interview skills with an AI HR executive tailored to your target position and company.

## Features

- 📝 **Personalized Setup**: Enter your name, experience, skills, position level, and target company
- 💬 **AI-Powered Interview**: Engage in realistic interview conversations with GPT-4o
- 📊 **Automated Feedback**: Receive scored feedback (1-10) on your interview performance
- 💾 **Auto-Save**: Conversations automatically saved to JSON files
- 📚 **History Management**: View, load, and delete past interview sessions
- 📥 **Export Options**: Download conversations as TXT or JSON files
- 🔄 **Session Persistence**: Resume previous interviews anytime

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "365 Projects"
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure secrets**
   - Create a `.streamlit` folder if it doesn't exist
   - Create a `secrets.toml` file inside `.streamlit/`
   - Add your OpenAI API key:
     ```toml
     OPENAI_API_KEY = "your-api-key-here"
     ```

## Usage

1. **Run the application**
   ```bash
   streamlit run app.py
   ```

2. **Open in browser**
   - The app will automatically open at `http://localhost:8501`
   - Or manually navigate to the URL shown in the terminal

3. **Complete the interview**
   - Fill in your personal information and target role
   - Click "Start Interview"
   - Respond to 5 interview questions
   - Get feedback on your performance

4. **Manage conversations**
   - View past interviews in the sidebar
   - Load previous sessions
   - Export as TXT or JSON
   - Delete unwanted conversations

## Project Structure

```
365 Projects/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── .streamlit/
│   └── secrets.toml           # API keys (not tracked by git)
├── .vscode/
│   └── settings.json          # VS Code settings
└── saved_conversations/       # Auto-saved interview sessions (not tracked)
```

## Configuration

### Supported Positions
- Data Scientist
- Data Engineer
- ML Engineer
- BI Analyst
- Financial Analyst

### Experience Levels
- Intern
- Junior
- Mid-level
- Senior
- Lead

### Target Companies
- Google
- Microsoft
- Apple
- Amazon
- Meta
- 365 Company

## Dependencies

- `streamlit==1.52.2` - Web application framework
- `openai==2.14.0` - OpenAI API client
- `streamlit-js-eval==0.1.7` - JavaScript evaluation for page reload

## Features in Detail

### Auto-Save
Conversations are automatically saved in two stages:
1. After completing 5 questions (before feedback)
2. After receiving feedback (complete session)

### Export Formats
- **TXT**: Human-readable format with headers and formatted messages
- **JSON**: Complete session state data for programmatic access

### Past Conversations
- Sorted by modification time (newest first)
- Load any previous session to review or continue
- Delete individual conversations
- Shows total count of saved interviews

## Security Notes

⚠️ **Important**: Never commit your `secrets.toml` file to version control. It contains your OpenAI API key.

The `.gitignore` file is configured to exclude:
- API keys and secrets
- Virtual environment
- Saved conversations
- Cache files

## Contributing

Feel free to open issues or submit pull requests for improvements.

## License

MIT License - See LICENSE file for details

## Support

For issues or questions, please open an issue on GitHub.

---

**Note**: This application uses the OpenAI API which incurs costs. Monitor your API usage to avoid unexpected charges.
