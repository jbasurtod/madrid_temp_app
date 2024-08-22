from datetime import datetime, timedelta
import pandas as pd
import requests
import pytz
import os

class Worker:
    def __init__(self) -> None:
        # URLs for the CSV files
        #self.historic_url, self.predictions_url = self.load_urls('data/urls.txt')
        self.historic_url = 'https://drive.google.com/uc?id=12IUAsaeNNcNbIgXsXcR0UBqrKPx-ZncK'
        self.predictions_url = 'https://drive.google.com/uc?id=1EofTofvRwQylkT_e8C0L5Iy0yUVO46dz'
        self.pred5days_url = 'https://drive.google.com/uc?id=1vTwOSjkZSpTqR6RYtVgKK0AEn5XBE4Dt'
        # Define local paths for caching
        self.data_dir = 'data'
        self.historic_cache_path = os.path.join(self.data_dir, 'historic_data.csv')
        self.predictions_cache_path = os.path.join(self.data_dir, 'predictions_data.csv')
        self.pred5days_cache_path = os.path.join(self.data_dir, 'predictions5days_data.csv')

        # Create the data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
    def load_urls(self,file_path):
    # Read URLs from the file
        with open(file_path, 'r') as file:
            urls = file.readlines()

        # Remove any leading/trailing whitespace characters like newline
        urls = [url.strip() for url in urls]

        # Ensure that we have exactly two URLs
        if len(urls) != 2:
            raise ValueError(f"Expected 2 URLs in the file, but found {len(urls)}.")

        return urls[0], urls[1]

    def download_csv(self, url, save_path):
        response = requests.get(url)
        with open(save_path, 'wb') as f:
            f.write(response.content)

    def GetData(self):
        # Load or download the historic data
        if not os.path.exists(self.historic_cache_path):
            self.download_csv(self.historic_url, self.historic_cache_path)
        historic_df = pd.read_csv(self.historic_cache_path)

        # Check if predictions data should be downloaded
        if not os.path.exists(self.predictions_cache_path):
            self.download_csv(self.predictions_url, self.predictions_cache_path)
            predictions_df = pd.read_csv(self.predictions_cache_path)
        else:
            predictions_df = pd.read_csv(self.predictions_cache_path)

        # Check if predictions data should be downloaded
        if not os.path.exists(self.pred5days_cache_path):
            self.download_csv(self.pred5days_url, self.pred5days_cache_path)
            pred5d_df = pd.read_csv(self.pred5days_cache_path)
        else:
            pred5d_df = pd.read_csv(self.pred5days_cache_path)


        # Convert 'datetime' columns to datetime objects
        historic_df['datetime'] = pd.to_datetime(historic_df['datetime'])
        predictions_df['datetime'] = pd.to_datetime(predictions_df['datetime'])
        pred5d_df['day'] = pd.to_datetime(pred5d_df['day'])

        # Check if the current historic data matches the cached historic data
        current_historic_df = pd.read_csv(self.historic_url)
        current_historic_df['datetime'] = pd.to_datetime(current_historic_df['datetime'])

        if not historic_df.equals(current_historic_df):
            # Historic data has changed, update the cache and download new predictions data
            historic_df = current_historic_df
            historic_df.to_csv(self.historic_cache_path, index=False)
            self.download_csv(self.predictions_url, self.predictions_cache_path)
            predictions_df = pd.read_csv(self.predictions_cache_path)
            self.download_csv(self.predictions_url, self.predictions_cache_path)
            pred5d_df = pd.read_csv(self.pred5days_cache_path)
        return self.ProcessData(historic_df, predictions_df, pred5d_df)

    def ProcessData(self, historic_df, predictions_df, pred5d_df):
        # Get the last item from the 'temperature' column
        last_temperature = historic_df['temperature'].iloc[-1]

        # Get the last datetime corresponding to the last_temperature
        last_temp_datetime = historic_df[historic_df['temperature'] == last_temperature]['datetime'].iloc[-1]

        # Add 30 minutes to the last datetime
        last_temp_datetime_plus_30 = last_temp_datetime + timedelta(minutes=30)

        # Format the datetime as "August 21, 12:30"
        formatted_datetime = last_temp_datetime_plus_30.strftime('%B %d, %H:%M')

        # Get the last 24 items from the 'pred_xgb' column
        last_24_predictions = predictions_df[['datetime', 'pred_xgb']].tail(24)

        # Define the Madrid time zone
        madrid_timezone = pytz.timezone('Europe/Madrid')

        # Get the current datetime in Madrid timezone
        current_datetime = datetime.now(madrid_timezone)
        
        # Extract the first datetime from last_24_predictions
        first_datetime_str = last_24_predictions['datetime'].iloc[0]
        
        # Convert the string to a datetime object
        first_datetime = pd.to_datetime(first_datetime_str)
        
        # Convert the naive first_datetime to timezone-aware using Madrid timezone
        if first_datetime.tzinfo is None:
            first_datetime = madrid_timezone.localize(first_datetime)
        
        # Compare the timezone-aware current_datetime to the timezone-aware first_datetime
        if current_datetime > first_datetime:
            # Pop the first datetime and update last_temperature
            first_temp = last_24_predictions['pred_xgb'].iloc[0]
            
            # Remove the first item
            last_24_predictions = last_24_predictions.iloc[1:]
            
            # Update last_temperature with the temperature of the first item
            last_temperature = first_temp
            
            # Update formatted_datetime to reflect the change
            formatted_datetime = first_datetime.strftime('%B %d, %H:%M')

        # Prepare data for table display
        dates, date_hour_temp_map = self.PrepareTableData(last_24_predictions)

        # Calculate today's max and min temperatures
        max_temp, min_temp = self.TodaysMaxMin(historic_df, predictions_df)

        return int(last_temperature), formatted_datetime, dates, date_hour_temp_map, max_temp, min_temp, pred5d_df
    
    def TodaysMaxMin(self, historic_df, predictions_df):
        # Ensure 'datetime' columns are in datetime format
        historic_df['datetime'] = pd.to_datetime(historic_df['datetime'])
        predictions_df['datetime'] = pd.to_datetime(predictions_df['datetime'])

        # Rename the 'predictions' column in predictions_df to 'temperature' for merging
        predictions_df.rename(columns={'predictions': 'temperature'}, inplace=True)

        # Get today's date
        today_date = pd.Timestamp.now().normalize()

        # Filter today's data
        today_df = historic_df[historic_df['datetime'].dt.date == today_date.date()]
        today_pred = predictions_df[predictions_df['datetime'].dt.date == today_date.date()]

        # Merge the dataframes on 'datetime'
        merged_df = pd.merge(today_df, today_pred, on='datetime', how='outer')

        # Combine the temperature data from both sources
        merged_df['temperature'] = merged_df['temperature_x'].combine_first(merged_df['temperature_y'])

        # Drop unnecessary columns after merging
        merged_df.drop(columns=['temperature_x', 'temperature_y'], inplace=True)

        # Check if merged_df has fewer than 24 records
        if len(merged_df) < 24:
            # Get the last datetime entry from merged_df
            if not merged_df.empty:
                last_datetime = merged_df['datetime'].max()
                # Filter the prediction data for times after the last entry from merged_df
                additional_data = today_pred[today_pred['datetime'] > last_datetime]
                # Merge additional data into merged_df
                merged_df = pd.concat([merged_df, additional_data]).drop_duplicates().reset_index(drop=True)

        # Calculate the max and min temperatures
        max_temp = merged_df['temperature'].max()
        min_temp = merged_df['temperature'].min()

        # Return as integer
        return int(max_temp), int(min_temp)



    def PrepareTableData(self, last_24_predictions):
        # Ensure 'datetime' column is used as the index
        last_24_predictions.set_index('datetime', inplace=True)

        # Convert index to DatetimeIndex and format as hours
        last_24_predictions.index = pd.to_datetime(last_24_predictions.index)
        hours = last_24_predictions.index.strftime('%H:%M').tolist()
        
        # Extract unique dates and temperatures
        unique_dates = last_24_predictions.index.normalize().unique()
        dates = [date.strftime('%B %d') for date in unique_dates]
        
        # Prepare the table data by date
        date_hour_temp_map = {}
        for date in unique_dates:
            date_data = last_24_predictions[last_24_predictions.index.normalize() == date]
            date_hour_temp_map[date.strftime('%B %d')] = {
                'hours': date_data.index.strftime('%H:%M').tolist(),
                'temperatures': date_data['pred_xgb'].round().astype(int).tolist()
            }
        
        return dates, date_hour_temp_map

