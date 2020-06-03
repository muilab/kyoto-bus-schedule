# -*- coding: utf-8 -*-

# 京都市バス停留所情報データパーサー

from html.parser import HTMLParser
from html.entities import name2codepoint

import xml.etree.ElementTree as et
import requests
import traceback


BUS_STOP_INFO_XML = 'http://www2.city.kyoto.lg.jp/kotsu/webguide/xml/busstop_multi.xml'

def parse_bus_stop_info():
    info = None
    try:
        response = requests.get(BUS_STOP_INFO_XML, timeout=5)
        if response.status_code != 200:
            print(response.content)
            return info

        info = []
        root = et.fromstring(response.content)
        stops = root.getchildren()
        for stop in stops:
            bcode = stop.find("bcode").text
            name = stop.find("kanji").text
            yomi = stop.find("kana").text
            en = stop.find("en").text
            address = stop.find("adrs").text
            lat = stop.find("lat").text
            lng = stop.find("lng").text
            elev = stop.find("elev").text

            info.append({
                "id" : bcode,
                "name" : name,
                "yomi" : yomi,
                "en" : en,
                "address" : {
                    "name" : address,
                    "lat" : lat,
                    "lng" : lng,
                    "elev" : elev
                }
            })

    except:
        print(traceback.format_exc())

    return info


class BusStopInfoParser(HTMLParser):

    def __init__(self):
        super().__init__()

        self._pre_schedule_id = False
        self._pre_destination = False
        self._pre_destination_en = False
        self._pre_line_name = False

        self._busstop = ''
        self._line_name = ''
        self._schedule_id = ''
        self._destination = ''
        self._destination_en = ''

        self._lines = []


    def _clear_flags(self):
        self._pre_schedule_id = False
        self._pre_destination = False
        self._pre_destination_en = False
        self._pre_line_name = False


    def set_busstop(self, _name):
        self._busstop = _name

    def get_lines(self):
        return self._lines


    def clear(self):
        self._clear_flags()
        self._lines = []


    def handle_starttag(self, tag, attrs):
        # print("Start tag:", tag)
        for name, value in attrs:
            # print("     attr: {} {}".format(name, value))

            if tag == 'div' and name == 'class' and value == "col-lg-1 col-md-1 col-sm-4 col-xs-4 col-lg-push-8 col-md-push-8 cell-center":
                self._pre_schedule_id = True

            elif tag == 'a' and name == 'href':
                if self._pre_schedule_id is True:
                    self._schedule_id = value

            elif name == 'class' and value == 'keito-name':
                self._pre_line_name = True
                if self._line_name != '':
                    self._line_name += '号系統/'

            elif name == 'class' and value == 'keito-name-small keito-name':
                self._pre_line_name = True
                if self._line_name != '':
                    self._line_name += '号系統/'

            elif name == 'class' and value == 'keito-sub keito-sub-express':
                self._pre_line_name = True
                if self._line_name != '':
                    self._line_name += '号系統/'

            elif name == 'class' and value == 'keito-name keito-name-menu':
                self._pre_line_name = True

            elif name == 'class' and value == "tt-dest dat-dest":
                self._pre_destination = True

            elif name == 'class' and value == "dest-en":
                self._pre_destination_en = True


    def handle_endtag(self, tag):
        # print("End tag  :", tag)
        pass


    def handle_data(self, data):
        # print("Data     :", data)

        if self._pre_line_name is True:
            self._line_name += data
            self._clear_flags()

        elif self._pre_destination is True:
            self._destination = data
            self._clear_flags()

        elif self._pre_destination_en is True:
            self._destination_en = data
            self._clear_flags()

            self._build_line()


    def _build_line(self):
        self._lines.append({
            "id" : self._schedule_id.strip('.htm'),
            "line" : '{}号系統'.format(self._line_name),
            "name" : self._busstop,
            "destination" : self._destination,
            "destination_en" : self._destination_en
        })

        self._line_name = ''
        self._destination = ''
        self._destination_en = ''
