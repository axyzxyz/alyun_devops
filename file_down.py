#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# @Time    : 2018/7/3 9:53
# @Author  : ysj

from ossbase import Oss


def down_load(file, bk='km-kj-cc1'):

    ak = '**************'
    st = '*******************'
    alioss = Oss(ak, st, bk)
    res_file = 'result_' + file
    with open(file, encoding='utf-8') as f:
        with open(res_file, 'w+', encoding='utf-8') as f2:
            title = f.readline()
            f2.write(title.strip("\n") + ',"目录"\n')
            count = 0
            for line in f:
                try:
                    file_path = line.split(",")[-1].split("/")[2]
                except:
                    f2.write(line.strip("\n") + ',"{}"\n'.format('目录不存在'))
                    continue
                else:
                    pass
                if file_path:
                    print(line.split(",")[-1])
                    if "/cc2/" in line.split(",")[-1]:
                        alioss.bucket_change('km-kj')
                    if "/cc1/" in line.split(",")[-1]:
                        alioss.bucket_change('km-kj-cc1')

                    while True:
                        try:
                            downinfo = alioss.download_dir(file_path)
                        except:
                            import time
                            time.sleep(2)
                            print(line)
                        else:
                            break

                    if downinfo:
                        file_path = downinfo
                    count += 1
                    print("已下载{}个，文件信息为：{}".format(count, line.replace('"', '').replace("\n", "")))
                    f2.write(line.strip("\n") + ',"{}"\n'.format(file_path))
                else:
                    f2.write(line.strip("\n") + ',"{}"\n'.format('目录不存在'))


if __name__ == '__main__':
    # 微课
    # down_load('sqlResult_1890815.csv')
    # scorm
    down_load('scrom.csv')
