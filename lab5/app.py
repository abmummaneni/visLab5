from flask import Flask, render_template, request
import duckdb
import pandas as pd

app = Flask(__name__)
continuous_columns = ['humidity', 'temp', 'wind']
discrete_columns = ['day']
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
days = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]
sorted_months = sorted(months)

@app.route('/')
def index():
    # Retrieve the minimum and maximum X and Y coordinates
    scatter_ranges_query = f'SELECT MIN(X), MAX(X), MIN(Y), MAX(Y) FROM forestfires.csv'
    scatter_ranges_results = duckdb.sql(scatter_ranges_query).df()
    scatter_ranges = scatter_ranges_results.iloc[0].tolist() 

    # Retrieve the maximum fire count across all months
    max_count_query = 'SELECT MAX(count) FROM (SELECT COUNT(*) as count FROM forestfires.csv GROUP BY month)' 
    max_count_results = duckdb.sql(max_count_query).df()
    max_count = max_count_results.iloc[0]['max(count)']
    
    # Return the min and max values present for temp, humidity, wind over all the data
    filter_ranges_query = 'SELECT MAX(temp), MIN(temp), MAX(humidity), MIN(humidity), MAX(wind), MIN(wind) FROM forestfires.csv' # TODO: write a query that retrieves the the minimum and maximum value for each slider
    filter_ranges_results = duckdb.sql(filter_ranges_query).df().iloc[0].tolist()
    filter_ranges = {
        "temp" : [filter_ranges_results[1], filter_ranges_results[0]],
        "humidity" : [filter_ranges_results[3], filter_ranges_results[2]],
        "wind": [filter_ranges_results[5], filter_ranges_results[4]]
    } 

    return render_template(
        'index.html', months=months, days=days,
        filter_ranges=filter_ranges, scatter_ranges=scatter_ranges, max_count=max_count
    )

@app.route('/update', methods=["POST"])
def update():
    request_data = request.get_json()

    # Update where clause from sliders (numerical ranges)
    continuous_predicate = ' AND '.join([f'({column} >= {request_data[column][0]} AND {column} <= {request_data[column][1]})' for column in continuous_columns])
    days = request_data['day']
    
    # If all days are unchecked, no data to  return
    if not days:
        return {'scatter_data': [], 'bar_data': [], 'max_count': 0}
    
    # Update where clause from checkboxes (days)
    discrete_predicate = ' AND '.join([f"{column} IN {tuple(days)}" for column in discrete_columns])
    
    # Combine where clause from sliders and checkboxes
    predicate = ' AND '.join([continuous_predicate, discrete_predicate])
    
    # Construct query for scatterplot
    scatter_query = f'SELECT X, Y FROM forestfires.csv WHERE {predicate}'
    scatter_results = duckdb.sql(scatter_query).df()
    scatter_data = scatter_results.values.tolist() # Extract the data that will populate the scatter plot

    # Construct query for bar plot
    bar_query = f'SELECT month, COUNT(*) as count FROM forestfires.csv WHERE {predicate} GROUP BY month' # TODO: Write a query that retrieves the number of forest fires per month after filtering
    bar_results = duckdb.sql(bar_query).df()
    bar_results['month'] = pd.to_datetime(bar_results['month']).dt.month

    # Format bar_results so that it contains each month even if it is zero
    bar_results = bar_results.sort_values(by='month')
    bar_results = bar_results.set_index('month')
    bar_results = bar_results.reindex(range(1, 13))
    bar_results = bar_results.fillna(0)
    

    # Extract the data that will populate the bar chart from the results
    bar_data = bar_results['count'].tolist() 
    # Extract the maximum number of forest fires in a single month from the results
    max_count = max(bar_results["count"]) 

    return {'scatter_data': scatter_data, 'bar_data': bar_data, 'max_count': max_count}

if __name__ == "__main__":
    app.run(debug=True, port=8000)
    