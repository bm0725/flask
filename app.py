import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
import datetime
import json
import os
import sys

now = datetime.datetime.now()
now = now + datetime.timedelta(hours=9)
app = Flask(__name__)

schulCode = "P100000425" #학교코드
schulname = "전주신흥고등학교" #사이트 학교알리미에서 받아옴
schulKndScCode= "04"
schulCrseScCode = "4"
schulGion = "stu.jbe.go.kr"
schulMeal = "1"
#이것들을 수정하면 다른 학교의 식단 파싱도 가능하다.
menu = [] #이곳에 메뉴를 넣는다.미완성

menuText = ' '

ID = ""#리로스쿨 일정파싱용 운영자 ID, 비번. /개발자명령어를 입력해 수정가능.
PS = ""
password = "chatbot206"

print(now.day, now.isoweekday())
print(type(now.day),type(now.isoweekday()))

behave = 0 #1은 급식파싱, 2는 일정파싱, 3은 강의실,4수행출력, 5는 급식 선택, 6은 시간표 개발자모드(데이터수정)
mealDay = 0 #급식파싱할때 쓸 날짜 넣을 변수다.
editbehave = 0 #데이터수정. 1은 시간표,
    
schulDate = f"{now.year}.{now.month}.{now.day}"

URL = "https://{}/sts_sci_md00_001.do?schulCode={}&schulCrseScCode={}&schulKndScCode={}&schMmealScCode={}&schYmd={}".format(schulGion,schulCode,schulCrseScCode,schulKndScCode, schulMeal ,schulDate)


alldata = {"a" : 1} #백업데이터
with open("data.json", "w") as f:
    json.dump(alldata, f)

with open("data.json", "r") as f:
    alldata = json.load(f)

def Parsing(url): # 함수.  URL넣으면 나이스에서 급식 파싱해 가져옴
    global menu, URL
    url = str(url)
    res = requests.get(url)
    soup = BeautifulSoup(res.text,"html.parser")
    text= soup.select_one('#contents > div:nth-child(2) > table > tbody') #급식

    menu = text.get_text()
    menu = menu.split("\n")
    remove = {'', ' '}
    menu = [i for i in menu if i not in remove]
    return menu 

def ParsingRiro(url2):#리로스쿨 학사일정 가져오기. 리로스쿨은 로그인필요해 id랑 PS로 로그인해 파싱.
    global ID, Ps
    #print(menu)
    
#https://stu.jbe.go.kr/popup.jsp?page=/ws/edusys/cm/sym/ocm/oi/sym_ocmoi_m02&popupID=20230313184856&w2xHome=/ws/edusys/pa/com/&w2xDocumentRoot= 하굑선택창미완성
    
def Weekday(weekday): #급식날짜계산함수. 			isoweekday에서 월요일은 1, 화요일은 2,수3,목4,금5,토6,일7임.
    global mealDay, behave
    
    weekday = int(weekday)
    weekdaynow = now.isoweekday()
    print(",,,,,,,,,,,,,,,,,",weekday,weekdaynow)
    if weekdaynow == weekday:
        mealDay = int(now.day)
        print(mealDay)
    else:
        if weekdaynow > weekday :
            mealDay = int(now.day) - (weekdaynow - weekday)
        else:
            mealDay = int(now.day) +(weekday - weekdaynow)
    
    behave = 1#급식파싱시작
        
    return mealDay, behave


def Menutrim(menu, mealDay): #메뉴를 보기 쉽게 정렬하는 합수다. 알레르기 정보를 전부 떼서 없앤다.

    global menuText
    c = menu[(mealDay -1)] #리스트는 0부터 시작하므로
    c = c.split('.')
    print(c)

    remove = {'1', '2' , '3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20'}
    c = [i for i in c if i not in remove]
    i = 0
    if (len(c) == 0) or (len(c) == 1):
        mealDay += 1
        menuText = f"{mealDay}일은 급식을 제공하지 않습니다."
    else:
        while True:
            blank = c[i][:-1]
            menuText += f"{blank}\n"
            i += 1
            if len(c) == i + 1:
                break

    return menuText

schedulebackup = []
movebackup = []

