#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# @Time    : 2018/2/26 15:29
# @Author  : ysj
import json
import time
from collections import namedtuple
from datetime import datetime
from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526 import DeleteSnapshotRequest, DeleteImageRequest
from aliyunsdkecs.request.v20140526 import CreateImageRequest, CreateInstanceRequest
from aliyunsdkecs.request.v20140526 import ModifyImageAttributeRequest
from aliyunsdkcore.acs_exception.exceptions import ServerException
import _config as conf


# 以下模块隐性引用，删除后脚本无法使用, 未防止pep8 采用exec导入
exec('from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest, '
     'DescribeImagesRequest, DescribeSnapshotsRequest')


def day():
    return datetime.now().strftime('%Y%m%d')


def time_make(time_str, make=True):
    """
    阿里云返回结果，时间转换
    :param time_str: ‘2018-03-10T13:09:15Z’
    :make : bool 为真则返回与当前时间的小时差值,
    :return: 1520658555.0
    """
    make_time = time.mktime(time.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ'))
    now_time = time.time()

    if make:
        return '{0:.2f}'.format((now_time-make_time)/3600 - 8)  # api返回创建时间为0时区
    return time.mktime(time.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ'))


class EcsMetaClass(type):
    """
    ECS查询元类，装13方法
    """
    def __new__(mcs, cls, bcs, attr):
        api_list = ['instance', 'image', 'snapshot']
        for fun in api_list:
            attr.update(mcs._make(fun))
        return type.__new__(mcs, cls, bcs, attr)

    @classmethod
    def _make(mcs, func):
        method = func[0].upper() + func[1:] + 's'
        use_class = 'Describe%sRequest' % method
        do_fun = '{}.{}()'.format(use_class, use_class)
        return {func: do_fun}


class EcsDone(metaclass=EcsMetaClass):
    """
    元类耦合了除get_instance_id外的所有get方法。。。。。
    其他独立方法不受影响
    """
    def __init__(self, ak, secret, region):
        self.clt = client.AcsClient(ak, secret, region)

    def get_instance_info(self, instance_name: str=''):
        """
        与元类无耦合！！！
        输入ecs实例的别名
        :param instance_name:
        :return: 实例id ,name, 公网ip， 内网ip组成的具名元组
        """
        ecs_instance = namedtuple('ecs_instance', 'id name out_ip in_ip')
        requset = DescribeInstancesRequest.DescribeInstancesRequest()
        if instance_name:
            requset.set_InstanceName(instance_name)
        response = self.clt.do_action_with_exception(requset)
        instances = json.loads(response)['Instances']['Instance']
        if instances:  # 未考虑多个ip地址的情况
            return [ecs_instance(x['InstanceId'], x['InstanceName'], x['PublicIpAddress']['IpAddress'][0],
                                 x['InnerIpAddress']['IpAddress'][0]) for x in instances]

    def get_instance_id(self, instance_name: str=''):
        """
        输入ecs实例的别名
        :param instance_name:
        :return: 实例id 存在多个默认获取第一个
        """
        request = eval(self.instance)
        request.set_InstanceName(instance_name)
        response = self.clt.do_action_with_exception(request)
        out, inner, instance_id = self.get_dict_result('instance')
        result = json.loads(response)
        return result.get(out).get(inner)[0].get(instance_id) if result.get('TotalCount') > 0 else None

    def get_image(self, instance_name: str=None, name=None):
            return self.do_result('image', instance_name, name)

    def get_instance(self, instance_name: str=''):
            return self.do_result('instance', instance_name)

    def get_snapshot(self, instance_name: str=None, name=None):
        return self.do_result('snapshot', instance_name, name)

    def do_result(self, func, instance_name: str=None, name=None):
        """
        查询中间结果整理接口，多页结果整理到一起。
        :param func: 方法名
        :param instance_name: 实例名
        :param name 对应对象的名字
        :return: 所有实例结果
        """
        request = eval(getattr(self, func, None))
        request_method = '{}_{}{}{}'.format('set', func[0].upper(), func[1:], 'Name')  # 设置对象名字
        # request_id_method = '{}_{}{}{}'.format('set', func[0].upper(), func[1:], 'Name')  # 设置对象id
        # if 'instance' in func:
        #     request.set_InstanceName(instance_name)
        # else:
        #     request.set_InstanceId(self.get_instance_id(instance_name))
        if name:
            getattr(request, request_method)(name)

        if instance_name:
            if hasattr(request, 'set_InstanceName'):
                request.set_InstanceName(instance_name)
            else:
                if hasattr(request, 'set_InstanceId'):
                    request.set_InstanceId(self.get_instance_id(instance_name))
                else:
                    print('该对象无法关联实例查询，跳过实例筛选,或请指定对象name名字查询')

        # 循环遍历结果，直至为空; 将所有对象结果合并至最后一个字典返回
        request.set_PageSize(100)
        response = list()
        page_num = 1
        while True:
            request.set_PageNumber(page_num)
            res = json.loads(self.clt.do_action_with_exception(request))
            response.append(res)
            if page_num * 100 >= res.get('TotalCount'):
                break
            page_num += 1
        if response:
            try:
                for key, value in response[0].items():
                    if isinstance(value, dict):
                        out_info_key = key
                        inner_info_key = key.rstrip('s')

                inner_info = list()
                [inner_info.extend(_.get(out_info_key).get(inner_info_key)) for _ in response]
                response[-1].get(out_info_key)[inner_info_key] = inner_info

                return response[-1]
            except Exception as e:
                print(e)
                return

    @staticmethod
    def get_dict_result(name: str='instance'):
        """
        便于阿里云api结果取值
        :param name: instance
        :return: Instances, Instance, InstanceId
        """
        rt3 = '{}{}{}'.format(name[0].upper(), name[1:], 'Id')
        rt2 = '{}{}'.format(name[0].upper(), name[1:])
        rt1 = '{}{}{}'.format(name[0].upper(), name[1:], 's')
        return rt1, rt2, rt3

    def create_image(self, instance_name: str='instance_name', suffix='new'):
        request = CreateImageRequest.CreateImageRequest()
        instance_id = self.get_instance_id(instance_name)
        # print(instance_id)
        if not instance_id:
            raise AttributeError('the instance_name is not exist')
        request.set_InstanceId(instance_id)
        image_name = '{}_{}'.format(instance_name, suffix)
        request.set_ImageName(image_name)
        try:
            response = self.clt.do_action_with_exception(request)
            return response
        except ServerException as e:
            return '镜像名字:{}，已存在;同一天只需创建一个镜像'.format(image_name)

    def create_instance(self, name, index, instance_type='ecs.c5.large'):
        # 2cpu 4 g ecs.c5.large  4c9g ecs.c5.xlarge
        """未完成接口，通过阿里弹性伸缩api实现自动扩容"""
        request = CreateInstanceRequest.CreateInstanceRequest()
        request.set_InstanceName('{}_{}_{}'.format(name, day(), index))
        image = self.get_image(name='{}_{}'.format(name, day()))['Images']['Image']
        if not image:
            raise AttributeError('the image is not exist')
        image_id = image[0]['Image_id']
        request.set_ImageId(image_id)
        request.set_InstanceChargeType('PayByTraffic')  # 默认 PayByTraffic
        request.set_InternetMaxBandwidthIn(100)  # 默认 100
        request.set_InstanceType(instance_type)
        request.set_SecurityGroupId('sg-2319o94a4')  # 安全组id
        request.set_ZoneId()

    def del_image(self, image_id, force=True):
        request = DeleteImageRequest.DeleteImageRequest()
        request.set_ImageId(image_id)
        request.set_Force(force)
        response = self.clt.do_action_with_exception(request)
        return response

    def del_snapshot(self, snapshot_id):
        request = DeleteSnapshotRequest.DeleteSnapshotRequest()
        request.set_SnapshotId(snapshot_id)
        response = self.clt.do_action_with_exception(request)
        return response

    def mod_image_name(self, image_id, image_name='old'):
        """修改image名字后缀"""
        request = ModifyImageAttributeRequest.ModifyImageAttributeRequest()
        request.set_ImageId(image_id)
        request.set_ImageName(image_name)
        reponse = self.clt.do_action_with_exception(request)
        return reponse


def image_create(ecs, suffix='new'):
    """传入ecs实例"""
    # 创建镜像
    instances = [x['InstanceName'] for x in ecs.get_instance()['Instances']['Instance']]
    # print(instances)
    for i in instances:
        print(ecs.create_image(i, suffix))


def snap_del(ecs, hour=23):
    """传入ecs实例"""
    # 删除快照 规则:未使用的且时间在23小时之前的快照
    snapshots = ecs.get_snapshot()
    # print(snapshots)
    snapshots = snapshots['Snapshots']['Snapshot']
    for snapshot in snapshots:
        snapshot_id, create_time, usage = snapshot['SnapshotId'], snapshot['CreationTime'], snapshot['Usage']

        # print(snapshot_id, create_time, usage, type(usage))
        if float(time_make(create_time)) > float(hour) and usage == 'none':
            print(ecs.del_snapshot(snapshot_id))


def image_del(ecs, hours=23, force=False):
    """传入ecs实例"""
    # 删除镜像 规则:未使用的且时间在23小时之前的镜像

    images = ecs.get_image()['Images']['Image']
    # print(len(images))
    for image in images:
        image_id, create_time, usage, alias = image['ImageId'], image['CreationTime'], image['Usage'], \
                                              image['ImageOwnerAlias']
        # print(image_id, create_time, usage)
        if float(time_make(create_time)) > float(hours) and alias == 'self':
            if not force and usage == 'none':
                continue
            print(ecs.del_image(image_id, force))


def image_rename(ecs, hours=23, suffix='old'):
    """修改23小时前的镜像名字，添加后缀old"""
    images = ecs.get_image()['Images']['Image']
    for image in images:
        image_id, create_time, name, alias = image['ImageId'], image['CreationTime'], image['ImageName'],\
                                             image['ImageOwnerAlias']
        if not name.endswith(suffix):
            name = name + '_' + suffix
        if float(time_make(create_time)) > float(hours) and alias == 'self':
            ecs.mod_image_name(image_id, name)

def green_print(*args):
    print('\033[1;32m', *args, '\033[0m')


if __name__ == '__main__':
    # 实例化
    green_print('实例化')
    my_ecs = EcsDone(conf.ak, conf.secret, conf.region)
    # # # 删除36小时前的旧镜像
    green_print('删除36小时前的旧镜像')
    image_del(my_ecs, 36, force=True)
    # # 删除未使用的旧快照
    green_print('删除未使用的旧快照')
    snap_del(my_ecs, 0)
    # 修改前一天镜像名字，添加后缀old
    # green_print('修改前一天镜像名字，后缀old')
    # image_rename(my_ecs, 16, 'old')
    # time.sleep(5)
    # 创建今天的镜像
    green_print('创建今天的镜像,后缀当天时间')
    suffix = time.strftime('%Y%m%d')
    image_create(my_ecs, suffix=suffix)
    # for i in my_ecs.get_instance_info(''):
    #     print(i.name, i.out_ip)

    # print(my_ecs.get_image(name='exam-linshi_new'))
    # print(my_ecs.get_instance('management'))
