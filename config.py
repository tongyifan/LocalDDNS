import configparser
import json

import requests

global config


def readconfig():
    global config
    config = configparser.ConfigParser()
    config.read("config.ini")


def editaddr(IP4TESTADDR, IP6TESTADDR):
    print()
    print("Your IPv4 test website/IP: " + str(IP4TESTADDR))
    print("Your IPv6 test website/IP: " + str(IP6TESTADDR))
    print()
    print("1.add IPv4 test website/IP")
    print("2.add IPv6 test website/IP")
    print("3.delete IPv4 test website/IP")
    print("4.delete IPv6 test website/IP")
    c1 = input("Please choose one or just click ENTER to skip:")
    if c1 == "1":
        add = input("Write some website/IP for IPv4, split by [,]:")
        for a in add.split(','):
            if a.lstrip().lower() not in IP4TESTADDR:
                IP4TESTADDR.append(a.lstrip().lower())
    elif c1 == "2":
        add = input("Write some website/IP for IPv6, split by [,]:")
        for a in add.split(','):
            if a.lstrip().lower() not in IP6TESTADDR:
                IP6TESTADDR.append(a.lstrip().lower())
    elif c1 == "3":
        i = 1
        for d in IP4TESTADDR:
            print(str(i) + '.' + d)
            i += 1
        delete = input("Choose the number of website/IP to delete, split by [,]:")
        todel = []
        for d in delete.split(','):
            try:
                if 1 <= int(d) < i:  # delete invalid value users input
                    todel.append(int(d))
            except:
                continue
        todel = sorted(todel, reverse=True)
        for td in todel:
            del IP4TESTADDR[td - 1]
    elif c1 == "4":
        i = 1
        for d in IP6TESTADDR:
            print(str(i) + '.' + d)
            i += 1
        delete = input("Choose the number of website/IP to delete, split by [,]:")
        todel = []
        for d in delete.split(','):
            try:
                if 1 <= int(d) < i:  # delete invalid value users input
                    todel.append(int(d))
            except:
                continue
        todel = sorted(todel, reverse=True)
        for td in todel:
            del IP6TESTADDR[td - 1]
    else:
        return IP4TESTADDR, IP6TESTADDR
    print("Your IPv4 test website/IP: " + str(IP4TESTADDR))
    print("Your IPv6 test website/IP: " + str(IP6TESTADDR))
    r = input("Do you want to edit others?(y/n):")
    if r != "n":
        return editaddr(IP4TESTADDR, IP6TESTADDR)
    else:
        return IP4TESTADDR, IP6TESTADDR


def checkrecord(iptype, name):
    global config
    url = "https://api.cloudflare.com/client/v4/zones/" + config['CloudFlare']['ZONEID'] + "/dns_records"
    headers = {"X-Auth-Email": config['CloudFlare']['AUTHEMAIL'], "X-Auth-Key": config['CloudFlare']['AUTHKEY'],
               "Content-Type": "application/json"}
    params = {"type": iptype, "name": name}
    resp = requests.get(url, params=params, headers=headers).json()
    return resp


def createdrecord(iptype, name):
    global config
    url = "https://api.cloudflare.com/client/v4/zones/" + config['CloudFlare']['ZONEID'] + "/dns_records"
    headers = {"X-Auth-Email": config['CloudFlare']['AUTHEMAIL'], "X-Auth-Key": config['CloudFlare']['AUTHKEY'],
               "Content-Type": "application/json"}
    data = {"type": iptype, "name": name, "content": "127.0.0.1", "ttl": 1, "proxied": False}
    resp = requests.post(url, data=json.dumps(data), headers=headers).json()
    return resp


