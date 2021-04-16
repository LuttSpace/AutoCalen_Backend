# -*- coding: utf-8 -*-
# import firebase_admin
import json
import base64
import requests
from pororo import Pororo
from flask import Flask, request

######## naver ocr 호출 ########
def get_ocr_data(_url):
    # 본인의 APIGW Invoke URL로 치환
    URL = "https://bd93513273b346afb64b27d4f20e7ab2.apigw.ntruss.com/custom/v1/7789/c7b68ac37f364473e922936708e7f43c293dd07b295171566c07ff5fe024fab9/general"
        
    # 본인의 Secret Key로 치환
    KEY = "YWd6d1dyRktDamdEc2dGRGpoa0dEQXVFVkZzSE1tY2g="
        
    headers = {
        "Content-Type": "application/json",
        "X-OCR-SECRET": KEY
    }
        
    data = {
        "lang": "ko",
        "version": "V1",
        "requestId": "sample_id", # 요청을 구분하기 위한 ID, 사용자가 정의
        "timestamp": 0, # 현재 시간값
        "resultType": "string",
        "images": [
            {
                "name": "sample_image",
                "format": "jpg",
                "data": None,
                "url" : _url #받은 url로 치환
            }
        ]
    }
    # data = json.dumps(data)
    result = requests.post(URL, data=json.dumps(data), headers=headers)
    result = result.json()
    # print("{}\n".format(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False)))
    result = json.dumps(result,sort_keys=True, indent=2, ensure_ascii=False)
    
    # res = json.loads(response)
    # print("[OCR] output:\n{}\n".format(json.dumps(response, sort_keys=True, indent=2)))
    # response = json.dumps(response).decode('utf-8')
    return result

    #  output = kakao_ocr(image_path, appkey).json()
    #  print("[OCR] output:\n{}\n".format(json.dumps(output, sort_keys=True, indent=2)))

app = Flask(__name__)

@app.route('/', methods=["GET"])
def hello_world():
    ######## flutter 앱으로부터 이미지 url 받기 ########
    _url = request.args.get("_url", "https://i.imgur.com/DZcyDFu.jpg")
    result = get_ocr_data(_url)
    
    ####### ocr 결과 가공해서 pororo 호출 #######
    # sts = Pororo(task="similarity", lang="ko")
    # result = sts(first,second)

    ####### pororo 결과 가공해서 firestore에 넣기 ######
    return result


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

# default_app = firebase_admin.initialize_app()
# export GOOGLE_APPLICATION_CREDENTIALS="/home/user/Downloads/service-account-file.json"

# with open("../img/DZcyDFu.jpg", "rb") as f:
#     img = base64.b64encode(f.read())





####### ocr 결과 가공해서 pororo 호출 #######
# sts = Pororo(task="similarity", lang="ko")
# result = sts(first,second)

####### pororo 결과 가공해서 firestore에 넣기 ######