from flask import Flask, render_template, request, jsonify
from Worker import Worker
import os
import time
import random
import json
from urllib.parse import unquote
os.environ['TZ'] = 'Europe/Madrid'
time.tzset()

app = Flask(__name__)

# Configuration for file uploads
app.config['UPLOAD_FOLDER'] = 'uploads'  # Directory where files will be saved
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max size of file (16MB)
SECRET_PASSWORD = 'fqacdp0ov0w1bce6w274sdhczys9iq'  # Define a secret password for validation

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/madridtemp')
def index():
    worker = Worker()
    last_temperature, formatted_datetime, dates, date_hour_temp_map, max_temp, min_temp, pred5d_df, current_model = worker.GetData()

    # Modify 'day' column to display as "Weekday DayNumber"
    pred5d_df['day'] = pred5d_df['day'].dt.strftime('%A %d')
    pred5d_df['mean_temp'] = pred5d_df['mean_temp'].round(0).astype(int)
    pred5d_df['min_temp'] = pred5d_df['min_temp'].round(0).astype(int)
    pred5d_df['max_temp'] = pred5d_df['max_temp'].round(0).astype(int)

    # Determine max number of hours for column headers
    max_hours = max(len(date_hour_temp_map[date]['hours']) for date in dates)

    # Prepare hours_map and temperatures_map
    hours_map = {date: date_hour_temp_map[date]['hours'] for date in dates}
    temperatures_map = {date: date_hour_temp_map[date]['temperatures'] for date in dates}

    # Convert pred5d_df to a list of dictionaries
    forecast_5d = pred5d_df.to_dict(orient='records')

    return render_template(
        'index.html',
        last_temperature=last_temperature,
        formatted_datetime=formatted_datetime,
        dates=dates,
        hours_map=hours_map,
        temperatures_map=temperatures_map,
        max_hours=max_hours,
        max=max_temp,
        min=min_temp,
        forecast_5d=forecast_5d,
        current_model=current_model
    )

@app.route('/uploadfiles', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        # Get the password from the form
        password = request.form.get('password')
        
        # Verify if the password is correct
        if password != SECRET_PASSWORD:
            return 'Invalid password, files not uploaded.', 403

        # Check if files were uploaded
        if 'file1' not in request.files or 'file2' not in request.files:
            return 'No file part', 400

        file1 = request.files['file1']
        file2 = request.files['file2']

        # Check if both files are selected
        if file1.filename == '' or file2.filename == '':
            return 'No selected files', 400
        
        # Save the files to the configured directory
        file1.save(os.path.join('data', 'predictions_data.csv'))
        file2.save(os.path.join('data', 'predictions5days_data.csv'))

        return 'Files successfully uploaded!', 200

    return '''
    <!doctype html>
    <title>Upload Files</title>
    <h1>Upload two files</h1>
    <form method=post enctype=multipart/form-data>
      Password: <input type="password" name="password"><br><br>
      File 1: <input type=file name=file1><br><br>
      File 2: <input type=file name=file2><br><br>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploadsentiment', methods=['POST'])
def uploadsentiment():
    if request.method == 'POST':
        # Get the password from the form
        password = request.form.get('password')
        
        # Verify if the password is correct
        if password != SECRET_PASSWORD:
            return 'Invalid password, files not uploaded.', 403

        # Get the filename and output from the form data
        filename = request.form.get('filename')
        output = request.form.get('output')

        if not filename or not output:
            return 'Missing filename or output data.', 400

        # Save the data to a file
        with open(f'nlp_data/{filename}_eval.txt', 'w') as f:
            f.write(output)

        return 'Files successfully uploaded!', 200
        
# Path to the folder containing JSON files
DATA_FOLDER = 'nlp_data'

# Route to serve the main voice analysis page
@app.route('/voiceanalysis')
def sentiment_analysis():
    return render_template('voiceanalysis.html')

# Route that receives the ID and returns the corresponding data from the JSON file
@app.route('/get-analysis-data', methods=['GET'])
def get_analysis_data():
    # Get the ID from the AJAX request (query parameter)
    analysis_id = request.args.get('id')

    if not analysis_id:
        return jsonify({'error': 'No ID provided'}), 400

    # Construct the file path using the ID
    file_path = os.path.join(DATA_FOLDER, f'{analysis_id}.json')

    # Check if the file exists
    if not os.path.exists(file_path):
        # If the file doesn't exist, return a JSON with status "not yet created"
        return jsonify({'status': 'not yet created'})

    # Load the JSON data from the file
    with open(file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    return jsonify(data)

@app.route('/updatesentiment', methods=['GET'])
def update_sentiment():
    password = request.args.get('password')
    
    if password != SECRET_PASSWORD:
        return 'Invalid password, files not uploaded.', 403
    
    analysis_id = request.args.get('id')
    json_data_str = request.args.get('json')
    
    if not analysis_id or not json_data_str:
        return jsonify({'error': 'ID or JSON data not provided'}), 400

    # URL decode the JSON string
    json_data_str = unquote(json_data_str)

    try:
        json_data_dict = json.loads(json_data_str)
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON data'}), 400

    file_path = os.path.join(DATA_FOLDER, f'{analysis_id}.json')

    # Save the data to the corresponding JSON file
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_data_dict, json_file, ensure_ascii=False, indent=4)

    return jsonify({'status': 'success', 'message': f'Data saved for ID {analysis_id}'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
