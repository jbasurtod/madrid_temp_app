# Madrid Temperature App

<img src="https://github.com/jbasurtod/madrid_temp_app/blob/main/img/live_app.png"  />

## Overview

The **Madrid Temperature App** is a Python-based application that retrieves, processes, and displays weather predictions for Madrid. The app is designed to provide users with the latest temperature data, as well as forecasts for the next 24 hours.

## Features

- **Temperature Data Retrieval**: Fetches historical and predicted temperature data from external sources.
- **Data Processing**: Processes the temperature data to calculate important metrics like the maximum and minimum temperatures for the day.
- **Timezone-Aware Comparisons**: Ensures that all datetime operations are handled in the Madrid timezone, providing accurate comparisons and data displays.

## Project Structure

- **app.py**: The main entry point of the application. Handles HTTP requests and responses.
- **Worker.py**: Contains the logic for retrieving and processing temperature data.
- **data/urls.txt**: A file that stores the URLs from which temperature data is fetched. This file is not tracked by Git.
- **README.md**: This file, providing an overview of the project.
- **.gitignore**: Ensures that sensitive or irrelevant files like `data/urls.txt` are not included in version control.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jbasurtod/madrid_temp_app.git
   cd madrid_temp_app
   ```

2. **Create a virtual environment**:
   ```bash
    python -m venv venv
    ```

3. **Install dependencies**:
   ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Run the Application**:
   ```bash
    python app.py
    ```
2. Access the app in your web browser at http://localhost:5000/madridtemp.

## Configuration
- The application uses the Madrid timezone for datetime comparisons. This is configured directly in the code using the pytz library.
- URLs for fetching temperature data are stored in data/urls.txt, which is not included in version control to protect sensitive data.

## Contributing
If you'd like to contribute to the project, please fork the repository and use a feature branch. Pull requests are warmly welcome.

## License
This project is licensed under the MIT License - see the LICENSE file for details.