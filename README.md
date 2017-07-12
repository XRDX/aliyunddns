# 将阿里云dns解析作为ddns使用

#### 原理

定时运行监测脚本，通过访问ip.cn来监测本地的公网ip是否发生更改

如果发现ip发生更改，更新Ali云上的DNS目标地址

#### 步骤

安装阿里云的python SDK

```shell
# apt-get install python-pip
# pip install aliyun-python-sdk-alidns
```

在 [Aliyun Access Key管理控制台](https://ak-console.aliyun.com/#/accesskey)里添加Api访问的 Access Key 

- Access Key ID
- Access Key Secret
- 以及你的阿里云账号ID

将以上内容添加到config.ini文件中

```ini
;config.ini
[keys]
access_key_id = ABCDEFGHIJKLMN
access_key_secret = abcdefghijklmnopqrstuvwxyz
account_id = myaccount@ali.com

[config]
format = json
domainname = qinyv.win
```

使用getAliDNS.py来获取当前的Records信息

```python
import json
import ConfigParser
from datetime import datetime

from aliyunsdkalidns.request.v20150109 import UpdateDomainRecordRequest, DescribeDomainRecordsRequest, \
    DescribeDomainRecordInfoRequest
from aliyunsdkcore import client

cp = ConfigParser.ConfigParser()
cp.read("config.ini")

access_key_id       = cp.get('keys','access_key_id')
access_Key_secret   = cp.get('keys','access_Key_secret')
account_id          = cp.get('keys','account_id')

domain_name         = cp.get('config', 'DomainName')
record_format       = cp.get('config', 'format')


def check_records(dns_domain, rc_format):
    clt = client.AcsClient(access_key_id, access_Key_secret, 'cn-hangzhou')
    request = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
    request.set_DomainName(dns_domain)
    request.set_accept_format(rc_format)
    result = clt.do_action_with_exception(request)
    print result

if __name__ == "__main__":
    check_records(domain_name, record_format)

```

如果一切正常，运行后输出类似于一下信息

```json
{
  "PageNumber":1,
  "TotalCount":5,
  "PageSize":20,
  "RequestId":"xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx",
  "DomainRecords":{
    "Record":[
      {
        "RR":"@",
        "Status":"ENABLE",
        "Value":"111.111.111.111",
        "RecordId":"1234567878099",
        "Type":"A",
        "DomainName":
        "qinyv.win",
        "Locked":false,
        "Line":"default",
        "TTL":"600"
      },
      {
        "RR":"www",
        "Status":"ENABLE",
        "Value":"111.111.111.111",
        "RecordId":"1234567878099",
        "Type":"A",
        "DomainName":"qinyv.win",
        "Locked":false,
        "Line":"default",
        "TTL":"600"},
    ]
  }
}
```

将需要修改的Records信息添加到config.ini文件，添加后仍能够执行getAliDNS.py来获取最新的信息

```ini
;config.ini
[keys]
access_key_id = ABCDEFGHIJKLMN
access_key_secret = abcdefghijklmnopqrstuvwxyz
account_id = myaccount@ali.com

[config]
ip = 111.111.111.111
format = json
domainname = qinyv.win
type = A
ttl = 600

[@]
recordid = 1234567878099

[www]
recordid = 1234567878000

```

使用updateAliDNS.py来检测本机的公网ip地址是否发生变动

```python
# -*- coding: UTF-8 -*-

import json
import re
import os
import sys
import ConfigParser
from datetime import datetime

from aliyunsdkalidns.request.v20150109 import UpdateDomainRecordRequest, DescribeDomainRecordsRequest, \
    DescribeDomainRecordInfoRequest
from aliyunsdkcore import client

cp = ConfigParser.ConfigParser()
cp.read("config.ini")
current_ip = cp.get('config', "ip")

access_key_id       = cp.get('keys','access_key_id')
access_Key_secret   = cp.get('keys','access_Key_secret')
account_id          = cp.get('keys','account_id')
 
rc_format       = cp.get('config', 'Format')
rc_domain       = cp.get('config', 'DomainName')
rc_type         = cp.get('config', 'Type')
rc_ttl          = cp.get('config', 'TTL')

rc1_rr = '@'
rc1_id = cp.get(rc1_rr, 'RecordId')
rc2_rr = 'www'
rc2_id = cp.get(rc2_rr, 'RecordId')
 
def my_ip():
    get_ip_method = os.popen('curl -s ip.cn')
    get_ip_responses = get_ip_method.readlines()[0]
    get_ip_pattern = re.compile(r'\d+\.\d+\.\d+\.\d+')
    get_ip_value = get_ip_pattern.findall(get_ip_responses)[0]
    return get_ip_value

def update_dns(dns_rc_rr, dns_rc_id, dns_value):
    clt = client.AcsClient(access_key_id, access_Key_secret, 'cn-hangzhou')
    request = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
    request.set_RR(dns_rc_rr)
    request.set_Type(rc_type)
    request.set_Value(dns_value)
    request.set_RecordId(dns_rc_id)
    request.set_TTL(rc_ttl)
    request.set_accept_format(rc_format)
    result = clt.do_action_with_exception(request)
    return result
 
def write_to_config(rc_value):
    cp.set("config", "ip", rc_value)
    with open("config.ini","w") as f:
        cp.write(f)

def log(msg):
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_script_path = sys.path[7]
    log_file = current_script_path + '/' + 'aliyun_ddns_log.txt'
    with open(log_file, 'a') as f:
        f.write(time_now + ' ' + str(msg) + '\n')
    return

if __name__ == "__main__":
    rc_value = my_ip()
    if current_ip != rc_value:
        update_dns(rc1_rr, rc1_id, rc_value)
        update_dns(rc2_rr, rc2_id, rc_value)
        write_to_config(rc_value)
        log(rc_value)
    else:
        log("-_-")
```

最后，使用crontab来定期执行该任务来达到监测公网ip地址变动的效果

```shell
crontab -e
*/5 * * * * $python ~/ddns/updateAliDNS.py
```

