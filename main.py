import json
from requests import get
import datetime
import pandas as pd

print('Введите токен учащегося. Как получить токен:\n'
      '1. Перейдите по ссылке - https://school.mos.ru/?backUrl=https%3A%2F%2Fschool.mos.ru%2Fv2%2Ftoken%2Frefresh\n'
      '2. Авторизуйтесь и скопируйте набор символов (ey...)\n'
      '3. Вставьте набор сюда:\n')
token = str(input())
id = json.loads(get("https://school.mos.ru/api/family/web/v1/profile", headers={'Auth-Token': token, "x-mes-subsystem": "familyweb"}).content.decode())['profile']['id']

print('За какой период необходима посещаемость?\n'
      'Напишите "Показать все" (без кавычек) или введите даты по примеру:\n'
      '2025-09-01:2026-09-01')
answer = str(input())
if answer == "Показать все":
    time1 = '2025-09-01'
    time2 = datetime.datetime.now().strftime("%Y-%m-%d")
    time_r = pd.date_range(time1, time2).strftime('%Y-%m-%d').tolist()
else:
    time1 = answer.split(':')[0]
    time2 = answer.split(':')[1]
    time_r = pd.date_range(answer.split(':')[0], answer.split(':')[1]).strftime('%Y-%m-%d').tolist()


def att(id, time1, time2):
    att = get(f"https://school.mos.ru/api/family/web/v1/attendance?student_id={id}&from={time1}&to={time2}",
                           headers={
                               'Auth-Token': token,
                               "x-mes-subsystem": "familyweb"
                           })
    data = json.loads(att.content.decode())
    return data

def att_goal(id, time):
    att_goal = get(f"https://school.mos.ru/api/family/web/v1/schedule/short?student_id={id}&dates={time}",
                           headers={
                               'Auth-Token': token,
                               "x-mes-subsystem": "familyweb"
                           })
    data = json.loads(att_goal.content.decode())
    return data['payload']

predm_all = []
predm = []

skips = att(id, time1, time2)['attendance']
for time in time_r:
    for x in att_goal(id, time)[0]['lessons']:
        if x['subject_name'] is None and x['group_name'] is not None:
            predm_all.append(x['group_name'])
            predm.append(x['group_name'])
        else:
            predm_all.append(x['subject_name'])
            predm.append(x['subject_name'])
    for n in range(len(skips)):
        if skips[n]['date'] == time:
            print('День с пропуском:', time)
            for x in skips[n]['lessons']:
                if x['subject_name'] is None and x['group_name'] is not None:
                    predm.remove(x['group_name'])
                else:
                    predm.remove(x['subject_name'])
            break


setpredm = set(predm_all)
for x in setpredm:
    print('Предмет:', x,'\n', 'Всего часов было:', predm_all.count(x), ' Посетил часов:', predm.count(x), ' Процент посещения:', predm.count(x) * 100 / predm_all.count(x))
    print()
