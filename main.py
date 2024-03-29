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
    # print('ocr_result : {}'.format(results_list))
    return results_list


def spacing_data(input) :

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
    one_input = " ".join(input[i]) # 한줄 하나로 합치기

    ##### 띄어진 n/m 붙이기
    matchObj_iter = re.finditer('(\d{1,2})(\s)?(\s)?/(\s)?(\s)?(\d{1,2})', one_input)
    # print(matchObj_iter)
    d_list = []
    for matchObj in matchObj_iter:
      d_list.append(matchObj)
    d_list.reverse()
    # print(d_list)
    for matchObj in d_list:
      d = matchObj.group()
      # print(d)
      s = matchObj.start()
      e = matchObj.end()
      d = d.replace(" ","")
      # print(d)
      one_input = one_input[:s]+d+one_input[e:]
      # print(one_input)
    ##### 월일 변경
    # one_input = re.sub(r'(\d{1,2})/(\d{1,2})', '\\1월\\2일', one_input)
    one_input = re.sub(r'(\d{1,2})/(\d{1,2})', '\\1월\\2일', one_input)

    ##### 기간인 경우 공백 없애기
    dur_date = re.search('(\d{1,2})(\s)?(\s)?월(\s)?(\s)?(\d{1,2})(\s)?(\s)?일(\s)?(\s)?~(\s)?(\s)?(\d{1,2})(\s)?(\s)?월(\s)?(\s)?(\d{1,2})(\s)?(\s)?일', one_input)
    # print(dur_date)
    if dur_date is not None :
      dur_g = dur_date.span()
      dur_date = dur_date.group().replace(" ","")
      # print('no blank date : {}'.format(dur_date))
      one_input = dur_date+one_input[dur_g[1]:]
    # print(one_input)

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
  # print('spacing_result with change date : {}'.format(input))
  # print('time_list : {}'.format(time_list))
  return input, time_list


