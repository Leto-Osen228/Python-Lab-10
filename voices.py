import pyttsx3
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
for i, voice in enumerate(voices):
    print(f"{i}: {voice.id} | {voice.name} | {voice.languages}")