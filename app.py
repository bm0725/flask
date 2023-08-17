import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
import datetime
import json
import os
import sys
import re

now = datetime.datetime.now()
now = now + datetime.timedelta(hours=9)
app = Flask(__name__)

schulCode = "8320109"  # 학교코드
schulname = "전주신흥고등학교"  # 사이트 학교알리미에서 받아옴
KEY = "3839047818934aeaa7790af7d7ebd61e"  # 나이스 api 키. 개인용이니 변경필요
base_url = "https://open.neis.go.kr/hub/"
YMD = ""  # 급식가져올 날짜. 20230101같은 형식
schulGion = "P10"  # 학교 지역코드

# 이것들을 수정하면 다른 학교의 식단 파싱도 가능하다.
menu = ""  # 이곳에 메뉴를 넣는다.

password = "chatbot206"

print(now.day, now.isoweekday())
print(type(now.day), type(now.isoweekday()))

alldata = {}

behave = 0  # 1은 급식파싱, 2 시간표, 6 학사. 345 7 수행. 8 인원 모집
mealDay = "0"  # 급식파싱할때 쓸 날짜 넣을 변수다.

schulDate = f"{now.year}.{now.month}.{now.day}"

MenuURL = f"{base_url}mealServiceDietInfo?KEY={KEY}&ATPT_OFCDC_SC_CODE={schulGion}&SD_SCHUL_CODE={schulCode}&MLSV_YMD={YMD}&Type=json"
ScheduleURL = f"{base_url}SchoolSchedule?KEY={KEY}&ATPT_OFCDC_SC_CODE={schulGion}&SD_SCHUL_CODE={schulCode}&AA_YMD={YMD}&Type=json"


def ParsingMenu(url):   # 함수. URL넣으면 나이스api에서 급식 파싱해 가져옴
    global menu
    print(url)
    menu = ""
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    basemenu = soup.get_text()
    basemenu = json.loads(basemenu)
    if "RESULT" in basemenu:
        menu = "급식 없음"
    else:
        treat = basemenu["mealServiceDietInfo"][1]["row"] #처리할부분만
        for i in range(0, len(treat)):
            menus = basemenu["mealServiceDietInfo"][1]["row"][i]
            menu += f"\n{menus['MMEAL_SC_NM']}\n\n" + "\n".join(menus['DDISH_NM'].split(" ")) + f"\n칼로리 : {menus['CAL_INFO']}"  #순서대로 식사 일정, 메뉴, 칼로리
    return menu

def ParsingSchedule(grade, month):  # 나이스 api 학사일정 가져오기
    global schedule, now
    if len(month) == 1:
        month = "0" + month
    print(str(now.year)+month)
    URL = f"{base_url}SchoolSchedule?KEY={KEY}&ATPT_OFCDC_SC_CODE={schulGion}&SD_SCHUL_CODE={schulCode}&AA_YMD={str(now.year)+month}&Type=json"  # url만듬
    print(URL)
    schedule = "선택한 월의 학사일정\n"
    if grade == "1":  # 학년별 검사
        grade = 'ONE_GRADE_EVENT_YN'
    elif grade == "2":
        grade = 'TW_GRADE_EVENT_YN'
    elif grade == "3":
        grade = 'THREE_GRADE_EVENT_YN'
    else:
        grade = "pass"
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, 'html.parser')
    basesch = soup.get_text()
    basesch = json.loads(basesch)
    if "RESULT" in basesch:
        schedule = "해당 월의 학사일정은 nice에 올라오지 않았습니다."
    else:
        basesch = basesch['SchoolSchedule'][1]['row']  # 학사일정 부분 뗴오기
        Days = len(basesch)
        if grade == "pass":  # 학년선택 안하면
            for i in range(Days):
                schedule = schedule + f"{int(basesch[i]['AA_YMD'][-2:])}일 : {basesch[i]['EVENT_NM']}\n"
        else:
            for i in range(Days):
                if basesch[i][grade] == "Y":
                    schedule = schedule + f"{int(basesch[i]['AA_YMD'][-2:])}일 : {basesch[i]['EVENT_NM']}\n"
    return schedule

