# -*-coding:utf8;-*-
import re
import urllib2, urllib, cookielib, json, csv
from hashlib import md5


def get_login_information(csvfilename):  # 定义读取器，读取目录下的csv文件，打印获得的登陆信息字典
    login_information = []
    with open(csvfilename, 'r') as csvfile:
        font = csv.reader(csvfile)
        for row in font:
            identify_information = {}
            identify_information['teaching_number'] = row[0]
            identify_information['password'] = row[1]
            identify_information['student_id'] = row[2]
            login_information.append(identify_information)
    return login_information  # 输出list，包含字典
    # 字典的格式是[{'teaching_number': '79150701', 'student_id': '70150701', 'password': '045724'},......


def uims_loginer(number, passwd):  # 定义uims登录器，输入账号和密码，输出名字和json原始数据，中途打印名字
    #    number = '11111111'
    #    passwd = '111111'
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
    # print username  # 打印名字
    request_last_score = urllib2.Request('http://uims.jlu.edu.cn/ntms/service/res.do', data_query, header)
    response_last_score = opener.open(request_last_score).read()  # json原始数据
    return username, response_last_score  # 名字，json原始数据


necessary_course_credit = [u'3', u'3', u'3.5', u'4', u'1', u'4', u'6']
necessary_course = ['医学免疫学A', '大学英语BⅣ', '数据库及程序设计', '病理生理学A', '体育IV', '医学微生物学A', '病理解剖学A']  # 这个list的内容是输出为str，以utf-8编码，获得的json是ascii码


def uims_parser(response_last_score, single_information):  # 获得未解码的原始json，和登录信息，输出学号和成绩list
    last_score_dict = json.loads(response_last_score)  # 解码json
    individual_dict = {}  # 建立个人成绩dict
    for one_course_dict in last_score_dict['value']:  # 获取json中的成绩区块（value），逐个抽出并保存到individual_dict
        course_name = one_course_dict['course']['courName']  # 课程名称
        score = one_course_dict['scoreNum']  # 对应成绩条的成绩
        if course_name.encode('utf-8') in necessary_course:  # 筛选 只保存必修课的成绩
            individual_dict[course_name] = score
    # {u'\u4f53\u80b2\u2162': u'92', u'\u4f53\u80b2\u2160': u'91', u'\u4f53\u80b2\u2161': u'88',  dict内部的样式

    output_list = []  # 定义输出list
    output_list.append(single_information['student_id'])  # 输出list的第一个字符是学号
    for course_name in necessary_course:  # 按necessary_course的顺序输出到output_list
        course_name = course_name.decode('utf-8')
        if course_name not in individual_dict:  # 如果有的人缺了某一门课的成绩，这门课的成绩输出为0
            # print course_name, '0'  # 输出空成绩
            output_list.append('0')
        else:
            # print course_name, individual_dict[course_name]
            output_list.append(individual_dict[course_name])
    # ['70150731', u'92', u'90', u'90', u'92', u'92', u'87', u'88', u'100', u'90', u'90', u'90',  list内部样式
    return output_list


necessary_course_credit.insert(0, '学分')
necessary_course.insert(0, '学号')  # 在首行最前端插入学号便于浏览，首行使用之前necessary_course的次序
with open('result.csv', 'a') as f:  # 建立result.csv文件，输出目录
    writer = csv.writer(f)
    writer.writerow(necessary_course_credit)
    writer.writerow(necessary_course)
necessary_course.pop(0)  # 去除学号

login_information = get_login_information('raw.csv')  # 获取login_information登录信息
print u'取得登录信息', login_information
# 批量获得成绩条
for single_information in login_information:  # 遍历login_information中的所有登录信息
    try:
        username, response_last_score = uims_loginer(single_information['teaching_number'],
                                                     single_information['password'])
        print u'取得json原始数据', single_information['student_id'], username, response_last_score
        output_list = uims_parser(response_last_score, single_information)
        print u'获得', single_information['student_id'], username, '成绩', output_list
    except IndexError:
        print single_information['student_id'], u'账号或密码错误'  # 密码错误的异常修正
        output_list = [single_information['student_id'], '账号或密码错误']
    with open('result.csv', 'a') as f:  # 向result.csv添加成绩
        writer = csv.writer(f)
        writer.writerow(output_list)
    print single_information['teaching_number'], u'成绩写入完成'
