from flask import Flask, request
from datetime import datetime
import ssl
app = Flask(__name__)

ssl._create_default_https_context = ssl._create_unverified_context

# This list stores data in memory (will be cleared when app restarts)
data_store = []

@app.route('/')
def home():
    # Creates a simple web form with:
    # 1. Text input field
    # 2. Submit button
    # 3. Link to view data
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
    # When form is submitted:
    # 1. Gets the entered data
    # 2. Adds timestamp
    # 3. Stores in data_store list
    data = request.form.get('data')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_store.append(f"{timestamp}: {data}")
    return f"""
    <h2>Data Added</h2>
    <p>Added: {data} at {timestamp}</p>
    <a href="/">Add More</a> | <a href="/view">View All</a>
    """

@app.route('/view')
def view_data():
    # Shows all stored data
    # If data remains after restart = Persistent
    # If data disappears after restart = Not Persistent
    if data_store:
        data_list = "<br>".join(data_store)
        return f"""
        <h2>Stored Data</h2>
        {data_list}
        <br><br>
        <p>If this data remains after restart, it's persistent!</p>
        <br>
        <a href="/">Back to Home</a>
        """
    else:
        return """
        <h2>No Data Found</h2>
        <p>Either no data added or data was lost (not persistent)</p>
        <br>
        <a href="/">Back to Home</a>
        """