movedata2 = {
    "물리" : {"A-1" : "","A-2" : '1',"B-1" : "2","B-2" : "3","C-1" : "4","C-2" : "5","D" : "6","E" : "7"},
    "화학" : {"A-1" : ' ',"A-2" : ' ',"B-1" : " ","B-2" : " ","C-1" : " ","C-2" : " ","D" : " ","E" : " "},
    "생물" : {"A-1" : ' ',"A-2" : ' ',"B-1" : " ","B-2" : " ","C-1" : " ","C-2" : " ","D" : " ","E" : " "},
    "지구" : {"A-1" : ' ',"A-2" : ' ',"B-1" : " ","B-2" : " ","C-1" : " ","C-2" : " ","D" : " ","E" : " "},
    "경제" : {"A-1" : ' ',"A-2" : ' ',"B-1" : " ","B-2" : " ","C-1" : " ","C-2" : " ","D" : " ","E" : " "},
    "정법" : {"A-1" : ' ',"A-2" : ' ',"B-1" : " ","B-2" : " ","C-1" : " ","C-2" : " ","D" : " ","E" : " "},
    "사문" : {"A-1" : ' ',"A-2" : ' ',"B-1" : " ","B-2" : " ","C-1" : " ","C-2" : " ","D" : " ","E" : " "},
    "세계사" : {"A-1" : ' ',"A-2" : ' ',"B-1" : " ","B-2" : " ","C-1" : " ","C-2" : " ","D" : " ","E" : " "},
    "한국지리" : {"A-1" : ' ',"A-2" : ' ',"B-1" : " ","B-2" : " ","C-1" : " ","C-2" : " ","D" : " ","E" : " "},
    "영어권문화" : {"A-1" : ' ',"A-2" : ' ',"B-1" : " ","B-2" : " ","C-1" : " ","C-2" : " ","D" : " ","E" : " "},
    "문학개론" : {"A-1" : ' ',"A-2" : ' ',"B-1" : " ","B-2" : " ","C-1" : " ","C-2" : " ","D" : " ","E" : " "},
    "확통" : {"A-1" : ' ',"A-2" : ' ',"B-1" : " ","B-2" : " ","C-1" : " ","C-2" : " ","D" : " ","E" : " "},
    "기하" : {"A-1" : ' ',"A-2" : ' ',"B-1" : " ","B-2" : " ","C-1" : " ","C-2" : " ","D" : " ","E" : " "},
    "미적" : {"A-1" : ' ',"A-2" : ' ',"B-1" : " ","B-2" : " ","C-1" : " ","C-2" : " ","D" : " ","E" : " "},
    "일본어" : {"A-1" : ' ',"A-2" : ' ',"B-1" : " ","B-2" : " ","C-1" : " ","C-2" : " ","D" : " ","E" : " "},
    "중국어" : {"A-1" : ' ',"A-2" : ' ',"B-1" : " ","B-2" : " ","C-1" : " ","C-2" : " ","D" : " ","E" : " "},
    "연극" : {"A-1" : ' ',"A-2" : ' ',"B-1" : " ","B-2" : " ","C-1" : " ","C-2" : " ","D" : " ","E" : " "},
    "미술" : {"A-1" : ' ',"A-2" : ' ',"B-1" : " ","B-2" : " ","C-1" : " ","C-2" : " ","D" : " ","E" : " "}
    
    
}

