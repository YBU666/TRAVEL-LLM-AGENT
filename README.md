# AI Travel Planner

An intelligent travel planning application that combines LLM reasoning with real-time data to help users plan their perfect trip. The application uses Groq LLM, OpenWeather API, and RapidAPI services for hotels and flights information.

## Features

- City information and cultural insights
- Real-time weather data
- Hotel recommendations
- Flight options
- Customized trip planning
- Interactive Streamlit interface

## Prerequisites

- Python 3.8+
- Groq API key
- OpenWeather API key
- RapidAPI key

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd travel_llm
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your API keys:
```
GROQ_API_KEY=your_groq_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
RAPIDAPI_KEY=your_rapidapi_key_here
```

## Running the Application

To start the application, run:
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Usage

1. Enter your destination city
2. Select the number of days for your trip
3. Choose the month of travel
4. Click "Plan My Trip" to generate your personalized travel plan

The application will provide:
- Cultural and historical information about the city
- Current weather and forecast
- Hotel recommendations
- Flight options
- A detailed day-by-day itinerary

## API Sources

- LLM: Groq (Mixtral-8x7b)
- Weather: OpenWeather API
- Hotels: RapidAPI Hotels API
- Flights: RapidAPI Skyscanner API

![images](https://github.com/YBU666/TRAVEL-LLM-AGENT/blob/main/images/t1.png?raw=true)

![images](https://github.com/YBU666/TRAVEL-LLM-AGENT/blob/main/images/t2.png?raw=true)

![images](https://github.com/YBU666/TRAVEL-LLM-AGENT/blob/main/images/t3.png?raw=true)

![images](https://github.com/YBU666/TRAVEL-LLM-AGENT/blob/main/images/t4.png?raw=true)

![images](https://github.com/YBU666/TRAVEL-LLM-AGENT/blob/main/images/t5.png?raw=true)