def ParsingBanSchedule(grade, ban):  # 학년, 반순서 데이터입력.   <-시간표 가져오는 함수. 데이터 변수 많아서 스파게티됨.
    global now, fillter, banSchedule
    banSchedule = f"이번 주(일요일 포함) {grade}-{ban} 시간표\n\n"  # 출력
    allschedule = []  # 요일시간표 다 넣을 리스트
    # 이번 주의 월요일 찾기
    start_of_week = now - datetime.timedelta(days=now.weekday())
    # 월요일부터 금요일까지의 날짜 계산
    days = []
    for i in range(0, 5):  # 월요일부터 금요일까지의 범위
        day = start_of_week + datetime.timedelta(days=i)
        if day > now:  # 이번 주를 넘어가면 종료
            break
        days.append(day)
    daylist = [day.strftime("%Y%m%d") for day in days]

    for YMD in daylist:
        URL = f"https://open.neis.go.kr/hub/hisTimetable?KEY={KEY}&ATPT_OFCDC_SC_CODE={schulGion}&SD_SCHUL_CODE={schulCode}&ALL_TI_YMD={YMD}&GRADE={grade}&CLASS_NM={ban}&Type=json"
        res = requests.get(URL)
        soup = BeautifulSoup(res.text, 'html.parser')
        schedule = soup.get_text()
        schedule = json.loads(schedule)
        if 'hisTimetable' not in schedule:
            allschedule.append([])
        else:
            schedule = schedule['hisTimetable'][1]['row']
            allschedule.append([schedule[i]['ITRT_CNTNT'] for i in range(len(schedule))])  # 한줄반복문으로 과목다떼옴
    print(allschedule)
    if len(allschedule) > 2:
        allschedule[2].insert(3, "예배")  # 예배는 나이스 시간표에 존재하지 않음
    # print(allschedule)
    for z in range(0,5):  # 시험 등 상황시 오류방지
        if z >= len(allschedule):  # 뭔가 오류나서 시간표 짤린경우
            allschedule.append(["특수", "특수", "특수", "특수", "시간표를 제대로 불러오지 못했습니다.", "nice에 시간표가 없을 수 있습니다.", "정상 시간표보다 수업시간 수가 적을 수 있습니다."])
        elif len(allschedule[z]) != 7:  #  시험처럼 시간수 줄어든경우
            allschedule[z] = ["특수", "특수", "특수", "특수", "시간표를 제대로 불러오지 못했습니다.", "nice에 시간표가 없을 수 있습니다.", "정상 시간표보다 수업시간 수가 적을 수 있습니다."]

    for x in range(0,5):
        banSchedule += "\n".join(f"{allschedule[x][y]}" if fillter[grade][str(x)][y] == 0 else f"{fillter[grade][str(x)][y]}" for y in range(0,7))  # test에 있는 고정시간표로 덮기, 텍스트화
        banSchedule += "\n\n"
    return banSchedule


def Weekday(day):  # 급식날짜계산함수. 이해할 것.
    global mealDay, behave
    if day == "오늘":
        mealDay = now.strftime('%Y%m%d')
    else:
        weekdays = ['월', '화', '수', '목', '금', '토', '일']
        today = datetime.datetime.today()
        days_until_day = (weekdays.index(day) - today.weekday()) % 7
        target_day = today + datetime.timedelta(days=days_until_day)
        mealDay = target_day.strftime('%Y%m%d')
    return mealDay

def PanLoading():
    global pan, panResult
    panResult = "게시글 목록\n\n"
    panResult += "\n".join(f"{z+1}. {pan[z]['name'][:20]}..." if len(pan[z]['name']) > 20 else f"{z+1}. {pan[z]['name']}" for z in range(0, len(pan)))
    return panResult

