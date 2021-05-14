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
# from pykospacing import spacing

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
    # result = requests.post(URL, data=json.dumps(data), headers=headers).json() #딕셔너리
    # # print(result)
    # result = result["images"][0]["fields"] #list>dict>list
    # # print(result)
    # result = list(map(lambda e : e["inferText"], result))
    # print(result)
    # # result = json.dumps(result,sort_keys=True, indent=2, ensure_ascii=False)
    # return result

    ## new approach
    results_list = []
    result = requests.post(URL, data=json.dumps(data), headers=headers).json()
    result = result["images"][0]["fields"]
    result_list = []
    for e in result:
      if e["lineBreak"] == False:
        result_list.append(e["inferText"])
      else :
        result_list.append(e["inferText"])
        results_list.append(result_list)
        result_list = []
    print('ocr_result : {}'.format(results_list))
    return results_list


def spacing_data(input) :
  # one_input = "".join(input[i]) # 하나로 합치기
  # one_input = re.sub(r'(\d{1,2})/(\d{1,2})', '\\1월 \\2일', one_input)
  # print('transfer date(before spacing) : {}'.format(one_input))
  # # ####### 이부분에..시간 바꿔야할 듯..
  # one_input = spacing(one_input)
  # print('after spacing : {}'.format(one_input))
  # input[i] = one_input

  ##### new approach
  ### 오윈 공백 제거
  for i in range(len(input)):
    for j in range(len(input[i])):
      input[i][j] = input[i][j].lstrip()
      input[i][j] = input[i][j].rstrip()
  # print('오/왼 공백 제거 : {}'.format(input))

  time_list = []
  for i in range(len(input)):
    ##### spacing 말고 다른 방법
    one_input = " ".join(input[i]) # 하나로 합치기
    ##### 월일 변경
    one_input = re.sub(r'(\d{1,2})/(\d{1,2})', '\\1월\\2일', one_input)
    ##### time 찾고 변경
    match_str1 = re.search("(\d{1,2})[\s]?시[\s]?(\d{1,2})[\s]?분[\s]?(am|pm|AM|PM)?",one_input)   #n시m분
    match_str2 = re.search("(\d{1,2})[\s]?시[\s]?반[\s]?(am|pm|AM|PM)?",one_input)  #n시반
    match_str3 = re.search("(\d{1,2})[\s]?시[\s]?(am|pm|AM|PM)?", one_input)  #n시
    match_str4 = re.search("(\d{1,2})[\s]?:[\s]?(\d{1,2})[\s]?분[\s]?(am|pm|AM|PM)?", one_input) #n:m분
    match_str5 = re.search("(\d{1,2})[\s]?:[\s]?(\d{1,2})[\s]?(am|pm|AM|PM)?", one_input) #n:m
    match_str6 = re.search("(\d{1,2})[\s]?(am|pm|AM|PM)", one_input) #nam/pm

    if match_str1:
      m = match_str1.group()
      # print(m)
      time_list.append(m)
      # print(time_list)
      copy_m = re.sub("(am|pm|AM|PM)","",m) # am,pm 제거
      copy_m = copy_m.replace(" ","")
      one_input = re.sub(m,copy_m,one_input)
    elif match_str2:
      m = match_str2.group()
      # print(m)
      time_list.append(m)
      # print(time_list)
      copy_m = re.sub("(am|pm|AM|PM)","",m) # am,pm 제거
      copy_m = copy_m.replace(" ","")
      one_input = re.sub(m,copy_m,one_input)
    elif match_str3:
      m = match_str3.group()
      # print(m)
      time_list.append(m)
      # print(time_list)
      copy_m = re.sub("(am|pm|AM|PM)","",m) # am,pm 제거
      copy_m = copy_m.replace(" ","")
      one_input = re.sub(m,copy_m,one_input)
    elif match_str4:
      m = match_str4.group()
      # print(m)
      time_list.append(m) # 원본
      # print(time_list)
      copy_m = m.replace(":","시")
      copy_m = re.sub("(am|pm|AM|PM)","",copy_m) # am,pm 제거
      copy_m = copy_m.replace(" ","")
      one_input = re.sub(m,copy_m,one_input)
    elif match_str5:
      m = match_str5.group()
      # print(m)
      time_list.append(m)
      copy_m = re.sub("(\d{1,2})[\s]?:[\s]?(\d{1,2})", "\\1시\\2분", m) #n시m분으로 변경
      copy_m = re.sub("(am|pm|AM|PM)","",copy_m) # am,pm 제거
      copy_m = copy_m.replace(" ","")
      one_input = re.sub(m,copy_m,one_input)
    elif match_str6:
      m = match_str6.group()
      # print('6번째 : {}'.format(m))
      time_list.append(m)
      # print(time_list)
      copy_m = re.sub("(am|pm|AM|PM)","시",m) # am,pm 제거 후 시로 변경
      # print(copy_m)
      copy_m = copy_m.replace(" ","")
      # print(copy_m)
      # one_input = re.sub(m,copy_m,one_input)
      one_input = one_input.replace(m,copy_m)
    else: #필터링 안된 time
      time_list.append('')
    input[i] = one_input
  print('spacing_result with change date : {}'.format(input))
  print('time_list : {}'.format(time_list))
  return input, time_list

  ############################
  # # 빈칸 재 할당
  # one_input = "".join(input)
  # print('before spacing one_input : {}'.format(one_input))
  # one_input = re.sub(r'(\d{1,2})/(\d{1,2})', '\\1월 \\2일', one_input)
  # one_input = one_input.replace(" ","")
  # print('switch to 월일 : {}'.format(one_input))

  # one_input = "6월1일병원9시점심약속1pm.6월2일운동3:30pm회의5시pm수영8시술약속9pm."
  # one_input = spacing(one_input)
  # # print(type(one_input))
  # print('after spacing one_input : {}'.format(one_input))
  # # one_input = re.sub(r'(\d{1,2})/(\d{1,2})', '\\1월 \\2일', one_input)  # 0/0 형태의 날짜를 0월 0일로 변경
  # # print('switch to 월일 : {}'.format(one_input))
  # return one_input

