from flask import Flask, request
from datetime import datetime
from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceExistsError
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def initialize_table():
    try:
        # Log connection string (remove in production)
        connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
        logging.info(f"Connection string exists: {bool(connection_string)}")
        
        if not connection_string:
            logging.error("No connection string found")
            return None

        table_name = "persistencetest"
        logging.info("Creating table service client...")
        
        # Create table client
        table_service = TableServiceClient.from_connection_string(connection_string)
        logging.info("Table service client created")
        
        # Create table
        try:
            table_client = table_service.create_table(table_name)
            logging.info(f"Table {table_name} created successfully")
        except ResourceExistsError:
            table_client = table_service.get_table_client(table_name)
            logging.info(f"Using existing table {table_name}")
        except Exception as e:
            logging.error(f"Error creating/getting table: {str(e)}")
            raise
            
        return table_client
    except Exception as e:
        logging.error(f"Error in initialize_table: {str(e)}")
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
            logging.error("Table client is None")
            return "Error: Table not initialized. Check logs for details."

        data = request.form.get('data')
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        
        entity = {
            "PartitionKey": "testdata",
            "RowKey": timestamp,
            "data": data
        }
        table_client.create_entity(entity=entity)
        logging.info(f"Data added successfully: {data}")
        
        return f"""
        <h2>Data Added Successfully</h2>
        <p>Added: {data} at {timestamp}</p>
        <a href="/">Add More</a> | <a href="/view">View All</a>
        """
    except Exception as e:
        logging.error(f"Error adding data: {str(e)}")
        return f"Error adding data: {str(e)}"

@app.route('/view')
def view_data():
    try:
        if not table_client:
            logging.error("Table client is None")
            return "Error: Table not initialized. Check logs for details."

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
        logging.error(f"Error viewing data: {str(e)}")
        return f"Error viewing data: {str(e)}"

if __name__ == '__main__':
    app.run()
