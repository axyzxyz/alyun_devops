#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# @Time    : 2018/3/16 17:11
# @Author  : ysj

import requests
from api_Signature import private_param, public_param, signature


class BaseApi:
    """
    基础api类，加载公共参数
    """

    def __init__(self, ak, secret, region_id, url='https://ecs.aliyuncs.com/', formats='json', version='2014-05-26'):
        """

        :param ak: AccessKeyID：
        :param secret:AccessKeySecret：
        :param region_id:区域id
        :param url:基础url， 不同服务url可能不同
        :param format:返回结果的格式
        :param version: api版本，不同服务版本可能不同
        """
        self.ak = ak
        self.secret = secret
        self.region_id = region_id
        self.url = url
        self.formats = formats
        self.public_param = public_param(ak, formats, Version=version)

    def get(self, Action, **kwargs):
        """
        因所有方法均为get请求，故不考虑请求方法
        :param Action: 请求动作参数
        :param kwargs: 其他附属参数
        :return: 字典格式;出错则返回None
        """
        priv_param = private_param(Action, **kwargs)
        try:
            params_encode = signature('get', self.secret, self.public_param, priv_param)
            url = '{0}{1}{2}'.format(self.url, '?', params_encode)
            response = requests.get(url)
            if self.formats.upper() == 'JSON':
                return response.json()
            else:
                return response
        except Exception as e:
            print(e)
            return None
