import configparser
import socket
import requests
import json
import logging

import time

log_filename = "logging.log"
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s [%(funcName)s: %(filename)s, %(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filemode='a')
'''

'''
global IP4TESTADDR, IP6TESTADDR, INTERVAL, ENABLELOCALIPv4, ENABLEIPv6, AUTHKEY, ZONEID, IPv4ID, IPv6ID, AUTHEMAIL, DOMAIN4, DOMAIN6
global now_ipv4, now_ipv6
def readconfig():
    global IP4TESTADDR, IP6TESTADDR, INTERVAL, ENABLELOCALIPv4, ENABLEIPv6, AUTHKEY, ZONEID, IPv4ID, IPv6ID, AUTHEMAIL, DOMAIN4, DOMAIN6
    config = configparser.ConfigParser()
    config.read("config.ini")
    IP4TESTADDR = config['Base']['ip4testaddr'].split(',')
    IP6TESTADDR = config['Base']['ip6testaddr'].split(',')
    INTERVAL = config['Base']['interval']
    ENABLELOCALIPv4 = config['Base']['enablelocalipv4']
    ENABLEIPv6 = config['Base']['enableipv6']
    AUTHKEY = config['CloudFlare']['authkey']
    ZONEID = config['CloudFlare']['zoneid']
    IPv4ID = config['CloudFlare']['ipv4id']
    IPv6ID = config['CloudFlare']['ipv6id']
    AUTHEMAIL = config['CloudFlare']['authemail']
    DOMAIN4 = config['CloudFlare']['domain4']
    DOMAIN6 = config['CloudFlare']['domain6']


def getip4(retry=0):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((IP4TESTADDR[retry], 0))
        ip = s.getsockname()[0]
        return ip
    except:
        retry += 1
        if retry >= len(IP4TESTADDR):
            logging.error("Cannot connect to IPv4 local network. You should configure the IP4TESTADDR first!")
            return None
        else:
            return getip4(retry)
    finally:
        s.close()


def getip6(retry=0):
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        s.connect((IP6TESTADDR[retry], 0))
        ip = s.getsockname()[0]
        return ip
    except:
        retry += 1
        if retry >= len(IP6TESTADDR):
            logging.error("Cannot connect to IPv6 network. You should configure the IP6TESTADDR first, or you don't "
                          "have any valid IPv6 address")
            return None
        else:
            return getip6(retry)
    finally:
        s.close()


def cfupdate():
    global now_ipv4, now_ipv6
    ipv4 = getip4()
    logging.debug(ipv4)
    ipv6 = getip6()
    logging.debug(ipv6)
    if ipv4 is not None and ipv4 != now_ipv4 and ENABLELOCALIPv4 == "1":
        url = "https://api.cloudflare.com/client/v4/zones/" + ZONEID + "/dns_records/" + IPv4ID
        data = {'type': 'A', 'name': DOMAIN4, 'content': ipv4, 'ttl': 300, 'proxied': False}
        headers = {"X-Auth-Email": AUTHEMAIL, "X-Auth-Key": AUTHKEY, "Content-Type": "application/json"}
        resp = requests.put(url, json.dumps(data), headers=headers).json()
        logging.debug(resp)
        if resp['success']:
            logging.info("IPv4(" + ipv4 + "-->" + DOMAIN4 + ") DNS refresh success!")
            now_ipv4 = ipv4
        else:
            logging.error("IPv4(" + ipv4 + "-->" + DOMAIN4 + ") DNS refresh failed--" + resp['errors'][0]['message'])

    if ipv6 is not None and ipv6 != now_ipv6 and ENABLEIPv6 == "1":
        url = "https://api.cloudflare.com/client/v4/zones/" + ZONEID + "/dns_records/" + IPv6ID
        data = {'type': 'AAAA', 'name': DOMAIN6, 'content': ipv6, 'ttl': 300, 'proxied': False}
        headers = {"X-Auth-Email": AUTHEMAIL, "X-Auth-Key": AUTHKEY, "Content-Type": "application/json"}
        resp = requests.put(url, json.dumps(data), headers=headers).json()
        logging.debug(resp)
        if resp['success']:
            logging.info("IPv6(" + ipv6 + "-->" + DOMAIN6 + ") DNS refresh success!")
            now_ipv6 = ipv6
        else:
            logging.error("IPv6(" + ipv6 + "-->" + DOMAIN6 + ") DNS refresh failed--" + resp['errors'][0]['message'])


if __name__ == "__main__":
    readconfig()
    global now_ipv4, now_ipv6
    now_ipv4 = "127.0.0.1"
    now_ipv6 = "::1"
    while True:
        cfupdate()
        time.sleep(int(INTERVAL))
