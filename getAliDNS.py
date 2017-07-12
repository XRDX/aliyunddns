# -*- coding: UTF-8 -*-
import json
import ConfigParser

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

