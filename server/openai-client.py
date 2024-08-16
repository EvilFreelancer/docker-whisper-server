from openai import OpenAI

client = OpenAI(base_url='http://127.0.0.1:5000', api_key='<key>')

file = open("audio.mp3", "rb")
model = 'tiny'

test = client.audio.transcriptions.create(file=file, model=model)
print(test.text)