def configDDNS():
    global config
    print(" ################################################################################")
    print("#                                   LocalDDNS                                    #")
    print("#  This Python application implements DDNS in Local Area Network.                #")
    print("#  It check your IPv4 and IPv6 address automatically and update them.            #")
    print("#  It uses CloudFlare DNS API, so you should have a domain use CloudFlare DNS.   #")
    print("#  If there are some bugs, please contact me.                                    #")
    print("#  Author: TongYifan                                                             #")
    print("#  Email: tongyfan@gmail.com                                                     #")
    print("#  Version: 0.1.20180429                                                         #")
    print(" ################################################################################")
    print()
    input("Press any key to start configure...")
    print(" ################################################################################")
    print("#                              1/2 Base configure                                #")
    print(" ################################################################################")
    print("Those followed website/IP will be connected for test to get your local IPv4 address, so you should add "
          "some website/IP what can be connected in your network environment(such as your router's gateway, "
          "a DNS server, etc.)")
    IP4TESTADDR = config['Base']['IP4TESTADDR'].split(',')
    IP6TESTADDR = config['Base']['IP6TESTADDR'].split(',')
    IP4TESTADDR, IP6TESTADDR = editaddr(IP4TESTADDR, IP6TESTADDR)
    config['Base']['IP4TESTADDR'] = ",".join(IP4TESTADDR)
    config['Base']['IP6TESTADDR'] = ",".join(IP6TESTADDR)
    print("If you keep this app running, it will update DNS records every few seconds.")
    c2 = input("The interval to update DNS(second, DEFAULT = " + config['Base']['INTERVAL'] + "):")
    if c2 != "":
        try:
            config['Base']['INTERVAL'] = int(c2)
        except:
            print("Invalid input, use default.")

    c3 = input("Do you want to update Local IPv4?(y/n, DEFAULT=Yes):")
    if c3 != 'n':
        config['Base']['ENABLELOCALIPv4'] = "1"
    else:
        config['Base']['ENABLELOCALIPv4'] = "0"
    c4 = input("Do you want to update IPv6?(y/n, DEFAULT=Yes):")
    if c4 != 'n':
        config['Base']['ENABLEIPv6'] = "1"
    else:
        config['Base']['ENABLEIPv6'] = "0"

    print(" ################################################################################")
    print("#                          2/2 CloudFlare configure                              #")
    print(" ################################################################################")
    print("In this section, you need to fill up some secret key from CloudFlare.")
    print("These key will save in [config.ini] and WILL NOT UPLOAD TO THE INTERNET.")
    print("In fact, you also can't upload it online, it will make your domain stolen.")
    print("If you don't know where to find these key, read the README in Github.")
    config['CloudFlare']['ZONEID'] = input("Please input zone_id of the domain you used:")
    config['CloudFlare']['AUTHKEY'] = input("Please input your API key:")
    config['CloudFlare']['AUTHEMAIL'] = input("Please input your email in CloudFlare:")
    print("Tips: One name can have two or more records.")
    print("For example, you can use ddns.example.com for both IPv4(A) and IPv6(AAAA) record")
    config['CloudFlare']['DOMAIN4'] = input("Please input DNS name for IPv4(eg. ddns.example.com)")
    config['CloudFlare']['DOMAIN6'] = input("Please input DNS name for IPv6(eg. ddns.example.com)")

    # check IPv6 domain name and get ID
    print("Searching the record in Type [A], name [" + config['CloudFlare']['DOMAIN4'] + "]")
    result = checkrecord("A", config['CloudFlare']['DOMAIN4'])
    if result['result_info']['count'] == 1:
        print("Check Type [A], domain name [" + config['CloudFlare']['DOMAIN4'] + "] successfully!")
        config['CloudFlare']['IPv4ID'] = result['result'][0]['id']
    elif result['result_info']['count'] == 0:
        c5 = input("Nothing matched! Do you want to create one?(y/n, DEFAULT=n):")
        if c5 == "y":
            create = createdrecord("A", config['CloudFlare']['DOMAIN4'])
            if create['success']:
                config['CloudFlare']['IPv4ID'] = create['result'][0]['id']
            else:
                print(create['errors'][0]['message'])
        else:
            config['CloudFlare']['IPv4ID'] = ""
    elif result['result_info']['count'] > 1:
        i = 1
        for j in result['result']:
            print(str(i) + '.' + j)
            i += 1
        c6 = input("Please choose one:")
        if 0 < c6 < i:
            config['CloudFlare']['IPv4ID'] = result['result'][c6]['id']
        else:
            print("Invalid input, use the first")
            config['CloudFlare']['IPv4ID'] = result['result'][0]['id']

    # check IPv6 domain name and get ID
    print("Searching the record in Type [AAAA], name [" + config['CloudFlare']['DOMAIN6'] + "]")
    result = checkrecord("AAAA", config['CloudFlare']['DOMAIN6'])
    if result['result_info']['count'] == 1:
        print("Check Type [AAAA], domain name [" + config['CloudFlare']['DOMAIN6'] + "] successfully!")
        config['CloudFlare']['IPv6ID'] = result['result'][0]['id']
    elif result['result_info']['count'] == 0:
        c7 = input("Nothing matched! Do you want to create one?(y/n, DEFAULT=n):")
        if c7 == "y":
            create = createdrecord("AAAA", config['CloudFlare']['DOMAIN6'])
            if create['success']:
                config['CloudFlare']['IPv6ID'] = create['result'][0]['id']
            else:
                print(create['errors'][0]['message'])
        else:
            config['CloudFlare']['IPv6ID'] = ""
    elif result['result_info']['count'] > 1:
        i = 1
        for j in result['result']:
            print(str(i) + '.' + j)
            i += 1
        c8 = input("Please choose one:")
        if 0 < c8 < i:
            config['CloudFlare']['IPv6ID'] = result['result'][c8]['id']
        else:
            print("Invalid input, use the first")
            config['CloudFlare']['IPv6ID'] = result['result'][0]['id']
    config.write(open("config.ini", "w"))
    print("All Complete! You can enjoy LocalDDNS now!")
    exit()


if __name__ == "__main__":
    readconfig()
    configDDNS()
