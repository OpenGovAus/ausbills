import os
import json
import requests


API_KEY = os.environ.get('THEYVOTE_API_KEY', None)

response = requests.get('https://theyvoteforyou.org.au/api/v1/people.json?key='+API_KEY)

current_people = json.loads(response.content)

"""
{'id': 10947, 'latest_member': {'id': 100906, 'name': {'first': 'Perin', 'last': 'Davey'}, 'electorate': 'NSW', 'house': 'senate', 'party':
'National Party'}}
"""

for person in current_people:
    print(person['id'], person['latest_member']['name']
          ['first'], person['latest_member']['name']['last'])
