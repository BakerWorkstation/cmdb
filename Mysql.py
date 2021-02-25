#!/usr/bin/env python
# -*- coding:UTF-8 -*-

import os
import yaml
import random
import string
import datetime
import mysql.connector

class ContinueI(Exception):
    pass

Continue_i = ContinueI()

def randomkey(lenth):
    key = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIGKLMNOPQRSTUVWXYZ0123456789'
    secret = string.join(random.sample(key, lenth)).replace(" ", "")
    return secret

class ManulMysql(object):
    def __init__(self):
        try:
            zabbixconf = './Mysql.yaml'
            self.stream = file(zabbixconf, 'r')
        except IOError:
            print 'Mysql.yaml not exist!'
            os._exit(0)
        self.connect()
     

    def connect(self):
        config = yaml.load(self.stream)
        try:
            self.cnn = mysql.connector.connect(**config)
            self.cnn1 = mysql.connector.connect(**config)
            self.cnn2 = mysql.connector.connect(**config)
            self.cursor = self.cnn.cursor()
            self.cursor1 = self.cnn1.cursor()
            self.cursor2 = self.cnn2.cursor()
        except mysql.connector.Error as e:
            print('connect fails!{}'.format(e))
            os._exit(0)

    def createUser(self, username, personname, password, department):
        args = (randomkey(16), username, personname, password, department)
        sql = "insert into tb_user  select %s, %s, %s, %s, thekey from tb_dict where thevalue=%s and parentid='4';"
        self.cursor.execute(sql, args)
        self.cnn.commit()

    def login(self, username, password):
        passwd =''
        args = (username, password)
        sql = "select password from tb_user where account=%s and password=%s;"
        self.cursor.execute(sql, args)
        try:
            for i in self.cursor:
                passwd = i[0]
        except:
            passwd = ''
        return passwd

    def gettype(self):
        typelist = []
        sql = "select thevalue from tb_dict where parentid='3';"
        self.cursor.execute(sql)
        try:
            for i in self.cursor:
                typelist.append(i[0])
        except:
            typelist = ''
        return typelist
    
    def getusername(self, account):
        args = (account, 1)
        sql = "select username from tb_user where account=%s and '1'=%s;"
        self.cursor.execute(sql, args)
        try:
            for i in self.cursor:
                return i[0]
        except:
            pass

    def getdepart(self):
        departlist = []
        sql = "select thevalue from tb_dict where parentid='4';"
        self.cursor.execute(sql)
        try:
            for i in self.cursor:
                departlist.append(i[0])
        except:
            departlist = ''
        return departlist

    def insertHost(self, aid):
        ctime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mtime = ctime
        
        sql = "select num from tb_host order by cast(`num` as decimal) desc limit 1;"
        self.cursor.execute(sql)
        num = ''
        for i in self.cursor:
            num = str(int(i[0]) + 1)
        if not num:
            num = '1'

        args = (aid, num, ctime, mtime)
        sql = "insert into tb_host values (%s, %s, %s, %s);"
        try:
            self.cursor.execute(sql, args)
            self.cnn.commit()
            return True
        except:
            return False

        #print num


 
    def gettid(self, asset_type):
        args = (asset_type , '3')
        sql = "select thekey from tb_dict where thevalue=%s and parentid=%s;"
        self.cursor.execute(sql, args)
        tid = ''
        try:
            for i in self.cursor:
                tid = i[0]
        except:
            tid = ''
        return tid

    def insertHostVerbose(self, *args):
        sql = "insert into tb_host_verbose values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        self.cursor.execute(sql, args)
        self.cnn.commit()

    def getHostlist(self, sortOrder, pageSize, pageNumber, searchText):
        total = ''
        dataList = []
        if sortOrder == 'asc':
            sortOrder = "desc"
        elif sortOrder == 'desc':
            sortOrder = "asc"
        else:
            sortOrder = ''

        if not searchText:
            sql = "select count(aid) from tb_host"
            self.cursor.execute(sql)
            for i in self.cursor:
                total = i[0]       
     
            if pageSize == '' and pageNumber == '':
                sql = "select * from tb_host order by cast(`num` as decimal) %s;" % sortOrder
                self.cursor.execute(sql)
            else:
                startItem = 0 + 10 * ( pageNumber - 1)
                sql = "select * from tb_host order by cast(`num` as decimal) desc limit %s,%s;"
                args = (startItem, pageSize)
                self.cursor.execute(sql, args)
    
            for i in self.cursor:
                dataDict = {}
                dataDict['num'] = i[1]
                dataDict['aid'] = i[0]
                dataDict['ctime'] = i[2].strftime("%Y-%m-%d %H:%M:%S")
                dataDict['mtime'] = i[3].strftime("%Y-%m-%d %H:%M:%S")
                sql = "select thevalue from tb_dict where thekey=(select tid from tb_host_verbose where aid=%s) and parentid=%s;"
                args = (dataDict['aid'], '3')
                self.cursor1.execute(sql, args)
                for j in self.cursor1:
                    dataDict['dtype'] = j[0]
                sql = "select * from tb_host_verbose where aid=%s and '1'=%s"
                args = (dataDict['aid'], 1)
                self.cursor2.execute(sql, args)
                try:
                    for k in self.cursor2:
                        dataDict['model'] = k[2]
                        #print str(k[4])
                        if str(k[3]) == "None":
                            dataDict['date'] = ''
                        else:
                            dataDict['date'] = str(k[3])
                        dataDict['dpart'] = k[4]
                        dataDict['personname'] = k[5]
                        dataDict['lid'] = k[6]
                        dataDict['pcname'] = k[7]
                        dataDict['pcid'] = k[8]
                        dataDict['mac'] = k[9]
                        dataDict['ticketid'] = k[10]
                        dataDict['comment'] = k[11]
                        dataDict['count'] = k[12]
                    dataList.append(dataDict)
                except ContinueI:
                    continue
        else:
            dataList = []

            sql = "SELECT\
                         count(a.aid)\
                   FROM\
                         tb_host_verbose AS a,\
                         tb_dict AS b\
                   WHERE\
                         CONCAT(\
                                 ifnull(aid,''),\
                                 ifnull(thevalue,''),\
                                 ifnull(model,''),\
                                 ifnull(date,''),\
                                 ifnull(depart,''),\
                                 ifnull(personname,''),\
                                 ifnull(lid,''),\
                                 ifnull(pcname,''),\
                                 ifnull(pcid,''),\
                                 ifnull(mac,''),\
                                 ifnull(ticketid,''),\
                                 ifnull(comment,''),\
                                 ifnull(count,'')\
                               )\
                         LIKE %s AND a.tid = b.thekey and '1'=%s"

            args = ('%' + searchText[0] + '%', 1)
            self.cursor.execute(sql, args)
            for i in self.cursor:
                total = i[0]

            sql = "SELECT\
                         a.aid,\
                         b.thevalue,\
                         a.model,\
                         a.date,\
                         a.depart,\
                         a.personname,\
                         a.lid,\
                         a.pcname,\
                         a.pcid,\
                         a.mac,\
                         a.ticketid,\
                         a.comment,\
                         a.count,\
                         c.num\
                   FROM\
                         tb_host_verbose AS a,\
                         tb_dict AS b,\
                         tb_host AS c\
                   WHERE\
                         CONCAT(\
                                ifnull(a.aid,''),\
                                ifnull(thevalue,''),\
                                ifnull(model,''),\
                                ifnull(date,''),\
                                ifnull(depart,''),\
                                ifnull(personname,''),\
                                ifnull(lid,''),\
                                ifnull(pcname,''),\
                                ifnull(pcid,''),\
                                ifnull(mac,''),\
                                ifnull(ticketid,''),\
                                ifnull(comment,''),\
                                ifnull(count,'')\
                               ) \
                         LIKE %s AND a.tid = b.thekey and a.aid = c.aid "
            try:
                startItem = 0 + 10 * ( pageNumber - 1)
                args = ('%' + searchText[0] + '%', startItem, pageSize)
                end = 'limit %s,%s'
            except:
                end = "and '1'=%s"
                args = ('%' + searchText[0] + '%', 1)
            sql = sql + end
            self.cursor.execute(sql, args)
            for i in self.cursor:
                dataDict = {}
                dataDict['aid'] = i[0]
                dataDict['dtype'] = i[1]
                dataDict['model'] = i[2]
                dataDict['date'] = str(i[3])
                dataDict['dpart'] = i[4]
                dataDict['personname'] = i[5]
                dataDict['lid'] = i[6]
                dataDict['pcname'] = i[7]
                dataDict['pcid'] = i[8]
                dataDict['mac'] = i[9]
                dataDict['ticketid'] = i[10]
                dataDict['comment'] = i[11]
                dataDict['count'] = i[12]
                dataDict['num'] = i[13]
                dataList.append(dataDict)

        data = {'total': total, 'rows': dataList}
        return data

    def getVerbose(self, aid):
        args = (aid, 1, 1)
        sql = "select * from tb_host_verbose where aid=%s and %s=%s;"
        self.cursor.execute(sql, args)
        dataDict = {}
        for i in self.cursor:
            dataDict['aid'] = i[0]
            dataDict['tid'] = i[1]
            dataDict['model'] = i[2]
            try:
                dataDict['buy_date'] = i[3].strftime("%Y-%m-%d")
            except:
                dataDict['buy_date'] = ''

            dataDict['depart'] = i[4]
            dataDict['personname'] = i[5]
            dataDict['lid'] = i[6]
            dataDict['pcname'] = i[7]
            dataDict['pcid'] = i[8]
            dataDict['mac'] = i[9]
            dataDict['ticketid'] = i[10]
            dataDict['comment'] = i[11]
            dataDict['count'] = i[12]
 
        args = (dataDict['tid'], 3)
        sql = "select thevalue from tb_dict where thekey=%s and parentid=%s;"
        self.cursor.execute(sql, args)
        for i in self.cursor:
            dataDict['tid'] = i[0]
        return dataDict

    def checkaid(self, oldaid, newaid):
        sql = "update tb_host set aid=%s where aid=%s;"
        args = (newaid, oldaid)
        try:
            self.cursor.execute(sql, args)
            self.cnn.commit()
            return True
        except Exception:
            return False

    def checktid(self, newaid, ticketid):
        sql = "select ticketid from tb_host_verbose where aid=%s and '1'=%s;"
        args = (newaid ,1)
        self.cursor.execute(sql, args)
        for i in self.cursor:
            tempdata = str(i[0])
        if tempdata == ticketid:
            return True
        else:
            return False

    def update(self, *args):
        sql = "update tb_host_verbose set tid=%s, model=%s, date=%s, depart=%s, personname=%s, \
               lid=%s, pcname=%s, pcid=%s, mac=%s, ticketid=%s, comment=%s, count=%s where aid=%s"
        try:
            self.cursor.execute(sql, args)
            self.cnn.commit()
        except Exception as e:
            #print str(e)
            pass

        mtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        args = (mtime, args[-1])
        sql = "update tb_host set mtime=%s where aid=%s"
        try:
            self.cursor.execute(sql, args)
            self.cnn.commit()
        except:
            pass

    def changepw(self, account, password):
        args = (password, account)
        sql = "update tb_user set password=%s where account=%s;"
        try:
            self.cursor.execute(sql, args)
            self.cnn.commit()
            return True
        except:
            pass

    def deleteRecord(self, data):
        for i in data:
            args = (i, '1')
            sql = "delete from tb_host where num=%s and '1'=%s;"
            try:
                self.cursor.execute(sql, args)
                self.cnn.commit()
            except Exception as e:
                #print str(e)
                pass

    def verifyTicket(self, ticketid):
        args = (ticketid, 1)
        sql = "select aid from tb_host_verbose where ticketid=%s and '1'=%s;"
        self.cursor.execute(sql, args)
        tempdata = ''
        for i in self.cursor:
            tempdata = i[0]
        if tempdata:
            return True
        else:
            return False

    def verifymac(self, mac, aid):
        args = (mac, aid)
        sql = "select aid from tb_host_verbose where mac=%s and aid!=%s;"
        self.cursor.execute(sql, args)
        tempdata = ''
        for i in self.cursor:
            tempdata = i[0]
        if tempdata:
            return True
        else:
            return False

    def verifyPcid(self, pcid, aid):
        args = (pcid, aid)
        sql = "select aid from tb_host_verbose where pcid=%s and aid!=%s;"
        self.cursor.execute(sql, args)
        tempdata = ''
        for i in self.cursor:
            tempdata = i[0]
        if tempdata:
            return True
        else:
            return False

    def close(self):
        self.cursor.close()
        self.cursor1.close()
        self.cursor2.close()
        self.cnn.close()
        self.cnn1.close()
        self.cnn2.close()

if __name__ == '__main__':
    #M = ManulMysql()
    print randomkey(16)
