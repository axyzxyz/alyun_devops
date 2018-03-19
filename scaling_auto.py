#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# @Time    : 2018/3/16 17:17
# @Author  : ysj
import time
import _config as conf
from ecsApi import EcsApi
from scalingApi import ScalingApi


def get_image_id(instance_name):
    """根据实例，返回当天的镜像id"""
    ecs = EcsApi(conf.ak, conf.secret, conf.region)
    image_name = '{}_{}'.format(instance_name, time.strftime('%Y%m%d'))
    image = ecs.get('DescribeImages', RegionId=conf.region, ImageName=image_name)
    if image['Images']['Image']:  # 有返回结果则返回image_id
        return image['Images']['Image'][0]['ImageId']


def create_scaling_conf(scaling_id, instance_name, secret_id, InstanceType="ecs.n4.xlarge",
                        InternetChargeType='PayByTraffic', LoadBalancerWeight=100):
    """

    :param scaling_id: 伸缩组id
    :param instance_name: 要扩展的实例名字
    :param secret_id: 安全组id
    :param InstanceType: 实例规格 ，默认4核8G
    :param InternetChargeType: 按流量
    :param LoadBalancerWeight=100 权重
    :return:
    """
    scaling = ScalingApi(conf.ak, conf.secret, conf.region)
    # response = scaling.get('DescribeScalingConfigurations', RegionId=conf.region, ScalingGroupId=scaling_id)

    # print(response)
    response = scaling.get('CreateScalingConfiguration', ScalingGroupId=scaling_id, ImageId=get_image_id(instance_name),
                           InstanceType=InstanceType, SecurityGroupId=secret_id, InternetChargeType=InternetChargeType,
                           InternetMaxBandwidthOut=100, KeyPairName='my', LoadBalancerWeight=100)
    return response

def main():
    """
    本函数功能，是配合ecs脚本中的自动镜像功能，保证采用当天最新的镜像，每天更自动新弹性伸缩配置，并删除旧的伸缩配置
    1.由于，弹性伸缩组，基本会保持不变，只会增加减少机器个数，请先用可视化web界面创建。
    :return:
    """
    # "sso 创建"
    sso = create_scaling_conf('asg-bp16ofi528ojaog7zvxv', 'SSO_SVR002', 'sg-2319o94a4')
    # "km 创建"
    time.sleep(2)
    km = create_scaling_conf('asg-bp1cty3i00izrrju3hw1', 'KM_SVR_MST002', 'sg-2319o94a4')
    # # 'exam 创建'
    time.sleep(2)
    exam = create_scaling_conf('asg-bp1fozn7s005zeorcenb', 'vmobel-exam01', 'sg-2319o94a4')
    print(sso, km, exam, sep='\n')

if __name__ == '__main__':
    main()