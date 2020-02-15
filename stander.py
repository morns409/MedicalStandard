import json
import requests
from requests.exceptions import RequestException
import re
from lxml import etree
from multiprocessing import Pool
import pymysql

# 实例化session
session = requests.session()
headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }


def log_page(url):
    """登陆 实例化session"""
    try:
        #session = requests.session()  # 实例化session
        response = session.post(url=url, headers=headers, allow_redirects=True)  # 将cookie保存在session
        # 判断返回的状态码是成功的
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


def navigation_bar(logurl):
    """登陆后进入含导航栏页面"""
    try:
        #logurl = "http://soo.simop.com.cn/tuijianbiaozhun/tuijianlist.aspx?fid=891&type=3&id=3907"
        response = session.get(url=logurl, headers=headers)  # session带着cookie请求
        # 判断返回的状态码是成功的
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


def parse_on_page(html, id, pId, name, lev, lyType, lyId):
    """获取标准列表"""
    pattern = re.compile('<tr.*?td-title.*?href="(.*?)".*?Black;">(.*?)</a>.*?">(.*?)</em>.*?table_txt">.*?_blank">' +
                         '(.*?)</a>.*?<span>(.*?)<em>(.*?)</em></span><span>'
                         + '(.*?)<em>(.*?)</em>.*?</tr>', re.S)
    items = re.findall(pattern, html)

    for item in items:
        data = (item[1], item[2], item[3], item[5], item[7], id, pId, name, lev, lyType, lyId)
        insert_id = mysql_data(data)
        details_html = parse_details("http:"+item[0])
        if lev == '1':
            parse_details_html(details_html, insert_id)  # 国内页面爬取
        else:
            parse_details_overseas_html(details_html, insert_id)  # 海外页面爬取
        # yield 生成器
        # yield {
        #     'name': item[1],
        #     'ifs': item[2],
        #     'describe': item[3],
        #     'release_time_name': item[4],
        #     'release_time': item[5],
        #     'publishing_agency_name': item[6],
        #     'publishing_agency': item[7]
        # }
    #http://www.simop.com.cn/detail-96-f7cac3e7113d5078.html
    # details_html = parse_details("http://www.simop.com.cn/detail-95-1054c0f8ad939127.html")
    # parse_details_overseas_html(details_html,1111)



def parse_details(detailsurl):
    """详情html"""
    try:
        response = session.get(url=detailsurl, headers=headers)  # session带着cookie请求
        response.encoding = 'utf8'
        # 判断返回的状态码是成功的
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


