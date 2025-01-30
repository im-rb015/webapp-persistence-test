from flask import Flask, request
from datetime import datetime
from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceExistsError
import os

app = Flask(__name__)

def initialize_table():
    try:
        # Get connection string from app settings
        connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']
        table_name = "persistencetest"

        # Create table client
        table_service = TableServiceClient.from_connection_string(connection_string)
        
        # Create table if it doesn't exist
        try:
            table_client = table_service.create_table(table_name)
            print(f"Table {table_name} created successfully")
        except ResourceExistsError:
            table_client = table_service.get_table_client(table_name)
            print(f"Table {table_name} already exists")
        
        return table_client
    except Exception as e:
        print(f"Error initializing table: {str(e)}")
        return None

# Initialize table client
table_client = initialize_table()

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
        if not table_client:
            return "Error: Table not initialized"

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
        return f"Error adding data: {str(e)}"

@app.route('/view')
def view_data():
    try:
        if not table_client:
            return "Error: Table not initialized"

        entities = table_client.query_entities(query_filter="PartitionKey eq 'testdata'")
        data_items = [f"{e['RowKey']}: {e['data']}" for e in entities]
        
        if data_items:
            data_list = "<br>".join(data_items)
            return f"""
            <h2>Stored Data</h2>
            {data_list}
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
        return f"Error viewing data: {str(e)}"

if __name__ == '__main__':
    app.run()