def doing_ner(input, date_list):
  # _date = str(year)+str(month)+str(day)
  _date = ".".join(date_list)


  ner_results = []
  for i in input:
    one_input = ner(i,apply_wsd=True)
    ner_results.append(one_input)
  # print('ner_result : {}'.format(ner_results)) # 2차원 배열

  
  ##### DATE, TIME 처리
  for i1, v1 in enumerate(ner_results):  ## i1 : index / v1 : 배열
    # print('before ner[{}] result : {}'.format(i1, v1))
    for i2, v2 in enumerate(v1): ## i2 : index / v2 : tuple -> ner 배열을 순회
      # print('before ner[{}][{}] result : {}'.format(i1, i2, v2))
      if v2[1] == 'DATE' and re.search("(\d{1,2})(\s)?월(\s)?(\d{1,2})(\s)?일", v2[0]) == None:  # 잘못된 DATE
        # print("잘못된 Date")
        ner_results[i1][i2] = (v2[0],'O')
      if v2[1] == 'TIME' and re.search("(\d{1,2})(\s)?시(\s)?(\d{1,2})?(\s)?(분|반)?", v2[0]):
        # print("Time이 섞임")
        #n시(n분/반) 형태가 있다
        tuple_t = len(v2[0].lstrip().rstrip())
        d = re.search("(\d{1,2})(\s)?시(\s)?(\d{1,2})?(\s)?(분|반)?", v2[0])
        s, e = d.span()
        reg_t = e-s+1
        if tuple_t > reg_t :  #TIME에 n시(n분/반) 형태 외에 다른 값이 껴있음
          t1 = (v2[0][:s], 'O')
          t2 = (v2[0][s:e], 'TIME')
          t3 = (v2[0][e:], 'O')
          # t1 = (v2[0][:s], 'O')
          # t2 = (v2[0][s:e+1], 'TIME')
          # t3 = (v2[0][e+1:], 'O')
          ner_results[i1][i2] = t1
          ner_results[i1].insert(i2+1,t2)
          if len(v2[0][e:]) > 0:
            ner_results[i1].insert(i2+2,t3)
        # else : #TIME에 맞는 형식 -> n시(n분/반) 형태
        #   pass
      elif v2[1] == 'TIME' and re.search("(\d{1,2})(\s)?시(\s)?(\d{1,2})?(\s)?(분|반)?", v2[0]) == None:  # 잘못된 형식의 TIME -> n시(n분/반) 형태가 아님
        # print("Time이면 안되는데 time")
        ner_results[i1][i2] = (v2[0],'O')
    t_list = [e[1] for e in v1]
    # print('t_list : {}'.format(t_list))
    t_count = t_list.count('TIME')
    if t_count > 1 or (v1[-1][1] != 'TIME' and t_count == 1) :
      t_idx_list = list(filter(lambda x: t_list[x] == 'TIME', range(len(t_list))))
      for i in t_idx_list:
        v1[i] = (v1[i][0], 'O')
      v1.append(('','TIME'))
    elif t_count == 0:
      v1.append(('','TIME'))
  #   print('after ner[{}] result : {}'.format(i1, v1))  
  # print('changed_ner_results : {}'.format(ner_results))

  #### ner 결과 1차원으로
  ner_results = [element for array in ner_results for element in array]
  # print('1D ner_results : {}'.format(ner_results))

  arranged_ner_results={}
  temp=""
  date=''
  sche_results = {}
  for result in ner_results:  #result는 tuple
    if result[1] == 'DATE': # 사진에 date가 있을 때
      # print(result)
      if '~' in result[0] : #기간인 date
        dur_idx = result[0].find('~')
        if date =='': # 처음 나온 Date
          if dur_idx != -1:
            s = result[0][:dur_idx]
            e = result[0][dur_idx+1:]
            s_temp_date = s.replace("일","")   #"일" 없애기
            s_temp_date = re.sub('월','.', s_temp_date)
            s_temp_date = s_temp_date.replace(" ","").lstrip().rstrip() # 빈칸 없애기
            e_temp_date = e.replace("일","")   #"일" 없애기
            e_temp_date = re.sub('월','.', e_temp_date)
            e_temp_date = e_temp_date.replace(" ","").lstrip().rstrip() # 빈칸 없애기

            sdate = date_list[0]+'.'+s_temp_date # 처음 나온 date  ###### 월일 형식 동일형식 문자열로 변경 필요
            edate = date_list[0]+'.'+e_temp_date 
            date = (sdate, edate)

        else: # 처음 나온 date가 아님
          arranged_ner_results[date] = sche_results
          sche_results={}

          if dur_idx != -1:
            s = result[0][:dur_idx]
            e = result[0][dur_idx+1:]
            s_temp_date = s.replace("일","")   #"일" 없애기
            s_temp_date = re.sub('월','.', s_temp_date)
            s_temp_date = s_temp_date.replace(" ","").lstrip().rstrip() # 빈칸 없애기
            e_temp_date = e.replace("일","")   #"일" 없애기
            e_temp_date = re.sub('월','.', e_temp_date)
            e_temp_date = e_temp_date.replace(" ","").lstrip().rstrip() # 빈칸 없애기

            sdate = date_list[0]+'.'+s_temp_date # 처음 나온 date  ###### 월일 형식 동일형식 문자열로 변경 필요
            edate = date_list[0]+'.'+e_temp_date 
            date = (sdate, edate)

      else : #기간인 Date가 아님
        if date =='':
          temp_date = result[0].replace("일","")   #"일" 없애기
          temp_date = re.sub('월','.',temp_date)
          temp_date = temp_date.replace(" ","").lstrip().rstrip() # 빈칸 없애기
          # print(temp_date)
          s_date = date_list[0]+'.'+temp_date # 처음 나온 date  ###### 월일 형식 동일형식 문자열로 변경 필요
          e_date = s_date
          date = (s_date, e_date)
          # date = result[0]
        else: # 처음 나온 date가 아님
          arranged_ner_results[date] = sche_results
          sche_results={}
          temp_date = result[0].replace("일","")   #"일" 없애기
          temp_date = re.sub('월','.',temp_date)
          temp_date = temp_date.replace(" ","").lstrip().rstrip()  # 빈칸 없애기
          # print(temp_date)
          s_date = date_list[0]+'.'+temp_date 
          e_date = s_date
          date = (s_date, e_date)
          # date = result[0]  ###### 월일 형식 동일형식 문자열로 변경 필요
    else: # 해당 단어가 date가 아님
      # print(result)
      if date=='': 
        s_date = _date # 사진에 date가 없을 때
        e_date = _date
        date = (s_date, e_date)
      if result[1] == 'TIME':
        temp = temp.lstrip().rstrip()
        sche_results[temp] = result[0]
        temp=""
      else:
        temp = temp+result[0]
        #  print(temp)
      # elif result[0] != ' ' :
      #    temp+=' '+result[0]
      #   #  print(temp)
    arranged_ner_results[date] = sche_results
  # print('arranged_ner_results : {}'.format(arranged_ner_results))
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
  # print('zsled_results : {}'.format(zsled_results))
  return zsled_results