def parse_details_html(html,insert_id):
    """解析国内详情页面"""
    title_name = ['基本信息','标准简介','标准摘要','标准目录','替代情况','引用标准','采标情况']
    title_details = ['0标准号：', '1发布时间：', '2实施时间：', '3首发日期：', '4出版单位：', '5起草人：', '6出版机构：', '7标准分类：',
                  '8ICS分类：', '9提出单位：', '10起草单位：', '11归口单位：', '12发布部门：', '13主管部门：', '14标准简介'
                     , '15标准目录', ' 16替代情况', '17引用标准', '18采标情况', '19标准名称', '20现行or即将实时',
                     '21在线阅读', '', '']
    htmls = etree.HTML(html)

    list = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']  # 长度29
    for num in range(2, 9):
        standerd_no = "/html/body/div[3]/div[2]/div[2]/div["+str(num)+"]"
        data_key = htmls.xpath(standerd_no)
        if data_key:
            t_name = htmls.xpath(standerd_no + "/div/strong")
            if t_name[0].text == '基本信息':
                print('!!!!基本信息')
                for num in range(2, 17):
                    details_key = htmls.xpath(standerd_no + "/div["+str(num)+"]")
                    if details_key:
                        if details_key[0].text != None:
                            key_key = htmls.xpath(standerd_no + "/div[" + str(num) + "]/span")
                            details_kye_name = str(details_key[0].text)
                            key_keys = str(key_key[0].text)
                            if details_kye_name == '标准号：':
                                list[1] = key_keys
                            elif details_kye_name == '发布时间：':
                                list[2] = key_keys
                                # list.insert(2,key_keys)
                            elif details_kye_name == '实施时间：':
                                list[3] = key_keys
                                #list.insert(3, key_keys)
                            elif details_kye_name == '首发日期：':
                                list[4] = key_keys
                                #list.insert(4, key_keys)
                            elif details_kye_name == '出版单位：':
                                list[5] = key_keys
                                #list.insert(5, key_keys)
                            elif details_kye_name == '起草人：':
                                list[6] = key_keys
                                #list.insert(6, key_keys)
                            elif details_kye_name == '出版机构：':
                                list[7] = key_keys
                                #list.insert(7, key_keys)
                            elif details_kye_name == '标准分类：':
                                list[8] = key_keys
                                #list.insert(8, key_keys)
                            elif details_kye_name == 'ICS分类：':
                                list[9] = key_keys
                                #list.insert(9, key_keys)
                            elif details_kye_name == '提出单位：':
                                list[10] = key_keys
                                #list.insert(10, key_keys)
                            elif details_kye_name == '起草单位：':
                                list[11] = key_keys
                                #list.insert(11, key_keys)
                            elif details_kye_name == '归口单位：':
                                list[12] = key_keys
                                #list.insert(12, key_keys)
                            elif details_kye_name == '发布部门：':
                                list[13] = key_keys
                                #list.insert(13, key_keys)
                            elif details_kye_name == '主管部门':
                                list[14] = key_keys
                                #list.insert(14, key_keys)

                    else:
                        break

            elif t_name[0].text == '标准简介':
                intro = htmls.xpath(standerd_no+"/p")
                list[15] = intro[0].text
                #list.insert(15, intro[0].text)
                print('!!标准简介')
            elif t_name[0].text == '标准摘要':
                digest = htmls.xpath(standerd_no + "/table/tr/td/text()")
                content = ""
                for temp in digest:
                    content = content + temp
                list[16] = content
                #list.insert(16, content)
                print('!!标准摘要')
            elif t_name[0].text == '标准目录':
                catalog_xpath = htmls.xpath(standerd_no + "/table/tr/td/text()")
                catalog = ""
                for temp in catalog_xpath:
                    if catalog == "":
                        catalog = catalog + temp
                    else:
                        catalog = catalog + ";" + temp
                list[17] = catalog
                #list.insert(17, catalog)
                print('!!标准目录')
            elif t_name[0].text == '替代情况':
                replace_xpath = htmls.xpath(standerd_no + "/p")
                replace = replace_xpath[0].text
                list[18] = replace
                #list.insert(18, replace)
                print('!!替代情况')
            elif t_name[0].text == '引用标准':
                quote_xpath = htmls.xpath(standerd_no + "/table/tr/td/text()")
                quote = ""
                for temp in quote_xpath:
                    if quote == "":
                        quote = quote + temp
                    else:
                        quote = quote + ";" + temp
                list[19] = quote
                #list.insert(19, quote)
                print('!!引用标准')
            elif t_name[0].text == '采标情况':
                gather_xpath = htmls.xpath(standerd_no + "/p")
                gather = gather_xpath[0].text
                list[20] = gather
                #list.insert(20, gather)
                print('!!采标情况')
            else:
                break

        else:
            break
    xqtt_title_url = "/html/body/div[3]/div[2]/div[1]/div[1]/div[1]/div[1]/h1"
    xqtt_title = htmls.xpath(xqtt_title_url)
    xqtt_title_em_url = "/html/body/div[3]/div[2]/div[1]/div[1]/div[1]/div[1]/h1/em"
    xqtt_title_em = htmls.xpath(xqtt_title_em_url)
    pdf_len_url = "/html/body/div[3]/div[2]/div[1]/div[1]/div[1]/div[3]/a[1]/@href"
    pdf_len = htmls.xpath(pdf_len_url)
    list[21] = xqtt_title[0].text  # 标准名称
    list[22] = xqtt_title_em[0].text  # 现行or即将实时
    print(pdf_len[0])
    list[23] = str(pdf_len[0]) # 在线阅读
    # list.insert(21, xqtt_title)  # 标准名称
    # list.insert(22, xqtt_title_em)  # 现行or即将实时
    # list.insert(23, pdf_len)  # 在线阅读
    #print(xqtt_title[0].text, xqtt_title_em[0].text, pdf_len[0])
    list[0] = str(insert_id)
    print(tuple(list))
    mysql_data_subset(tuple(list))


