import os
from google import genai
client = genai.Client(api_key='AIzaSyBaXt09sOEcI0p39GwCmsn25LDdsMS-JH8')
for m in client.models.list():
    if 'embed' in m.name.lower():
        print(m.name)
