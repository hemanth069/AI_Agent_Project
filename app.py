import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import serpapi

# Title for the web app
st.title("AI Agent Dashboard")
st.write("This tool helps you extract specific information based on custom queries from a dataset of entities.")

# Choice of file type
file_type = st.radio("Select file type to upload:", ["CSV", "Google Sheet"])

# Initialize DataFrame to hold data
df = None

# Handle CSV file upload
if file_type == "CSV":
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    
    if uploaded_file is not None:
        # Load the CSV file and display column options
        df = pd.read_csv(uploaded_file)
        
        # Display the first few rows of columns only for structure preview
        st.write("Preview of columns:")
        st.write(df.head(3))  # Display first 3 rows for column overview

        # Display dropdown to select columns for entities
        column_names = df.columns.tolist()
        selected_column = st.selectbox("Select the required column with entities", column_names)
        st.write(f"You selected: {selected_column}")

# Handle Google Sheets input
elif file_type == "Google Sheet":
    google_sheet_url = st.text_input("Enter the Google Sheets URL")
    
    if google_sheet_url:
        # Define Google Sheets API scope
        scope = ["https://spreadsheets.google.com/feeds", 
                 "https://www.googleapis.com/auth/spreadsheets",
                 "https://www.googleapis.com/auth/drive.file", 
                 "https://www.googleapis.com/auth/drive"]
        
        # Authorize and read the Google Sheet
        credentials = Credentials.from_service_account_file(
            "give the address of json file", 
            scopes=scope
        )
        client = gspread.authorize(credentials)
        
        try:
            # Open the Google Sheet by URL and fetch the first worksheet
            sheet = client.open_by_url(google_sheet_url)
            worksheet = sheet.get_worksheet(0)
            
            # Load the sheet data into a DataFrame
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            
            # Display the first few rows of columns only for structure preview
            st.write("Preview of columns:")
            st.write(df.head(3))  # Display first 3 rows for column overview

            # Display dropdown to select columns for entities
            column_names = df.columns.tolist()
            selected_column = st.selectbox("Select the required column with entities", column_names)
            st.write(f"You selected: {selected_column}")
        except Exception as e:
            st.write("Error loading Google Sheet:", e)

# Placeholder for custom query
st.write("Input your custom query template:")
custom_query = st.text_input("Query Template (e.g., 'Get me the email of the company')", 
                             placeholder="Enter query here")

# List to store search results
search_results = []

# Define the perform_search function using serpapi.search
def perform_search(query):
    try:
        # SerpApi API key
        api_key = "give your serp api key"
        
        # Set up the query parameters for SerpApi
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
        }
        
        # Perform the search using serpapi.search
        results = serpapi.search(params)
        
        # Extract the first result's URL and snippet if available
        if "organic_results" in results and results["organic_results"]:
            first_result = results["organic_results"][0]
            url = first_result.get("link", "")
            snippet = first_result.get("snippet", "")
            return {'url': url, 'snippet': snippet}
        else:
            st.write(f"No results found for query: {query}")
            return None
    except Exception as e:
        st.write("Error during search:", e)
        return None

# Trigger search on button click
if st.button("Perform Search"):
    if df is not None and selected_column and custom_query:
        for entity in df[selected_column]:
            # Construct the search query
            query = f"{entity} {custom_query}"
            
            # Perform the search and append results
            result = perform_search(query)
            if result:
                search_results.append(result)
        
        # Display the search results
        st.write("Search Results:")
        for result in search_results:
            st.write(f"URL: {result['url']}")
            st.write(f"Snippet: {result['snippet']}")
            st.write("---")

st.write("Project setup complete. Further steps will involve web search and data extraction based on the selected entities.")
