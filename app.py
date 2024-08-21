import streamlit as st
from streamlit_chat import message
from langchain.memory import ConversationBufferWindowMemory
from preprocessing import extract_text_from_pdf
from together import initialize_together_client

# Streamlit UI
st.subheader("VJ Bot")

# Initialize session state for storing chat history and memory
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if 'buffer_memory' not in st.session_state:
    st.session_state.buffer_memory = ConversationBufferWindowMemory(k=100, return_messages=True)

# PDF file uploader
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    # Extract text from the uploaded PDF
    all_text = extract_text_from_pdf(uploaded_file)

    # Prepare the system content
    data = f'{all_text}'
    system_content = f"You are a helpful AI assistant. You will be given knowledge and need to answer the question strictly based on that document. If any question is asked out of the text, just answer 'idk'. Don't reveal that you are answering based on the document provided while answering the prompt. Here is your data: {data}"

    # Initialize Together client
    together_client = initialize_together_client()

    # Display chat history
    for i, chat in enumerate(st.session_state['chat_history']):
        message(chat['content'], is_user=chat['role'] == 'user', key=f"message_{i}")

    # User input for question
    user_prompt = st.chat_input("Ask me anything...")

    if user_prompt:
        # Add the user's question to chat history and display it
        st.session_state['chat_history'].append({"role": "user", "content": user_prompt})
        message(user_prompt, is_user=True, key=f"user_message_{len(st.session_state['chat_history'])}")

        # Send the question to the model
        response = together_client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000,
            temperature=0.11,
            top_p=1,
            top_k=50,
            repetition_penalty=1,
            stop=[""],
        )

        # Get the response from the model
        assistant_response = response.choices[0].message.content

        if assistant_response.lower() == "idk":
            # If the response is 'idk', generate a new response
            alternative_response = together_client.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant. Answer the given questions."
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                max_tokens=500,
                temperature=0.11,
                top_p=1,
                top_k=50,
                repetition_penalty=1,
                stop=[""],
            )
            text_2 = alternative_response.choices[0].message.content
            custom_message = "IMPORTANT NOTE : This inquiry may be tangentially or entirely unrelated to AiLite, but since you've posed the question, I'm sharing the pertinent information within my cognitive scope."
            assistant_response = f"{custom_message}\n\n{text_2}"

        # Add the assistant's response to chat history and display it
        st.session_state['chat_history'].append({"role": "assistant", "content": assistant_response})
        message(assistant_response, key=f"assistant_message_{len(st.session_state['chat_history'])}")

else:
    st.write("Please upload a PDF file to continue.")