##### time 원본으로 돌리기
def restoring_time(arranged_ner_results, time_list): 
  tdx = 0
  for idx1, (k1, v1) in enumerate(arranged_ner_results.items()): #k1 : 날짜 / v1 : 객체
    # print(idx1, k1, v1)
    for idx2, (k2, v2) in enumerate(v1.items()):  #k2: 일정 / v2 : 시간
      # print(idx2, k2, v2)
      if v2 == "" or time_list[tdx] == "":
        arranged_ner_results[k1][k2] = arranged_ner_results[k1][k2]+""
      else :
        arranged_ner_results[k1][k2] = time_list[tdx]
      tdx = tdx+1
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
        name = doc.get('name')
        color = doc.get('color')
        tag_list.append(name)
        tag_info[name] = { "tagid" : doc.id, "tagcolor" : color}
    # print('tag_list : {}'.format(tag_list))
    
    ##### ocr 호출 #####
    ocr_result = get_ocr_data(_url)

    ##### ocr 결과 전처리 
    spacing_result, time_list = spacing_data(ocr_result)
    # time_list = ["2시반 pm", "2시반", "10am", "2시 pm", "2시 30분am"]

    date_list = [str(year),str(month),str(day)]
    ##### ner
    # ner_result = doing_ner("", date_list)
    ner_result = doing_ner(spacing_result, date_list)
    ##### zsl
    zsl_result = doing_zsl(ner_result, tag_list)
    ##### TIME부분 형식 되돌리기
    restored_time_result = restoring_time(ner_result, time_list)

    #####firebase에 write
    for idx, (key, value) in enumerate(restored_time_result.items()): #key는 date, value는 딕셔너리      
      start_date = key[0]
      end_date = key[1]
      # print(start_date)
      # print(end_date)
      start_date = start_date.split(".")
      # print(start_date)
      start_year = int(start_date[0])
      start_month = int(start_date[1])
      start_day = int(start_date[2])

      end_date = end_date.split(".")
      # print(end_date)
      end_year = int(end_date[0])
      end_month = int(end_date[1])
      end_day = int(end_date[2])

      for inidx, (inkey, invalue) in enumerate(value.items()) : #inkey는 일정, invalue는 시간
        # print('{} : {}'.format(inkey, invalue))
        start = datetime.datetime(start_year, start_month, start_day, 0, 0, 0) #시간 넣어주기
        end = datetime.datetime(end_year, end_month, end_day, 23, 59, 59)
        max_tag = zsl_result[key][inkey] #최적 tag
        total_title = inkey+' '+invalue
        doc = db.collection('UserList').document(_id).collection('ScheduleHub').document()
        doc.set({
            # u'title': inkey+' '+invalue,  # pororo결과 넣기..
            u'title': total_title.lstrip().rstrip(),  # pororo결과 넣기..
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



