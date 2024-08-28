# Program for automating configuration management
import configparser,json,sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)

# Create a ConfigParser object
config = configparser.ConfigParser()

try:
    # Read the configuration file
    files_read = config.read('C:\\Users\\Admin\\Desktop\\Vired\\Assignment\\Application.ini')

    if not files_read:
        raise FileNotFoundError("Configuration file not found.")

    # Accessing values
    try:
        host = config['Network']['host']

        # Convert section to dictionary
        network_host = dict(config.items('Network'))

        # Convert the dictionary to a JSON string
        config_json = json.dumps(network_host)
    
    except KeyError as e:
        print(f"Missing key in configuration file: {e}")
        
except FileNotFoundError as e:
    print(e)

except configparser.Error as e:
    print(f"Failed to read the configuration file: {e}")


# Function to save JSON data to the database
def save_to_database(config_json):
    try:
        # Connect to the SQLite database (or create it if it doesn't exist)
        conn = sqlite3.connect('configurations.db')
        cursor = conn.cursor()

        # Create a table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Configurations (
                id INTEGER PRIMARY KEY,
                config_data TEXT NOT NULL
            )
        ''')

        # Insert JSON data into the table
        cursor.execute('''
            INSERT INTO Configurations (config_data)
            VALUES (?)
        ''', (config_json,))

        # Commit the transaction
        conn.commit()

        print("Configuration data saved to the database successfully.")

    except sqlite3.Error as e:
        print(f"An error occurred while interacting with the database: {e}")
    
    finally:
        # Close the database connection
        conn.close()

# Save the JSON data to the database
if 'config_json' in locals():
    save_to_database(config_json)
else:
    print("No configuration data available to save.")


# Function to fetch JSON data from the database
def fetch_from_database():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('configurations.db')
        cursor = conn.cursor()

        # Execute a query to fetch the configuration data
        cursor.execute('SELECT config_data FROM Configurations ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()

        # If data is found, return it; otherwise, return None
        if row:
            return row[0]
        else:
            return None

    except sqlite3.Error as e:
        print(f"An error occurred while interacting with the database: {e}")
        return None
    
    finally:
        # Close the database connection
        conn.close()

# Route to fetch the configuration data
@app.route('/config', methods=['GET'])
def get_config():

    # Fetch the configuration data from the database
    config_data = fetch_from_database()

    # If data is found, parse it to a dictionary and return it as JSON
    if config_data:
        try:
            # Convert the JSON string back to a Python dictionary
            config_dict = json.loads(config_data)
            # Converts the dictionary back to JSON and returns it in the response with a 200 status code if successful.
            return jsonify({"config_data": config_dict}), 200
        
        except json.JSONDecodeError as e:
            return jsonify({"error": "Failed to decode JSON data"}), 500
    else:
        return jsonify({"error": "No configuration data found"}), 404


if __name__ == '__main__':
    app.run(debug=True)