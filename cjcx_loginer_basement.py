# -*-coding:utf8;-*-
import re
import urllib2, urllib, cookielib, json
from hashlib import md5


def uims_loginer(number, passwd):
    # number = '79150731'
    # passwd = '210053'

    if len(passwd) == 0:
        print u"密码为空"
    inp = md5('UIMS' + number + passwd).hexdigest()

    url_login = 'http://cjcx.jlu.edu.cn/score/action/security_check.php'
    header = {
        'Content-Type': 'application/json;charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'
    }

    cookie = cookielib.CookieJar()
    handler = urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(handler)
    data = urllib.urlencode({
        'j_username': number,
        'j_password': inp,
    })
    request_login = urllib2.Request(url_login, data)
    response_login = opener.open(request_login).read()  # 这行不能省略
    data_query = json.dumps(
        {'tag': "lessonSelectResult@oldStudScore", 'params': {'termId': 132}})
    request_last_score = urllib2.Request('http://cjcx.jlu.edu.cn/score/action/service_res.php', data_query, header)
    response_last_score = opener.open(request_last_score).read()  # json原始数据
    return response_last_score



response_last_score = uims_loginer('79150731', '210053')
print response_last_score
last_score_dict = json.loads(response_last_score)  # 解码json
individual_dict = {}  # 建立个人成绩dict
course_credit = {}  # 建立课程与学分dict
for one_course_dict in last_score_dict['items']:
    course_name = one_course_dict['kcmc']  # 课程名称
    score = one_course_dict['zscj']  # 对应成绩条的成绩
    credit = one_course_dict['credit']
    individual_dict[course_name] = score
    course_credit[course_name] = credit

for course_name in individual_dict:
    print course_name, individual_dict[course_name]

print 'necessary_course_list = ['
for course_name in individual_dict:
    print '\'' + course_name + '\', '
print ']'

necessary_course_list = [
    '数据库及程序设计',
    '体育Ⅳ',
    '医学免疫学A',
    '大学英语BⅣ',
    '病理生理学A',
]

necessary_course_credit = []  # 按照上述必修课表格的次序建立学分dict
for course_name in necessary_course_list:
    course_name = course_name.decode('utf-8')
    # credit = float(course_credit[course_name])  将绩点转换为浮点数，需要计算的时候可以使用
    credit = course_credit[course_name]
    necessary_course_credit.append(credit)

print 'necessary_course_credit =', necessary_course_credit

necessary_course_credit = [3.5, 1, 3, 3, 4]