import requests

def signup():
    data = {
    "username": "정승원테스트",
    "password1": "qwer1234",
    "password2": "qwer1234",
    "email": "test_tmddnjs3369@naver.com",
    "gender": True
    }

    req = requests.post("http://j3pbl.kro.kr/stack/api/v1/signup", json=data)
    print(req.status_code)
    print(req.json())

def login():
    data = {
        "username": "tmddnjs01@naver.com",
        "password": "qwer1234"
    }
    req = requests.post("http://j3pbl.kro.kr/stack/api/v1/login", data=data)
    print(req.status_code)
    print(req.json())

login()