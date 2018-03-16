#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# @Time    : 2018/3/13 16:08
# @Author  : ysj
from collections import OrderedDict
from hashlib import sha1
import hmac
from urllib.parse import urlencode, urlsplit
from uuid import uuid4
import datetime
import base64
import requests
import _config as conf
import json


def now_str():
    """当前时间变成阿里云api要求的格式, 需要0时区的"""
    t = datetime.datetime.now() + datetime.timedelta(hours=-8)
    return t.strftime('%Y-%m-%dT%H:%M:%SZ')


def ensure_str(word, encoding='utf-8'):
    """确保str格式"""
    return word.decode(encoding=encoding) if isinstance(word, bytes) else word


def ensure_bytes(word, encoding='utf-8'):
    """确保bytes格式"""
    return word.encode(encoding=encoding) if isinstance(word, str) else word


def get_uuid():
    return str(uuid4())


def public_param(AccessKeyId, Format='XML', Timestamp=now_str(), SignatureVersion=1.0,
                 SignatureMethod='HMAC-SHA1', Version='2014-05-26',
    SignatureNonce=get_uuid()):
    """公共参数"""
    return locals()


def private_param(Action,**kwargs):
    """私有参数"""
    if kwargs:
        locals().update(kwargs)
    del kwargs
    return locals()


def tran_code(word):
    """
    根据阿里云签名规则，对签名字符串进行特定字符的转换
    :param word:
    :return:
    """
    trans = [('=', '%3D'),
             ("+", "%20"),
             ("%7E", "~"),
             ('&', '%26'),
             ('*', '%2A'),
             ('%3A', '%253A'),
             ]
    words = word
    for tran in trans:
        words = words.replace(*tran)
    return words


def signature(httpmethod, Secret, public, private):
    """
    签名,注意，时间格式为UTC0时区的，即-8hours，同时签名时，时间需要urlencode 两次,即时间中间的":" --> %3A -->%253A
    :param httpmethod: 请求方法
    :param Secret: 秘钥
    :param public: 公共请求参数集，
    :param private:私有请求参数集，
    :return: 包括签名在内的所有参数的urlencode字符串，加访问网址，即可直接请求
    """
    all_param = {}
    all_param.update(public)
    all_param.update(private)
    sort_param = OrderedDict({key: all_param[key] for key in sorted(all_param)})
    param_str = urlencode(sort_param, encoding='utf-8')
    param_string = tran_code(param_str)
    sign_string = httpmethod.upper() + '&%2F&' + param_string
    key = Secret + '&'
    sign = hmac.new(ensure_bytes(key), ensure_bytes(sign_string), sha1)
    sign_string = base64.b64encode(sign.digest()).decode()
    all_param['Signature'] = sign_string
    return urlencode(all_param)


if __name__ == '__main__':
    # 阿里云签名对比，保证签名结果正确性
    # pub = public_param('testid', 'xml', '2014-08-15T11:10:07Z', 1.0, 'HMAC-SHA1', '2014-08-28',
    #                    '1324fd0e-e2bb-4bb1-917c-bd6e437f1710')
    # priv = private_param('DescribeScalingGroups', RegionId='cn-qingdao')
    # signature('get', 'testsecret', pub, priv)
    # pub = public_param(conf.ak, 'JSON', Version='2014-08-28')
    pub = public_param(conf.ak, 'JSON')
    # priv = private_param('DescribeScalingConfigurations', RegionId=conf.region, ScalingGroupId='asg-bp1cty3i00izrrju3hw1')
    priv = private_param('DescribeImages', RegionId=conf.region, PageSize=50, ImageOwnerAlias='self' )
    url = signature('get', conf.secret, pub, priv)
    req = requests.get('https://ecs.aliyuncs.com/?' + url)
    print(json.loads(req.text))
