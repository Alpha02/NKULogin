import urllib
import http
import re
from http import client
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
import subprocess
import time
import threading
import os
class logger():
    logined=0
    status_str=''
    status_int=0
    infos={
    'user':'1210483', 
    'password':'303018', 
    'valicode':'1234'
    }
    headers = {
    "Accept":"text/html, application/xhtml+xml, */*",
    'Accept-Language':"en-US",
    "User-Agent":"Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
    "Accept-Encoding":" gzip, deflate",
    "Host":"222.30.32.10",
    "DNT":"1",
    "Connection":"Keep-Alive"
    }
    headers2 = {
    "Accept":"text/html, application/xhtml+xml, */*",
    'Referer':'http://222.30.32.10/',
    'Accept-Language':"en-US",
    "User-Agent":"Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
    "Content-Type":"application/x-www-form-urlencoded",
    "Accept-Encoding":" gzip, deflate",
    "Host":"222.30.32.10",
    "Content-Length":"97",
    "DNT": "1",
    "Connection":"Keep-Alive",
    'Cache-Control':'no-cache'
    };
    url = "222.30.32.10"
    def changeInfos(self, name, value):
        self.infos[name]=value
        print(self.infos)
    
    def changeUser(self, value):
        self.changeInfos('user', value)
        if(self.logined):
            self.logined=0
            self.init()
    def changePassword(self, value):
        self.changeInfos('password', value)
        
    def changeValicode(self, value):
        self.changeInfos('valicode', value)
    
    def init(self):
        self.reportStatus('建立HTTP连接....', 10)
        self.target_ui.lineEdit_valicode.setProperty('enabled', 'False')
        con=http.client.HTTPConnection(self.url)    
        con.request('GET',url='/',headers=self.headers)
        res=con.getresponse()
        con.close()
        data=res.read()
        self.reportStatus('获取Cookie....', 30)
        if res.getheader('Set-Cookie')!=None:                               #判断是否存在Set-Cookie，有的话，将cookie保存起来
           cj=res.getheader('Set-Cookie').split(';')[0]
           self.headers['Cookie']=cj
           self.headers2['Cookie']=cj
        else:
           print('got no cookie')
        self.reportStatus('获取验证码....', 50)
        con=http.client.HTTPConnection(self.url)
        con.request('GET',url='/ValidateCode',headers=self.headers)
        data=con.getresponse().read()
        con.close()
        self.reportStatus('保存验证码', 80)
        f = open('validate_code','wb')
        f.write(data)
        f.close()
        self.reportStatus('Hehe开发', 100)
        self.target_ui.pushButton_fuckTeachers.setProperty('enabled', 'True')
        self.target_ui.pushButton_cryForGPA.setProperty('enabled', 'True')  
        #subprocess.Popen('VC.bmp',stdout=subprocess.PIPE,shell=True).stdout.readlines()
        self.showValicode()
        self.target_ui.lineEdit_valicode.setProperty('enabled', 'True')
        return 1
    def login(self):
        data={'checkcode_text':self.infos['valicode'],
                'operation':'',
                'submittype':'确 认'.encode('gbk'),
                'usercode_text':self.infos['user'],
                'userpwd_text':self.infos['password']}
        postdata=urllib.parse.urlencode(data)
        con=http.client.HTTPConnection(self.url)
        self.reportStatus('正在登录....', 10)
        con.request('POST','/stdloginAction.do',postdata,self.headers2)
        data=con.getresponse().read().decode('gbk')
        con.close()
        tmp=re.search('<LI>(.*)',data) 
        if tmp:
            #if the login is failed
            self.reportStatus(tmp.group(1), 0)
            time.sleep(1)
            self.init()
            
            return False
        else:
            self.logined=1
            return True
            
    def getScore(self):
        self.target_ui.pushButton_fuckTeachers.setProperty('enabled', 'False')
        self.target_ui.pushButton_cryForGPA.setProperty('enabled', 'False')        
        if self.logined==0: 
            if not self.login():
                return False


        con=http.client.HTTPConnection(self.url)
        self.reportStatus('获取学业警示....', 20)
        con.request('GET','/xsxk/scoreAlarmAction.do',headers=self.headers)
        data=con.getresponse().read().decode('gbk') 
        
        GPA_alarm_list=re.findall('(<p align="center">(.*\n)*?</table>)',data)
        GPA_alarm=GPA_alarm_list[0][0]+GPA_alarm_list[1][0]+'\r\n'
        
        self.reportStatus('获取GPA....', 30)
        
        con.request('GET','/xsxk/studiedAction.do',headers=self.headers)
        data=con.getresponse().read().decode('gbk')
        
        
        self.reportStatus('获取页数...', 35)

        m_obj=re.search('共 (.) 页', data)
        GPA_count=' '.join(re.findall('(\\[.*?类课.*?\\])',data))
        page_numbers=int(m_obj.group(1))
        page_index=0
        self.headers['Referer']='http://222.30.32.10/xsxk/studiedAction.do'
        course_index_all=0
        self.reportStatus('创建HTML...', 40)
        f = open('score.html','w')
        f.write('<html>'+GPA_alarm)  
        f.write(GPA_count) 
        f.write('<table bgcolor="#CCCCCC" border="0" cellspacing="2" cellpadding="3" width="100%">')
        f.write('<tr bgcolor="#3366CC"><td>序号</td><td>课程代码</td><td>课程名称</td><td>课程类型</td><td>成绩</td><td>学分</td><td>重修成绩</td><td>重修情况</td></tr>')
        for page_index in range(page_numbers):
            
            all_courses=re.findall('<tr bgcolor="#FFFFFF">((\r\n *\t\t.*?)+?)\r\n *\t</tr>',data)
            course_index_page=0
  
            final_course_list={}
            for each_course in all_courses:
                self.reportStatus('获取课程%s...'%course_index_all, 40+60*(page_index+course_index_page/len(all_courses))/page_numbers)
                final_course_list[course_index_all]=re.findall('<td align="center" class="NavText">(.*?)\r\n *\t\t</td>\r\n *\t\t',all_courses[course_index_page][0])
                f.write('<tr bgcolor="#FFFFFF">')
                for data_idx in range(len(final_course_list[course_index_all])):
                    f.write('<td>%s</td>'%(final_course_list[course_index_all][data_idx]))
                f.write('</tr>')
                course_index_page+=1
                course_index_all+=1
                
            con.request('GET','/xsxk/studiedPageAction.do?page=next',headers=self.headers)
            data=con.getresponse().read().decode('gbk')    
        self.headers.pop('Referer')
        self.reportStatus('就绪', 100)
        f.write('</table></html>')
        f.close() 
        subprocess.Popen('score.html',stdout=subprocess.PIPE,shell=True)  
        
        self.target_ui.pushButton_fuckTeachers.setProperty('enabled', 'True')
        self.target_ui.pushButton_cryForGPA.setProperty('enabled', 'True')
        time.sleep(1)
        try:
            os.remove('score.html')
        except Exception as ex:
            print(ex)
            
        return True
        
    def getScoreThread(self):
        t=threading.Thread(target=self.getScore)
        t.start()
    def evaluateTeacher(self):
        self.target_ui.pushButton_fuckTeachers.setProperty('enabled', 'False')
        self.target_ui.pushButton_cryForGPA.setProperty('enabled', 'False')        
        if self.logined==0: 
            if not self.login():
                return False


        con=http.client.HTTPConnection(self.url)
        self.reportStatus('获取课程数....', 15)
        con.request('GET','/evaluate/stdevatea/queryCourseAction.do',headers=self.headers)
        data=con.getresponse().read().decode('gbk')
        all_course_index= re.findall('<td class=\\"NavText\\"><a href=\\"queryTargetAction.do\\?operation=target&amp;index=(.)\\">',data)
        course_number=int(max(all_course_index))+1
        self.reportStatus('你有%d门课程,请耐心等待'%course_number, 20)
        value=0
        con=http.client.HTTPConnection(self.url)
        format='/evaluate/stdevatea/queryTargetAction.do?operation=target&index=%s'
        con.request('GET',format%value,headers=self.headers)
        temp_data=con.getresponse().read().decode('gbk')
        self.reportStatus('获取评价项...', 25)
        post_value=re.findall('<select name=\\"(array\\[.*?\\])\\" style=\\"width:110px\\"><option value=\\"null\\">&nbsp;</option>\r\n\t\t<option value=\\"(.*?)\\"',temp_data)
        post_dict={'opinion':'Good!','operation':'Store'}
        post_index=0
        self.reportStatus('创建报表...', 30)
        for i in post_value:
            post_dict[post_value[post_index][0]]=post_value[post_index][1]
            post_index+=1

        postdata=urllib.parse.urlencode(post_dict)
        self.headers2["Content-Length"]="851"

        for idx in all_course_index: 
            
            con.close()
            con=http.client.HTTPConnection(self.url)
            format='/evaluate/stdevatea/queryTargetAction.do?operation=target&index=%s'
            con.request('GET',format%idx,headers=self.headers)
            con.getresponse()
            con.close()
            con=http.client.HTTPConnection(self.url)
            format='http://222.30.32.10/evaluate/stdevatea/queryTargetAction.do?operation=target&index=%s'
            self.headers2['Referer']=format % idx
            format='/evaluate/stdevatea/queryTargetAction.do'
            self.reportStatus('正在评价第%s门课...'%idx, 30+70*int(idx)/course_number)
            con.request('POST',format, postdata, self.headers2 )
            con.getresponse()
            
        self.headers2["Content-Length"]="97"    
        self.reportStatus('就绪', 100)
        con.close()
        self.target_ui.pushButton_fuckTeachers.setProperty('enabled', 'True')
        self.target_ui.pushButton_cryForGPA.setProperty('enabled', 'True')   
    def evaluateTeacherThread(self):
        t=threading.Thread(target=self.evaluateTeacher)        
        t.start()          
    def reportStatus(self, string, value):
        print('report')
        self.status_str=string
        self.status_int=value
        self.target_ui.eventGen.emit(QtCore.SIGNAL('reportStatus'))
    def showValicode(self):
        print('change')
        self.target_ui.eventGen.emit(QtCore.SIGNAL('showValicode(QString)'), 'validate_code')        
        
        
        
        
        
        
        