def doing_ner(input, date_list):
  # _date = str(year)+str(month)+str(day)
  _date = ".".join(date_list)

  # # one_input = '5월 7일 병원 10시 회의 5시 5월 11일 회의 2시 반'
  # # # 빈칸 재 할당
  # one_input = "".join(input)
  # print('before spacing one_input : {}'.format(one_input))
  # one_input = spacing(one_input)
  # # print(type(one_input))
  # print('after spacing one_input : {}'.format(one_input))
  # one_input = re.sub(r'(\d{1,2})/(\d{1,2})', '\\1월 \\2일', one_input)  # 0/0 형태의 날짜를 0월 0일로 변경
  # print('switch to 월일 : {}'.format(one_input))

  # one_input = "5월9일병원10시반5월11일회의2시15분" #('5월9일', 'DATE'), ('병원10시반', 'TIME'), ('5월11일', 'DATE'), ('회의2시15분', 'TIME')]
  # ner
  # date처리
  # ner_results = ner(one_input,apply_wsd=True)
  # print('ner_result : {}'.format(ner_results))

  # one_input = ""
  # for i in input:
  #   one_input = one_input+i+"  "
  # print('one_input: {}'.format(one_input))
  # ner_results = ner(one_input,apply_wsd=True)
  # print('ner_result : {}'.format(ner_results))

  ner_results = []
  for i in input:
    one_input = ner(i,apply_wsd=True)
    ner_results.append(one_input)
  print('ner_result : {}'.format(ner_results)) # 2차원 배열
  
  ##### 아침, 점심, 저녁 처리
  for i1,v1 in enumerate(ner_results):  # i1 : index / v1 : 배열
    print('before ner[{}] result : {}'.format(i1, v1))
    for i2, v2 in enumerate(v1): # i2 : index / v2 : tuple -> ner 배열을 순회
      if v2[1] == 'DATE' and re.search("(\d{1,2})(\s)?월(\s)?(\d{1,2})(\s)?일", v2[0]) == None:  # 잘못된 DATE
        ner_results[i1][i2] = (v2[0],'O')
      if v2[1] == 'TIME':
        if re.search("(\d{1,2})(\s)?시(\s)?(\d{1,2})?(\s)?(분|반)?", v2[0]):  #n시(n분/반) 형태가 있다
          tuple_t = len(v2[0].lstrip().rstrip())
          d = re.search("(\d{1,2})(\s)?시(\s)?(\d{1,2})?(\s)?(분|반)?", v2[0])
          s, e = d.span()
          reg_t = e-s+1
          if tuple_t > reg_t :  #TIME에 n시(n분/반) 형태 말고 다른 값이 껴있음
            t1 = (v2[0][:s], 'O')
            t2 = (v2[0][s:], 'TIME')
            ner_results[i1][i2] = t1
            ner_results[i1].insert(i2+1,t2)
            # if len(v2[0])-1 > e :
            #   t2 = (v2[0][s:e+1], 'TIME')
            #   t3 = (v2[0][e+1:], 'O')
            #   ner_results[i1][i2] = t1
            #   ner_results[i1].insert(i2+1,t2)
            #   ner_results[i1].insert(i2+2,t3)
            # else:
            #   t2 = (v2[0][s:], 'TIME')
            #   ner_results[i1][i2] = t1
            #   ner_results[i1].insert(i2+1,t2)
          else : #TIME에 맞는 형식 -> n시(n분/반) 형태
            pass
        else :  # 잘못된 형식의 TIME -> n시(n분/반) 형태가 아님
          ner_results[i1][i2] = (v2[0],'O')
    t_list = [e[1] for e in v1]
    if 'TIME' not in t_list:
      v1.append(('','TIME'))
    print('after ner[{}] result : {}'.format(i1, v1))  
  print('changed_ner_results : {}'.format(ner_results))

  # ##### 아침, 점심, 저녁 처리
  # for i1,v1 in enumerate(ner_results):  # i1 : index / v1 : 배열
  #   for i2, v2 in enumerate(v1): # i2 : index / v2 : tuple
  #   # print(i)
  #     if v2[1] == 'DATE' and re.search("(\d{1,2})(\s)?월(\s)?(\d{1,2})(\s)?일", v2[0]) == None:  # 잘못된 DATE
  #       ner_results[i1][i2] = (v2[0],'O')
  #     if re.search("(아침|점심|저녁)", v2[0]):
  #       # print(v)
  #       if re.search("(\d{1,2})(\s)?시(\s)?(\d{1,2})?(\s)?(분|반)?", v2[0]):
  #         # print(ner_results[i])
  #         d = re.search("(\d{1,2})(\s)?시(\s)?(\d{1,2})?(\s)?(분|반)?", v2[0])
  #         # print(d.group())
  #         ds = d.start()
  #         t1 = (v2[0][:ds], 'O')
  #         t2 = (v2[0][ds:], 'TIME')
  #         ner_results[i1][i2] = t1
  #         ner_results[i1].insert(i2+1,t2)
  #       else :
  #           ner_results[i1][i2] = (v2[0],'O')
  #   t_list = [e[1] for e in v1]
  #   if 'TIME' not in t_list:
  #     v1.append(('','TIME'))
  #   # print(ner_results)
  #   # print(len(ner_results))
  # print('changed_ner_results : {}'.format(ner_results))

  #### ner 결과 1차원으로
  ner_results = [element for array in ner_results for element in array]
  print('1D ner_results : {}'.format(ner_results))
  
  arranged_ner_results={}
  temp=""
  date=''
  sche_results = {}
  for result in ner_results:  #result는 tuple
    if result[1] == 'DATE': # 사진에 date가 있을 때
      # print(result)
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
      # print(result)
      if date=='': date = _date # 사진에 date가 없을 때
      if result[1] == 'TIME':
        temp = temp.lstrip().rstrip()
        sche_results[temp] = result[0]
        # print(temp)
        # print(sche_results)
        temp=""
      else :
         temp+=result[0]
        #  print(temp)
    arranged_ner_results[date] = sche_results
  print('arranged_ner_results : {}'.format(arranged_ner_results))

  return arranged_ner_results  