schedule2 = { #2학년 학교 시간표. 딕셔너리 형태
    "1" : ["1교시 : 문학\n 2교시 : 2학년 선택과목 C\n 3교시 : 미술\n 4교시 : 미술\n 5교시 : 수학Ⅰ\n6교시 : 2학년 선택과목 B\n7교시 : 2학년 선택과목 A\n",
	   "1교시 : 일본어/중국어\n 2교시 : 수학 Ⅰ\n 3교시 : 문학\n 4교시 : 2학년 선택과목 A\n 5교시 : 영어 Ⅰ\n6교시 : 2학년 선택과목 B\n7교시 : 2학년 선택과목 C\n",
	   "1교시 : 2학년 선택과목 B\n 2교시 : 문학\n 3교시 : 예배\n 4교시 : 창체\n 5교시 : 영어 Ⅰ\n6교시 : 일본어/중국어\n7교시 : 2학년 선택과목 C\n",
	   "1교시 : 2학년 선택과목 C\n 2교시 : 일본어/중국어\n 3교시 : 2학년 선택과목 A\n 4교시 : 2학년 선택과목 B\n 5교시 : 수학 Ⅰ\n6교시 : 영어 Ⅰ\n7교시 : 문학\n",
	   "1교시 : 2학년 선택과목 A\n 2교시 : 영어 Ⅰ\n 3교시 : 수학 Ⅰ\n 4교시 : \n 5교시 : 창체\n6교시 : 창체\n7교시 : 창체\n"],
    "2" : ["데이터 없음","데이터 없음","데이터 없음","데이터 없음","데이터 없음"],
    "3" : ["데이터 없음","데이터 없음","데이터 없음","데이터 없음","데이터 없음"],
    "4" : ["데이터 없음","데이터 없음","데이터 없음","데이터 없음","데이터 없음"],
    "5" : ["데이터 없음","데이터 없음","데이터 없음","데이터 없음","데이터 없음"],
    "6" : ["1교시 : 문학\n 2교시 : 2학년 선택과목 C\n 3교시 : 체육\n 4교시 : 일본어/중국어\n 5교시 : 영어Ⅰ\n6교시 : 2학년 선택과목 B\n7교시 : 2학년 선택과목 A\n",
           "1교시 : 문학\n 2교시 : 영어 Ⅰ\n 3교시 : 수학 Ⅰ\n 4교시 : 2학년 선택과목 A\n 5교시 : 일본어/중국어\n6교시 : 2학년 선택과목 B\n7교시 : 2학년 선택과목 C\n",
           "1교시 : 2학년 선택과목 B\n 2교시 : 일본어/중국어\n 3교시 : 예배\n 4교시 : 창체\n 5교시 : 수학 Ⅰ\n6교시 : 영어 Ⅰ\n7교시 : 2학년 선택과목 C\n",
           "1교시 : 2학년 선택과목 C\n 2교시 : 영어 Ⅰ\n 3교시 : 2학년 선택과목 A\n 4교시 : 2학년 선택과목 B\n 5교시 : 연극\n6교시 : 문학\n7교시 : 수학 Ⅰ\n",
           "1교시 : 2학년 선택과목 A\n 2교시 : 문학\n 3교시 : 수학 Ⅰ\n 4교시 : 연극\n 5교시 : 창체\n6교시 : 창체\n7교시 : 창체\n"],
    "7" : ["데이터 없음","데이터 없음","데이터 없음","데이터 없음","데이터 없음"],
    "8" : ["데이터 없음","데이터 없음","데이터 없음","데이터 없음","데이터 없음"],
    "9" : ["데이터 없음","데이터 없음","데이터 없음","데이터 없음","데이터 없음"],
	"10" : ["데이터 없음","데이터 없음","데이터 없음","데이터 없음","데이터 없음"]
}




jsonChoiceDay = {
    "version": "2.0",
    "template": {"outputs": [{"simpleText": {"text": "날짜를 선택해 주세요. 이번주 해당 요일의 급식이 출력됩니다."}}],
                 "quickReplies": [{"label": "오늘", "action": "message", "messageText": "오늘"},
                                  {"label": "월", "action": "message", "messageText": "월"},
                                  {"label": "화", "action": "message", "messageText": "화"},
                                  {"label": "수", "action": "message", "messageText": "수"},
                                  {"label": "목", "action": "message", "messageText": "목"},
                                  {"label": "금", "action": "message", "messageText": "금"},
                                  {"label": "사용자 지정", "action": "message", "messageText": "사용자 지정"}
                                  ]
                 }
}

jsonChoiceMonth = {
    "version": "2.0",
    "template": {"outputs": [{"simpleText": {"text": "어떤 월의 학사일정을 가져오시겠어요?"}}],
                 "quickReplies": [{"label": "오늘", "action": "message", "messageText": "오늘"},
                                  {"label": "월", "action": "message", "messageText": "월"},
                                  {"label": "화", "action": "message", "messageText": "화"},
                                  {"label": "수", "action": "message", "messageText": "수"},
                                  {"label": "목", "action": "message", "messageText": "목"},
                                  {"label": "금", "action": "message", "messageText": "금"},
                                  {"label": "사용자 지정", "action": "message", "messageText": "사용자 지정"}
                                  ]
                 }
}

