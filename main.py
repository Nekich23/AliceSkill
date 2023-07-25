from flask import Flask, request
import requests

app = Flask(__name__)
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


@app.route('/alice', methods=['POST'])
def resp():
    text = request.json.get('request', {}).get('command')
    response_text = f'Вы назвали {text}'

    if text.lower() in hi_response:
        response_text = 'Привет! Я погодный чат-бот. Приступим!'

    if text.lower() in weather_response:
        try:
            url = 'https://api.openweathermap.org/data/2.5/weather?q=' + text + \
            '&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347'

            weather_data = requests.get(url).json()

            temperature = round(weather_data['main']['main'])
            temperature_feels = round(weather_data['main']['feels_like'])

            response_text = 'В городе: ' + weather_data['weather'][0]['description'] + '\n'
            response_text += 'Сейчас в городе ' + str(text) + ': ' + str(temperature) + '°C\n'
            response_text += 'Ощущается как: ' + str(temperature_feels) + '°C'
        except:
            response_text = 'Не удалось совершить операцию!'
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
                }]
        },
        'version': '1.0'
    }
    return response


app.run('0.0.0.0', port=4001, debug=True)