def doing_zsl(arranged_ner_results, tags):
  #zsl
  zsled_results = {}
  for date_box in arranged_ner_results.items():
    # print(date_box)
    zsl_results = {}
    for sche in date_box[1]:
      # print(sche)
      zsl_result = zsl(sche,tags)
      zsl_results[sche] = sorted(zsl_result.items(),key=(lambda x:x[1]),reverse=True)[0][0]
      # print(zsl_results)
    zsled_results[date_box[0]] = zsl_results
  print('zsled_results : {}'.format(zsled_results))
  return zsled_results

##### time 원본으로 돌리기
def restoring_time(arranged_ner_results, time_list): 
  tdx = 0
  for idx1, (k1, v1) in enumerate(arranged_ner_results.items()): #k1 : 날짜 / v1 : 객체
    print(idx1, k1, v1)
    for idx2, (k2, v2) in enumerate(v1.items()):  #k2: 일정 / v2 : 시간
      print(idx2, k2, v2)
      if v2 == '' or time_list[tdx] == '':
        arranged_ner_results[k1][k2] = arranged_ner_results[k1][k2]+time_list[tdx]
      else :
        arranged_ner_results[k1][k2] = time_list[tdx]
      tdx = tdx+1
  print('restoring time : {}'.format(arranged_ner_results))
  # tdx = 0
  # for idx1, (k1, v1) in enumerate(arranged_ner_results.items()): #k1 : 날짜 / v1 : 객체
  #   print(idx1, k1, v1)
  #   for idx2, (k2, v2) in enumerate(v1.items()):  #k2: 일정 / v2 : 시간
  #     print(idx2, k2, v2)
  #     if v2 is not '':
  #       arranged_ner_results[k1][k2] = time_list[tdx]
  #       tdx = tdx+1
  # print('restoring time : {}'.format(arranged_ner_results))
  return arranged_ner_results



