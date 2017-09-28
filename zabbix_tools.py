#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Created by YuLL <yu.liang.liang@wowoohr.com>
#Last Modified: 20170816

import json
import sys
import requests

class zabbix_tools:
    '''
    Zabbix API调用工具类
    该工具用于调用Zabbix API实现获取主机、主机组、模板、Items信息，创建主机、删除主机、更新主机信息等功能。
    API接口参考：https://www.zabbix.com/documentation/3.2/manual/api/reference

    使用说明：
    1、user_login和get_data为公共函数。
    2、get_host方法需要提供zabbix监控中host_name。返回值为主机组基本信息，并return hostid。
    3、get_grouphost和get_templates方法只能获取所有主机组和模板信息，暂不支持单独获取指定主机组和模板。
    4、get_items方法需要提供参数host_name，根据get_host return的hostid来获取items。
    5、create_host支持的参数为hostip, hostport, groupid, hostname, templateid。其中hostip和hostport为必须提供参数，groupid='12'和templateid='10117'为默认值，hostname如果为空，则hostname=hostip。
    6、del_host方法需要提供参数host_name，根据get_host return的hostid来删除主机。
    7、update_host支持的参数为host_name, template_add_id, groupid, template_clear_id。其中host_name为必须提供参数，更新操作一次只能更新一个参数。
    '''
    def __init__(self):
        self.url = 'http://zabbix.rlwops.com/api_jsonrpc.php'
        self.headers = {"Content-Type": "application/json"}
        self.session = requests.Session()
        self.zabbix_user = "Admin"
        self.zabbix_pwd = "Z5BlWvyiSRqHQJe9aI4r"
        self.authID = self.user_login()

    def user_login(self):
        auth_data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "user.login",
                "params": {
                    "user": self.zabbix_user,
                    "password": self.zabbix_pwd
                },
                "id": 0
            })
        try:
            r = self.session.post(self.url,data=auth_data,headers=self.headers)
            response = json.loads(r.text)
            return response['result']
        except requests.RequestException as e:
            print e

    def get_data(self, data=None):
        try:
            result = self.session.post(self.url,data=data,headers=self.headers)
            response = json.loads(result.text)
            if response['result'] != []:
                return response
            else:
                print "The data is empty, please check the hostname is correct..."
                sys.exit(33)
        except Exception, e:
            print e

    def get_host(self, host_name):
        data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                    "output": "extend",
                    "filter": {"host": [host_name]}
                },
                "auth": self.authID,
                "id": 1
            })
        response = self.get_data(data)
        print json.dumps(response, sort_keys=True, indent=2)
        r = self.get_data(data)['result']
        if (r != 0) and (len(r) != 0):
            hostid = r[0]
            return hostid['hostid']

    def get_proxy_id(self):
        data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "proxy.get",
                "params": {
                    "output": "extend",
                    "selectInterface": "extend"
                },
                "auth": self.authID,
                "id": 1
            })
        response = self.get_data(data)
        json.dumps(response, sort_keys=True, indent=2)

    def get_grouphost(self):
        data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "hostgroup.get",
                "params": {
                    "output": "extend",
                },
                "auth": self.authID,
                "id": 1
            })
        response = self.get_data(data)
        print json.dumps(response, sort_keys=True, indent=2)

    def get_templates(self):
        data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "template.get",
                "params": {
                    "output": ["templateid","name"],
                },
                "auth": self.authID,
                "id": 1,
            })
        response = self.get_data(data)
        print json.dumps(response, sort_keys=True, indent=2)

    def get_items(self,host_name):
        hostid = self.get_host(host_name)
        print hostid
        data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "item.get",
                "params": {
                    "output": "extend",
                    "hostids": hostid,
                    "sortfield": "name"
                },
                "auth": self.authID,
                "id": 1
            })
        response = self.get_data(data)
        print json.dumps(response, sort_keys=True, indent=2)

    def create_host(self, hostip=None, hostport=None, groupid="12", hostname=None, templateid="10117", proxyid=None):
        g_list = []
        t_list = []
        if hostname is None:
            hostname = hostip

        if groupid:
            for i in groupid.split(','):
                vlaue = {}
                vlaue['groupid'] = i
                g_list.append(vlaue)

        if hostip and groupid:
            data = {
                "jsonrpc": "2.0",
                "method": "host.create",
                "params": {
                    "host": hostname,
                    "interfaces": [
                        {
                            "type": 1,
                            "main": 1,
                            "useip": 1,
                            "ip": hostip,
                            "dns": "",
                            "port": hostport
                        }
                    ],
                    "groups": g_list,
                },
                "auth": self.authID,
                "id": 1
            }
            if templateid:
                for i in templateid.split(','):
                    vlaue = {}
                    vlaue['templateid'] = i
                    t_list.append(vlaue)
                data["params"]["templates"] = t_list

            if proxyid:
                data["params"]["proxy_hostid"] = proxyid

            json_data = json.dumps(data)
            print json_data
            response = self.get_data(json_data)
            print json.dumps(response, sort_keys=True, indent=2)
        else:
            print "The hostip and groupid cannot be empty..."
            sys.exit(44)

    def del_host(self,host_name):
        hostid = self.get_host(host_name)
        data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "host.delete",
                "params": [hostid],
                "auth": self.authID,
                "id": 1
            })
        response = self.get_data(data)
        print json.dumps(response, sort_keys=True, indent=2)

    def update_host(self,host_name=None, template_add_id=None, groupid=None, template_clear_id=None):
        g_list = []
        t_a_list = []
        t_c_list = []
        def get_t_id(host_name):
            if host_name:
                data = json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "method": "host.get",
                        "params": {
                            "output": ["hostid"],
                            "selectParentTemplates": ["templateid", "name"],
                            "selectGroups": "extend",
                            "hostids": hostid,
                        },
                        "auth": self.authID,
                        "id": 1
                    })
                r = self.get_data(data)['result']
                if (r != 0) and (len(r) != 0):
                    g_id = r[0]['groups'][0]['groupid']
                    return g_id
            else:
                print "Please specify the host to be modified..."
                sys.exit(55)

        if host_name:
            hostid = self.get_host(host_name)
            get_t_id(host_name)
            data = {
                "jsonrpc": "2.0",
                "method": "host.update",
                "params": {
                    "hostid": hostid,
                },
                "auth": self.authID,
                "id": 1
            }
            if groupid and template_add_id:
                print "The update operation can only update one parameter at a time..."
                sys.exit(66)
            elif groupid:
                for i in groupid.split(','):
                    vlaue = {}
                    vlaue['groupid'] = i
                    g_list.append(vlaue)
                data["params"]['groups'] = g_list
                json_data = json.dumps(data)
                response = self.get_data(json_data)
                print json.dumps(response, sort_keys=True, indent=2)
            elif template_clear_id:
                for i in template_clear_id.split(','):
                    vlaue = {}
                    vlaue['templateid'] = i
                    t_c_list.append(vlaue)
                data["params"]['templates_clear'] = t_c_list
                json_data = json.dumps(data)
                response = self.get_data(json_data)
                print json.dumps(response, sort_keys=True, indent=2)
            elif template_add_id:
                for i in template_add_id.split(','):
                    vlaue = {}
                    vlaue['templateid'] = i
                    t_a_list.append(vlaue)
                data["params"]['templates'] = t_a_list
                print json.dumps(data, sort_keys=True, indent=2)
                json_data = json.dumps(data)
                response = self.get_data(json_data)
                print json.dumps(response, sort_keys=True, indent=2)
            else:
                print "Please specify the host to be modified..."
                sys.exit(77)

if __name__ == "__main__":
    z = zabbix_tools()
    z.user_login()
#    z.get_templates()
    '''get_host示例'''
#    z.get_host('Online-Consumer-10.15.66.56')
    '''update_host示例'''
#    z.update_host(host_name='test-ip-01',template_add_id='10117')
    '''create_host示例'''
    z.create_host(hostip='10.11.1.1', hostport='10050', groupid='11', hostname='test-ip-01', templateid='10001,10048', proxyid='10124')