jsonChoiceBase = {
  "version": "2.0",
  "template": {
    "outputs": [
      {
        "carousel": {
          "type": "basicCard",
          "items": [
            {
              "title": "명령어1",
              "description": "명령어를 선택해 주세요",
              "thumbnail": {
                "imageUrl": "https://drive.google.com/file/d/1T-2cJlqVa-5Dj8tIpwtlMdMjBEOGhmMG/view?usp=sharing"
              },
              "buttons": [
                {
                  "action": "message",
                  "label": "명령어 기능 확인하기",
                  "messageText": "추가 명령어"
                },
		{
                  "action": "message",
                  "label": "시간표 확인하기",
                  "messageText": "시간표"
                },
		{
                  "action": "message",
                  "label": "이동수업 위치 확인하기",
                  "messageText": "강의실"
                }
              ]
            },
            {
              "title": "명령어2",
              "description": "어떤 명령어를 사용하시겠어요?",
              "thumbnail": {
                "imageUrl": "https://drive.google.com/file/d/1aNTnmhP5ZBOesQpL3WFyM2izOQ5vhgrr/view?usp=sharing"
              },
              "buttons": [
                {
                  "action": "message",
                  "label": "급식 메뉴 확인하기",
                  "messageText": "급식"
                },
		{
                  "action": "message",
                  "label": "수행평가 추가/확인하기(미완성 기능)",
                  "messageText": "미완성입니다."
                },
		{
                  "action": "message",
                  "label": "사용자 정보 등록하기(미완성 기능)",
                  "messageText": "미완성입니다."
                }
              ]
            },
            {
              "title": "명령어3",
              "description": "어떤 명령어를 사용하시겠어요?",
              "thumbnail": {
                "imageUrl": "https://drive.google.com/file/d/1UdjkhhNb_N5wdupdK-fU6okUuuvT0wo1/view?usp=sharing"
              },
              "buttons": [
                {
                  "action": "message",
                  "label": "학사일정 확인하기(미완성 기능)",
                  "messageText": "미완성 기능입니다."
                },
		{
                  "action": "message",
                  "label": "챗봇에 대해 알아보기",
                  "messageText": "챗봇 알아보기."
                }
              ]
            }
          ]
        }
      }
    ]
  }
}


jsonChoiceBan = {
    "version": "2.0",
    "template": {"outputs": [{"simpleText": {"text": "채팅 대신 버튼을 눌러 몇반의 시간표를 볼 것인지 골라주세요. 버튼을 사용하지 않을 시 오류가 있을 수 있습니다."}}],
                 "quickReplies": [
                                {"label": "1반", "action": "message", "messageText": "1"},
			 	{"label": "2반", "action": "message", "messageText": "2"},
			 	{"label": "3반", "action": "message", "messageText": "3"},
			 	{"label": "4반", "action": "message", "messageText": "4"},
			 	{"label": "5반", "action": "message", "messageText": "5"},
			 	{"label": "6반", "action": "message", "messageText": "6"},
			 	{"label": "7반", "action": "message", "messageText": "7"},
			 	{"label": "8반", "action": "message", "messageText": "8"},
			 	{"label": "9반", "action": "message", "messageText": "9"},
			 	{"label": "10반", "action": "message", "messageText": "10"}
                                  ]
                 }
}