def parse_details_overseas_html(html,insert_id):
    """解析海外详情页面"""
    title_name = ['基本信息','标准简介','标准摘要','标准目录','替代情况','引用标准','采标情况']
    title_details = ['0标准号：', '1发布时间：', '2实施时间：', '3首发日期：', '4出版单位：', '5起草人：', '6出版机构：', '7标准分类：',
                  '8ICS分类：', '9提出单位：', '10起草单位：', '11归口单位：', '12发布部门：', '13主管部门：', '14标准简介'
                     , '15标准目录', ' 16替代情况', '17引用标准', '18采标情况', '19标准名称', '20现行or即将实时',
                     '21在线阅读', '', '']
    htmls = etree.HTML(html)

    list = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']  # 长度29
    for num in range(2, 9):
        standerd_no = "/html/body/div[3]/div[2]/div[2]/div["+str(num)+"]"
        data_key = htmls.xpath(standerd_no)
        if data_key:
            t_name = htmls.xpath(standerd_no + "/div/strong")
            if t_name[0].text == '基本信息':
                print('!!!!基本信息')
                for num in range(1, 17):
                    details_key = htmls.xpath(standerd_no + "/div[2]/div["+str(num)+"]")
                    if details_key:
                        if details_key[0].text != None:
                            key_key = htmls.xpath(standerd_no + "/div[2]/div[" + str(num) + "]/span")
                            details_kye_name = str(details_key[0].text)
                            key_keys = str(key_key[0].text)
                            if details_kye_name == '标准编号：':
                                list[1] = key_keys
                            elif details_kye_name == '发布时间：':
                                list[2] = key_keys
                                # list.insert(2,key_keys)
                            elif details_kye_name == '实施时间：':
                                list[3] = key_keys
                                #list.insert(3, key_keys)
                            elif details_kye_name == '首发日期：':
                                list[4] = key_keys
                                #list.insert(4, key_keys)
                            elif details_kye_name == '出版单位：':
                                list[5] = key_keys
                                #list.insert(5, key_keys)
                            elif details_kye_name == '起草人：':
                                list[6] = key_keys
                                #list.insert(6, key_keys)
                            elif details_kye_name == '出版单位：':
                                list[7] = key_keys
                                #list.insert(7, key_keys)
                            elif details_kye_name == '标准类别：':
                                list[8] = key_keys
                                #list.insert(8, key_keys)
                            elif details_kye_name == 'ICS分类：':
                                list[9] = key_keys
                                #list.insert(9, key_keys)
                            elif details_kye_name == '提出单位：':
                                list[10] = key_keys
                                #list.insert(10, key_keys)
                            elif details_kye_name == '起草单位：':
                                list[11] = key_keys
                                #list.insert(11, key_keys)
                            elif details_kye_name == '归口单位：':
                                list[12] = key_keys
                                #list.insert(12, key_keys)
                            elif details_kye_name == '发布部门：':
                                list[13] = key_keys
                                #list.insert(13, key_keys)
                            elif details_kye_name == '主管部门：':
                                list[14] = key_keys
                                #list.insert(14, key_keys)
                            elif details_kye_name == '标准页数：':
                                list[25] = key_keys
                                #list.insert(14, key_keys)

                    else:
                        break
            elif t_name[0].text == '标准简介':
                intro = htmls.xpath(standerd_no+"/p")
                list[15] = intro[0].text
                #list.insert(15, intro[0].text)
                print('!!标准简介')
            elif t_name[0].text == '标准摘要':
                digest = htmls.xpath(standerd_no + "/table/tr/td/text()")
                content = ""
                for temp in digest:
                    content = content + temp
                list[16] = content
                print('!!标准摘要')
            elif t_name[0].text == '标准目录':
                catalog_xpath = htmls.xpath(standerd_no + "/table/tr/td/text()")
                catalog = ""
                for temp in catalog_xpath:
                    if catalog == "":
                        catalog = catalog + temp
                    else:
                        catalog = catalog + ";" + temp
                list[17] = catalog
                print('!!标准目录')
            elif t_name[0].text == '替代情况':
                replace_xpath = htmls.xpath(standerd_no + "/p")
                replace = replace_xpath[0].text
                list[18] = replace
                print('!!替代情况')
            elif t_name[0].text == '引用标准':
                quote_xpath = htmls.xpath(standerd_no + "/table/tr/td/text()")
                quote = ""
                for temp in quote_xpath:
                    if quote == "":
                        quote = quote + temp
                    else:
                        quote = quote + ";" + temp
                list[19] = quote
                #list.insert(19, quote)
                print('!!引用标准')
            elif t_name[0].text == '采标情况':
                gather_xpath = htmls.xpath(standerd_no + "/p")
                gather = gather_xpath[0].text
                list[20] = gather
                #list.insert(20, gather)
                print('!!采标情况')
            elif t_name[0].text == '本标准替代的旧标准':
                print('！！本标准替代的旧标准')
                old_str = ""
                for old in range(1, 10):
                    dt_url = htmls.xpath(standerd_no + "/p["+str(old)+"]")
                    if dt_url:
                        dt_old_url = htmls.xpath(standerd_no + "/p[" + str(old) + "]/a")
                        dt_old_key = dt_old_url[0].text
                        if old_str == "":
                            old_str = old_str + dt_old_key
                        else:
                            old_str = old_str + ";" + dt_old_key
                list[26] = old_str
            elif t_name[0].text == '替代本标准的新标准':
                print('！！替代本标准的新标准')
                dtnew_str = ""
                for dtnew in range(1, 10):
                    dtnew_url = htmls.xpath(standerd_no + "/p["+str(dtnew)+"]")
                    if dtnew_url:
                        dt_new_url = htmls.xpath(standerd_no + "/p[" + str(dtnew) + "]/a")
                        dt_new_key = dt_new_url[0].text
                        if dtnew_str == "":
                            dtnew_str = dtnew_str + dt_new_key
                        else:
                            dtnew_str = dtnew_str + ";" + dt_new_key
                list[27] = dtnew_str
            elif t_name[0].text == '本标准修订后的版本':
                print('！！本标准修订后的版本')
                xdh_str = ""
                for xdh in range(1, 10):
                    xd_url = htmls.xpath(standerd_no + "/p["+str(xdh)+"]")
                    if xd_url:
                        xdh_url = htmls.xpath(standerd_no + "/p[" + str(xdh) + "]/a")
                        xdh_key = xdh_url[0].text
                        if xdh_str == "":
                            xdh_str = xdh_str + xdh_key
                        else:
                            xdh_str = xdh_str + ";" + xdh_key
                list[28] = xdh_str
            elif t_name[0].text == '等同采用的国际标准':
                print('！！等同采用的国际标准')
                cy_str = ""
                for cy in range(1, 10):
                    cy_url = htmls.xpath(standerd_no + "/p["+str(cy)+"]")
                    if cy_url:
                        cy_gb_url = htmls.xpath(standerd_no + "/p[" + str(cy) + "]/a")
                        cy_gb_key = cy_gb_url[0].text
                        if cy_str == "":
                            cy_str = cy_str + cy_gb_key
                        else:
                            cy_str = cy_str + ";" + cy_gb_key
                list[29] = cy_str
            else:
                break

        else:
            break
    xqtt_title_url = "/html/body/div[3]/div[2]/div[1]/div[1]/div[1]/div[1]/h1"
    xqtt_title = htmls.xpath(xqtt_title_url)
    xqtt_title_em_url = "/html/body/div[3]/div[2]/div[1]/div[1]/div[1]/div[1]/h1/em"
    xqtt_title_em = htmls.xpath(xqtt_title_em_url)
    pdf_len_url = "/html/body/div[3]/div[2]/div[1]/div[1]/div[1]/div[3]/a[1]/@href"
    pdf_len = htmls.xpath(pdf_len_url)
    msxq_url = "/html/body/div[3]/div[2]/div[1]/div[1]/div[1]/p"  # 海外描述
    msxq_ch = htmls.xpath(msxq_url)

    list[21] = xqtt_title[0].text  # 标准名称
    list[22] = xqtt_title_em[0].text  # 现行or即将实时
    list[23] = pdf_len[0]  # 在线阅读
    if msxq_ch:
        list[24] = msxq_ch[0].text  # 海外 中文描述
    #print(xqtt_title[0].text, xqtt_title_em[0].text, pdf_len[0])
    list[0] = str(insert_id)
    #print(tuple(list))
    mysql_data_subset(tuple(list))


