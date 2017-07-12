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
rc3_rr = 'blog'
rc3_id = cp.get(rc3_rr, 'RecordId')
 
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
    log_file = current_script_path + '/' + 'aliyun_ddns.log'
    with open(log_file, 'a') as f:
        f.write(time_now + ' ' + str(msg) + '\n')
    return
 

if __name__ == "__main__":
    rc_value = my_ip()
    if current_ip != rc_value:
        update_dns(rc1_rr, rc1_id, rc_value)
        update_dns(rc2_rr, rc2_id, rc_value)
        update_dns(rc3_rr, rc3_id, rc_value)
        write_to_config(rc_value)
        log(rc_value)
    else:
        log("-_-")
