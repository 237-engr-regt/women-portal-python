import requests

url = "https://script.google.com/macros/s/AKfycbyzkKdboNzQZkt63BresWTN__1qrDbIwJ-dEou_9EY_4D-OwvMdXX69SCyXyfIl5GWz/exec"

res = requests.post(url, json={
    "complaint_id": "TEST999",
    "name": "Test User",
    "address": "Test Address",
    "contact": "9999999999",
    "email": "test@test.com",
    "unit": "Unit",
    "wo": "WO",
    "quarter": "Q1",
    "complaint": "Testing Google Sheet",
    "category": "Test",
    "subcategory": "Test",
    "reply": "Pending",
    "audio": ""
})

print(res.text)