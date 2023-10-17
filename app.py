import streamlit as st
import time
from google.oauth2 import service_account
import gspread
from helpers import get_id, empty, save_data, generate_response
from datetime import datetime
import os 

def app() -> None:

    st.set_page_config(
        page_title="Chatbot-Group8",
        page_icon="🧊",
        layout="wide",
        menu_items={"About": "This an experiment app for UU students."})

    st.sidebar.title("Restaurants Recommendations Chatbot")
    st.sidebar.image('chatbot_image.jpeg', width=200)
    st.sidebar.write("Before running the experimet, make sure to read and agree to the informed consent. "
                     "Please fill in the evaluation afterword")
    with st.sidebar.expander('Informed Consent'):
        st.markdown("Before we begin, it's important to know that all data that we collect will be "
                    "anonymous and confidential, and you will not be identifiable in any report, thesis or "
                    "publication which arises from this study. If the dataset will be published as part of scientific "
                    "communications this will be done in an anonymized fashion. We will kindly ask your permission to "
                    "use your data for research purposes. You are free to decline this request, of course, but you can't "
                    "finish the experiment. ")
        st.checkbox("**By checking this checkbox, I confirm that:**")

        st.markdown(" - I have read and understood the information provided to me for this study")
        st.markdown(" - I understand that my participation is voluntary and that I am free to withdraw at any time,"
                    " without giving a reason,"
                    " without my medical care or legal rights being affected")
        st.markdown(" - I understand that the research data will be archived in a completely anonymous way in an "
                    "online database and/or data repository and/or published as supplementary material to a scientific"
                    " article and may be accessed by other researchers as well as the general public")
        st.markdown(" -I understand that the anonymized research data can be used in future projects on similar "
                    "or different topics to this study and potential results can be published in other scientific"
                    " publications. At all times, my personal data will be kept anonymized in accordance with data "
                    "protection guidelines")

    placeholder = st.empty()
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"
        ],
    )
    client = gspread.authorize(credentials)
    sheet_id = '1Xad8Afp0sRP98zARuHqPHdDCTLdnyTaB_KxfKOnGtpc'
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    sheet = client.open_by_url(csv_url).sheet1
    last_recored = sheet.get_all_records()[-1]
    periv_mode = last_recored.get('mode')
    if periv_mode == 'human': mode = 'not human'
    else :mode ='human'

    now = datetime.now()
    with st.sidebar:
        add_radio = st.checkbox("**Ready to fill in the evaluation?**", value=False)
    if not add_radio:
        st.title('Chat area')

        with st.expander("Instructions"):
            st.write('''This is a restaurants recommendations chatbot. For this experiment,
                     we kindly ask you the following instructions:
                     **Choose 3 of the following cases and test with the chatbot**''')
            st.markdown("- Case 1: Italian cheap south No restaurant")
            st.markdown("- Case 2: French east moderate Change preferences")
            st.markdown("- Case 3: Find a recommendation that fits your own preferences.")
            st.markdown("- Case 4: Find a restaurant that is romantic, but cheap.")

            st.markdown('''
            <style>
            [data-testid="stMarkdownContainer"] ul{
                padding-left:40px;
            }
            </style>
            ''', unsafe_allow_html=True)
            # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
         if "REQUEST_METHOD" in os.environ and os.environ["REQUEST_METHOD"] == "GET":
            # Clear the chat history on page refresh
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        # Accept user input
        if prompt := st.chat_input("What is up?"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                assistant_response = generate_response(prompt, mode)
                print(assistant_response)
                # Simulate stream of response with milliseconds delay
                for chunk in assistant_response.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    if mode == 'human':
                        # Add a blinking cursor to simulate typing
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
    if add_radio:
        empty(placeholder)
        # st.title("Informed Consent")


        # with st.expander(" "):
        #
        # st.write("-------")
        st.header('Evaluation form')
        st.markdown("We kindly ask you to fill in the following questions **after** you did the experiment."
                    "\n Make sure to click on the submit button, otherwise none of the data would be saved.")
        # Survey questions
        age = st.number_input("What is your age?", min_value=18)

        fun_rating = st.slider("On a scale from 1 to 5, how would you rate the **fun** you had during this conversation?"
                               "\n *A score of 1 would be a very unpleasant experience (offensive, boring or annoying),"
                               "a score of 5 would be a great experience (very helpful, funny or interesting)*",
                               1, 5)
        trust_rating = st.slider("On a scale from 1 to 5, how much do you **trust** the responses from the system? "
                               "*A score of 1 would be not trustworthy at all (wrong/no recommendation, "
                               "preferences not taken into account, feeling of distrust) "
                               "and a score of 5 would be that you are fully confident that the right recommendation has been given*",
                               1, 5)
        chatbot_enjoy_rating = st.slider("On a scale from 1 to 5, how much do you usually enjoy talking to chatbots?"
                                         "*A score of 1 would mean that you usually greatly dislike talking to chatbots,"
                                         "and a score of 5 would mean that they enjoy talking to chatbots very much.*",
                                         1, 5)
        recommendation_received = st.radio("Did you receive a recommendation for the preferences you entered?",
                                           ("Yes", "No"))
        received_unexpected_result = st.radio("Did you receive an unexpected result from the system?", ("Yes", "No"),)

        # If the answer is "Yes," ask for additional information
        if received_unexpected_result == "Yes":
            additional_info = st.text_area("If yes, please provide details:", max_chars=200, height=30)
        else:
            additional_info = ""
        st.write("-----")
        sub_button = st.button("Submit")
        if sub_button:
            database_df = save_data(str(get_id()), now, st.session_state.messages, [age, fun_rating, trust_rating, chatbot_enjoy_rating,
                                                                    recommendation_received, received_unexpected_result,
                                                                    additional_info, mode])
            database_df = database_df.astype(str)
            sheet.insert_rows(database_df.values.tolist(), len(sheet.get_all_records()) + 2)
            st.markdown("Your answers are saved, thank you!")


app()