def main():
    # 登陆
    url = 'http://soo.simop.com.cn/JsonHandler/sooUserLoginHandler.ashx?username=huanbiao&password=123456'
    html = log_page(url)

    val = [
        {"id": 3899, "pId": 0, "name": "疫情防控相关国内标准", "lev": 0, "lyType": 0, "lyId": 0},
        {"id": 3912, "pId": 0, "name": "疫情防控相关海外标准", "lev": 0, "lyType": 0, "lyId": 0},
        {"id": 3927, "pId": 3912, "name": "国外口罩标准", "lev": 1, "lyType": 0, "lyId": 0},
        {"id": 3935, "pId": 3912, "name": "国外医用防护服标准", "lev": 1, "lyType": 0, "lyId": 0},
        {"id": 3942, "pId": 3927, "name": "欧洲口罩标准", "lev": 2, "lyType": 0, "lyId": 0},
        {"id": 3955, "pId": 3935, "name": "欧洲医用防护服", "lev": 2, "lyType": 0, "lyId": 0},
        {"id": 3907, "pId": 3899, "name": "防护口罩相关标准", "lev": 1, "lyType": 3, "lyId": 891},
        {"id": 3908, "pId": 3899, "name": "防护服相关标准", "lev": 1, "lyType": 3, "lyId": 892},
        {"id": 3909, "pId": 3899, "name": "医用手套相关标准", "lev": 1, "lyType": 3, "lyId": 893},
        {"id": 3910, "pId": 3899, "name": "消毒防护相关标准", "lev": 1, "lyType": 3, "lyId": 894},
        {"id": 3911, "pId": 3899, "name": "体温计相关标准", "lev": 1, "lyType": 3, "lyId": 895},
        {"id": 3939, "pId": 3927, "name": "美国口罩标准", "lev": 2, "lyType": 3, "lyId": 899},
        {"id": 3945, "pId": 3927, "name": "日本口罩标准", "lev": 2, "lyType": 3, "lyId": 901},
        {"id": 3963, "pId": 3927, "name": "澳大利亚口罩", "lev": 2, "lyType": 3, "lyId": 913},
        {"id": 3948, "pId": 3935, "name": "美国医用防护服", "lev": 2, "lyType": 3, "lyId": 905},
        {"id": 3960, "pId": 3935, "name": "日本医用防护服", "lev": 2, "lyType": 3, "lyId": 907},
        {"id": 3964, "pId": 3935, "name": "澳大利亚防护服", "lev": 2, "lyType": 3, "lyId": 914},
        {"id": 3943, "pId": 3942, "name": "iso口罩标准", "lev": 3, "lyType": 3, "lyId": 902},
        {"id": 3962, "pId": 3942, "name": "欧盟口罩标准", "lev": 3, "lyType": 3, "lyId": 903},
        {"id": 3956, "pId": 3955, "name": "iso防护服标准", "lev": 3, "lyType": 3, "lyId": 908},
        {"id": 3957, "pId": 3955, "name": "欧盟防护服标准", "lev": 3, "lyType": 3, "lyId": 909},
        {"id": 3958, "pId": 3955, "name": "英国防护服标准", "lev": 3, "lyType": 3, "lyId": 910},
        {"id": 3959, "pId": 3955, "name": "德国防护服标准", "lev": 3, "lyType": 3, "lyId": 911}]

    for line in val:
        if line['lyId'] == 0:
            data = ('', '', '', '', '', str(line['id']), str(line['pId']), str(line['name']), str(line['lev']),
                        str(line['lyType']), str(line['lyId']))
            mysql_data(data)
        else:
            vsurl = "http://soo.simop.com.cn/tuijianbiaozhun/tuijianlist.aspx?fid=" + str(line['lyId']) + \
                    "&type=3&id=" + str(line['id'])
            html = navigation_bar(vsurl)
            parse_on_page(html, str(line['id']), str(line['pId']), str(line['name']), str(line['lev']),
                      str(line['lyType']), str(line['lyId']))


