from flask import Flask, render_template, request, jsonify
import requests
from datetime import *
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

name = None
chat_history = []

WEATHER_API_KEYS = "46f39b60cd5f7dc35fd549b7d4ec833f"
NEWS_API_KEYS = "10127189f9a245bdb8da23af92202a7b"
CURRENCY_API_KEYS = "3a2141a32ab11fbc16edc830"

def clean_city_name(text):
    return re.sub(r'[^a-zA-Z\\s]', '', text).strip()

def get_weather(city):
    city = clean_city_name(city)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEYS}&units=metric"
    try:
        res = requests.get(url)
        data = res.json()
        if data["cod"] == 200:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            return f"The weather in {city.title()} is {desc} with temperature {temp}°C."
        else:
            return f"City not found. (Code: {data.get('cod')})"
    except Exception as e:
        return f"Error fetching weather: {str(e)}"

def get__jokes():
    try:
        res = requests.get("https://official-joke-api.appspot.com/random_joke")
        data = res.json()
        return f"{data['setup']}... {data['punchline']}"
    except:
        return "Couldn't fetch a joke now."

def get_news():
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEYS}"
        res = requests.get(url)
        articles = res.json().get("articles", [])[:3]
        if not articles:
            return "No news found."
        headlines = [f"{i+1}. {a['title']}" for i, a in enumerate(articles)]
        return "Top headlines:\n" + "\\n".join(headlines)
    except:
        return "Couldn't fetch the news."

def converte_currency(amount, from_currency, to_currency):
    try:
        url = f"https://v6.exchangerate-api.com/v6/{CURRENCY_API_KEYS}/latest/{from_currency.upper()}"
        res = requests.get(url)
        data = res.json()
        rate = data["conversion_rates"].get(to_currency.upper())
        if rate:
            converted = round(amount * rate, 2)
            return f"{amount} {from_currency.upper()} = {converted} {to_currency.upper()}"
        else:
            return "Invalid currency code."
    except:
        return "Currency conversion failed. Check your codes."

def chatbot_response(user_input):
    global name
    user_input = user_input.lower().strip()

    match = re.match(r'convert (\\d+\\.?\\d*) (\\w{3}) to (\\w{3})', user_input)
    if match:
        amount = float(match.group(1))
        from_curr = match.group(2)
        to_curr = match.group(3)
        return converte_currency(amount, from_curr, to_curr)

    if any(word in user_input for word in ['hello', 'hi', 'hey']):
        return "Hello! How can I help you?"
    elif "my name is" in user_input:
        name = user_input.split("is")[-1].strip()
        return f"Nice to meet you, {name}!"
    elif "how are you" in user_input or "what's up" in user_input:
        return "I'm doing great! How about you?"
    elif "your name" in user_input or "who are you" in user_input:
        return "I'm your friendly chatbot assistant!"
    elif "weather" in user_input or "temperature" in user_input:
        return "Please tell me the city name:"
    elif "time" in user_input:
        now = datetime.now()
        return f"The current time is {now.strftime('%H:%M:%S')}."
    elif "date" in user_input or "day" in user_input:
        today = date.today()
        return f"Today's date is {today.strftime('%B %d, %Y')}."
    elif "joke" in user_input:
        return get__jokes()
    elif "news" in user_input or "headlines" in user_input:
        return get_news()
    elif "calculate" in user_input or "calculator" in user_input:
        return "Try typing a math expression like '5+3' or '12 / 4'."
    elif any(op in user_input for op in ['+', '-', '*', '/']):
        try:
            result = eval(user_input.replace('what is', '').replace('=', '').strip())
            return f"Result: {result}"
        except:
            return "Invalid math expression."
    elif "bye" in user_input:
        return "Goodbye! Have a great day!"
    elif "thank" in user_input:
        return "You're welcome."
    elif user_input == "history":
        if not chat_history:
            return "No chat history yet."
        return "\n".join([f"You: {q}\nBot: {a}" for q, a in chat_history])   
    elif len(user_input.split()) <= 3 and user_input.isalpha():
        return get_weather(user_input)
    else:
        return "I'm still learning! Try asking about weather, news, jokes, or currency conversion."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({'error': 'Please provide a message'}), 400
        bot_reply = chatbot_response(user_message)
        chat_history.append((user_message, bot_reply))
        return jsonify({'response': bot_reply})
    except Exception as e:
        return jsonify({'error': f'Error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
