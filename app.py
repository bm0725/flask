import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
import datetime
import json

now = datetime.datetime.now()

app = Flask(__name__)

schulCode = "P100000425"
schulname = "전주신흥고등학교" #사이트 학교알리미에서 받아옴
schulKndScCode= "04"
schulCrseScCode = "4"
schulGion = "stu.jbe.go.kr"
schulMeal = "1"
#이것들을 수정하면 다른 학교의 식단 파싱도 가능하다.
menu = [] #이곳에 메뉴를 넣는다.

menuText = ' '

ID = ""#리로스쿨 일정파싱용 운영자 ID, 비번. /개발자명령어를 입력해 수정가능.
PS = ""
password = "chatbot206"

print(now.day, now.isoweekday())
print(type(now.day),type(now.isoweekday()))

behave = 0 #1은 급식파싱, 2는 일정파싱, 3은 시간표, 4는 수행출력, 5는 급식 선택, 6은 jsonchoicedata, 7은 개발자모드(데이터수정)
mealDay = 0 #급식파싱할때 쓸 날짜 넣을 변수다.
    
schulDate = f"{now.year}.{now.month}.{now.day}"


URL = "https://{}/sts_sci_md00_001.do?schulCode={}&schulCrseScCode={}&schulKndScCode={}&schMmealScCode={}&schYmd={}".format(schulGion,schulCode,schulCrseScCode,schulKndScCode, schulMeal ,schulDate)



def Parsing(url): # 함수.  URL넣으면 나이스에서 급식 파싱해 가져옴
    global menu, URL
    url = str(url)
    res = requests.get(url)
    soup = BeautifulSoup(res.text,"html.parser")
    text= soup.select_one('#contents > div:nth-child(2) > table > tbody') #급식

    menu = text.get_text()
    menu = menu.split("\n")
    remove = {'', ' '}
    menu = [i for i in menu if i not in remove] #잡코드 정리
    #print(menu)
    return menu 

def Weekday(weekday): #급식날짜계산함수. 월이 0 ~ 일이 6
    global mealDay, behave
    
    weekday = int(weekday)
    weekdaynow = now.isoweekday()
    if weekdaynow == weekday:
        mealDay = int(now.day - 1)
    else:
        if weekdaynow > weekday :
            mealDay = int(now.day) - (weekdaynow - weekday)
        else:
            mealDay = int(now.day) +(weekday - weekdaynow)
    
    behave = 1#급식파싱시작
        
    return mealDay, behave

def Menutrim(menu, mealDay): #메뉴를 보기 쉽게 정렬하는 합수다. 알레르기 정보를 전부 떼서 없앤다.
    
    global menuText
    c = menu[mealDay]
    c = c.split('.')
    
    remove = {'1', '2' , '3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20'}
    c = [i for i in c if i not in remove]
    i = 0
    while True:
        blank = c[i][:-1]
        menuText += f"{blank}\n"
        i = i + 1
        if len(c) == i + 1:
            break
    return menuText

schedule = [
    "월요일\n 1교시 : 문학\n 2교시 : 2학년 선택과목 C\n 3교시 : 체육\n 4교시 : 일본어/중국어\n 5교시 : 영어Ⅰ\n6교시 : 2학년 선택과목 B\n7교시 : 2학년 선택과목 A\n",
    "화요일\n 1교시 : 문학\n 2교시 : 영어 Ⅰ\n 3교시 : 수학 Ⅰ\n 4교시 : 2학년 선택과목 A\n 5교시 : 일본어/중국어\n6교시 : 2학년 선택과목 B\n7교시 : 2학년 선택과목 C\n",
    "수요일\n 1교시 : 2학년 선택과목 B\n 2교시 : 일본어/중국어\n 3교시 : 예배\n 4교시 : 창체\n 5교시 : 수학 Ⅰ\n6교시 : 영어 Ⅰ\n7교시 : 2학년 선택과목 C\n",
    "목요일\n 1교시 : 2학년 선택과목 C\n 2교시 : 영어 Ⅰ\n 3교시 : 2학년 선택과목 A\n 4교시 : 2학년 선택과목 B\n 5교시 : 연극\n6교시 : 문학\n7교시 : 수학 Ⅰ\n",
    "금요일\n 1교시 : 2학년 선택과목 A\n 2교시 : 문학\n 3교시 : 수학 Ⅰ\n 4교시 : 연극\n 5교시 : 창체\n6교시 : 창체\n7교시 : 창체\n"
]

