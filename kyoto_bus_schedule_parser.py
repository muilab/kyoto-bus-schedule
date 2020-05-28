# -*- coding: utf-8 -*-

# 京都市バス時刻表データパーサー

from html.parser import HTMLParser
from html.entities import name2codepoint

class BusScheduleParser(HTMLParser):

    def __init__(self):
        super().__init__()

        self._pre_weekday_time = False
        self._weekday_time = False

        self._pre_saturday_time = False
        self._saturday_time = False

        self._pre_holiday_time = False
        self._holiday_time = False

        self._note_block = False

        self._current_hour = 0

        self._name = ''
        self._data_bkmk = ''
        self._busstop = ''
        self._line_group = 0
        self._destination = ''

        self._weekday_schedule = []
        self._saturday_schedule = []
        self._holiday_schedule = []
        self._notes = {}

        self.schedule = {}


    def _clear_flags(self):
        self._pre_weekday_time = False
        self._weekday_time = False

        self._pre_saturday_time = False
        self._saturday_time = False

        self._pre_holiday_time = False
        self._holiday_time = False

        self._note_block = False


    def get_schedule(self):
        return self.schedule


    def clear(self):
        self._clear_flags()
        self._weekday_schedule = []
        self._saturday_schedule = []
        self._holiday_schedule = []
        self._notes = {}
        self.schedule = {}



    def handle_starttag(self, tag, attrs):
        # print("Start tag:", tag)
        for name, value in attrs:
            # print("     attr: {} {}".format(name, value))

            if tag == 'h3' and name == "id" and value.startswith('h'):
                self._pre_weekday_time = True
                self._current_hour = int(value[1:])

            elif tag == 'h3' and name == "id" and value.startswith('d'):
                self._pre_saturday_time = True
                self._current_hour = int(value[1:])

            elif tag == 'h3' and name == "id" and value.startswith('k'):
                self._pre_holiday_time = True
                self._current_hour = int(value[1:])

            elif tag == 'li' and name == "class" and value == "note-sign":
                self._note_block = True

            elif name == "data-bkmk-str":
                self._parse_busstopinfo(value)

            elif name == "data-bkmk-num":
                self._data_bkmk = value


    def handle_endtag(self, tag):
        # print("End tag  :", tag)
        if tag == 'h3':
            if self._pre_weekday_time is True:
                self._weekday_time = True
                self._pre_weekday_time = False

            elif self._pre_saturday_time is True:
                self._saturday_time = True
                self._pre_saturday_time = False

            elif self._pre_holiday_time is True:
                self._holiday_time = True
                self._pre_holiday_time = False

        elif tag == 'td' or tag == 'tr':
            if self._weekday_time or self._saturday_time or self._holiday_time:
                self._clear_flags()

        elif tag == 'li':
            if self._note_block:
                self._clear_flags()

        elif tag == 'html':
            self._build_schedule()


    def handle_data(self, data):
        # print("Data     :", data)

        if self._weekday_time is True:
            if data is not None:
                times = self._parse_times(data)

                for t in times:
                    self._weekday_schedule.append(t)

            self._clear_flags()

        elif self._saturday_time is True:
            if data is not None:
                times = self._parse_times(data)

                for t in times:
                    self._saturday_schedule.append(t)

            self._clear_flags()

        elif self._holiday_time is True:
            if data is not None:
                times = self._parse_times(data)

                for t in times:
                    self._holiday_schedule.append(t)

            self._clear_flags()

        elif self._note_block is True:
            if data.startswith('( )'):
                self._notes["()"] = data.strip('( )印は')

            elif data.startswith('*'):
                self._notes["*"] = data.strip('*印は')

            elif data.startswith('△'):
                self._notes["△"] = data.strip('△印は')

            else:
                self._notes["."] = data


    def _parse_times(self, _data):
        _times = _data.split(' ')
        times = []
        for t in _times:
            if t.startswith('('):
                times.append({
                    "t" : '{}:{}'.format(str(self._current_hour).zfill(2), t.strip('()').zfill(2)),
                    "note" : "()"
                })

            elif t.startswith('*'):
                times.append({
                    "t" : '{}:{}'.format(str(self._current_hour).zfill(2), t.strip('*').zfill(2)),
                    "note" : "*"
                })

            elif t.startswith('△'):
                times.append({
                    "t" : '{}:{}'.format(str(self._current_hour).zfill(2), t.strip('△').zfill(2)),
                    "note" : "△"
                })

            else:
                times.append({
                    "t" : '{}:{}'.format(str(self._current_hour).zfill(2), t.zfill(2)),
                    "note" : " "
                })

        return times


    def _parse_busstopinfo(self, _data):
        self._name = _data
        
        datas = _data.split(' ')
        self._busstop = datas[0]
        self._line_group = datas[2]
        self._destination = datas[4] if len(datas) == 5 else datas[3]


    def _build_schedule(self):
        self._add_note()

        id = self._data_bkmk.strip('kmtb-b').replace('-', '')
        self.schedule["id"] = id
        self.schedule["bkmk"] = self._data_bkmk
        self.schedule["name"] = self._name
        self.schedule["busstop"] = self._busstop
        self.schedule["line"] = self._line_group
        self.schedule["destination"] = self._destination
        self.schedule["notes"] = self._notes
        self.schedule["weekday"] = self._weekday_schedule
        self.schedule["saturday"] = self._saturday_schedule
        self.schedule["holiday"] = self._holiday_schedule


    def _add_note(self):
        for note in self._notes:
            content = self._notes[note]
            for t in self._weekday_schedule:
                if t['note'] == note:
                    t['note'] = content

            for t in self._saturday_schedule:
                if t['note'] == note:
                    t['note'] = content

            for t in self._holiday_schedule:
                if t['note'] == note:
                    t['note'] = content



