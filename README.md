# alyun_devops
## 本项目采用pipenv作版本控制， python版本为python3
#### Pipfile
版本控制文件，使用方法如下：
```bash
pipenv --python 3.6
pipenv install
pipenv run *.py
```
#### _config.py
阿里云sdk api使用秘钥，该秘钥已禁用（删除）
#### api_Signature.py
阿里云api接口签名脚本，简化api请求过程，设定好公共参数的对应版本，即可自由添加对应接口的请求参数；得到返回结果

#### baseApi.py
各项服务的基础api接口类
#### ecsApi.py
ecs服务器api接口类，继承自基础api类，使用该类get方法可请求访问ecs对用的所有服务
```python
a = EcsApi(conf.ak, conf.secret, conf.region)
print(a.get('DescribeInstances', PageSize=100, RegionId=conf.region))
```
#### scalingApi.py
- 虽有瑕疵，但可以在服务器横向扩展时，自动添加对应数据库的白名单，及不多于5个slb负载均衡服务器；目前只有api接口，无sdk；故导致前后
两种请求方式混合使用
scaling 弹性伸缩服务api接口类，继承自基础api类，使用该类get方法可请求访问scaling对用的所有服务
```python
b = ScalingApi(conf.ak, conf.secret, conf.region)
print(b.get('DescribeScalingGroups', RegionId=conf.region))
````
#### scaling_auto.py
弹性伸缩自动加载最新镜像的脚本
#### ecs.py
ecs服务自动创建镜像，并删除两天前的镜像（镜像依赖快照，快照为收费业务）。使用sdk服务，非api接口
#### rds.py
rds数据库管理基础类，实现了服务器扩展自动添加白名单功能，后被弹性伸缩的功能所替代。囧
#### slb.py
负载均衡接口，弹性伸缩的功能已包含，因此未实现
#### ossbase.py
oss下载文件,主要实现了oss下载目录的方法，（限制，目录内文件包括各个目录，上限为1000个）