def mysql_data(data):
    # 建立连接
    conn = pymysql.connect('127.0.0.1', 'root', 'morns409', 'morns', charset='utf8')
    # 建立游标
    cursor = conn.cursor()
    # 数据库操作
    # (1)定义一个格式化的sql语句
    sql = 'insert into listStandard1(namess,ifs,describes,release_time,publishing_agency,cId,pId,cname,lev,lyType,lyId)'\
          +' values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) '
    # (2)准备数据
    #data = ('nancy', '30', '100', '太好笑了','nancy', '30', '100', '太好笑了','nancy', '30', '100')
    # (3)操作
    inse_id = 0
    try:
        cursor.execute(sql, data)
        inse_id = conn.insert_id()
        conn.commit()
        print("成功：列表页_插入成功")
    except Exception as e:
        print('失败：列表页_插入数据失败', e)
        conn.rollback()  # 回滚

    # 关闭游标
    cursor.close()
    # 关闭连接
    conn.close()
    return inse_id


def mysql_data_subset(data):
    # 建立连接
    conn = pymysql.connect('127.0.0.1', 'root', 'morns409', 'morns', charset='utf8')
    # 建立游标
    cursor = conn.cursor()
    # 数据库操作
    # (1)定义一个格式化的sql语句
    sql = 'insert into subset(sid, a, b, c, d, e, f, g, h, i, j, k, l, m ,n, o, p, q, r, s, t, u, v, w,x, y,z,aa,ab,ac) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) '
    # (2)准备数据
    #data = ('nancy', '30', '100', '太好笑了','nancy', '30', '100', '太好笑了','nancy', '30', '100')
    # (3)操作
    try:
        cursor.execute(sql, data)
        conn.commit()
        print("成功：详情页_插入成功")
    except Exception as e:
        print('失败：详情页_插入数据失败', e)
        conn.rollback()  # 回滚

    # 关闭游标
    cursor.close()
    # 关闭连接
    conn.close()


if __name__ == '__main__':
    main()