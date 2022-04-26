# 오또칼렌 | Autocalen
#### Backend Repository
<br/>

## 소개
>**오또칼렌 : Otto(Auto) Calen**
```바쁜 현대인들을 위한 일정 정리 자동화 솔루션!

기존 캘린더 앱은 직접 일정 태그 등록을 해주지 않으면 어떤 일정인지 한눈에 알아보기 쉽지 않아 관리가 어렵습니다. 
그리고 아날로그 감성도 포기하지 않는 현대인에게 기존 다이어리를 일일이 디지털화하는 것은 여간 귀찮은 일이 아닙니다.

오또 칼렌은 종이로 된 아날로그 다이어리를 사진 촬영하면 일정에 맞게 태그가 되어 디지털 캘린더에 연동합니다. 
그러므로 흩어져 있는 일정들을 태그별로 분류하여 한눈에 알아보기 쉽고, 일정 관리가 수월해집니다.

작품명 오또칼렌은 "Automatic"과 "Calendar"를 합친 것을 한글로 발음하여 표기했습니다.
```
<br/>

## 주요 기능
**OCR**
1. 촬영된 메모 사진을 ocr 기법으로 추출
2. 사용된 api : [Naver Cloud Platform CLOVA OCR](https://www.ncloud.com/product/aiService/ocr)

**문자열 처리**
1. ocr기법으로 추출된 문자열 처리
2. 정규표현식

**NLP**
1. 추출된 일정 문자열의 태그화(카테고리화)를 위해 날짜/일정/시간으로 분류 필요
2. 날짜/일정/시간 파악을 위해 자연어처리 프레임워크 [Pororo](https://github.com/kakaobrain/pororo) 사용
<br/>

## Tech Stack
1. Navor Cloud Platform CLOVA OCR
2. Pororo 
3. Flask
4. Firebase
5. Docker
<bt/>

## Video
https://www.youtube.com/watch?v=4prgEn_bIYg