if __name__ == "__main__":

    import traceback
    import sys
    import os
    import argparse
    import json
    import shutil

    try:
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument("path")
        args = arg_parser.parse_args()

        path_to_dir = args.path
        print(path_to_dir)

        if os.path.isdir(path_to_dir) is False:
            raise Exception("ディレクトリへのパスを指定してください")

        current_dir = os.path.dirname(os.path.abspath(__file__))
        out_dir = os.path.normpath(os.path.join(current_dir, './json'))


        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)

        os.mkdir(out_dir)

        # parse schedule data
        print('>>> start parse schedule data >>>')
        parser = BusScheduleParser()
        files = os.listdir(path_to_dir)
        for file in files:
            if file[0].isdigit() is False:
                continue

            parser.clear()

            full_path = os.path.normpath(os.path.join(path_to_dir, './{}'.format(file)))
            with open(full_path, 'r') as f:
                print('  -- {}'.format(file))
                parser.feed(f.read())

            schedule = parser.get_schedule()
            # print(schedule)

            out_file = os.path.normpath(os.path.join(out_dir, '{}.json'.format(schedule["id"])))
            with open(out_file, 'w') as f:
                f.write(json.dumps(schedule, ensure_ascii=False))

        parser.clear()
        print('<<< finished parse schedule data <<<')

        # parse bus stop info
        print('>>> start parse bus stop info >>>')
        from kyoto_bus_stop_parser import parse_bus_stop_info, BusStopInfoParser

        bus_stop = parse_bus_stop_info()
        # print(bus_stop)

        busStopParser = BusStopInfoParser()
        for bs in bus_stop:
            busStopParser.clear()

            id = bs["id"]
            menu_file = 'menu{}.htm'.format(id)
            menu_file_path = os.path.normpath(os.path.join(path_to_dir, menu_file))
            if os.path.exists(menu_file_path):
                with open(menu_file_path, 'r') as f:
                    print('  -- {}'.format(menu_file))
                    busStopParser.set_busstop(bs["name"])
                    busStopParser.feed(f.read())

            else:
                continue


            lines = busStopParser.get_lines()
            bs["lines"] = lines

        busStopParser.clear()


        bus_stop_file = os.path.normpath(os.path.join(out_dir, 'busstop.json'))
        with open(bus_stop_file, 'w') as f:
            f.write(json.dumps(bus_stop, ensure_ascii=False))


        print('<<< finished parse bus stop info <<<')

    except:
        print(traceback.format_exc())


    sys.exit(0)
