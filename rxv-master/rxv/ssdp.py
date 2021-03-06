#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function

import re
import socket
import requests
from collections import namedtuple
import xml.etree.ElementTree as ET

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin


SSDP_ADDR = '239.255.255.250'
SSDP_PORT = 1900
SSDP_MSEARCH_QUERY = \
   'M-SEARCH * HTTP/1.1\r\n' \
   'MX: 1\r\n' \
   'HOST: 239.255.255.250:1900\r\n' \
   'MAN: "ssdp:discover"\r\n' \
   'ST: upnp:rootdevice\r\n\r\n'

URL_BASE_QUERY = '*/{urn:schemas-yamaha-com:device-1-0}X_URLBase'
CONTROL_URL_QUERY = '***/{urn:schemas-yamaha-com:device-1-0}X_controlURL'
MODEL_NAME_QUERY = "{urn:schemas-upnp-org:device-1-0}device/{urn:schemas-upnp-org:device-1-0}modelName"


RxvDetails = namedtuple("RxvDetails", "ctrl_url model_name")


def discover(timeout=0.5):
    """Crude SSDP discovery. Returns a list of RxvDetails objects
       with data about Yamaha Receivers in local network"""
    socket.setdefaulttimeout(timeout)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.sendto(SSDP_MSEARCH_QUERY.encode("utf-8"), (SSDP_ADDR, SSDP_PORT))

    responses = []
    try:
        while True:
            responses.append(sock.recv(10240))
    except socket.timeout:
        pass

    results = []
    for res in responses:
        m = re.search(r"LOCATION:(.+)", res.decode('utf-8'))
        if not m:
            continue
        url = m.group(1).strip()
        res = rxv_details(url)
        if res:
            results.append(res)

    return results


def rxv_details(location):
    """Looks under given UPNP url, and checks if Yamaha amplituner lives there
       returns RxvDetails if yes, None otherwise"""
    xml = ET.XML(requests.get(location).content)
    url_base_el = xml.find(URL_BASE_QUERY)
    if url_base_el is None:
        return None
    ctrl_url = xml.find(CONTROL_URL_QUERY).text
    model_name = xml.find(MODEL_NAME_QUERY).text
    ctrl_url = urljoin(url_base_el.text, ctrl_url)

    return RxvDetails(ctrl_url, model_name)


if __name__ == '__main__':
    print(discover())
