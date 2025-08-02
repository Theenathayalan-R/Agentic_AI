import os
import streamlit as st
from dotenv import load_dotenv
# Import the new ChatGoogleGenerativeAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage

# 1. Load environment variables
load_dotenv()

# Change the environment variable name check
if "GOOGLE_API_KEY" not in os.environ:
    st.error("Google API key not found. Please set the GOOGLE_API_KEY environment variable.")
    st.stop()

# 2. Set up the Streamlit UI
st.title("Simple AI Agent Chatbot (Powered by Sanjay and Sathyadev)")
st.write("I am a helpful assistant that translates English to French using the Gemini API.")

# 3. Initialize chat history in Streamlit's session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello! How can I help you?"),
    ]

# 4. Create the LangChain components
# Use ChatGoogleGenerativeAI instead of ChatOpenAI
# You might want to try "gemini-pro" or "gemini-1.5-flash"
# Check Google AI Studio for available models and their capabilities.
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0) # You can adjust temperature

# 5. Define the Prompt (This is the agent's goal and instruction)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant Math problem Solver."),
    ("user", "{text}")
])
chain = prompt | llm | StrOutputParser()

# 6. Display chat messages from history
for message in st.session_state.chat_history:
    with st.chat_message(message.type):
        st.write(message.content)

# 7. Handle user input
user_query = st.chat_input("Enter your Math text here...")

if user_query is not None and user_query != "":
    # Add user message to chat history
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    # Display the user message
    with st.chat_message("user"):
        st.write(user_query)

    # Invoke the chain to get the AI response
    with st.chat_message("assistant"):
        try:
            # The chain.invoke method calls the LLM with the user's input
            response = chain.invoke({"text": user_query})
            st.write(response)
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.write("Please check your API key and model access.")

    # Add AI response to chat history
    if 'response' in locals(): # Only add if response was successful
        st.session_state.chat_history.append(AIMessage(content=response))