jsonChoiceBan1 = {
                 "version": "2.0",
                 "template": {
                 "outputs": [{
                     "carousel": { # 스킬가이드에 나온 캐러셀 형태
                         "type": "basicCard", # 기본형 선택 (<->비즈니스형도 존재)
                         "items": [{"title": "시간표 반 선택", # 제목
                             "description": "채팅 대신 버튼을 눌러 몇반의 시간표를 볼 것인지 골라주세요.", # 설명
                             #"thumbnail": { # 썸네일 이미지
                                 #"imageUrl": can[0].imgurl
                             "buttons": [ # 버튼
                                 {"action": "message", # 동작 형태(텍스트 출력)
                                 "label": "6반", # 버튼 이름
                                 "messageText": "6"},                       
                                 {"action": "message", # 동작 형태(텍스트 출력)
                                 "label": "1반", # 버튼 이름
                                 "messageText": "1"},   
                                 {"action": "message", # 동작 형태(텍스트 출력)
                                 "label": "2반", # 버튼 이름
                                 "messageText": "2"},          
                                 {"action": "message", # 동작 형태(텍스트 출력)
                                 "label": "3반", # 버튼 이름
                                 "messageText": "3"},             
                                 {"action": "message", # 동작 형태(텍스트 출력)
                                 "label": "4반", # 버튼 이름
                                 "messageText": "4"},
                                 {"action": "message", # 동작 형태(텍스트 출력)
                                 "label": "5반", # 버튼 이름
                                 "messageText": "5"},           
                                {"action": "message", # 동작 형태(텍스트 출력)
                                 "label": "7반", # 버튼 이름
                                 "messageText": "7"},
                                 {"action": "message", # 동작 형태(텍스트 출력)
                                 "label": "8반", # 버튼 이름
                                 "messageText": "8"},
                                 {"action": "message", # 동작 형태(텍스트 출력)
                                 "label": "9반", # 버튼 이름
                                 "messageText": "9"},
                                 {"action": "message", # 동작 형태(텍스트 출력)
                                 "label": "10반", # 버튼 이름
                                 "messageText": "10"}
                                 
                             ]}]}}]}}

jsonChoiceParse = {
    "version": "2.0",
    "template": {"outputs": [{"simpleText": {"text": "무엇을 하시겠어요?"}}],
                 "quickReplies": [
                                  {"label": "취소", "action": "message", "messageText": "취소"},
                                  {"label": "선택한 급식메뉴 확인하기", "action": "message", "messageText": "급식 파싱"}
                                  ]
                 }
}

@app.route('/keyboard')

def Keyboard():

    return jsonify( {"type" : "text"} )



@app.route('/message', methods=['POST'])
def message():  
    
    global mealDay, behave, now, schedule, URL, a1, classpos, menuText, menu, jsonChoiceMonth, jsonChoiceBase, editbehave, jsonChoiceBan, choiceban
    global movedata2, schedule2, schedulebackup, movebackup, editbehave
    
    now = datetime.datetime.now()
    now = now + datetime.timedelta(hours=9)
    print(now.day)
    
    dataReceive = request.get_json()
    content = dataReceive['userRequest']['utterance']
#   content = "Received data: {}".format(dataReceive)
    ###n_data = "Received data: {}".format(dataReceive)
