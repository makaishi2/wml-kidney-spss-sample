#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib3, requests, json
import os
from cfenv import AppEnv
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, request, render_template

# 認証情報の読み取り (.env または IBM Cloud上のバインド)
env = AppEnv()
pm20 = env.get_service(label='pm-20')
if pm20 is None:
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    wml_credentials = {
        "url": os.environ.get("WML_URL"),
        "username": os.environ.get("WML_USERNAME"),
        "password":  os.environ.get("WML_PASSWORD"),
        "instance_id": os.environ.get("WML_INSTANCE_ID"),
    }
else:
    wml_credentials = pm20.credentials

scoring_url = os.environ.get("SCORING_URL")

app = Flask(__name__)

print('pwd: ', os.getcwd())

@app.route('/')
def top():
    name = "Top"
    return render_template('wml-sample.html', title='Kidney Sample Web', name=name)

# 「予測」ボタンが押された時の処理
@app.route('/predict', methods=['POST'])
def predict():
    req_json = request.json
    age = req_json['AGE']
    bp = req_json['BP']
    al = req_json['AL']
    sc = req_json['SC']
    pot = req_json['POT']
    pcv = req_json['PCV']
    value1 = [None, age, bp, al, sc, pot, pcv]
    print('step3')
    print(value1)
    # トークン取得
    auth = '{username}:{password}'.format(username=wml_credentials['username'], password=wml_credentials['password'])
    headers = urllib3.util.make_headers(basic_auth=auth)
    url = '{}/v3/identity/token'.format(wml_credentials['url'])
    response = requests.get(url, headers=headers)
    print(response)
    mltoken = json.loads(response.text).get('token')
    print('mltoken = ', mltoken)
    
    # API呼出し用ヘッダ
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}
    # value1 = [75,70,0,0.8,3.5,46]
    payload_scoring = {"fields": ["CLASS", "AGE", "BP", "AL", "SC", "POT", "PCV"], "values": [value1]}

    # API呼出し
    response_scoring = requests.post(scoring_url, json=payload_scoring, headers=header)
    res = json.loads(response_scoring.text)
    print(json.dumps(res, indent=2))
    fields = res['fields']
    ret_list = res['values']
    ret = ret_list[0]
    for index, field in enumerate(fields):
        if field == '$LC-CLASS':
            prob = ret[index]
            prob = round(prob, 4)
        if field == '$L-CLASS':
            pred = ret[index]
    if pred == 'notckd':
        pred2 = 'ckd'
    else:
        pred2 = 'notckd'       
    result = {pred: prob, pred2: round((1-prob), 4)}
    print(result)      
    return(json.dumps(result))

@app.route('/favicon.ico')
def favicon():
   return ""

port = os.getenv('VCAP_APP_PORT', '8000')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(port), debug=True)