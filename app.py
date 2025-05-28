import streamlit as st
import os
from datetime import datetime, timedelta
from dateutil.parser import parse
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
import requests
from typing import Dict, List, Optional
import json

# Load environment variables
load_dotenv()

# Initialize API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

# Initialize LLM
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant",
    temperature=0.7
)

def get_weather_data(city: str) -> Dict:
    """Get current weather and forecast data for a city"""
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching weather data: {str(e)}")
        return {}

def get_city_coordinates(city: str) -> tuple:
    """Get city coordinates using OpenStreetMap Nominatim API"""
    url = f"https://nominatim.openstreetmap.org/search"
    params = {
        "q": city,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "TravelPlanner/1.0"  # Required by Nominatim
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
        return None, None
    except Exception as e:
        st.error(f"Error fetching city coordinates: {str(e)}")
        return None, None

def search_hotels(city: str) -> List[Dict]:
    """Search for hotels using OpenStreetMap Overpass API"""
    # First get city coordinates
    lat, lon = get_city_coordinates(city)
    if lat is None or lon is None:
        return []
    
    # Define the search radius (in meters)
    radius = 5000  # 5km radius
    
    # Overpass API query to find hotels
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json][timeout:25];
    (
      node["tourism"="hotel"](around:{radius},{lat},{lon});
      way["tourism"="hotel"](around:{radius},{lat},{lon});
      relation["tourism"="hotel"](around:{radius},{lat},{lon});
    );
    out body;
    >;
    out skel qt;
    """
    
    try:
        response = requests.post(overpass_url, data={"data": overpass_query})
        response.raise_for_status()
        data = response.json()
        
        hotels = []
        for element in data.get("elements", [])[:5]:  # Limit to top 5 hotels
            if element.get("type") == "node":  # Only process node elements for simplicity
                tags = element.get("tags", {})
                hotel = {
                    "name": tags.get("name", "Unnamed Hotel"),
                    "address": {
                        "street": tags.get("addr:street", "Street not available"),
                        "city": tags.get("addr:city", city),
                        "country": tags.get("addr:country", "Country not available")
                    },
                    "stars": tags.get("stars", "N/A"),
                    "phone": tags.get("phone", "Phone not available"),
                    "website": tags.get("website", "Website not available"),
                    "coordinates": {
                        "lat": element.get("lat"),
                        "lon": element.get("lon")
                    }
                }
                hotels.append(hotel)
                
                if len(hotels) >= 3:  # Limit to 3 hotels
                    break
        
        return hotels
    except Exception as e:
        st.error(f"Error fetching hotel data: {str(e)}")
        return []

def search_flights(origin: str, destination: str) -> List[Dict]:
    """Search for flights using AviationStack API"""
    url = "http://api.aviationstack.com/v1/flights"
    params = {
        "access_key": AVIATIONSTACK_API_KEY,
        "dep_iata": origin,
        "arr_iata": destination,
        "limit": 3
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        flights = []
        for flight in data.get("data", [])[:3]:
            airline = flight.get("airline", {}).get("name", "Unknown Airline")
            flight_number = flight.get("flight", {}).get("number", "Unknown")
            departure = flight.get("departure", {}).get("scheduled", "Unknown")
            arrival = flight.get("arrival", {}).get("scheduled", "Unknown")
            
            flights.append({
                "airline": airline,
                "flight_number": flight_number,
                "departure": departure,
                "arrival": arrival
            })
        return flights
    except Exception as e:
        st.error(f"Error fetching flight data: {str(e)}")
        return []

def get_airport_code(city: str) -> str:
    """Get airport code for a city using OpenFlights data"""
    # Using a simplified airport code mapping
    airport_codes = {
        "tokyo": "HND",
        "osaka": "KIX",
        "kyoto": "KIX",  # Kyoto uses Osaka's airport
        "delhi": "DEL",
        "mumbai": "BOM",
        "udaipur": "UDR",
        "london": "LHR",
        "paris": "CDG",
        "new york": "JFK",
        "singapore": "SIN",
        "bangkok": "BKK"
    }
    return airport_codes.get(city.lower(), city[:3].upper())

def generate_trip_plan(city: str, days: int, month: str) -> str:
    """Generate a trip plan using LangChain and Groq"""
    system_prompt = """You are a knowledgeable travel advisor. Provide detailed information about the city, including:
    1. A paragraph about the city's cultural and historical significance
    2. Major attractions and must-visit places
    3. Local cuisine recommendations
    4. Best areas to stay
    5. Transportation tips
    6. Cultural etiquette and customs
    Format the response in a clear, organized manner."""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Create a {days}-day trip plan for {city} in {month}.")
    ]
    
    response = llm.invoke(messages)
    return response.content

def main():
    st.title("🌍 AI Travel Planner")
    st.write("Plan your perfect trip with AI-powered recommendations and real-time data!")

    # User inputs
    col1, col2, col3 = st.columns(3)
    with col1:
        city = st.text_input("Destination City", "Tokyo")
    with col2:
        days = st.number_input("Number of Days", min_value=1, max_value=14, value=3)
    with col3:
        month = st.selectbox("Month of Travel", 
                           ["January", "February", "March", "April", "May", "June",
                            "July", "August", "September", "October", "November", "December"])

    origin_city = st.text_input("Departure City", "London")

    if st.button("Plan My Trip"):
        with st.spinner("Generating your perfect trip plan..."):
            # Get weather data
            weather_data = get_weather_data(city)
            if weather_data:
                st.subheader("🌤️ Weather Information")
                temp = weather_data.get("main", {}).get("temp")
                weather_desc = weather_data.get("weather", [{}])[0].get("description")
                st.write(f"Current temperature: {temp}°C")
                st.write(f"Weather conditions: {weather_desc}")

            # Generate trip plan
            trip_plan = generate_trip_plan(city, days, month)
            st.subheader("🗺️ Your Trip Plan")
            st.write(trip_plan)

            # Get hotel recommendations
            st.subheader("🏨 Hotel Options")
            hotels = search_hotels(city)
            if hotels:
                for hotel in hotels:
                    st.write(f"- {hotel['name']}")
                    address = hotel['address']
                    st.write(f"  Address: {address['street']}, {address['city']}, {address['country']}")
                    if hotel['stars'] != "N/A":
                        st.write(f"  Rating: {hotel['stars']} stars")
                    if hotel['phone'] != "Phone not available":
                        st.write(f"  Phone: {hotel['phone']}")
                    if hotel['website'] != "Website not available":
                        st.write(f"  Website: {hotel['website']}")
                    st.write(f"  [View on Map](https://www.openstreetmap.org/?mlat={hotel['coordinates']['lat']}&mlon={hotel['coordinates']['lon']}#map=16/{hotel['coordinates']['lat']}/{hotel['coordinates']['lon']})")
                    st.write("---")
            else:
                st.warning("Could not fetch hotel data. Please check hotel booking websites directly.")

            # Get flight options
            st.subheader("✈️ Flight Options")
            origin_code = get_airport_code(origin_city)
            dest_code = get_airport_code(city)
            flights = search_flights(origin_code, dest_code)
            
            if flights:
                for flight in flights:
                    st.write(f"- {flight['airline']} - Flight {flight['flight_number']}")
                    st.write(f"  Departure: {flight['departure']}")
                    st.write(f"  Arrival: {flight['arrival']}")
            else:
                st.warning("Could not fetch real-time flight data. Please check airline websites directly.")

if __name__ == "__main__":
    main() 