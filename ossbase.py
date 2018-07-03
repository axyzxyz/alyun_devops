#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# @Time    : 2018/6/26 20:01
# @Author  : ysj
import os
import logging
import oss2

logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


class Oss:
    """阿里云oss sdk类"""

    def __init__(self, AccessKeyID, AccessKeySecret, bucket, endpoint=None):
        self.auth = oss2.Auth(AccessKeyID, AccessKeySecret)
        if not endpoint:
            logging.warning("endpoint is not set ,will used 'http://oss-cn-hangzhou.aliyuncs.com'\n")
            self.endpoint = 'http://oss-cn-hangzhou.aliyuncs.com'
        self.bucket = oss2.Bucket(self.auth, self.endpoint, bucket)

    def bucket_change(self, bucket, endpoint=None):
        """change bucket, if endpoint is set ,self.endpoint will be changed"""
        if endpoint:
            self.endpoint = endpoint
        self.bucket = oss2.Bucket(self.auth, self.endpoint, bucket)

    def downloadfile(self, rpath, lpath, **kwargs):
        """
        :param rpath: 远程文件路径
        :param lpath: 本地文件路径
        :return:
        """
        oss2.resumable_download(self.bucket, rpath, lpath, **kwargs)

    def download_dir(self, rpath, ldir=None):
        """下载目录，目录内文件最多1000个，包含目录本身。
            ldir will replace the root path of the rpath
        """
        rpath = rpath.strip("/") + "/"
        file_list_object = self.bucket.list_objects(rpath, max_keys=1000)
        file_list = [x.key for x in file_list_object.object_list]
        if not file_list:
            return "目录不存在"
        for file in file_list:
            if file.endswith('/'):
                os.path.exists(file) or os.makedirs(file)
            else:
                file_dir, filename = os.path.split(file)
                os.path.exists(file_dir) or os.makedirs(file_dir)
                self.downloadfile(file, file)

        root_dir = file.split('/')[0]
        if ldir:
            if os.path.exists(ldir):
                logging.warning("dir %s is exists, %s can not  rename to %s" % (ldir, root_dir, ldir))
            else:
                os.rename(root_dir, ldir)


if __name__ == '__main__':
    ak = 'weqeqwewq'
    st = 'asdasdsdasdsweqw'
    bk = 'fulan-test'
    alioss = Oss(ak, st, bk)
    alioss.download_dir('tmp', 'tests')