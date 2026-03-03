from flask import Flask, render_template, request
import duckdb

app = Flask(__name__)
continuous_columns = ['humidity', 'temp', 'wind']
discrete_columns = ['day']
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
days = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]
sorted_months = sorted(months)

@app.route('/')
def index():
    scatter_ranges_query = f'SELECT MIN(X), MAX(X), MIN(Y), MAX(Y) FROM forestfires.csv' # Retrieves the minimum and maximum X and Y coordinates
    scatter_ranges_results = duckdb.sql(scatter_ranges_query).df()
    scatter_ranges = [0, 0, 0, 0] # TODO: Define a list [minimum of X, maximum of X, minimum of Y, maximum of Y]
    
    max_count_query = 'SELECT * FROM forestfires.csv' # TODO: Write a query that retrieves the maximum number of forest fires that occurred in a single month
    max_count_results = duckdb.sql(max_count_query).df()
    max_count = 0 # TODO: Extract the maximum count from the query results

    filter_ranges_query = 'SELECT * FROM forestfires.csv' # TODO: write a query that retrieves the the minimum and maximum value for each slider
    filter_ranges_results = duckdb.sql(filter_ranges_query).df()
    filter_ranges = {} # TODO: Create a dictionary where each key is a filter and values are the minimum and maximum values

    return render_template(
        'index.html', months=months, days=days,
        filter_ranges=filter_ranges, scatter_ranges=scatter_ranges, max_count=max_count
    )

@app.route('/update', methods=["POST"])
def update():
    request_data = request.get_json()
    continuous_predicate = ' AND '.join([f'({column} >= 0 AND {column} <= 0)' for column in continuous_columns]) # TODO: update where clause from sliders
    discrete_predicate = ' AND '.join([f'{column} IN ()' for column in discrete_columns]) # TODO: update where clause from checkboxes
    predicate = ' AND '.join([continuous_predicate, discrete_predicate]) # Combine where clause from sliders and checkboxes

    scatter_query = f'SELECT X, Y FROM forestfires.csv WHERE {predicate}'
    scatter_results = duckdb.sql(scatter_query).df()
    scatter_data = [] # TODO: Extract the data that will populate the scatter plot

    bar_query = f'SELECT * FROM forestfires.csv' # TODO: Write a query that retrieves the number of forest fires per month after filtering
    bar_results = duckdb.sql(bar_query).df()
    bar_results['month'] = bar_results.index.map({i: sorted_months[i] for i in range(len(sorted_months))})
    bar_data = [] # TODO: Extract the data that will populate the bar chart from the results
    max_count = 0 # TODO: Extract the maximum number of forest fires in a single month from the results

    return {'scatter_data': scatter_data, 'bar_data': bar_data, 'max_count': max_count}

if __name__ == "__main__":
    app.run(debug=True)
    