#   print(json_data)
#   json_obj = json.loads(json_data)
#   print(json_obj)
#   content = json_obj['userRequest']['utterance']
#   print(content)
    #content = dataReceive['content']
    
    print("아래 :",content)
    print(type(content)) 
    print(behave)
    
    if content == u"오늘":
        response = jsonChoiceParse
        Weekday(now.isoweekday())
    
    elif (content == u"취소") or (content == "끝내기"):
        behave = 0
        editbehave = 0
        response = {
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : "작업이 취소되었습니다."}}
                ]
            }
        }

	
    elif content == password: # 운영자기능 설명
        response = {
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : 
"""
아래는 데이터 수정및 주요 내용에 접근할 수 있는 명령어들입니다.
/시간표수정 -> 반의 시간표 정보를 수정할 수 있다.
/강의실수정 -> 학년 강의실 정보를 수정할 수 있다. 둘다 지금 2학년전용
/수행평가수정->잘못 추가한 수행평가 정보나, 일부러 추가한 가짜 수행평가 정보를 수정할수 있다.
                """}} # isoweekday로 얻은값이 4면 금요일을 의미하므로 금요일 초과(토,일)인지 확인한다.
                ]
            }
        }
    elif editbehave == 1: #시간표수정기능
        a1 = content.split('.') #a1은 여기저기서 쓰이는 잡변수
        schedulebackup.append(schedule2[a1[1]][int(a1[2]) - 1])
        schedule2[a1[1]][int(a1[2]) - 1] = f"1교시 : {a1[3]}\n 2교시 : {a1[4]}\n 3교시 : {a1[5]}\n 4교시 : {a1[6]}\n 5교시 : {a1[7]}\n6교시 : {a1[8]}\n7교시 : {a1[9]}\n"
        editbehave = 0
        response = {
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : f"수정되었습니다."}} #달력과 다르게 리스트는 0부터 시작하므로 -1을 해줘야 한다.
                ]
            }
        }
    
    elif editbehave == 2:
        movebackup.append(content)
        a1 = content.split('/','.')
        while True:
            i = 0 #반복용잡변수
            if a1[(i+1)] not in movedata2:
                movedata2[a1[(i+1)]] = {"A-1" : ' ',"A-2" : ' ',"B-1" : " ","B-2" : " ","C-1" : " ","C-2" : " ","D" : " ","E" : " "}
                movedata2[a1[(i+1)]][a1[(i+2)]] = a1[(i + 3)]
            else:
                movedata2[a1[(i+1)]][a1[(i+2)]] = a1[(i + 3)]
            i += 3
            if len(a1)-1 < i + 3:
                    break
        response = {
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : f"수정되었습니다."}} #달력과 다르게 리스트는 0부터 시작하므로 -1을 해줘야 한다.
                ]
            }
        }
                
        
    elif behave == 5: #급식 날짜선택기능
        a1 = content.split('.')
        print(a1)
        if len(a1) == 0:
            behave = 0
            response = {
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : f"형식에 맞춰 주세요. 이번년도 급식 데이터만 가능합니다."}} #달력과 다르게 리스트는 0부터 시작하므로 -1을 해줘야 한다.
                ]
            }
        }
            mealDay = 0
        else:
            mealDay = int(a1[1])
            schulDate = f"{now.year}.{a1[0]}.{a1[1]}"
            behave = 1
            URL = "https://{}/sts_sci_md00_001.do?schulCode={}&schulCrseScCode={}&schulKndScCode={}&schMmealScCode={}&schYmd={}".format(schulGion,schulCode,schulCrseScCode,schulKndScCode, schulMeal ,schulDate)
            response = jsonChoiceParse
        #URL = 에서 급식을 파싱할때 날짜가 변할 수 있으므로 현재 날짜로 바꿔 출력한다.
        
        
    elif behave == 6: #시간표 선택하기
        choiceban = content #선택한 반 저장
        response = {
    "version" : "2.0",
    "template": {"outputs" : [{"simpleText" : {"text" : f"언제의 시간표를 원하십니까?"}}],
                 "quickReplies" : [
                                  {"label" : "일주일 전체", "action" : "message", "messageText" : "일주일 시간표"},
                                  {"label" : "오늘", "action" : "message", "messageText" : "오늘 시간표"}
                                  ]
                 }
}
        behave = 0
        
    elif behave == 3: #a1 a2 a3 a4 b 모두 잡변수
        a1 = content.split('.')
        a2 = ''
        b = 0
        for i in range (0,len(a1)):
            a3 = movedata2.get(a1[i])
            a4 = list(a3.keys())
            a2 +=f"{a1[i]} 강의실\n"
            for b in range (0,len(a4)):
                a2 += f"{a4[b]} : {a3[a4[b]]}\n"
        a2 += "\nA,B,C중 -2가 없는 과목은 1이 강의실 위치입니다."
        response = {
    "version" : "2.0",
        "template" : {"outputs" : [{"simpleText" : {"text" : f"{a2}"}}],
                "quickReplies" : [  
                                    {"label" : "강의실 출력하기", "action" : "message", "messageText" : "강의실"},
                                    {"label" : "끝내기", "action" : "message", "messageText" : "끝내기"}
                                    ]
                    }
}
        behave = 0
        

    elif (content in u"시간표") or (content == "시간표") or (content == "시간표 확인하기"):
        behave = 6
        response = jsonChoiceBan # 반선택

    elif content == "오늘 시간표":
        if int(now.isoweekday()) > 5:#isoweekday는 5일이 금요일이므로
            response = {
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : "오늘은 수업이 진행되지 않습니다.."}} # isoweekday로 얻은값이 4면 금요일을 의미하므로 금요일 초과(토,일)인지 확인한다.
                ]
            }
        }
        else:
            response = {
    "version" : "2.0",
    "template" : {"outputs" : [{"simpleText" : {"text" : f"{schedule2[choiceban][int(now.weekday())]}"}}],
                 "quickReplies" : [
                                  {"label" : "강의실 출력하기", "action" : "message", "messageText" : "강의실"},
                                  {"label" : "끝내기", "action" : "message", "messageText" : "끝내기"}
                                  ]
                 }
}
        behave = 0
        

    elif (content == "강의실") or (content in "강의실") or (content == "이동수업") or (content in "이동수업") or (content == "이동수업 위치 확인하기"): #강의실내용 가져오기ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
        response = {
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : f"어떤 과목을 원하십니까. 목록: \n{list(movedata2.keys())}\n두개 이상의 과목도 고를 수 있습니다.\n출력예시->물리.확통"}}
                ]
            }
        }
        behave = 3
        
        
    elif content == "일주일 시간표":
        response = {
    "version" : "2.0",
    "template" : {"outputs" : [{"simpleText" : {"text" : f"{schedule2[choiceban][int(0)]}\n{schedule2[choiceban][int(1)]}\n{schedule2[choiceban][int(2)]}\n{schedule2[choiceban][int(3)]}\n{schedule2[choiceban][int(4)]}"}}],
                 "quickReplies" : [
                                  {"label" : "강의실 출력하기", "action" : "message", "messageText" : "강의실"},
                                  {"label" : "끝내기", "action" : "message", "messageText" : "끝내기"}
                                  ]
                 }
}
    
    elif content == "추가 명령어":
        response = {
    "version" : "2.0",
    "template": {"outputs" : [{"simpleText": {"text": 
"""
'명령어'를 입력해 사용가능한 기능을 확인하실 수 있습니다.\n'급식 메뉴'를 입력해 선택한 날짜의 급식을 확인할 수 있습니다.\n'시간표'를 입력해 학급 시간표를 확인할 수 있습니다.
'강의실'을 입력해 이동수업 위치를 확인하실 수 있습니다.
"""
}}]
                 }
}
        #아래는 학사일정 
    elif (content == "학사일정 확인하기") or (content in "학사일정"): #학사일정 파싱시작. 몇달치 가져올건지 물어봄
        response = {
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : f"zzzzzz"}}
                ]
            }
        }
        #아래는 급식관련내용
        
    elif content == u"월":
        response = jsonChoiceParse
        Weekday(1)
        
    elif content == u"화":
        response = jsonChoiceParse
        Weekday(2)
    
    elif content == u"수":
        response = jsonChoiceParse
        Weekday(3)

    elif content == u"목":
        response = jsonChoiceParse
        Weekday(4)

    elif content == u"금":
        response = jsonChoiceParse
        Weekday(5)
        
    elif content == u"사용자 지정":
        response = {
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : "원하는 날짜를 입력해주세요. ex> 3월 1일 급식을 원하면 3.1"}}
                ]
            }
        }
        behave = 5
        
    elif (content == (u"급식 파싱" or u"급식파싱")) and behave == 1:
        Parsing(URL)
        if str(mealDay) in menu:
            response = {
            "version" : "2.0",
            "template" : {"outputs" : [{"simpleText" : {"text" : f"해당 날짜[{mealDay}]는 급식을 제공하지 않습니다."}}],
                          "quickReplies": [
                                  {"label": "급식 파싱 그만하기", "action": "message", "messageText": "끝내기"},
                                  {"label": "다시 하기", "action": "message", "messageText": "급식 재출력"}]
            }
    }
        elif mealDay < 0 or mealDay > len(menu):
            response = {
            "version" : "2.0",
            "template" : {"outputs" : [{"simpleText" : {"text" : f"해당 날짜[{mealDay}]는 이번 달에 포함되어 있지 않습니다. 이번 주가 달의 첫 주거나 마지막 주일때 비슷한 오류가 발생합니다."}}],
                            "quickReplies": [
                                    {"label": "급식 파싱 그만하기", "action": "message", "messageText": "끝내기"},
                                    {"label": "다시 하기", "action": "message", "messageText": "급식 재출력"}]
            }
    }
        else: #선택한 날짜메뉴 있을때
            Menutrim(menu, mealDay)     
            response = {
            "version" : "2.0",
            "template" : {"outputs" : [{"simpleText" : {"text" : f"{menuText}"}}],
                                "quickReplies": [
                                    {"label": "급식 파싱 그만하기", "action": "message", "messageText": "끝내기"},
                                    {"label": "다시 하기", "action": "message", "messageText": "급식 재출력"}]
            }
    }
        behave = 0
        menuText = ' '#메뉴텍스트는 리스트 아님 주의.
        menu = []
        mealDay = 0
        
    elif (content in "급식 메뉴") or (content in "급식메뉴") or (content == "급식 메뉴 확인하기") or (content == "급식 재출력"):
        response = jsonChoiceDay
        schulDate = f"{now.year}.{now.month}.{now.day}"
        URL = "https://{}/sts_sci_md00_001.do?schulCode={}&schulCrseScCode={}&schulKndScCode={}&schMmealScCode={}&schYmd={}".format(schulGion,schulCode,schulCrseScCode,schulKndScCode, schulMeal ,schulDate)
        #아래는 수행
        
    elif content == "수행평가":
        response = {
            "version" : "2.0",
            "template" : {"outputs" : [{"simpleText" : {"text" : "학생들이 과목별로 수행평가를 업로드하거나 확인할 수 있습니다. 현재 미완성 기능입니다."}}],
                          "quickReplies": [
                                {"label": "수행평가 확인하기", "action": "message", "messageText": "수행 확인"},
                                {"label": "수행평가 추가하기", "action": "message", "messageText": "수행 추가"}]
            }
    }

