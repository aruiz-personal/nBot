# Llama a la API de Trend

import base64
import jwt
import hashlib
import requests
import time
import json

def create_checksum(http_method, raw_url, headers, request_body):
    string_to_hash = http_method.upper() + '|' + raw_url.lower() + '|' + headers + '|' + request_body
    base64_string = base64.b64encode(hashlib.sha256(str.encode(string_to_hash)).digest()).decode('utf-8')
    return base64_string

def create_jwt_token(appication_id, api_key, http_method, raw_url, headers, request_body,
                     iat=time.time(), algorithm='HS256', version='V1'):
    payload = {'appid': appication_id,
               'iat': iat,
               'version': version,
               'checksum': create_checksum(http_method, raw_url, headers, request_body)}
    token = jwt.encode(payload, api_key, algorithm=algorithm).decode('utf-8')
    return token 
	
# Use this region to setup the call info of the Apex Central server (server url, application id, api key)

productAgentAPIPath = '/WebApp/api/SuspiciousObjects/UserDefinedSO/'
# productAgentAPIPath = '/WebApp/api/v1/SuspiciousObjects/UserDefinedSO/'

def send_ioc_cloud(tipo,content,notes,scan_action):
    # server info
    # server info
    use_url_base = '' 
    use_application_id = ''
    use_api_key = ''

    canonicalRequestHeaders = ''
    useQueryString = '' 

    payload = {
        "param":{
            "type":tipo,
            "content":content,
            "notes":notes,
            "scan_action":scan_action
        }
    }

    useRequestBody = json.dumps(payload)  
 
    jwt_token = create_jwt_token(use_application_id, use_api_key, 'PUT',
                              productAgentAPIPath + useQueryString,
                              canonicalRequestHeaders, useRequestBody, iat=time.time())

    headers = {'Authorization': 'Bearer ' + jwt_token, 'Content-Type': "application/json"}

    #Choose by call type. 
    r = requests.put(use_url_base + productAgentAPIPath + useQueryString, headers=headers, data=useRequestBody, verify=False) 

    print(r.status_code)
   # print(json.dumps(r.json(), indent=4))