app = Flask(__name__)

_year = datetime.datetime.today().year        # 현재 연도 가져오기
_month = datetime.datetime.today().month      # 현재 월 가져오기  
_day = datetime.datetime.today().day

ner = Pororo(task="ner", lang="ko")
zsl = Pororo(task="zero-topic", lang="ko")

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
    tag_list = []
    tag_info = {}
    collections = db.collection('UserList').document(_id).collection('TagHub')
    # print(collections) # CollectionReference
    for doc in collections.stream():
        # print(doc)  # DocumentSnapshot Object
        # print(u'{} => {} / {}'.format(doc.id, doc.get('color'), doc.get('name')))
        # print(u'{} => {}'.format(doc.id, doc.to_dict()))
        name = doc.get('name')
        color = doc.get('color')
        tag_list.append(name)
        tag_info[name] = { "tagid" : doc.id, "tagcolor" : color}
    # print('tag_list : {}'.format(tag_list))
    # print('tag_info : {}'.format(tag_info))
    
    ##### ocr 호출 #####
    # ocr_result = get_ocr_data(_url)
    # print('ocr_result : {}'.format(ocr_result))   #list
    # ocr_result = ['졸작', '회의', '4:', '30', 'PM', '운동', '5pm']
    # ocr_result = ['5/28', '회의', '10시', '병원', '2pm', '5/29', '수영', '4:30pm', '강의', '6시pm', '술약속', '9시']
    # ocr_result = [['6/1', '병원', '9'], ['점심약속', '1pm'], [' 현충일', ' 저녁 6:30분PM '], ['1%', '어린이날', '휴가', '1%'], ['회의', '저녁 5시pm '], ['6/2', '운동', '3:30', 'pm'], ['수영', '8시'], ['술약속', '9pm']]

    ##### ocr 결과 전처리 
    spacing_result, time_list = spacing_data(ocr_result)
 

    # date_list = [str(year),str(month),str(day)]
    # ner_result, zsl_result = doing_ner(ocr_result, tag_list, date_list)
    date_list = [str(year),str(month),str(day)]
    ##### ner
    ner_result = doing_ner(spacing_result, date_list)
    ##### zsl
    zsl_result = doing_zsl(ner_result, tag_list)
    ##### TIME부분 형식 되돌리기
    restored_time_result = restoring_time(ner_result, time_list)

    #####firebase에 write
    for index, (key, value) in enumerate(restored_time_result.items()): #key는 date, value는 딕셔너리
      doc_date = key
      # print(doc_date)
      doc_date = doc_date.split(".")
      # print(doc_date)
      doc_year = int(doc_date[0])
      doc_month = int(doc_date[1])
      doc_day = int(doc_date[2])
      for inindex, (inkey, invalue) in enumerate(value.items()) : #inkey는 일정, invalue는 시간
        # print('{} : {}'.format(inkey, invalue))
        start = datetime.datetime(doc_year, doc_month, doc_day, 0, 0, 0) #시간 넣어주기
        end = datetime.datetime(doc_year, doc_month, doc_day, 23, 59, 59)
        max_tag = zsl_result[key][inkey] #최적 tag
        doc = db.collection('UserList').document(_id).collection('ScheduleHub').document()
        doc.set({
            # u'title': inkey+' '+invalue,  # pororo결과 넣기..
            u'title': inkey+' '+invalue,  # pororo결과 넣기..
            u'isAllDay' : True,
            u'tag' : {
                u'color' : tag_info[max_tag]['tagcolor'],
                u'name' : max_tag,
                u'tid' : tag_info[max_tag]['tagid']
            },
            u'start' : start - datetime.timedelta(hours=9),
            u'end' : end - datetime.timedelta(hours=9),
            u'memo' : None,
            u'needAlarm' : True,
            u'imgUrl' : _url
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


