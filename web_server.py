#!/usr/bin/env python
#! -*- coding:UTF-8 -*-

import re
import os
import json
import threading
import datetime
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.options
import tornado.web
from tornado import template
from tornado.concurrent import Future
from tornado.options import define, options
from tornado.escape import json_decode

from Mysql import ManulMysql

#from operate_db import insert
#from operate_db import search
#from operate_db import traversal
#from operate_db import delete

from iptables import operate_iptables
from log import record

from mod_config import getConfig
from readExcel import patchData
record()



class timer1(threading.Thread):
    def __init__(self, info):
        threading.Thread.__init__(self)
        self.data = json.loads(info)
    def run(self):
        operate_iptables('add', self.data['ban_ip'])
        insert(self.data)


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("username")


define("port", default=8888, help="run on the given port", type=int)

class IndexHandler(BaseHandler):
    def get(self):
        self.redirect("/login")

class LoginHandler(BaseHandler):
    def get(self):
        try:
            path = str(self.request.arguments['next'][0])
        except:
            path = None
        cookie = self.get_secure_cookie("username")
        if cookie:
            if path:
                self.redirect("%s" % path)
            else:
                self.redirect("/menu?show=CMDBManage")
        else:
            self.render('login.html')
    def post(self):
        full_path = self.request.headers['Referer']
        path = self.request.headers['Referer'].split('next=')[-1].replace('%2F', '/')
        print path
        if not 'next' in full_path:
            path = 'login'
        user_remote = self.get_argument("username")
        pd_remote = self.get_argument("password")

        user_local = getConfig('relation', 'username')
        pd_local = getConfig('relation', 'password')
        if user_remote == user_local and pd_remote == pd_local:
            self.set_secure_cookie("username", self.get_argument("username"))
#            print 'path : %s' % path
            #self.render('whole.html',user=user_remote)
            if path:
                self.redirect("%s" % path)
            else:
                self.redirect("/status")
        else:
            self.write('Bad User or Bad Password !')

class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.clear_cookie("username")
        self.clear_cookie("password")
        self.redirect("/login")

class UploadHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        #self.redirect("/uploads/image/")
        #self.write('asdfsadf')
        self.render('pic.html')

class RegHandler(tornado.websocket.WebSocketHandler):
    def get(self):
        self.render('reg.html')

class CMDBManageHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('cmdblist.html')

class CMDBAddHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('cmdbadd.html')


class CMDBDataHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        sortOrder = self.request.arguments['sortOrder'][0]
        try:
            pageSize = int(self.request.arguments['pageSize'][0])
            pageNumber = int(self.request.arguments['pageNumber'][0])
        except KeyError:
            pageSize = ''
            pageNumber = ''
        try:
            searchText = self.request.arguments['searchText']
        except KeyError:
            searchText = ''
        
        M = ManulMysql()
        dataList = M.getHostlist(sortOrder, pageSize, pageNumber, searchText)
        M.close()
        data = json.dumps(dataList, ensure_ascii = False)
        self.write(data)

class DetailHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        aid = self.request.arguments['aid']
        self.render('detail.html', aid=aid)

class UploadExcelHandler(BaseHandler):
    #@tornado.web.authenticated
    def post(self):
        file_dict_list = self.request.files['my']
        #print 1
        M = ManulMysql()
        ticketstr = 'ticketError: '
        macstr = 'macError: '
        pcidstr = 'pcidError: '
        for eachfile in file_dict_list:
            filename = eachfile['filename'].encode('cp936')
            content = eachfile['body']
            #ff = open('./temp/%s' % filename, 'w')
            ff = open('/dev/shm/%s' % filename, 'w')
            ff.write(content)
            ff.close()
            
            flag = ''
            result = patchData('/dev/shm/%s' % filename)
            for eachrow in result:
                #print eachrow
                try:
                    if eachrow[12]:
                        try:
                            int(eachrow[12])
                        except ValueError:
                            continue
                except IndexError:
                     continue

                flag = M.verifyTicket(eachrow[10])
                if flag:
                    ticketstr =  ticketstr + eachrow[0].strip() + '  '
                    flag = 'error'
                    continue
                try:
                    flag = M.verifymac(str(eachrow[9]).strip(), eachrow[0].strip())
                    if flag:
                        macstr =  macstr + eachrow[0].strip() + '  '
                        flag = 'error'
                        continue
                except:
                    pass

                try:
                    flag = M.verifyPcid(str(eachrow[8]).strip(), eachrow[0].strip())
                    if flag:
                        pcidstr =  pcidstr + eachrow[0].strip() + '  '
                        flag = 'error'
                        continue
                except:
                    pass

                flag = M.insertHost(eachrow[0].strip())
                if not flag:
                    flag = 'error'
                    continue

                tid = M.gettid(eachrow[1].strip())

                M.insertHostVerbose(eachrow[0], \
                                    tid, \
                                    eachrow[2], \
                                    eachrow[3], \
                                    eachrow[4], \
                                    eachrow[5], \
                                    eachrow[6], \
                                    eachrow[7], \
                                    eachrow[8], \
                                    eachrow[9], \
                                    eachrow[10], \
                                    eachrow[11], \
                                    eachrow[12])

        M.close()
        dic = {
               'flag': flag,
               'result': ticketstr + '\n' + macstr + '\n' + pcidstr
              }
        self.write(json.dumps(dic))

class MenuHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        account = self.get_current_user()
        M = ManulMysql()
        username = M.getusername(account)
        M.close()
        self.render('menu.html', username=username)

class CpasswdHandler(BaseHandler):
    def get(self):
        self.render('cpasswd.html')

class DeleteHandler(BaseHandler):
    def get(self):
        data = json.loads(self.get_argument("data"))#.replace("%22", ""))
        M = ManulMysql()
        username = M.deleteRecord(data['order'])
        M.close()

class CpasswdDataHandler(BaseHandler):
    def get(self):
        data = json.loads(self.get_argument("data"))
        username = data['username'].strip()
        oldpw = data['oldpw'].strip()
        newpw = data['newpw'].strip()
        renewpw = data['renewpw'].strip()
        if not username:
            dic = {"result": "false","message": u"用户名不能为空"}
            self.write(json.dumps(dic))
            return 

        if not oldpw:
            dic = {"result": "false","message": u"原密码不能为空"}
            self.write(json.dumps(dic))
            return 

        if not newpw:
            dic = {"result": "false","message": u"新密码不能为空"}
            self.write(json.dumps(dic))
            return 

        if not renewpw:
            dic = {"result": "false","message": u"新密码不能为空"}
            self.write(json.dumps(dic))
            return 

        if oldpw == newpw:
            dic = {"result": "false","message": u"新密码不能和原密码相同"}
            self.write(json.dumps(dic))
            return 

        M = ManulMysql()
        passwd = M.login(username, oldpw)
        M.close()
        if not passwd == oldpw:
            dic = {"result": "false","message": u"用户名和原密码不匹配"}
            self.write(json.dumps(dic))
            return 

        if not newpw == renewpw:
            dic = {"result": "false","message": u"两次密码不一致"}
            self.write(json.dumps(dic))
            return 

        M = ManulMysql()
        result =  M.changepw(username, newpw)
        M.close()
        if result:
            dic = {"result": "true"}
            self.write(json.dumps(dic))
            return 

class RecordHandler(tornado.websocket.WebSocketHandler):
    #def open(self):
    #    print("WebSocket opened")

    def on_message(self, message):
        message = json.loads(message)
        #print message
        aid = message['asset_id'].strip()
        #des = message['asset_des'].strip()
        asset_type = message['asset_type'].strip()
        model = message['model'].strip()
        buy_date = message['buy_date'].strip()
        depart = message['depart'].strip()
        personname = message['personname'].strip()
        lid = message['loginid'].strip()
        pcname = message['pcname'].strip()
        pcid = message['pcid'].strip()
        mac = message['mac'].strip()
        ticketid = message['ticketid'].strip()
      
        M = ManulMysql()
        if ticketid:
            #try:
            #    if int(ticketid):
            #        pass
            #except:
            #    dic = {'result': 'false', 'message': u'签字单据号格式不正确'}
            #    self.write_message(json.dumps(dic))
            #    return
 
            flag = M.verifyTicket(ticketid)
            if flag:
                dic = {'result': 'false', 'message': u'签字单据号已存在'}
                self.write_message(json.dumps(dic))
                M.close()
                return
                
        else:
            dic = {'result': 'false', 'message': u'签字单据号不能为空'}
            self.write_message(json.dumps(dic))
            M.close()
            return

        if mac:
            flag = M.verifymac(mac, aid)
            if flag:
                dic = {'result': 'false', 'message': u'mac地址已存在'}
                self.write_message(json.dumps(dic))
                M.close()
                return

        if pcid:
            flag = M.verifyPcid(pcid, aid)
            if flag:
                dic = {'result': 'false', 'message': u'机身编号已存在'}
                self.write_message(json.dumps(dic))
                M.close()
                return

        comment = message['comment']
        count = message['count']
        if not aid:
            dic = {'result': 'false', 'message': u'资产编号不能为空'}
            self.write_message(json.dumps(dic))
            M.close()
            return

        #if not aid.isalnum():
        #    dic = {'result': 'false', 'message': u'资产编号格式不正确'}
        #    self.write_message(json.dumps(dic))
        #    return

        #if asset_type == u'请选择':
        #    dic = {'result': 'false', 'message': u'资产类型不能为空'}
        #    self.write_message(json.dumps(dic))
        #    return

        if not buy_date:
            buy_date = None
            #dic = {'result': 'false', 'message': u'购入日期不能为空'}
            #self.write_message(json.dumps(dic))
            #return

        if count:
            try:
                int(count)
            except ValueError:
                dic = {'result': 'false', 'message': u'数量应为整数'}
                self.write_message(json.dumps(dic))
                M.close()
                return

        flag = M.insertHost(aid)
        if not flag:
            dic = {'result': 'false', 'message': u'资产编号已存在'}
            self.write_message(json.dumps(dic))
            M.close()
            return
        else:
            if asset_type == u"请选择":
                tid = ''
            else:
                tid = M.gettid(asset_type)

            M.insertHostVerbose(aid, \
                                #des, \
                                tid, \
                                model, \
                                buy_date, \
                                depart, \
                                personname, \
                                lid, \
                                pcname, \
                                pcid, \
                                mac, \
                                ticketid, \
                                comment, \
                                count)
            M.close()
            dic = {'result': 'true'}
            self.write_message(json.dumps(dic))


