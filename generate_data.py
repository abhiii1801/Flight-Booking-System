import random
from datetime import datetime, timedelta
import psycopg2

conn = psycopg2.connect(
    dbname="Flights_Data",
    user="postgres",
    password="qwerty123",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

indian_airports = ['DEL', 'BOM', 'BLR', 'HYD', 'MAA', 'CCU', 'PNQ', 'AMD', 'COK', 'GOI', 'JAI', 'LKO', 'SXR', 'IXC']
intl_airports = ['DXB', 'LHR', 'JFK', 'SIN', 'BKK', 'HKG', 'KUL', 'DOH', 'FRA', 'CDG', 'SYD', 'NRT', 'YYZ']
airports = indian_airports + intl_airports

airports_data = [
    # Indian Airports
    ("Indira Gandhi International Airport", "Delhi", "India", "DEL"),
    ("Chhatrapati Shivaji Maharaj International Airport", "Mumbai", "India", "BOM"),
    ("Kempegowda International Airport", "Bangalore", "India", "BLR"),
    ("Rajiv Gandhi International Airport", "Hyderabad", "India", "HYD"),
    ("Chennai International Airport", "Chennai", "India", "MAA"),
    ("Netaji Subhas Chandra Bose International Airport", "Kolkata", "India", "CCU"),
    ("Pune Airport", "Pune", "India", "PNQ"),
    ("Sardar Vallabhbhai Patel International Airport", "Ahmedabad", "India", "AMD"),
    ("Cochin International Airport", "Kochi", "India", "COK"),
    ("Goa International Airport", "Goa", "India", "GOI"),
    ("Jaipur International Airport", "Jaipur", "India", "JAI"),
    ("Chaudhary Charan Singh Airport", "Lucknow", "India", "LKO"),
    ("Srinagar Airport", "Srinagar", "India", "SXR"),
    ("Shaheed Bhagat Singh International Airport", "Chandigarh", "India", "IXC"),

    # International Airports
    ("Dubai International Airport", "Dubai", "UAE", "DXB"),
    ("Heathrow Airport", "London", "UK", "LHR"),
    ("John F. Kennedy International Airport", "New York", "USA", "JFK"),
    ("Changi Airport", "Singapore", "Singapore", "SIN"),
    ("Suvarnabhumi Airport", "Bangkok", "Thailand", "BKK"),
    ("Hong Kong International Airport", "Hong Kong", "Hong Kong", "HKG"),
    ("Kuala Lumpur International Airport", "Kuala Lumpur", "Malaysia", "KUL"),
    ("Hamad International Airport", "Doha", "Qatar", "DOH"),
    ("Frankfurt Airport", "Frankfurt", "Germany", "FRA"),
    ("Charles de Gaulle Airport", "Paris", "France", "CDG"),
    ("Sydney Kingsford Smith Airport", "Sydney", "Australia", "SYD"),
    ("Narita International Airport", "Tokyo", "Japan", "NRT"),
    ("Toronto Pearson International Airport", "Toronto", "Canada", "YYZ")
]

airlines = [
    'IndiGo', 'Vistara', 'Air India', 'SpiceJet', 'Go First', 'AirAsia India',
    'Emirates', 'Singapore Airlines', 'Qatar Airways', 'Lufthansa',
    'British Airways', 'Air France', 'Turkish Airlines', 'Etihad', 'Cathay Pacific'
]

airline_codes = {
    'IndiGo': '6E', 'Vistara': 'UK', 'Air India': 'AI', 'SpiceJet': 'SG', 'Go First': 'G8', 'AirAsia India': 'I5',
    'Emirates': 'EK', 'Singapore Airlines': 'SQ', 'Qatar Airways': 'QR', 'Lufthansa': 'LH',
    'British Airways': 'BA', 'Air France': 'AF', 'Turkish Airlines': 'TK', 'Etihad': 'EY', 'Cathay Pacific': 'CX'
}

cabin_class = ['Economy', 'Premium Economy', 'Business', 'First']
start_date = datetime.now()
total_days = 90
records_to_generate = 10000

seat_config = {
    "Boeing 737": {
        "Economy": 110,
        "Premium Economy": 16,
        "Business": 12,
        "First": 4
    },
    "Airbus A320": {
        "Economy": 120,
        "Premium Economy": 20,
        "Business": 10,
        "First": 5
    },
    "Boeing 777": {
        "Economy": 250,
        "Premium Economy": 40,
        "Business": 50,
        "First": 8
    },
    "Airbus A350": {
        "Economy": 270,
        "Premium Economy": 36,
        "Business": 48,
        "First": 10
    }
}

def random_time():
    hour = random.randint(0, 23)
    minute = random.choice([0, 15, 30, 45])
    return hour, minute

def format_time(hour, minute):
    return f"{hour:02}:{minute:02}"

def calc_duration(dep_hour, dep_min, arr_hour, arr_min):
    dep = timedelta(hours=dep_hour, minutes=dep_min)
    arr = timedelta(hours=arr_hour, minutes=arr_min)
    if arr <= dep:
        arr += timedelta(hours=2)
    dur = arr - dep
    return f"{dur.seconds // 3600}h {(dur.seconds % 3600) // 60}m"


flight_info_set = set()

class Flights_data_generator:
    def insert_flight_info(self, flight_no, airline):
        if flight_no not in flight_info_set:
            rating = round(random.uniform(3.0, 5.0), 1)
            reviews = random.randint(50, 1000)
            aircraft = random.choice(['Airbus A320', 'Boeing 737', 'Airbus A350', 'Boeing 777'])

            cur.execute("""
                INSERT INTO flight_info (flight_no, airline, average_rating, total_reviews, aircraft_type)
                VALUES (%s, %s, %s, %s, %s)
            """, (flight_no, airline, rating, reviews, aircraft))

            flight_info_set.add(flight_no)

    def generate_flights(self):
        flight_map = {}

        for _ in range(records_to_generate):
            origin, destination = random.sample(airports, 2)
            company = random.choice(airlines)

            key = (origin, destination, company)
            if key in flight_map:
                flight_number = flight_map[key]
            else:
                flight_number = f"{airline_codes[company]}{random.randint(1000, 9999)}"
                flight_map[key] = flight_number
                self.insert_flight_info(flight_number, company)

            dep_hour, dep_min = random_time()
            dep_time = format_time(dep_hour, dep_min)

            duration_minutes = random.randint(90, 600)
            arr_hour = (dep_hour + duration_minutes // 60) % 24
            arr_min = (dep_min + duration_minutes % 60) % 60
            arr_time = format_time(arr_hour, arr_min)

            duration = calc_duration(dep_hour, dep_min, arr_hour, arr_min)
            price = random.randint(4000, 12000)
            flight_date = (start_date + timedelta(days=random.randint(1, total_days))).strftime('%Y-%m-%d')
            cabin = random.choice(cabin_class)

            cur.execute("""
                INSERT INTO flights (
                    flight_no, origin, destination, company,
                    departure_time, arrival_time, duration_time,
                    flight_price, date, cabin_class
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (flight_number, origin, destination, company,
                  dep_time, arr_time, duration,
                  price, flight_date, cabin))
    
    def generate_airports(self):
        for airport in airports_data:
            cur.execute("""
                INSERT INTO airports(
                    name, city, country, code
                ) VALUES (%s,%s,%s,%s)
            """, (airport[0], airport[1], airport[2], airport[3]))

    def generate_flight_seats(self):
        cur.execute("SELECT flight_no, aircraft_type FROM flight_info")
        flights = cur.fetchall()

        start_date = datetime.now() - timedelta(days=1)
        days = 90

        for flight_no, aircraft in flights:
            if aircraft not in seat_config:
                continue
            for i in range(days):
                flight_date = (start_date + timedelta(days=i)).date()
                for cabin, total in seat_config[aircraft].items():
                    filled = random.randint(0, int(total * 0.75))
                    available = total - filled
                    cur.execute("""
                        INSERT INTO flight_seats (flight_no, date, cabin_class, total_seats, available_seats)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (flight_no, flight_date, cabin, total, available))

        
if __name__ == '__main__':
    g = Flights_data_generator()
    # g.generate_flights()
    # g.generate_airports()
    g.generate_flight_seats()
    conn.commit()
    cur.close()
    conn.close()
    