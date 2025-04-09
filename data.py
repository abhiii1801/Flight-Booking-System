import psycopg2
from datetime import datetime

class Data:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="Flights_Data",
            user="postgres",
            password="qwerty123",
            host="localhost",
            port="5432"
        )
        self.cur = self.conn.cursor()

class Get_data(Data):
    def get_cities(self):
        query = "SELECT city, code from airports"
        self.cur.execute(query)
        res = self.cur.fetchall()
        return res
    
    def get_min_date(self):
        query = "Select min(date) from flights"
        self.cur.execute(query)
        res = self.cur.fetchone()
        return res
    
    def get_max_date(self):
        query = "Select max(Date) from flights"
        self.cur.execute(query)
        res = self.cur.fetchone()
        return res
    
    def get_dis_cabin_class(self):
        query = "Select distinct cabin_class from flight_seats"
        self.cur.execute(query)
        res = self.cur.fetchall()
        return res
    
    def get_flights(self, search_params):
        origin = search_params.get('origin')
        destination = search_params.get('destination')
        start_date = search_params.get('start_date')
        end_date = search_params.get('end_date')
        cabin_class = search_params.get('cabin_class')

        query = """
            SELECT 
                f.flight_no, f.origin, f.destination, f.company, f.departure_time, 
                f.arrival_time, f.duration_time, f.flight_price, f.date, 
                i.average_rating, i.total_reviews, i.aircraft_type, 
                s.cabin_class
            FROM flights f
            LEFT JOIN flight_info i ON f.flight_no = i.flight_no
            JOIN flight_seats s ON s.flight_no = f.flight_no AND s.date = f.date
            WHERE 
                f.origin = %s AND f.destination = %s 
                AND f.date BETWEEN %s AND %s
                AND s.cabin_class = %s AND s.available_seats > 0
        """

        self.cur.execute(query, (origin, destination, start_date, end_date, cabin_class))
        rows = self.cur.fetchall()

        flights = self.add_info_flights(rows)
        
        return flights
    
    def add_info_flights(self, flights):
        columns = [
            "flight_no", "origin", "destination", "company", "departure_time",
            "arrival_time", "duration_time", "flight_price", "date",
            "average_rating", "total_reviews", "aircraft_type", "cabin_class"
        ]    
        
        flights_found = [dict(zip(columns, row)) for row in flights]
        
        for flight in flights_found:
            flight['departure_time_formatted'] = flight['departure_time'].strftime("%I:%M %p")
            flight['arrival_time_formatted'] = flight['arrival_time'].strftime("%I:%M %p")
            flight['duration_time_formatted'] = str(flight['duration_time'])[:-3].replace(":", " hours ", 1).replace(":", " minutes")
            flight['date_formatted'] = flight['date'].strftime("%B %d, %Y")
            flight['origin_city'] = self.get_city_flight(flight['origin'])[0] 
            flight['destination_city'] = self.get_city_flight(flight['destination'])[0]   
        
        return flights_found

    def get_city_flight(self, code):
        query = 'SELECT city FROM airports WHERE code = %s'
        self.cur.execute(query, (code,))
        return self.cur.fetchone()

    def get_airlines(self):
        query = 'select distinct company from flights'
        self.cur.execute(query)
        return self.cur.fetchall()
    
    def get_flitered_flights(self,search_params, price_range, airlines, min_review):
        origin = search_params.get('origin')
        destination = search_params.get('destination')
        start_date = search_params.get('start_date')
        end_date = search_params.get('end_date')
        cabin_class = search_params.get('cabin_class')

        query = """
            SELECT 
                f.flight_no, f.origin, f.destination, f.company, f.departure_time, 
                f.arrival_time, f.duration_time, f.flight_price, f.date, 
                i.average_rating, i.total_reviews, i.aircraft_type, 
                s.cabin_class
            FROM flights f
            LEFT JOIN flight_info i ON f.flight_no = i.flight_no
            JOIN flight_seats s ON s.flight_no = f.flight_no AND s.date = f.date
            WHERE 
                f.origin = %s AND f.destination = %s 
                AND f.date BETWEEN %s AND %s
                AND s.cabin_class = %s AND s.available_seats > 0
                AND f.flight_price <= %s
        """
        values = [origin, destination, start_date, end_date, cabin_class, price_range]

        if airlines:
            placeholders = ','.join(['%s'] * len(airlines))
            query += f" AND f.company IN ({placeholders})"
            values.extend(airlines)

        if min_review:
            query += " AND i.average_rating >= %s"
            values.append(min_review)

        self.cur.execute(query, tuple(values))
        rows = self.cur.fetchall()
        return self.add_info_flights(rows)
    
class Post_data(Data):
    pass

        


if __name__ == '__main__':
    gd = Get_data()
    search_params = {
            'origin': 'DEL',
            'destination': 'BOM',
            'departure_date': '2025-05-23',
            'cabin_class': 'First'
    }
    print(gd.get_flights(search_params))