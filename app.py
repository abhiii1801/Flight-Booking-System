from flask import Flask, render_template, request, redirect, session
from data import Get_data, Post_data

app = Flask(__name__)
get = Get_data()
post = Post_data()

app.secret_key = 'super_secret_key'

@app.route('/')
def red():
    return redirect('/home')

@app.route('/home', methods=['GET'])
def home():
    cities = get.get_cities()
    min_date = get.get_min_date()
    max_date = get.get_max_date()
    cabin_classes = get.get_dis_cabin_class()

    # Store in session
    session['cities'] = cities
    session['min_date'] = min_date
    session['max_date'] = max_date
    session['cabin_classes'] = cabin_classes

    return render_template('home.html', cities=cities, min_date=min_date, max_date=max_date, cabin_classes=cabin_classes)

@app.route('/flights')
def flights():
    return render_template('flights.html')

@app.route('/search_flights', methods=['POST'])
def search_flights():
    # Fallback if session missing (just in case)
    if not all(k in session for k in ['cities', 'min_date', 'max_date', 'cabin_classes']):
        return redirect('/home')

    origin = request.form.get('origin')
    destination = request.form.get('destination')
    start_date = request.form.get('departure_date')
    end_date = request.form.get('end_date')
    cabin_class = request.form.get('cabin_class')

    if not all([origin, destination, start_date, end_date, cabin_class]):
        return "Please fill in all fields!", 400

    search_params = {
        'origin': origin,
        'destination': destination,
        'start_date': start_date,
        'end_date': end_date,
        'cabin_class': cabin_class
    }

    flights_found = get.get_flights(search_params)

    airlines = get.get_airlines()
    max_price = max([flight['flight_price'] for flight in flights_found])

    session['search_params'] = search_params
    session['airlines'] = airlines
    session['max_price'] = max_price

    return render_template('flights.html', flights=flights_found,
                           cities=session['cities'], min_date=session['min_date'],
                           max_date=session['max_date'], cabin_classes=session['cabin_classes'],
                           params=search_params, airlines=airlines, max_price=max_price)

@app.route('/filter_flights', methods=['POST'])
def filter_flights():
    search_params = session.get('search_params')
    airlines = session.get('airlines')
    max_price = session.get('max_price')

    price = request.form.get('price')
    selected_airlines = request.form.getlist('airlines')
    min_review = request.form.get('min_review')

    filtered_flights = get.get_flitered_flights(
        search_params,
        price_range=price,
        airlines=selected_airlines,
        min_review=min_review
    )
    
    return render_template('flights.html', 
        flights=filtered_flights,
        cities=session['cities'],
        min_date=session['min_date'],
        max_date=session['max_date'],
        cabin_classes=session['cabin_classes'],
        params=session['search_params'],
        airlines=airlines,
        max_price=max_price,
        selected_airlines=selected_airlines,
        selected_price=price,
        selected_review=min_review
    )
    
    
@app.route('/billing')
def billing():
    return render_template('billing.html')

if __name__ == '__main__':
    app.run(debug=True)