jsonChoiceDay = {
    "version": "2.0",
    "template": {"outputs": [{"simpleText": {"text": "날짜를 선택해 주세요. 이번주 해당 요일의 급식이 출력됩니다.\nEX->0807입력시 이번년 8월 7일자 급식 출력됨."}}],
                 "quickReplies": [{"label": "오늘", "action": "message", "messageText": "오늘"},
                                  {"label": "월", "action": "message", "messageText": "월"},
                                  {"label": "화", "action": "message", "messageText": "화"},
                                  {"label": "수", "action": "message", "messageText": "수"},
                                  {"label": "목", "action": "message", "messageText": "목"},
                                  {"label": "금", "action": "message", "messageText": "금"},
                                  {"label": "취소하기", "action": "message", "messageText": "취소"}
                                  ]
                 }
}
choice = {
    "물리": ["315호(2023 2학기)"],
    "화학": ["416호(2023 2학기)"],
    "생명": ["312호(2023 2학기)"],
    "지구": ["A/C-1 => 412호, B/C-2 => 415호(2023 2학기)"],
    "경제": ["2-9반(2023 2학기)"],
    "정법": ["2-8반(2023 2학기)"],
    "사문": ["2-10반(2023 2학기)"],
    "세계사": ["2-7반(2023 2학기)"],
    "한국지리": ["2-1반(2023 2학기)"],
    "생윤" : ["A/B-1/C => 2-2반, B-2 => 2-5반(2023 2학기)"],
    "영미문학읽기": ["도서관 212호(2023 2학기)"],
    "기본영어" : ["2-3반(2023 2학기)"],
    "문학개론": ["213호(2023 2학기)"],
    "심화국어" : ["2-5반(2023 2학기)"],
    "확통": ["A/B => 2-7반, C => 2-6반(2023 2학기)"],
    "수과탐": ["214호(2023 2학기)"],
    "일본어": ["119호(2023 2학기)"],
    "중국어": ["118호(2023 2학기)"],
    "고전읽기" : ["3-3반(2023 2학기)"],
    "현대문학감상" : ["213호(2023 2학기)"]
            }

pan = [
        {"user" : "백민재", "name" : "동아리 프레너미 모집", "detail" : "프로그래밍/코딩 동아리 프레너미에서 컴퓨터에 관심있는 학생들을 모집합니다. 2024년 동아리 신청 때 많이 신청해 주세요.", "number" : "2211011@jsh.hs.kr", "date" : "2023.7.23"}
        ]
    
homeworkdata = {
    "1": {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [], "10": []},
    "2": {"1": [], "2": [], "3": [], "4": [], "5": [], "6": ["지각하지 않기", "화작 EBS 수특 부교재 구매"], "7": [], "8": [], "9": [], "10": []},
    "3": {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [], "10": []}
     
                }
fillter = {
    "1": {"0": [0, 0, 0, 0, 0, 0, 0], "1": [0, 0, 0, 0, 0, 0, 0], "2": [0, 0, 0, 0, 0, 0, 0], "3": [0, 0, 0, 0, 0, 0, 0], "4": [0, 0, 0, 0, 0, 0, 0]},
    "2": {"0": ["선택과목 A", "선택과목 B", 0, 0, "선택과목 C", 0, 0], "1": ["선택과목 C", 0, 0, "선택과목 A", "선택과목 B", 0, 0], "2": ["선택과목 B", 0, 0, 0, "선택과목 A", 0, 0], "3": [0, "선택과목 A", 0, "선택과목 B", 0, 0,"선택과목 C"], "4": [0, "선택과목 C", 0, 0, 0, 0, 0]},
    "3": {"0": [0, 0, "선택과목 B", 0, 0, "선택과목 A", "선택과목 C"], "1": [0, "선택과목 A", "선택과목 C", 0, 0, "선택과목 B", 0], "2": [0, 0, 0, 0, 0, 0, "선택과목 B"], "3": ["선택과목 B", 0, 0, 0, 0, "선택과목 A", "선택과목 C"], "4": [0, 0, "선택과목 A", "선택과목 C", 0, 0, 0]}
            }

idlog = {
    
        } #id마다의 행동을 저장해둘 딕셔너리.

@app.route('/keyboard')


def Keyboard():
    return jsonify({"type": "text"})


