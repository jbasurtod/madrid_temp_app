from flask import Flask, render_template
from Worker import Worker

app = Flask(__name__)

@app.route('/madridtemp')
def index():
    worker = Worker()
    last_temperature, formatted_datetime, dates, date_hour_temp_map, max_temp, min_temp, pred5d_df = worker.GetData()

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
        forecast_5d=forecast_5d  # Pass the forecast data to the template
    )


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
