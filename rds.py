#! /usr/local/bin python3.6
"""
@Time    : 2018/3/11 0:04
@Author  : ysj
@Site    : 
@File    : rds.py
@Software: PyCharm
"""
#!/usr/bin/env python
#coding=utf-8
import  json
from collections import namedtuple
from aliyunsdkcore import client
from aliyunsdkrds.request.v20140815 import DescribeDBInstancesRequest
from aliyunsdkrds.request.v20140815 import ModifySecurityIpsRequest
import _config as conf







class RdsDone:

    def __init__(self, ak, secret, region):
        self.clt = client.AcsClient(ak, secret, region)

    def get_db_instance(self, name=None):
        """
        返回实例具名元祖组成的列表
        :param name: 指定别名，则只返回该实例
        :return: [db_instance(name='report_readonly', id='rr-bp1se0dwk3vueq89k')]
        """
        request = DescribeDBInstancesRequest.DescribeDBInstancesRequest()
        response = self.clt.do_action_with_exception(request)
        instance = namedtuple('db_instance', 'name id')
        return [instance(x['DBInstanceDescription'], x['DBInstanceId']) for x in
                json.loads(response)['Items']['DBInstance'] if x['DBInstanceDescription'] == name or not name]

    def add_ip(self, name, ip, array='py_api'):
        """
        添加白名单
        :name: rds实例别名
        :param ip: 要添加的ip
        :param array: 分组
        :return:
        """
        request = ModifySecurityIpsRequest.ModifySecurityIpsRequest()
        db_list = self.get_db_instance(name)
        if not db_list:
            raise AttributeError('the db instance is not exist')
        print(db_list[0].id)
        request.set_DBInstanceId(db_list[0].id)
        request.set_DBInstanceIPArrayName(array)
        request.set_SecurityIps(ip)
        response = self.clt.do_action_with_exception(request)
        return response


if __name__ == '__main__':
    rds = RdsDone(conf.ak, conf.secret, conf.region)
    res = rds.get_db_instance('report_readonly')
    print(rds.add_ip('testdb', '111.111.111.111'))