@app.route('/message', methods=['POST'])
def message():

    global mealDay, behave, now, schedule, MenuURL, menu, response
    global homeworkdata, fillter, banSchedule, alldata, choice, pan, idlog, ID

    now = datetime.datetime.now()
    now = now + datetime.timedelta(hours=9)
    print(now.day)

    dataReceive = request.get_json()
    content = dataReceive['userRequest']['utterance']
    ID = dataReceive['userRequest']['user']['id']
    if ID not in idlog: #아이디 미등록. behave를 id마다 다르게 지정해 오류 방지
        idlog[ID] = 0
    
    print("아래 :", content)
    # print(type(content))
    print(idlog[ID])

    if (content == u"취소") or (content == "끝내기"):
        idlog[ID] = 0
        response = {
            "version": "2.0",
            "template": {
                "outputs": [{"simpleText": {"text": "작업이 취소되었습니다."}}
                           ]
                        }
                    }

    elif idlog[ID] == 1:  # 급식파싱
        if len(content) < 3:  # 월화수목금 오늘 등 시
            Weekday(content)
        else:  # 선텍날짜일때
            content = content.replace("월", "").replace("일", "").replace(" ", "").replace(",", "")  # 실수 방지
            if len(content) == 4:  # 형식맞추면
                mealDay = now.strftime("%Y")+content  # 해당급식으로 선택.
            else:
                idlog[ID] = 0
                response = {"version": "2.0", 
                            "template": {
                                       "outputs": [{"simpleText": {"text": f"형식에 맞춰 주세요. 이번년도 급식 데이터만 가능합니다. ex) 1212 ->12월 12일 급식"}} # 형식안맞으면 취소.
                                                  ]
                                        }
                            }
        if idlog[ID] == 1:  # 오류없으면
            MenuURL = f"{base_url}mealServiceDietInfo?KEY={KEY}&ATPT_OFCDC_SC_CODE={schulGion}&SD_SCHUL_CODE={schulCode}&MLSV_YMD={mealDay}&Type=json"
            ParsingMenu(MenuURL)
            if menu == "급식없음":  # 급식없으면
                response = {
                    "version": "2.0",
                    "template": {"outputs": [{"simpleText": {"text": f"해당 날짜[{mealDay}]는 급식을 제공하지 않습니다."}}],
                                 "quickReplies": [
                                                {"label": "끝내기", "action": "message", "messageText": "끝내기"},
                                                {"label": "다시 하기", "action": "message", "messageText": "급식 재출력"}]
                                 }
                            }
            else:  # 급식있으면
                response = {
                    "version": "2.0",
                    "template": {"outputs": [{"simpleText": {"text": f"{mealDay}일 급식메뉴\n{menu}"}}],
                                 "quickReplies": [
                                                {"label": "끝내기", "action": "message", "messageText": "끝내기"},
                                                {"label": "다시 하기", "action": "message", "messageText": "급식 재출력"}]
                                 }
                           }
        idlog[ID] = 0
        menu = ""
        mealDay = "0"

    elif idlog[ID] == 2:  # 학년 월 순 데이터, 학사일정 파싱
        content = content.replace("월", "").replace("학년", "").replace(",", ".")
        a1 = content.split(".")
        if len(a1) == 1:
            ParsingSchedule("없음", a1[0])
            response = {
                "version": "2.0",
                "template": {"outputs": [{"simpleText": {"text": f"{schedule}"}}],
                             "quickReplies": [
                                            {"label": "학사일정 확인 그만하기", "action": "message", "messageText": "끝내기"},
                                            {"label": "다시 하기", "action": "message", "messageText": "학사일정 재출력"}]
                            }
                       }
        elif len(a1) == 2:
            ParsingSchedule(a1[0], a1[1])
            response = {
                "version": "2.0",
                "template": {"outputs": [{"simpleText": {"text": f"{schedule}"}}],
                             "quickReplies": [
                                            {"label": "학사일정 확인 그만하기", "action": "message", "messageText": "끝내기"},
                                            {"label": "다시 하기", "action": "message", "messageText": "학사일정 재출력"}]
                            }
                       }
        else:
            response = {
                "version": "2.0",
                "template": {"outputs": [{"simpleText": {"text": f"형식을 맞춰주세요."}}],
                             "quickReplies": [
                                            {"label": "학사일정 확인 그만하기", "action": "message", "messageText": "끝내기"},
                                            {"label": "다시 하기", "action": "message", "messageText": "학사일정 재출력"}]
                            }
                       }
        idlog[ID] = 0
        schedule = ""

    elif idlog[ID] == 3:
        if (content not in choice) or (len(choice[content])) == 0:
            response = {
                "version": "2.0",
                "template": {"outputs": [{"simpleText": {"text": "해당 과목의 정보가 없거나, 등록되지 않았습니다." } } ],
                             "quickReplies": [
                                            {"label": "그만하기", "action": "message", "messageText": "끝내기"},
                                            {"label": "다른과목 확인", "action": "message", "messageText": "수행평가 확인/선택"}]
                            }
                       }
        else:
            response = {
                "version": "2.0",
                "template": {"outputs": [{"simpleText": {"text": f"{content} 정보"+"\n\n"+"\n-- ".join(choice[content]) } } ],
                             "quickReplies": [
                                            {"label": "그만하기", "action": "message", "messageText": "끝내기"},
                                            {"label": "다른과목 확인", "action": "message", "messageText": "수행평가 확인/선택"}]
                            }
                       }
        idlog[ID] = 0

    elif idlog[ID] == 4:
        choban = content.replace(",",".").replace(" ","").split(".")
        if (len(choban) != 2) or (choban[1] not in ["1","2","3","4","5","6","7","8","9","10"]) or(choban[0] not in ["1","2","3"]):
            response = {
                "version": "2.0",
                "template": {"outputs": [{"simpleText": {"text": "해당 학반의 정보가 없거나, 정상적인 학반 데이터가 아닙니다." }}],
                             "quickReplies": [
                                            {"label": "그만하기", "action": "message", "messageText": "끝내기"},
                                            {"label": "다시하기", "action": "message", "messageText": "수행평가 확인/반"}]
                            }
                       }
        else:
            response = {
                "version": "2.0",
                "template": {"outputs": [{"simpleText": {"text": f"{content} 반 정보\n\n"+"\n".join(homeworkdata[choban[0]][choban[1]]) } } ],
                             "quickReplies": [
                                            {"label": "그만하기", "action": "message", "messageText": "끝내기"},
                                            {"label": "다른 반 확인", "action": "message", "messageText": "수행평가 확인/반"}]
                            }
                       }
        idlog[ID] = 0

    elif idlog[ID] == 5:
        work = content.split("/")
        if len(work) != 2:
            response = {
                "version": "2.0",
                "template": {"outputs": [{"simpleText": {"text": "혹시 /를 2번 이상 사용하셨나요? 자료 처리에 오류가 발생했습니다.\n 적합한 형태로 입력해 주세요." } } ],
                             "quickReplies": [
                                            {"label": "취소", "action": "message", "messageText": "취소"},
                                            {"label": "다시 등록", "action": "message", "messageText": "수행평가 등록/선택"}]
                            }
                       }
        else:
            if work[0] not in choice:
                choice[work[0]] = []
            choice[work[0]].append(work[1])
            response = {
                "version": "2.0",
                "template": {"outputs": [{"simpleText": {"text": f"등록 완료.\n 과목 : {work[0]}\n 내용 : {work[1]}" } } ],
                             "quickReplies": [
                                            {"label": "다시 등록", "action": "message", "messageText": "수행평가 등록/선택"}]
                            }
                       }
            idlog[ID] = 0
            
    elif idlog[ID] == 6:  # 시간표 선택하기
        schlist = content.replace(" ","").replace(",",".").split(".")
        if len(schlist) != 2:
            response = {
            "version": "2.0",
            "template": {
                "outputs": [{"simpleText" : {"text" : f"입력 형태를 맞춰 주세요."}}  # 달력과 다르게 리스트는 0부터 시작하므로 -1을 해줘야 한다.
                           ]
                        }
                   }
        else:
            ParsingBanSchedule(schlist[0], schlist[1])
            response = {
            "version": "2.0",
            "template": {
                "outputs": [{"simpleText" : {"text" : f"{banSchedule}"}}  # 달력과 다르게 리스트는 0부터 시작하므로 -1을 해줘야 한다.
                           ]
                        }
                   }
        idlog[ID] = 0

    elif idlog[ID] == 7:
        banlist = content.split("/")
        if (len(banlist) != 3) or (banlist[1] not in ["1","2","3","4","5","6","7","8","9","10"]) or(banlist[0] not in ["1","2","3"]):
            response = {
                "version": "2.0",
                "template": {"outputs": [{"simpleText": {"text": "혹시 / 를 3번 이상 사용하셨나요?\n 학반을 정확히 입력하지 않았나요?\n자료 처리에 오류가 발생했습니다.\n 적합한 형태로 입력해 주세요." } } ],
                             "quickReplies": [
                                            {"label": "취소", "action": "message", "messageText": "취소"},
                                            {"label": "다시 등록", "action": "message", "messageText": "수행평가 등록/반"}]
                            }
                       }
        else:
            if banlist[1] not in homeworkdata[banlist[0]]:
                homeworkdata[banlist[0]][banlist[1]] = []
            homeworkdata[banlist[0]][banlist[1]].append(banlist[2])
            response = {
                "version": "2.0",
                "template": {"outputs": [{"simpleText": {"text": f"등록 완료.\n 학반 : {banlist[0]}/{banlist[1]}\n 내용 : {banlist[2]}" } } ],
                             "quickReplies": [
                                            {"label": "다시 등록", "action": "message", "messageText": "수행평가 등록/반"}]
                            }
                       }
            idlog[ID] = 0

    elif idlog[ID] == 8:
        panchoice = content.replace(".","").replace("번","")
        try:
            pch = int(panchoice)
            pch2 = pan[pch-1]
            response = {
                "version": "2.0",
                "template": {"outputs": [{"simpleText": {"text": f"{pch2['name']} / {pch2['user']}"+"\n\n"+f"{pch2['detail']}\n\n연락처 : {pch2['number']}\n등록 날짜 : {pch2['date']}" } } ],
                             "quickReplies": [
                                            {"label": "글 그만 보기", "action": "message", "messageText": "끝내기"}]
                            }
                       }
        except:
            response = {
                "version": "2.0",
                "template": {"outputs": [{"simpleText": {"text": "한글을 섞으면 정상적 출력이 불가합니다. 다시 시도해주세요." } } ],
                             "quickReplies": [
                                            {"label": "글 그만 보기", "action": "message", "messageText": "끝내기"}]
                            }
                       }

    elif idlog[ID] == 9:
        pansplit = content.split("/")
        if len(pansplit) == 4:
            pan.append({'name' : pansplit[0], 'user' : pansplit[1], 'detail' : pansplit[2], 'number' : pansplit[3], 'date' : now.strftime('%Y.%m.%d')})
            response = {
                "version": "2.0",
                "template": {"outputs": [{"simpleText": {"text": "등록되었습니다." } } ],
                             "quickReplies": [
                                            {"label": "올라갔는지 확인하기", "action": "message", "messageText": "모집/게시판"}]
                            }
                       }
            idlog[ID] = 0

        else:
            response = {
                "version": "2.0",
                "template": {"outputs": [{"simpleText": {"text": "오류 발생\n/를 기준으로 데이터를 나눕니다. /은 꼭 3번만 사용해 주세요.\n다시 입력해 보시고 또 오류 발생시 상담원에게 연락해 주세요." } } ],
                             "quickReplies": [
                                            {"label": "취소", "action": "message", "messageText": "취소"}]
                            }
                       }


    elif (content in u"시간표") or (content == "시간표") or (content == "시간표 확인하기"):
        idlog[ID] = 6
        response = {
    "version": "2.0",
        "template": {"outputs": [{"simpleText": {"text" : "몇학년 몇반의 이번주 시간표를 보시겠습니까? 2.6 입력시 2학년 6반 시간표가 출력됩니다."}}],
                "quickReplies": [  
                                    {"label": "취소하기", "action" : "message", "messageText" : "취소"}
                                    ]
                    }
}

        # 아래는 학사일정
    elif (content == "학사일정 확인하기") or (content in "학사일정") or (content == "학사일정 재출력"):  # 학사일정 파싱시작. 몇달치 가져올건지 물어봄
        response = {
            "version": "2.0",
            "template": {"outputs": [{"simpleText": {"text": "원하는 학년과 월을 선택해주세요. ex)2.3->2학년 3월 학사일정.\n선택을 원하지 않을 경우 학년을 입력하지 마세요. ex)4->4월 학사일정"}}],
                          "quickReplies": [
                                {"label": "취소하기", "action": "message", "messageText": "취소"}]
                        }
                   }
        idlog[ID] = 2

        # 아래는 급식관련내용

    elif (content in ("급식 메뉴" or "급식메뉴")) or (content == "급식 메뉴 확인하기") or (content == "급식 재출력"):
        response = jsonChoiceDay
        idlog[ID] = 1
        # 아래는 수행

    elif content == "수행평가 확인/선택":
        response = {
                    "version": "2.0",
                    "template": {"outputs": [{"simpleText": {"text": "수행평가 내역/강의실 위치를 알고 싶은 과목을 골라주세요.\n" + " ".join(choice.keys()) } } ],
                                  "quickReplies": [{"label": "취소하기", "action": "message", "messageText": "취소"}]
                                 }
                   }
        idlog[ID] = 3
    
    elif content == "수행평가 확인/반":
        response = {
                    "version": "2.0",
                    "template": {"outputs": [{"simpleText": {"text": "수행평가 정보를 알고 싶은 반을 입력해주세요.\n입력 형식 ㅡ>1.10 시 1학년 10반" } } ],
                                  "quickReplies": [{"label": "취소하기", "action": "message", "messageText": "취소"}]
                                 }
                   }
        idlog[ID] = 4
    
    elif content == "수행평가 등록/선택":
        response = {
                    "version": "2.0",
                    "template": {"outputs": [{"simpleText": {"text": 
f"""수행평가 등록을 원하는 과목 이름을 짧게(화학1->화1, 정치와 법->정법) 입력해 주세요.
학년이 끝나거나 학기가 끝나면 데이터는 초기화 될 수 있습니다. 데이터 입력 시 내용과 기한을 입력해주세요.
과도한 / 사용 시 오류가 발생할 수 있습니다. 과목과 내용을 끊을 때만 /을 사용해 주세요.

예>화학/교과서 검사 1월 1일까지

주의사항 : 자체적으로 데이터 삭제가 불가합니다. 삭제 필요시 상담원 전달해주세요.

현재 과목: {choice.keys()}"""} } ],
                                  "quickReplies": [{"label": "취소하기", "action": "message", "messageText": "취소"}]
                                 }
                   }
        idlog[ID] = 5

    elif content == "수행평가 등록/반":
        response = {
                    "version": "2.0",
                    "template": {"outputs": [{"simpleText": {"text": 
f"""수행평가 등록을 원하는 학년/반 이름을 짧게(3학년 1반 -> 3/1) 입력해 주세요.
학년이 끝나거나 학기가 끝나면 데이터는 초기화 될 수 있습니다. 데이터 입력 시 내용과 기한을 입력해주세요.
과도한 / 사용 시 오류가 발생할 수 있습니다. 학년, 반과 내용을 끊을 때만 /을 사용해 주세요.

예>3/1/리로스쿨 보고서 n월 n일까지

주의사항 : 자체적으로 데이터 삭제가 불가합니다. 삭제 필요시 상담원 전달해주세요.
"""} } ],
                                  "quickReplies": [{"label": "취소하기", "action": "message", "messageText": "취소"}]
                                 }
                   }
        idlog[ID] = 7

    elif content == "모집/게시판":
        PanLoading()
        response = {
                "version": "2.0",
                "template": {"outputs": [{"simpleText": {"text": f"{panResult}" +"\n\n 게시글 번호를 입력하면 해당 게시글을 볼 수 있습니다.\n취소하기 전까지 게시글 선택은 유지됩니다."} } ],
                             "quickReplies": [
                                            {"label": "취소", "action": "message", "messageText": "취소"}]
                            }
                       }
        idlog[ID] = 8

    elif content == "모집/공고":
        response = {
                "version": "2.0",
                "template": {"outputs": [{"simpleText": {"text": 
f"""모집 공고를 올립니다. 번호는 선착순으로 지정되며, 학기마다 관리자 재량으로 삭제될 수 있습니다.\n
입력 형태 -> 제목/이름/내용/연락처\n
예시-> 홍길동/학생회 인원 모집합니다!/학생회 XX부서에 지원할 학생을 모집합니다. ~같은 활동을 합니다. 아래로 연락주세요!/123-1234-1234
취소를 누르거나 공고 등록되기 전까지 이 선택은 유지됩니다."""} } ],
                             "quickReplies": [
                                            {"label": "취소", "action": "message", "messageText": "취소"}]
                            }
                       }
        idlog[ID] = 9

    elif content == "출력":
        response = {
            "version": "2.0",
            "template": {
                "outputs": [{"simpleText": {"text": f"choice = {choice}\n\n pan = {pan}\n\n homeworkdata = {homeworkdata}\n\n fillter = {fillter}"}}]
            }
        }

    else:
        response = {
                 "version": "2.0",
                 "template": {
                  "outputs": [{
                     "carousel": {  # 스킬가이드에 나온 캐러셀 형태
                         "type": "basicCard",  # 기본형 선택 (<->비즈니스형도 존재)
                         "items": [{
                             "title": "이해하지 못했습니다.",  # 제목
                             "description": "'명렁어'를 입력해 사용가능한 기능들을 확인해주세요.",  # 설명
                             # "thumbnail": { # 썸네일 이미지
                                 # "imageUrl": can[0].imgurl
                             "buttons": [{  # 버튼
                                 "action": "message",  # 동작 형태(텍스트 출력)
                                 "label": "명령어 출력하기",  # 버튼 이름
                                 "messageText": "명령어"
                                        }]
                                  }]
                                }
                            }]
                            }
                  }
    return jsonify(response)


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, debug=True)
