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
        else:
            self.endpoint = endpoint
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

    def push_file(self, filename, ossfilename=None, cdn_host=None):
        """

        :param filename: 本地文件地址
        :param ossfilename: oss存储文件名，为空则为filename
        :cdn_host cdn的域名，带http or https，不存在则为公网oss地址
        :return:链接地址

        """
        if not os.path.isfile(filename):
            print("warnning: the {} is not a file or not existed".format(filename))
            return
        base_name = os.path.basename(filename)
        ossfilename = ossfilename or base_name
        result = self.bucket.put_object_from_file(ossfilename, filename)
        url = result.resp.response.url
        internal_url = url.replace('.aliyuncs.com/', '-internal.aliyuncs.com/')
        if cdn_host:
            if cdn_host.lower().startswith(['https', 'http']):
                cdn_url = cdn_host.strip() + result.resp.response.request.path_url
            else:
                logging.warning("cdn_host is must started with 'https' or 'http' ")
                cdn_url = url
        else:
            cdn_url = url
        return dict(url=url, internal_url=internal_url, cdn_url=cdn_url)



if __name__ == '__main__':
    ak = '***********'
    st = '***********'
    bk = 'fulan-test'
    alioss = Oss(ak, st, bk)
    # alioss.download_dir('tmp', 'tests')
    print(alioss.push_file('a.html', 'aaa/aaaa/aaaaaaaaaaa.html'))
