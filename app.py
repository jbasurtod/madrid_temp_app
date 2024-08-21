from flask import Flask, render_template
from Worker import Worker

app = Flask(__name__)

@app.route('/madridtemp')
def index():
    worker = Worker()
    last_temperature, formatted_datetime, dates, date_hour_temp_map, max_temp, min_temp = worker.GetData()

    # Determine max number of hours for column headers
    max_hours = max(len(date_hour_temp_map[date]['hours']) for date in dates)

    # Prepare hours_map and temperatures_map
    hours_map = {date: date_hour_temp_map[date]['hours'] for date in dates}
    temperatures_map = {date: date_hour_temp_map[date]['temperatures'] for date in dates}

    return render_template(
        'index.html',
        last_temperature=last_temperature,
        formatted_datetime=formatted_datetime,
        dates=dates,
        hours_map=hours_map,
        temperatures_map=temperatures_map,
        max_hours=max_hours,
        max=max_temp,
        min=min_temp
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)