classpos = [
]


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

jsonChoiceBase = {
    "version": "2.0",
    "template": {"outputs": [{"simpleText": {"text": "무엇을 하시겠어요?"}}],
                 "quickReplies": [
                                  {"label": "명령어 확인하기", "action": "message", "messageText": "명령어 확인하기"},
                                  {"label": "급식 메뉴 확인하기", "action": "message", "messageText": "급식 메뉴 확인하기"},
                                  {"label": "학사일정 확인하기", "action": "message", "messageText": "학사일정 확인하기"},
                                  {"label": "시간표 확인하기", "action": "message", "messageText": "시간표 확인하기"},
                                  {"label": "수행평가 확인하기", "action": "message", "messageText": "수행평가 확인하기"},
                                  {"label": "사용자 지정", "action": "message", "messageText": "사용자 지정"}
                                  ]
                 }
}

jsonChoiceParse = {
    "version": "2.0",
    "template": {"outputs": [{"simpleText": {"text": "무엇을 하시겠어요?"}}],
                 "quickReplies": [
                                  {"label": "취소", "action": "message", "messageText": "취소"},
                                  {"label": "선택한 급식메뉴 확인하기", "action": "message", "messageText": "급식 파싱"}
                                  ]
                 }
}

instruct ="""명령어 목록입니다.
'명령어'가 들어간 채팅을 쳐 이 명령어 설명들과 빠른 이동을 불러올 수 있습니다.
'급식'이 들어간 채팅을 쳐 원하는 요일이나 오늘의 급식 메뉴를 확인할 수 있습니다.
"""

@app.route('/keyboard')

def Keyboard():

    return jsonify( {"type" : "text"} )



