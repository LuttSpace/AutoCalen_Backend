#-*- coding: utf-8 -*-

import os
import json
import base64
import requests
import datetime
import re
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
        "version": "V2",
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
    # print(result)
    result = result["images"][0]["fields"] #list>dict>list
    result = list(map(lambda e : e["inferText"], result))
    # result = json.dumps(result,sort_keys=True, indent=2, ensure_ascii=False)
    return result



def arranging(input, tags, date_list):
  
  # _date = str(year)+str(month)+str(day)
  _date = ".".join(date_list)
  # one_input = '5월 7일 병원 10시 회의 5시 5월 11일 회의 2시 반'
  # # 빈칸 재 할당
  one_input = "".join(input)
  print('before spacing one_input : {}'.format(one_input))
  one_input = spacing(one_input)
  # print(type(one_input))
  print('after spacing one_input : {}'.format(one_input))
  one_input = re.sub(r'(\d{1,2})/(\d{1,2})', '\\1월 \\2일', one_input)  # 0/0 형태의 날짜를 0월 0일로 변경
  print('switch to 월일 : {}'.format(one_input))
  ner = Pororo(task="ner", lang="ko")
  zsl = Pororo(task="zero-topic", lang="ko")
  # one_input = "5월9일병원10시반5월11일회의2시15분" #('5월9일', 'DATE'), ('병원10시반', 'TIME'), ('5월11일', 'DATE'), ('회의2시15분', 'TIME')]
  # ner
  # date처리
 
  ner_results = ner(one_input,apply_wsd=True)
  print('ner_result : {}'.format(ner_results))

  arranged_ner_results={}
  temp=""
  date=''
  sche_results = {}
  for result in ner_results:  #result는 tuple
    if result[1] == 'DATE': # 사진에 date가 있을 때
      print(result)
      if date =='':
        # m = result[0][result[0].find('월')-1]
        # d = result[0][result[0].find('일')-1]
        temp_date = result[0].replace("일","")   #"일" 없애기
        temp_date = re.sub('월','.',temp_date)
        temp_date = temp_date.replace(" ","") # 빈칸 없애기
        # print(temp_date)
        date = date_list[0]+'.'+temp_date # 처음 나온 date  ###### 월일 형식 동일형식 문자열로 변경 필요
        # date = result[0]
      else: # 처음 나온 date가 아님
        arranged_ner_results[date] = sche_results
        sche_results={}
        # m = result[0][result[0].find('월')-1]
        # d = result[0][result[0].find('일')-1]
        temp_date = result[0].replace("일","")   #"일" 없애기
        temp_date = re.sub('월','.',temp_date)
        temp_date = temp_date.replace(" ","")  # 빈칸 없애기
        # print(temp_date)
        date = date_list[0]+'.'+temp_date 
        # date = result[0]  ###### 월일 형식 동일형식 문자열로 변경 필요
    else: # 해당 단어가 date가 아님
      print(result)
      if date=='': date = _date # 사진에 date가 없을 때
      if result[1] == 'TIME' or result[1] == 'QUANTITY':
        sche_results[temp] = result[0]
        print(sche_results)
        temp=""
      else :
         temp+=result[0]
    arranged_ner_results[date] = sche_results
  print('arranged_ner_results : {}'.format(arranged_ner_results))
  
  #zsl
  zsled_results = {}
  for date_box in arranged_ner_results.items():
    print(date_box)
    zsl_results = {}
    for sche in date_box[1]:
      print(sche)
      zsl_result = zsl(sche,tags)
      zsl_results[sche] = sorted(zsl_result.items(),key=(lambda x:x[1]),reverse=True)[0][0]
      print(zsl_results)
    zsled_results[date_box[0]] = zsl_results
  print('zsled_results : {}'.format(zsled_results))
  return arranged_ner_results, zsled_results

app = Flask(__name__)

_year = datetime.datetime.today().year        # 현재 연도 가져오기
_month = datetime.datetime.today().month      # 현재 월 가져오기  
_day = datetime.datetime.today().day

@app.route('/', methods=["GET"])
def hello_world():

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
    print('tagList : {}'.format(tagList))
    print('tagInfo : {}'.format(tagInfo))
    
    ##### ocr 호출 #####
    ocr_result = get_ocr_data(_url)
    print('ocr_result : {}'.format(ocr_result))   #list
    date_list = [str(year),str(month),str(day)]
    ner_result, zsl_result = arranging(ocr_result, tagList, date_list)

    for index, (key, value) in enumerate(ner_result.items()): #key는 date, value는 딕셔너리
      doc_date = key
      print(doc_date)
      doc_date = doc_date.split(".")
      print(doc_date)
      doc_year = int(doc_date[0])
      doc_month = int(doc_date[1])
      doc_day = int(doc_date[2])
      for inindex, (inkey, invalue) in enumerate(value.items()) : #inkey는 일정, invalue는 시간
        print('{} : {}'.format(inkey, invalue))
        start = datetime.datetime(doc_year, doc_month, doc_day, 0, 0, 0) #시간 넣어주기
        end = datetime.datetime(doc_year, doc_month, doc_day, 23, 59, 59)
        max_tag = zsl_result[key][inkey] #최적 tag
        doc = db.collection('UserList').document(_id).collection('ScheduleHub').document()
        doc.set({
            # u'title': inkey+' '+invalue,  # pororo결과 넣기..
            u'title': inkey+' '+invalue,  # pororo결과 넣기..
            u'isAllDay' : True,
            u'tag' : {
                u'color' : tagInfo[max_tag]['tagcolor'],
                u'name' : max_tag,
                u'tid' : tagInfo[max_tag]['tagid']
            },
            u'start' : start - datetime.timedelta(hours=9),
            u'end' : end - datetime.timedelta(hours=9),
            u'memo' : None,
        })





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


