import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
from langchain_groq import ChatGroq
from langchain_experimental.agents import create_pandas_dataframe_agent
from pandasai import SmartDataframe
import re

pandasai_api_key = "Your api key"
groq_api_key = "Your api key"
jsonFilePath = "Your google sheet json file path"

os.environ['PANDASAI_API_KEY'] = pandasai_api_key
os.environ['GROQ_API_KEY'] = groq_api_key

if "uploaded_data" not in st.session_state:
    st.session_state["uploaded_data"] = None
if "query_history" not in st.session_state:
    st.session_state["query_history"] = []

st.title("ChatBUDDY")

st.write("Choose an option to upload data:")

action = st.radio(
    "",
    options=["Upload CSV or Excel File", "Connect Google Sheet"],
    index=0
)

def clean_response(response):
    if not isinstance(response, str):
        response = str(response)
    response = re.sub(r'^\s*[\w\s]+:\s*', '', response, flags=re.MULTILINE)
    unwanted_phrases = ["Header:", "Context:", "Summary:"]
    for phrase in unwanted_phrases:
        response = response.replace(phrase, "")
    return response.strip()

def extract_answer(response):
    if not isinstance(response, str):
        response = str(response)
    match = re.search(r"The answer is[:\-]?\s*(.*)", response, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    else:
        return response.strip()

def handle_csv_upload():
    uploaded_file = st.file_uploader("Upload your CSV or Excel file:", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            if df.empty:
                st.warning("The uploaded file is empty. Please upload a valid file.")
                return
            with st.expander("Preview CSV File"):
                st.dataframe(df.head())
            st.session_state["uploaded_data"] = df
            return df
        except pd.errors.EmptyDataError:
            st.error("The uploaded file is empty or not a valid CSV/Excel.")
        except Exception as e:
            st.error(f"An error occurred while reading the file: {e}")
    else:
        st.info("No file uploaded yet.")

def handle_google_sheet():
    google_sheet_url = st.text_input("Enter Google Sheet URL:")
    if google_sheet_url:
        try:
            scope = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.file",
                "https://www.googleapis.com/auth/drive",
            ]
            creds = Credentials.from_service_account_file(jsonFilePath, scopes=scope)
            client = gspread.authorize(creds)
            sheet = client.open_by_url(google_sheet_url)
            worksheet = sheet.get_worksheet(0)
            data = worksheet.get_all_records()
            if not data:
                st.warning("The Google Sheet is empty.")
                return
            df = pd.DataFrame(data)
            with st.expander("Preview Google Sheet Data"):
                st.dataframe(df.head())
            st.session_state["uploaded_data"] = df
            return df
        except gspread.exceptions.SpreadsheetNotFound:
            st.error("The provided Google Sheet URL is invalid or inaccessible.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

main_df = None
if action == "Upload CSV or Excel File":
    main_df = handle_csv_upload()
else:
    main_df = handle_google_sheet()

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name='mixtral-8x7b-32768'
)

pandas_lake = SmartDataframe(main_df, config={"LLM": llm, "conversational": True, "verbose": True}) if main_df is not None else None

if main_df is not None:
    selected_column = st.selectbox("Select the main column:", main_df.columns)

    st.write("Enter your query template (use {entity} as a placeholder):")
    query = st.text_area("Write your query here:", "Get me the email address of {entity}.")

    submit_btn = st.button("Submit")
    responses = []
    response_df = None

    if submit_btn:
        if query:
            if "{entity}" in query:
                for entity in main_df[selected_column]:
                    prompt = query.replace("{entity}", entity)
                    try:
                        response = pandas_lake.chat(prompt)
                        if "Unfortunately, I was not able to answer your question, because of the following error:" in response or response.strip() == "":
                            llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")
                            agent = create_pandas_dataframe_agent(
                                llm,
                                main_df,
                                verbose=True,
                                allow_dangerous_code=True,
                                max_iterations=10,
                                max_execution_time=30
                            )
                            response = agent.invoke({'input': prompt})
                            response = response['output']
                        answer = extract_answer(response)
                        responses.append({"Entity": entity, "Answer": answer})
                        st.session_state["query_history"].append({"Query": prompt, "Answer": answer})
                    except Exception as e:
                        responses.append({"Entity": entity, "Answer": f"Error: {str(e)}"})
            else:
                try:
                    response = pandas_lake.chat(query)
                    if "Unfortunately, I was not able to answer your question, because of the following error:" in response or response.strip() == "":
                        llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")
                        agent = create_pandas_dataframe_agent(
                            llm,
                            main_df,
                            verbose=True,
                            allow_dangerous_code=True,
                            max_iterations=10,
                            max_execution_time=30
                        )
                        response = agent.invoke({'input': query})
                        response = response['output']
                    answer = extract_answer(response)
                    responses.append({"Entity": "General Query", "Answer": answer})
                    st.session_state["query_history"].append({"Query": query, "Answer": answer})
                except Exception as e:
                    responses.append({"Entity": "General Query", "Answer": f"Error: {str(e)}"})
            if responses:
                try:
                    response_df = pd.DataFrame(responses)
                except Exception as e:
                    st.error(f"Could not create DataFrame: {e}")
        else:
            st.error("Please enter a query.")

    if response_df is not None:
        st.write("Response for your query is:")
        st.dataframe(response_df)
        st.download_button(
            label="Download CSV",
            data=response_df.to_csv(index=False),
            file_name="responses.csv",
            mime="text/csv"
        )
    else:
        st.warning("No valid responses to display.")
else:
    st.error("No data available. Please upload a valid file or connect to a Google Sheet.")

if st.session_state["query_history"]:
    st.write("Previous Queries (History):")
    for record in st.session_state["query_history"]:
        st.write(f"**Query:** {record['Query']}")
        st.write(f"**Answer:** {record['Answer']}")
        st.write("---")