@app.route('/message', methods=['POST'])
def message():  
    
    global mealDay, behave, now, instruct, schedule, URL, a1, classpos, menuText
    
    now = datetime.datetime.now()
    
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
    
    if content == u"오늘":
        response = jsonChoiceParse
        Weekday(now.isoweekday())
	
    elif content == password:
       response = {
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : 
"""
가나다라마바사아자
                """}} # isoweekday로 얻은값이 4면 금요일을 의미하므로 금요일 초과(토,일)인지 확인한다.
                ]
            }
        }
        
    elif behave == 5:
        a1 = content.split('.')
        print(a1)
        schulDate = f"{now.year}.{a1[0]}.{a1[1]}" #
        behave = 1
        URL = "https://{}/sts_sci_md00_001.do?schulCode={}&schulCrseScCode={}&schulKndScCode={}&schMmealScCode={}&schYmd={}".format(schulGion,schulCode,schulCrseScCode,schulKndScCode, schulMeal ,schulDate)
        response = jsonChoiceParse
        #URL = 에서 급식을 파싱할때 날짜가 변할 수 있으므로 현재 날짜로 바꿔 출력한다.
        
        
    elif behave == 6 and (content == "오늘 시간표"):
        now = datetime.datetime.now()
        if int(now.isoweekday()) > 4:
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
            "template" : {
                "outputs" : [{"simpleText" : {"text" : f"{schedule[(now.isoweekday()-1)]}"}} #달력과 다르게 리스트는 0부터 시작하므로 -1을 해줘야 한다.
                ]
            }
        }
        behave = 0
       
    elif content == "강의실":
        response = {
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : f"{classpos}"}}
                ]
            }
        }
        
    elif behave == 6 and (content == "일주일 시간표"):
        response = {
    "version": "2.0",
    "template": {"outputs": [{"simpleText": {"text": f"{schedule[0]}\n{schedule[1]}\n{schedule[2]}\n{schedule[3]}\n{schedule[4]}"}}],
                 "quickReplies": [
                                  {"label": "강의실 출력하기", "action": "message", "messageText": "강의실"},
                                  {"label": "끝내기", "action": "message", "messageText": "끝내기"}
                                  ]
                 }
}
        behave = 0

    elif content == u"월":
        response = jsonChoiceParse
        Weekday(0)
        
    elif content == u"화":
        response = jsonChoiceParse
        Weekday(1)
    
    elif content == u"수":
        response = jsonChoiceParse
        Weekday(2)

    elif content == u"목":
        response = jsonChoiceParse
        Weekday(3)

    elif content == u"금":
        response = jsonChoiceParse
        Weekday(4)
        
    elif content == u"사용자 지정":
        response = {
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : "원하는 날짜를 입력해주세요. ex> 3월 1일 급식을 원하면 3.1"}}
                ]
            }
        }
        behave = 5
        
    elif (content in u"시간표") or (content == "시간표") or (content == "시간표 확인하기"):
        response = {
    "version": "2.0",
    "template": {"outputs": [{"simpleText": {"text": f"언제의 2학년 6반 시간표를 원하십니까? 강의실 정보도 같이 출력됩니다."}}],
                 "quickReplies": [
                                  {"label": "일주일 전체", "action": "message", "messageText": "일주일 시간표"},
                                  {"label": "오늘", "action": "message", "messageText": "오늘 시간표"}
                                  ]
                 }
}
        behave = 6
        
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
        menuText = []
        print(menu)
        menu = []
        
    elif (content in "급식 메뉴") or (content in "급식메뉴") or (content == "급식 메뉴 확인하기") or (content == "급식 재출력"):
        response = jsonChoiceDay
        now = datetime.datetime.now()
        schulDate = f"{now.year}.{now.month}.{now.day}"
        URL = "https://{}/sts_sci_md00_001.do?schulCode={}&schulCrseScCode={}&schulKndScCode={}&schMmealScCode={}&schYmd={}".format(schulGion,schulCode,schulCrseScCode,schulKndScCode, schulMeal ,schulDate)
    
    elif content == u"취소":
        behave = 0
        response = {
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : "작업이 취소되었습니다."}}
                ]
            }
        }
    elif content == "끝내기":
        behave = 0
        response = {
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : "작업이 끝났습니다. 해당 작업을 다시 하고 싶으시다면 '급식 메뉴'와 같이 시작 발화를 입력해주세요."}}
                ]
            }
        }
    elif (content in u"명령어") or (content == "명령어") or (content == "명령어 확인하기"):
        behave = 0
        response = {
    "version": "2.0",
    "template": {"outputs": [{"simpleText": {"text": f"{instruct}"}}],
                 "quickReplies": [
                                  {"label": "명령어 확인하기", "action": "message", "messageText": "명령어 확인하기"},
                                  {"label": "급식 메뉴 확인하기", "action": "message", "messageText": "급식 메뉴 확인하기"},
                                  {"label": "학사일정 확인하기", "action": "message", "messageText": "학사일정 확인하기"},
                                  {"label": "시간표 확인하기", "action": "message", "messageText": "시간표 확인하기"},
                                  {"label": "수행평가 확인하기", "action": "message", "messageText": "수행평가 확인하기"}
                                  ]
                 }
}
    elif content == u"안녕":
        response = {
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : "안녕하세요."}}
                ]
            }
        }

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
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : "이해못했다. ㅇㅇ"}}]
            }
        }

    return jsonify(response)


#2023.3.01.content인식오류 발생함. 이거 해결해야함. 해결

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, debug=True)
