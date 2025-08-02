# Simple AI Agent Chatbot (Powered by Gemini)

This is a Streamlit web app that uses Google's Gemini API (via LangChain) to translate English text to French. The app provides a conversational interface and maintains chat history for a smooth user experience.

## Features

- Translate English to French using Gemini (Google Generative AI)
- Interactive chat interface with history
- Powered by [LangChain](https://python.langchain.com/) and [Streamlit](https://streamlit.io/)
- Easy setup with `.env` for API key management

## Setup

1. **Clone the repository or copy the files**

2. **Install dependencies**

```sh
pip install streamlit python-dotenv langchain langchain-google-genai
```

3. **Set up your Google API key**

Create a `.env` file in the project directory:

```
GOOGLE_API_KEY="your_google_api_key_here"
```

You can find your API key in [Google AI Studio](https://aistudio.google.com/).

4. **Run the app**

```sh
streamlit run app.py
```

## Usage

- Enter English text in the chat input box.
- The assistant will reply with the French translation.
- Chat history is preserved during your session.

## File Structure

- `app.py` — Main Streamlit application
- `.env` — Stores your Google API key (not included in version control)

## Troubleshooting

- If you see an error about the API key, make sure `.env` exists and contains a valid `GOOGLE_API_KEY`.
- If you encounter issues with the Gemini API, check your quota and model access in Google AI Studio.

## License

MIT License

---

**Powered by Gemini, LangChain, and