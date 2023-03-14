import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
import datetime
import json

now = datetime.datetime.now().today()

app = Flask(__name__)

schulCode = "P100000425" #학교코드
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
    menu = [i for i in menu if i not in remove]
    return menu 

def ParsingRiro(url2):#리로스쿨 학사일정 가져오기. 리로스쿨은 로그인필요해 id랑 PS로 로그인해 파싱.
    global ID, Ps
    #print(menu)
    
#https://stu.jbe.go.kr/popup.jsp?page=/ws/edusys/cm/sym/ocm/oi/sym_ocmoi_m02&popupID=20230313184856&w2xHome=/ws/edusys/pa/com/&w2xDocumentRoot= 하굑선택창
    
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
                 "outputs": [{
                     "carousel": { # 스킬가이드에 나온 캐러셀 형태
                         "type": "basicCard", # 기본형 선택 (<->비즈니스형도 존재)
                         "items": [{
                             "title": "명령어 목록.", # 제목
                             "description": "아래는 사용 가능한 기능들입니다. 기능들을 상세히 알고 싶다면 첫 버튼을 눌러주세요.",
                             #"thumbnail": { # 썸네일 이미지
                                 #"imageUrl": can[0].imgurl
                             "buttons": [ # 버튼
                {
                                 "action": "message", # 동작 형태(텍스트 출력)
                                 "label": "명령어 확인하기", # 버튼 이름
                                 "messageText": "추가 명령어"
                },
                {
                                 "action": "message", # 동작 형태(텍스트 출력)
                                 "label": "급식 메뉴 확인하기",
                                 "messageText": "급식 메뉴"
                },
                {
                                 "action": "message", # 동작 형태(텍스트 출력)
                                 "label": "시간표 확인하기",
                                 "messageText": "시간표"
                },
                {
                                 "action": "message", # 동작 형태(텍스트 출력)
                                 "label": "수행평가 확인/추가하기",
                                 "messageText": "수행평가"
                },
                {
                                 "action": "message", # 동작 형태(텍스트 출력)
                                 "label": "사용자 등록",
                                 "messageText": "사용자 등록"
                }]
            }
          ]
        }
      }
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
    
    global mealDay, behave, now, instruct, schedule, URL, a1, classpos, menuText, menu, jsonChoiceMonth, jsonChoiceBase
    
    now = datetime.datetime.now().today()
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
    
    if content == u"오늘":
        response = jsonChoiceParse
        Weekday(now.isoweekday())
	
    elif content == password:
        response = {
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : 
"""
아래는 데이터 수정및 주요 내용에 접근할 수 있는 명령어들입니다.
/시간표정보수정 -> 반의 시간표 정보를 수정할 수 있다.
/수행평가수정->잘못 추가한 수행평가 정보나, 일부러 추가한 가짜 수행평가 정보를 수정할수 있다.
                """}} # isoweekday로 얻은값이 4면 금요일을 의미하므로 금요일 초과(토,일)인지 확인한다.
                ]
            }
        }
        
    elif behave == 5:
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
        
        
    elif behave == 6 and (content == "오늘 시간표"):
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
    
    elif (content == "학사일정 확인하기") or (content in "학사일정"): #학사일정 파싱시작. 몇달치 가져올건지 물어봄
        response = jsonChoiceMonth
        behave = 2
        
    elif (content == "1") and (behave == 2):  #각 달마다 링크 달라짐.
        pass
        
    elif content == "강의실": #강의실내용 가져오기ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
        response = {
            "version" : "2.0",
            "template" : {
                "outputs" : [{"simpleText" : {"text" : f"{classpos}"}}
                ]
            }
        }
        
    elif behave == 6 and (content == "일주일 시간표"):
        response = {
    "version" : "2.0",
    "template" : {"outputs" : [{"simpleText" : {"text" : f"{schedule[0]}\n{schedule[1]}\n{schedule[2]}\n{schedule[3]}\n{schedule[4]}"}}],
                 "quickReplies" : [
                                  {"label" : "강의실 출력하기", "action" : "message", "messageText" : "강의실"},
                                  {"label" : "끝내기", "action" : "message", "messageText" : "끝내기"}
                                  ]
                 }
}
        behave = 0
        
    elif (content in u"시간표") or (content == "시간표") or (content == "시간표 확인하기"):
        response = {
    "verson" : "2.0",
    "template": {"outputs" : [{"simpleText" : {"text" : f"언제의 2학년 6반 시간표를 원하십니까?"}}],
                 "quickReplies" : [
                                  {"label" : "일주일 전체", "action" : "message", "messageText" : "일주일 시간표"},
                                  {"label" : "오늘", "action" : "message", "messageText" : "오늘 시간표"}
                                  ]
                 }
}
        behave = 6
    
    elif content == "추가 명령어":
        response = {
    "verson" : "2.0",
    "template": {"outputs" : [{"simpleText": {"text": 
"""
명령어'를 입력해 사용가능한 기능을 확인하실 수 있습니다.\n'급식 메뉴'를 입력해 선택한 날짜의 급식을 확인할 수 있습니다.\n'시간표'를 입력해 학급 시간표를 확인할 수 있습니다.
"""
}}]
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
        now = datetime.datetime.now().today()
        schulDate = f"{now.year}.{now.month}.{now.day}"
        URL = "https://{}/sts_sci_md00_001.do?schulCode={}&schulCrseScCode={}&schulKndScCode={}&schMmealScCode={}&schYmd={}".format(schulGion,schulCode,schulCrseScCode,schulKndScCode, schulMeal ,schulDate)

        #아래는 현재작업중단
        
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
        
        #아래는 수행
        
    elif content == "수행평가":
    	response = {
            "version" : "2.0",
            "template" : {"outputs" : [{"simpleText" : {"text" : "학생들이 과목별로 수행평가를 업로드하거나 확인할 수 있습니다."}}],
                          "quickReplies": [
                                  {"label": "수행평가 확인하기", "action": "message", "messageText": "수행 확인"},
                                  {"label": "수행평가 추가하기", "action": "message", "messageText": "수행 추가"}]
            }
    }
        
    #아래는 사용자 등록기능
    
    elif content == "사용자 등록":
        pass
        #아래는 기타
        
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
