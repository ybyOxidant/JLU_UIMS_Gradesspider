# -*-coding:utf8;-*-
import re
import urllib2, urllib, cookielib, json
from hashlib import md5


def uims_loginer(number, passwd):
    # number = '79150731'
    # passwd = '210053'
    mousePath_code = 'UHQABUAQAQUAgAaUAwBdUCABpUCwBxVEQB9VGwCJVIwCVVMACiVOQCqVRgC2VUgDCVYQDOVbwDiVegDoViQDxVlwD7WogEGYrwESYvAEeZxwEqZ0wE2a4AE+b6wFKX7gH/'

    if len(passwd) == 0:
        print u"密码为空"
    inp = md5('UIMS' + number + passwd).hexdigest()

    url_login = 'http://uims.jlu.edu.cn/ntms/j_spring_security_check'
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
        'mousePath': mousePath_code
    })
    request_login = urllib2.Request(url_login, data)
    response_login = opener.open(request_login).read()  # 这行不能省略
    data_query = json.dumps(
        {"tag": "archiveScore@queryCourseScore", "branch": "latest", "params": {}, "rowlimit": 15, })
    request_info = urllib2.Request('http://uims.jlu.edu.cn/ntms/action/getCurrentUserInfo.do')
    response_info = opener.open(request_info).read()
    username = re.findall('"nickName":"(.*?)"', response_info)[0]
    print username  # 打印名字
    request_last_score = urllib2.Request('http://uims.jlu.edu.cn/ntms/service/res.do', data_query, header)
    response_last_score = opener.open(request_last_score).read()  # json原始数据
    return username, response_last_score


username, response_last_score = uims_loginer('79161203', '016177')
last_score_dict = json.loads(response_last_score)  # 解码json
individual_dict = {}  # 建立个人成绩dict
course_credit = {}  # 建立课程与学分dict
for one_course_dict in last_score_dict['value']:
    course_name = one_course_dict['course']['courName']  # 课程名称
    score = one_course_dict['scoreNum']  # 对应成绩条的成绩
    credit = one_course_dict['credit']
    individual_dict[course_name] = score
    course_credit[course_name] = credit

for course_name in individual_dict:
    print course_name, individual_dict[course_name]

necessary_course_list = ['医学免疫学A', '大学英语BⅣ', '数据库及程序设计',
                         '生物化学A', '毛泽东思想和中国特色社会主义理论体系概论', '大学英语BⅢ', '生理学A', '体育Ⅲ',
                         '卫生法学A', '细胞生物学A', '大学计算机基础', '大学英语BⅡ', '人体解剖学A', '医用大学物理与实验',
                         '中国近现代史纲要', '马克思主义基本原理概论', '体育Ⅱ', '组织学与胚胎学A', '有机化学实验D',
                         '有机化学E', '形势与政策Ⅰ', '大学英语AⅠ', '思想道德修养与法律基础', '无机化学实验B', '无机化学B',
                         '医用数学C', '体育Ⅰ', '军事理论']

necessary_course_credit = []  # 按照上述必修课表格的次序建立学分dict
for course_name in necessary_course_list:
    course_name = course_name.decode('utf-8')
    # credit = float(course_credit[course_name])  将绩点转换为浮点数，需要计算的时候可以使用
    credit = course_credit[course_name]
    necessary_course_credit.append(credit)

print necessary_course_credit

necessary_course_credit = [u'3', u'3', u'3.5',
                           u'7', u'4', u'3', u'7', u'1', u'2', u'3', u'3.5', u'3', u'5', u'4.5', u'2', u'2.5', u'1',
                           u'5', u'1', u'3', u'1', u'3', u'2.5', u'1', u'3', u'3', u'1', u'1']
