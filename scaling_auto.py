#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# @Time    : 2018/3/16 17:17
# @Author  : ysj
import _config as conf
from ecsApi import EcsApi
from scalingApi import ScalingApi

def main(iamge_name):
    """
    本函数功能，是配合ecs脚本中的自动镜像功能，保证采用当天最新的镜像，每天更自动新弹性伸缩配置，并删除旧的伸缩配置
    1.由于，弹性伸缩组，基本会保持不变，只会增加减少机器个数，请先用可视化web界面创建。
    :return:
    """

    scaling = ScalingApi(conf.ak, conf.secret, conf.region)
    # 取镜像
    image = ecs.get('')

def get_image_id(iamge_name):
