import json
import requests

PATTERN_URL = 'http'
URL = 'rikka.e:5000'

def request_krionard(tokens):
    token_list = '"' + '", "'.join(tokens) + '"'
    json_input_string = '''{
  "request": {
    "command": "''' + ' '.join(tokens) + ''''",
    "nlu": {
      "tokens": [
        ''' + token_list + '''
      ]
    }
  },
  "session": {
    "session_id": "574d41e0-a41e-4028-a73a-6f5b5bfed299",
    "user_id": "11c5d2e04b28077d3b2a385b8c332b2f3f261fab10e88b539512e68ccd80a294",
    "new": true,
    "message_id": 0
  },
  "version": "1.0"
}'''
    print(json_input_string)
    try:
        response = requests.post('%s://%s/omega/' % (PATTERN_URL, URL), json=json.loads(json_input_string))
    except Exception as ex:
        print('Error request to krionard:', ex)
        return ('Error request omega server to krionard\n', -1)
    print('Status: ', response)
    json_response = json.loads(response.text)
    print('Json response: ', json_response)
    print('Code:', json_response['response']['code'])
    return (json_response['response']['tts'] + '\n' + str(json_response['response']['code']) + '\n')
