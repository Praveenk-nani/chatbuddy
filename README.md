
# ChatBUDDY: A Data Querying Tool

## Description
**ChatBUDDY** is an intuitive data querying tool that allows users to upload CSV/Excel files or connect to a Google Sheet. It leverages conversational AI to help users interact with their data and extract valuable insights. Users can input queries with placeholders like `{entity}` to dynamically retrieve answers from their dataset.

## Features
- **CSV/Excel File Upload:** Upload your local CSV or Excel files for querying.
- **Google Sheets Integration:** Connect directly to a Google Sheet using its URL.
- **Conversational AI Interface:** Query your dataset using natural language queries.
- **Dynamic Querying:** Use placeholders like `{entity}` to query specific data in a column.
- **Download Responses:** Download the queried data in CSV format.
- **Query History:** View and track your past queries.

## Installation


### Video Link (  https://drive.google.com/file/d/1aZlHk0qnnz0yPrVTalSNRfev5SqSA8qx/view?usp=sharing  )

### Step 1: Clone the Repository
Clone the repository to your local machine:
```bash
git clone https://github.com/yourusername/chatbuddy.git
```

### Step 2: Install Dependencies
Navigate to the project directory and install all required packages:
```bash
cd chatbuddy
pip install -r requirements.txt
```

### Step 3: Obtain API Keys and File Path
You will need the following credentials for the application to work:
1. **Groq API Key**: [Get your Groq API key here](https://groq.com).
2. **PandasAI API Key**: [Get your PandasAI API key here](https://pandas.ai).
3. **Google Sheets JSON Credential File**: [Create a Google service account and download the credentials file](https://cloud.google.com/docs/authentication/getting-started).

### Step 4: Configure API Keys and File Path
In the script, assign your keys and file path to the following variables:
```python
pandasai_api_key = "Your pandasai API key"
groq_api_key = "Your groq API key"
jsonFilePath = "Path to your Google Sheets JSON file"
```

### Step 5: Run the Application
To run the application, use the following command:
```bash
streamlit run your_script.py
```

## Usage Guide

After running the application, you will be redirected to the dashboard with the following options:

### 1. Choose Your Data Source
- **Upload CSV or Excel File:** Click the option to upload a CSV or Excel file from your local machine.
- **Connect Google Sheet:** Enter the URL of your Google Sheet to load data directly from Google Sheets.

### 2. View Uploaded Data
Once the data is uploaded, you will see a preview of your dataset in a dropdown.

### 3. Select the Main Column
Select the main column you wish to query. The selected column will be used for dynamic queries.

### 4. Enter Your Query
There are two types of queries you can input:
- **Simple Query**: No need to select a main column. For example:
  - "Get me the age of Praveen"
  - "Get me the email address of John"
  
- **Dynamic Query**: The main column is essential. Use placeholders like `{entity}` for the dynamic part of your query. For example, if you selected "Name" as the main column, you can enter:
  - "Get me the age and location of {entity}"

**Important**: Do not replace `{entity}` with the actual values. Just keep `{entity}` as is in your dynamic query.

### 5. Get Responses
Once the query is entered, the AI will process it and provide the results, which will be displayed in a table.

### 6. Download the Results
You can download the extracted data as a CSV file using the "Download CSV" button.

### 7. View Query History
The query history section displays all the past queries and their results.

## Notes
- If the AI fails to process a query, it will fallback to another model for better accuracy.
- Ensure that your Google Sheets credentials are set up correctly before using the Google Sheets integration.