class DeviceTypeHandler(tornado.websocket.WebSocketHandler):
    #def open(self):
    #    print("WebSocket opened")

    def on_message(self, message):
        try:
            message = json.loads(message)
        except:
            pass
        if message == 'GETTYPE':
            M = ManulMysql()
            typelist = M.gettype()
            M.close()
            dic = {"data": typelist}
            data = json.dumps(dic)
            self.write_message(data)
        else:
            data = ''
            self.write_message(data)

        if message == 'GETDEPART':
            M = ManulMysql()
            departlist = M.getdepart()
            M.close()
            data = json.dumps(departlist)
            self.write_message(data)
        else:
            data = ''
            self.write_message(data)

    #def on_close(self):
    #    print("WebSocket closed")

class DetailDataHandler(tornado.websocket.WebSocketHandler):
    #def open(self):
    #    print("WebSocket opened")

    def on_message(self, message):
        temp = json.loads(message)["aid"]
        aid = temp.split(';')[1].split('&')[0]
        if aid:
            M = ManulMysql()
            data = M.getVerbose(aid)
            M.close()
            data = json.dumps(data)
            self.write_message(data)

    #def on_close(self):
    #    print("WebSocket closed")

class UpdateHandler(tornado.websocket.WebSocketHandler):
    #def open(self):
    #    print("WebSocket opened")

    def on_message(self, message):
        data = json.loads(message)
        oldaid = data["oldaid"].strip()
        newaid = data["asset_id"].strip()
        atype = data["asset_type"].strip()
        model = data["model"].strip()
        buy_date = data["buy_date"].strip()
        depart = data["depart"].strip()
        personname = data["personname"].strip()
        lid = data["lid"].strip()
        pcname = data["pcname"].strip()
        pcid = data["pcid"].strip()
        mac = data["mac"].strip()
        ticketid = data["ticketid"].strip()
        comment = data["comment"].strip()
        count = data["count"].strip()
 
        M = ManulMysql()
        if not buy_date:
            buy_date = None

        if count:
            try:
                int(count)
            except ValueError:
                dic = {'result': 'false', 'message': u'数量应为整数'}
                self.write_message(json.dumps(dic))
                M.close()
                return

        #if not buy_date:
        #    dic = {'result': 'false', 'message': u'购入日期不能为空'}
        #    self.write_message(json.dumps(dic))
        #    return

        #if atype == u"请选择":
        #    dic = {'result': 'false', 'message': u'资产类型不能为空'}
        #    self.write_message(json.dumps(dic))
        #    return

        if not oldaid == newaid:
            if not newaid:
                dic = {'result': 'false', 'message': u'资产编号不能为空'}
                self.write_message(json.dumps(dic))
                M.close()
                return

            #if not newaid.isalnum():
            #    dic = {'result': 'false', 'message': u'资产编号格式不正确'}
            #    self.write_message(json.dumps(dic))
            #    return
            #for i in newaid:
            #    if re.match('[a-zA-Z0-9]', i):
            #        print True
                

            flag = M.checkaid(oldaid, newaid)
            if not flag:
                dic = {"result": "false", "message": "资产编号已存在"}
                self.write_message(dic)
                M.close()
                return

        if ticketid:
            flag1 = M.checktid(newaid,ticketid)
            if not flag1:
                flag2 = M.verifyTicket(ticketid)
                if flag2:
                    dic = {'result': 'false', 'message': u'签字单据号已存在'}
                    self.write_message(json.dumps(dic))
                    M.close()
                    return

        else:
            dic = {'result': 'false', 'message': u'签字单据号不能为空'}
            self.write_message(json.dumps(dic))
            M.close()
            return

        if mac:
            flag = M.verifymac(mac, newaid)
            if flag:
                dic = {'result': 'false', 'message': u'mac地址已存在'}
                self.write_message(json.dumps(dic))
                M.close()
                return

        if pcid:
            flag = M.verifyPcid(pcid, newaid)
            if flag:
                dic = {'result': 'false', 'message': u'机身编号已存在'}
                self.write_message(json.dumps(dic))
                M.close()
                return

        if atype == u"请选择":
            tid = ''
        else:
            tid = M.gettid(atype)
        result = M.update(tid, model, buy_date, depart, personname, lid, pcname, pcid, mac, ticketid, comment, count, newaid)
        dic = {"newaid": newaid, "result": "true"}
        self.write_message(json.dumps(dic))
        M.close()
        return



