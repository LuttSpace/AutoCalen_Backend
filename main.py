#-*- coding: utf-8 -*-

import os
import json
import base64
import requests
import datetime
from pororo import Pororo
from flask import Flask, request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from pykospacing import spacing

##### naverocr 연결 #####
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# print(BASE_DIR)
secret_file = os.path.join(BASE_DIR, "ncpocr.json")
# print(secret_file)
with open(secret_file) as f:
    secrets = json.loads(f.read())
    # print(secrets)

##### firebase 연결 #####
cred = credentials.Certificate('autocalen.json')
firebase_admin.initialize_app(cred, {
    'projectId' : 'autocalen-1c7f1'
})

db = firestore.client()

##### naver ocr 호출 #####
def get_ocr_data(_url):
    # 본인의 APIGW Invoke URL로 치환
    URL = secrets["APIGWInvokeURL"]
        
    # 본인의 Secret Key로 치환
    KEY = secrets["secretkey"]
        
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
    result = requests.post(URL, data=json.dumps(data), headers=headers).json() #딕셔너리
    result = result["images"][0]["fields"] #list>dict>list
    result = list(map(lambda e : e["inferText"], result))
    # result = json.dumps(result,sort_keys=True, indent=2, ensure_ascii=False)
    return result



def arranging(input, tags, year, month, day):
  
  date = str(year)+str(month)+str(day)
  # 빈칸 재 할당
  one_input = "".join(input)
  print(one_input)
  one_input=spacing(one_input)
  print(type(one_input))
  print(one_input)

  ner = Pororo(task="ner", lang="ko")
  zsl = Pororo(task="zero-topic", lang="ko")
  # ner
  # date처리
  ner_results = ner(one_input,apply_wsd=True)
  arranged_ner_results={}
  temp=""
#   date=''
  sche_results={}
  for result in ner_results:
    if result[1] == 'DATE': # 사진에 date가 있을 때
      print(result)
      if date=='': date= result[0] # 처음 나온 date
      else: # 처음 나온 date가 아님
        arranged_ner_results[date]=sche_results
        sche_results={}
        date = result[0]
    else: # 해당 단어가 date가 아님
      print(result)
      if date=='': date= date # 사진에 date가 없을 때
      if result[1] == 'TIME':
        sche_results[temp]=result[0]
        print(sche_results)
        temp=""
      else :
         temp+=result[0]
    arranged_ner_results[date]=sche_results
  print(arranged_ner_results)
  
  #zsl
  zsled_results={}
  for date_box in arranged_ner_results.items():
    print(date_box)
    zsl_results={}
    for sche in date_box[1]:
      print(sche)
      zsl_result=zsl(sche,tags)
      zsl_results[sche]=sorted(zsl_result.items(),key=(lambda x:x[1]),reverse=True)[0][0]
      print(zsl_results)
    zsled_results[date_box[0]]=zsl_results
  print(zsled_results)

app = Flask(__name__)

@app.route('/', methods=["GET"])
def hello_world():
    _year = datetime.datetime.today().year        # 현재 연도 가져오기
    _month = datetime.datetime.today().month      # 현재 월 가져오기  
    _day = datetime.datetime.today().day 
    ##### flutter 앱으로부터 이미지 url 받기 #####
    _url = request.args.get("_url", "https://i.imgur.com/EJ0mOeK.jpg")
    _id = request.args.get("_id", "5NxFVmOkPhPx62Y2Xl2xWDmpSoN2")
    year = int(request.args.get("year",_year))
    month = int(request.args.get("month",_month))
    day = int(request.args.get("day",_day))
    # print('{} , {}\n{}, {}, {}'.format(_url,_id,year,month,day))

    ##### user의 tag를 read #####
    tagList = []
    tagInfo = {}
    collections = db.collection('UserList').document(_id).collection('TagHub')
    # print(collections) # CollectionReference
    for doc in collections.stream():
        # print(doc)  # DocumentSnapshot Object
        # print(u'{} => {} / {}'.format(doc.id, doc.get('color'), doc.get('name')))
        # print(u'{} => {}'.format(doc.id, doc.to_dict()))
        name = doc.get('name')
        color = doc.get('color')
        tagList.append(name)
        tagInfo[name] = { "tagid" : doc.id, "tagcolor" : color}
    print(tagList)
    print(tagInfo)
    
    ##### ocr 호출 #####
    ocr_result = get_ocr_data(_url)
    print(ocr_result)   #list
    print(spacing("".join(ocr_result)))
    arranging(ocr_result, tagList, year, month, day)

    ##### ocr 결과 가공해서 pororo 호출 #####
    # ner = Pororo(task="ner", lang="ko")
    # zsl = Pororo(task="zero-topic", lang="ko")
    # zsl_result = zsl(ocr_result[0],tagList)
    # print(zsl_result)

    # ##### pororo 결과 가공해서 최적의 tag search #####
    # max_tag = max(zsl_result.keys(), key=(lambda k:zsl_result[k]))
    # print(max_tag)
    # # print(tagInfo[max_tag])

    ##### user의 schedule에 write #####
    ##### isAllDay 결정 #####
    # isAllDay = True
    # if day != -1:
    #     isAllDay = False
    # ##### 날짜 시간 결정 #####
    # ##### ocr 결과에 따라서 time 로직 추가 필요!!!!!!
    # start = datetime.datetime(year, month, day, 13, 0, 0)
    # end = datetime.datetime(year, month, day, 22, 0, 0)
    # doc = db.collection('UserList').document(_id).collection('ScheduleHub').document()
    # doc.set({
    #     # u'title': u'졸작회의',  # pororo결과 넣기..
    #     u'title': ocr_result[0],  # pororo결과 넣기..
    #     u'isAllDay' : isAllDay, #day -1인경우
    #     u'tag' : {
    #         u'color' : tagInfo[max_tag]['tagcolor'],
    #         u'name' : max_tag,
    #         u'tid' : tagInfo[max_tag]['tagid']
    #     },
    #     u'start' : start - datetime.timedelta(hours=9),
    #     u'end' : end - datetime.timedelta(hours=9),
    #     u'memo' : None,
    # })

    return 'Hello'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)



    # collections = db.collection('UserList').document('5NxFVmOkPhPx62Y2Xl2xWDmpSoN2').collection('ScheduleHub')
    # # print(collections) # CollectionReference
    # for doc in collections.stream():
    #     # print(doc)  # DocumentSnapshot Object
    #     # tag = doc.get('tag')
    #     # print(type(tag))
    #     print(u'{} => {}'.format(doc.id, doc.to_dict()))
    #     # print(f'Document data: {doc.get('start')}')


