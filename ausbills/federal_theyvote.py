import os
import json
import requests

API_KEY = os.environ.get('THEYVOTE_API_KEY', None)

print(API_KEY)

response = requests.get('https://theyvoteforyou.org.au/api/v1/people.json?key='+API_KEY)


print(response.content)