#아래는 사용자 등록기능

    elif content == "사용자 등록":
        response = {
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : "작업이 취소되었습니다."}}
                ]
            }
        }

    #아랜 명령어

    elif content == "/시간표수정":
        response = {
            "version" : "2.0",
            "template" : {"outputs" : [{"simpleText" : { "text" :
"""
수정할 반과 바뀐 시간표내용을 입력해주세요.
예시, 2학년 6반의 월요일을 수정할때->

주의 : 요일 대신 요일코드를 입력해주세요.
월요일은 1, 화 : 2, 수 : 3, 목 : 4, 금 : 5

2.6.1.선택과목A.선택과목B.수학.수학.수학.수학.창체
이 경우 2학년 6반 월요일 1교시 선택B, 마지막 교시 창체. 실수했거나 오류시 상담원에게 물어보세요."""}}],
                          "quickReplies": [
                                 {"label": "취소", "action": "message", "messageText": "취소"}]
             }
    }
        editbehave = 1
        
    elif content == "/강의실수정":
        response = {
            "version" : "2.0",
            "template" : {"outputs" : [{"simpleText" : { "text" :
"""
수정할 과목과 바뀐 이동위치를 입력해주세요.
예시, 정치와 법 B의 위치를 수정할때->

주의 : 예시에 있는 그대로 입력해야 인식가능합니다. 이름이 다를시 새 과목으로 인식합니다.
예: 정치와 법 과목 수정시-> 정치와 법이 아닌 정법으로 입력

2.정법.B.203호/2.확통.C-1.교무실
이 경우 2학년 정치와법 B 위치를 203호로, 확통 C-1의 위치를 교무실로 수정. 실수했거나 오류시 상담원에게 물어보세요."""}}],
                          "quickReplies": [
                                 {"label": "취소", "action": "message", "messageText": "취소"}]
             }
    }
        editbehave = 2
        
    elif content == "/백업":
        response = {
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : f"{schedulebackup},{movedata2}"}}]
            }
        }

    elif (content in u"명령어") or (content == "명령어") or (content == "명령어 확인하기"):
        behave = 0
        response = jsonChoiceBase

    elif content == u"시작하기":
         response = {
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : "카카오톡 봇이 시작되었습니다."}}]
            }
        }


    elif content == u"수행업로드":
        response = {
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : "ㄴ"}}]
            }
        }
        
    else:
        response = {
                 "version": "2.0",
                 "template": {
                 "outputs": [{
                     "carousel": { # 스킬가이드에 나온 캐러셀 형태
                         "type": "basicCard", # 기본형 선택 (<->비즈니스형도 존재)
                         "items": [{
                             "title": "이해하지 못했습니다.", # 제목
                             "description": "'명렁어'를 입력해 사용가능한 기능들을 확인해주세요.", # 설명
                             #"thumbnail": { # 썸네일 이미지
                                 #"imageUrl": can[0].imgurl
                             "buttons": [ # 버튼
                {
                                 "action": "message", # 동작 형태(텍스트 출력)
                                 "label": "명령어 출력하기", # 버튼 이름
                                 "messageText": "명령어"
                }]
            }
          ]
        }
      }
    ]
  }
}

    return jsonify(response)


#2023.3.01.content인식오류 발생함. 이거 해결해야함. 해결

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, debug=True)
