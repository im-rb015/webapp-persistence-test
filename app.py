from flask import Flask, request
from datetime import datetime
from azure.data.tables import TableServiceClient
import os

app = Flask(__name__)

# Connect to Azure Storage Table
connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']
table_name = "persistencetest"

# Initialize Table Service
table_service = TableServiceClient.from_connection_string(connection_string)
try:
    table_client = table_service.create_table_if_not_exists(table_name)
except:
    table_client = table_service.get_table_client(table_name)

@app.route('/')
def home():
    return """
    <h1>Web App Persistence Test</h1>
    <form action="/add" method="post">
        <input type="text" name="data" placeholder="Enter test data">
        <input type="submit" value="Add Data">
    </form>
    <br>
    <a href="/view">View Data</a>
    """

@app.route('/add', methods=['POST'])
def add_data():
    try:
        data = request.form.get('data')
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        
        # Store in Azure Table
        entity = {
            "PartitionKey": "testdata",
            "RowKey": timestamp,
            "data": data
        }
        table_client.create_entity(entity=entity)
        
        return f"""
        <h2>Data Added Successfully</h2>
        <p>Added: {data} at {timestamp}</p>
        <a href="/">Add More</a> | <a href="/view">View All</a>
        """
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/view')
def view_data():
    try:
        entities = table_client.query_entities(query_filter="PartitionKey eq 'testdata'")
        data_list = ["<br>".join([f"{e['RowKey']}: {e['data']}" for e in entities])]
        
        if data_list:
            return f"""
            <h2>Stored Data</h2>
            {data_list[0]}
            <br><br>
            <p>This data will persist after restart!</p>
            <br>
            <a href="/">Back to Home</a>
            """
        return """
        <h2>No Data Found</h2>
        <p>No data added yet</p>
        <br>
        <a href="/">Back to Home</a>
        """
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run()
