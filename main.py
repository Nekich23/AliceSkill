from flask import Flask, request
import requests
from pyowm import OWM
from translate import Translator


translator = Translator(from_lang='en', to_lang='ru')

app = Flask(__name__)

owm = OWM('1319c8dd2276b010e23222a923fa6c24')
mgr = owm.weather_manager()

hi_response = [
    'привет',
    'здравствуйте',
    'hello'
]
weather_response = [
    'погода',
    'хочу узнать погоду',
    'инфо о погоде'

]
city_response = [
    'запомнить город',
    'город',
    'сохранить город'
]
savedCity_response = [
    'инфо в сохранённом',
    'погода в городе',
    'погода в сохранённом городе'
]

s = 0
savedCity = ''
saving = savedCity

@app.route('/alice', methods=['POST'])
def resp():
    global s
    global savedCity
    global saving
    text = request.json.get('request', {}).get('command')
    response_text = f'Вы назвали {text}'

    # связка функций через условия
    if text.lower() in hi_response:
        response_text = 'Привет! Я погодный чат-бот. Приступим!'

    elif text.lower() in weather_response and s == 0:
        s = 1
        response_text = 'Введи название города: '

    elif text.lower() in city_response and s == 0:
        s = 2
        response_text = 'Введи название города: '

    elif text.lower() in savedCity_response and s == 0:
        s = 3
        response_text = 'Сохранённый город: ' + savedCity

    # логика основных функций
    elif s == 1:
        city = str(request.json.get('request', {}).get('command'))
        observation = mgr.weather_at_place(city)
        w = observation.weather

        celsius = round(w.temperature('celsius')['temp'])
        temperature = round(celsius)
        temperature_feels = celsius - 1
        answer = translator.translate(w.detailed_status) + '\n'
        answer += 'Сейчас в городе ' + str(city) + ' ' +  str(temperature) + '°C\n'
        answer += 'Ощущается как ' + str(temperature_feels) + '°C\n'
        answer += 'Скорость ветра ' + str(w.clouds) + ' м/c\n'
        answer += 'Тумманность ' + str(w.humidity) + '%'

        response_text = answer
        s = 0

    elif s == 2:
        saving = str(request.json.get('request', {}).get('command'))
        if saving.lower() != '' or ' ' or 0 or '0':
            savedCity = saving
            response_text = 'Сохранённый город: ' + savedCity
        else:
            response_text = 'Город не указан!'

    elif s == 3:
        city = savedCity

        url = 'https://api.openweathermap.org/data/2.5/weather?q=' + city + '&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347'

        weather_data = requests.get(url).json()

        temperature = round(weather_data['main']['temp'])
        temperature_feels = round(weather_data['main']['feels_like'])
        answer = weather_data['weather'][0]['description'] + '\n'
        answer += 'Сейчас в городе' + str(city) + ' ' + str(temperature) + '°C\n'
        answer += 'Ощущается как' + ' ' + str(temperature_feels) + '°C\n'

        response_text = answer

    response = {
        'response': {
            'text': response_text,
            'end_session': False,
            'buttons': [
                {
                    'title': 'Привет 👋',
                    'hide': True
                },
                {
                    'title': 'Погода ☔',
                    'hide': True
                },
                {
                    'title': 'Сохранить город 🏙',
                    'hide': True
                },
                {
                    'title': 'Погода в сохранённом городе 🌆',
                    'hide': True
                }]
        },
        'version': '1.0'
    }
    return response


app.run('0.0.0.0', port=4100, debug=True)
