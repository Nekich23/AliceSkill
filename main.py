from flask import Flask, request
from pyowm import OWM
from translate import Translator

translator = Translator(from_lang='en', to_lang='ru')

app = Flask(__name__)

owm = OWM('a1190779fb61715499b46fb3a68166b4')
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
clothes_response = [
    'дай рекомендацию по одежде',
    'рекомендации по одежде',
    'рекомендация по одежде'
]
tommorow_response = [
    'прогноз погоды'
]

s = 0


@app.route('/alice', methods=['POST'])
def resp():
    global s
    text = request.json.get('request', {}).get('command')
    response_text = f'Вы назвали {text}'

    # связка функций через условия
    if text.lower() in hi_response:
        response_text = 'Привет! Я погодный чат-бот. Приступим!'

    elif text.lower() in weather_response and s == 0:
        s = 1
        response_text = 'Введи название города: '

    elif text.lower() in clothes_response and s == 0:
        s = 2
        response_text = 'Введи название города: '

    elif text.lower() in tommorow_response and s == 0:
        s = 3
        response_text = 'Введи название города: '

    # логика основных функций
    elif s == 1:
        city = str(request.json.get('request', {}).get('command'))
        observation = mgr.weather_at_place(city)
        w = observation.weather

        celsius = round(w.temperature('celsius')['temp'])
        temperature = round(celsius)
        temperature_feels = celsius - 1
        answer = translator.translate(w.detailed_status) + '\n'
        answer += 'Сейчас в городе ' + str(city) + ' ' + str(temperature) + '°C\n'
        answer += 'Ощущается как ' + str(temperature_feels) + '°C\n'
        answer += 'Скорость ветра ' + str(w.clouds) + ' м/c\n'
        answer += 'Тумманность ' + str(w.humidity) + '%'

        response_text = answer
        s = 0

    elif s == 2:
        city = str(request.json.get('request', {}).get('command'))
        observation = mgr.weather_at_place(city)
        w = observation.weather

        celsius = round(w.temperature('celsius')['temp'])
        temperature = round(celsius)
        temperature_feels = celsius - 1
        answer = translator.translate(w.detailed_status) + '\n'
        answer += 'Сейчас в городе ' + str(city) + ' ' + str(temperature) + '°C\n'
        answer += 'Ощущается как ' + str(temperature_feels) + '°C\n'
        answer += 'Скорость ветра ' + str(w.wind()['speed']) + ' м/c\n'
        answer += 'Тумманность ' + str(w.humidity) + '%\n\n'

        if temperature_feels >= 15 and int(w.wind()['speed']) >= 40:
            answer += 'Ветренно! 🍃 Советую надеть:' \
                      '\n-Ветровка 🧥' \
                      '\n-Кепка с капюшоном(шапка) 🧢' \
                      '\n-Джинсы 👖' \
                      '\n-Кросовки 👞'
        elif temperature_feels >= 15 and int(w.wind()['speed']) <= 40:
            answer += 'Очень оптимальная погода! 🌞 Советую надеть: ' \
                      '\n-Кофта 👘' \
                      '\n-Шорты 🩳' \
                      '\n-Лёгкие кросовки 👞'
        elif temperature_feels >= 25:
            answer += 'Вот это жарко! ☀☀☀ Советую надеть: ' \
                      '\n-Майка(футболка) 👕' \
                      '\n-Шорты 🩳' \
                      '\n-Кросовки 👞'
        elif 'дождь' in translator.translate(w.detailed_status):
            answer += 'На улице дождь! 🌧⛈ Советую надеть: ' \
                      '\n-Пальто 🧥' \
                      '\n-Кепка с капюшоном 🧢' \
                      '\n-Ботинки для дождя 👞' \
                      '\n-Тёплые штаны 👖'
        elif temperature_feels <= 15:
            answer += 'Холодно! ❄ Советую надеть: ' \
                      '\n-Куртка(теплая курта) 🧥' \
                      '\n-Шапка 👲' \
                      '\n-Ботинки 👞' \
                      '\n-Тёплые штаны 👖'
        s = 0

        response_text = answer

    elif s == 3:
        city = str(request.json.get('request', {}).get('command'))

        monitoring = owm.weather_manager().weather_at_place(city)
        weather = monitoring.weather
        status = weather.detailed_status
        temperaturestatus = weather.temperature('celsius')['temp']

        response_text = 'В ближайшее время в городе ' + str(city) + ' ожидается: ' + str(translator.translate(status))
        response_text += '\nТемпература: ' + str(temperaturestatus)
        response_text += '\nСкорость ветра ожидается: ' + str(weather.wind()['speed']) + ' м/с'
        
        if temperaturestatus >= 15:
            response_text += '\n\nБудет тепло! 😎☀'
        elif temperaturestatus <= 15:
            response_text += '\n\nБудет холодно! 🥶❄'

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
                    'title': 'Рекомендации по одежде 🧥',
                    'hide': True
                },
                {
                    'title': 'Прогноз погоды 📅',
                    'hide': True
                }]
        },
        'version': '1.0'
    }
    return response


app.run('0.0.0.0', port=4150, debug=True)