class SendFormHandler(tornado.websocket.WebSocketHandler):
    #def open(self):
    #    print("WebSocket opened")

    def on_message(self, message):
        data = json.loads(message)
        username = data['username'].strip()
        personname = data['personname'].strip()
        password = data['password'].strip()
        repassword = data['repassword'].strip()
        department = data['department'].strip()
        if not username:
            self.write_message(u'Error : 登录名不能为空')
            return
 
        if not personname:
            self.write_message(u'Error : 用户名不能为空')
            return

        if not password:
            self.write_message(u'Error : 密码不能为空')
            return

        if not repassword == password:
            self.write_message(u'Error : 两次密码不一致')
            return
       
        if department == u'请选择':
            self.write_message(u'Error : 请选择部门')
            return
            
        try:
            M = ManulMysql()
            M.createUser(username, personname, password, department)
            M.close()
            self.write_message(u'注册成功')
        except Exception as e:
            if "for key 'username_index'" in str(e):
                self.write_message(u'注册失败,登录名已存在')
                return
            self.write_message(u'注册失败')

    #def on_close(self):
    #    print("WebSocket closed")


class VerifyHandler(tornado.web.RequestHandler):
    def get(self):
        data = json.loads(self.get_argument("data"))
        username = data['username'].strip()
        password = data['password'].strip()
        #try:
        M = ManulMysql()
        passwd = M.login(username, password)
        M.close()

        if not username.strip():
            dic = {"result": "false", "message": u"用户名不能为空"}
            self.write(json.dumps(dic))
            return

        if not password.strip():
            dic = {"result": "false", "message": u"密码不能为空"}
            self.write(json.dumps(dic))
            return

        if passwd:
            self.set_secure_cookie("username",  username, expires_days=None)
            self.set_secure_cookie("password",  passwd, expires_days=None)
            #self.redirect("/reg")
            #self.render('menu.html')
            dic = {"result": "true"}
            self.write(json.dumps(dic))
        else:
            dic = {"result": "false", "message": u"用户名或密码错误"}
            self.write(json.dumps(dic))
            #self.clear_cookie("password")
      

if __name__ == '__main__':
    path = ''
    tornado.options.parse_command_line()

    settings = {
        "template_path" :  os.path.join(os.path.dirname(__file__),"templates"),
        "static_path" :  os.path.join(os.path.dirname(__file__), "static"),
        "cookie_secret" : "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
        "login_url" : "/login"
        }

    app = tornado.web.Application(
        handlers=[
                  (r'/uploads/image/*.*', UploadHandler),
                  (r'/', IndexHandler),
                  (r'/login', LoginHandler),
                  (r'/logout', LogoutHandler),
                  (r'/reg', RegHandler),
                  (r'/menu', MenuHandler),
                  (r'/cmdblist', CMDBManageHandler),
                  (r'/uploadExcel', UploadExcelHandler),
                  (r'/cmdbadd', CMDBAddHandler),
                  (r'/checklistdata', CMDBDataHandler),
                  (r'/devicetype', DeviceTypeHandler),
                  (r'/detail', DetailHandler),
                  (r'/detaildata', DetailDataHandler),
                  (r'/update', UpdateHandler),
                  (r'/record', RecordHandler),
                  (r'/sendForm', SendFormHandler),
                  (r'/cpasswd', CpasswdHandler),
                  (r'/cpasswddata', CpasswdDataHandler),
                  (r'/delete', DeleteHandler),
                  (r'/verify', VerifyHandler)],
        #template_path=('./')
        debug= True,**settings
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
