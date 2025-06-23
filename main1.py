import json, time, os
import pyttsx3, pyaudio, vosk
import requests


class Speech:
    def __init__(self):
        self.speaker = 0
        self.tts = pyttsx3.init('sapi5')
        self.voices = self.tts.getProperty('voices')

    def text2voice(self, text='Готов'):
        self.tts.say(text)
        self.tts.runAndWait()


class Recognize:
    def __init__(self):
        model_path = os.path.abspath('Python-Lab-10/vosk-model-small-ru-0.22')
        model = vosk.Model(model_path)
        self.record = vosk.KaldiRecognizer(model, 16000)
        self.stream()

    def stream(self):
        pa = pyaudio.PyAudio()
        self.stream = pa.open(format=pyaudio.paInt16,
                         channels=1,
                         rate=16000,
                         input=True,
                         frames_per_buffer=8000)


    def listen(self):
        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.record.AcceptWaveform(data) and len(data) > 0:
                answer = json.loads(self.record.Result())
                if answer['text']:
                    yield answer['text']


class UserAssistant:
    def __init__(self):
        self.user = None
        self.photo_path = None

    def create_user(self):
        try:
            response = requests.get('https://randomuser.me/api/')
            data = response.json()
            self.user = data['results'][0]
            print(self.user)
            self.photo_path = None
            return 'Пользователь создан успешно'
        except Exception as e:
            print('Ошибка при создании пользователя:', e)
            return 'Ошибка при создании пользователя'

    def get_name(self):
        if not self.user:
            return 'Сначала создайте пользователя.'
        name = self.user['name']
        return f"{name['title']} {name['first']} {name['last']}"

    def get_country(self):
        if not self.user:
            return 'Сначала создайте пользователя.'
        return self.user['location']['country']

    def get_profile(self):
        if not self.user:
            return 'Сначала создайте пользователя.'
        name = self.get_name()
        country = self.get_country()
        age = self.user['dob']['age']
        email = self.user['email']
        return f"Имя: {name}. Страна: {country}. Возраст: {age}. Email: {email}."

    def save_photo(self):
        if not self.user:
            return 'Сначала создайте пользователя.'
        url = self.user['picture']['large']
        try:
            response = requests.get(url)
            photo_path = os.path.join(os.getcwd(), 'Python-Lab-10/user_photo.jpg')
            with open(photo_path, 'wb') as f:
                f.write(response.content)
            self.photo_path = photo_path
            return f'Фото сохранено'
        except Exception as e:
            return f'Ошибка при сохранении фото: {e}'


speech = Speech()

rec = Recognize()
text_gen = rec.listen()
rec.stream.stop_stream()

speech.text2voice('Голосовой ассистент запущен')

time.sleep(0.5)
rec.stream.start_stream()

assistant = UserAssistant()
commands = {
    'создать': assistant.create_user,
    'имя': assistant.get_name,
    'страна': assistant.get_country,
    'анкета': assistant.get_profile,
    'сохранить': assistant.save_photo
}

for text in text_gen:
    if text == 'закрыть':
        speech.text2voice('Бывай, ихтиандр')
        quit()
    elif text in commands.keys():
        gen = commands[text]()
        rec.stream.stop_stream()
        speech.text2voice(gen)
        time.sleep(0.5)
        rec.stream.start_stream()
    else:
        print(f"Неизвестная команда: {text}")
