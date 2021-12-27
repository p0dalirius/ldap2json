#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name          : analysis.py
# Author             : Podalirius (@podalirius_)
# Date created       : 27 Dec 2022

import json
import readline
import argparse
import sys


class CommandCompleter(object):
    def __init__(self):
        self.options = {
            "searchbase": [],
            "object_by_dn": [],
            "object_by_property_value": [],
            "object_by_property_name": [],
            "help": [],
            "exit": []
        }

    def complete(self, text, state):
        if state == 0:
            if len(text) == 0:
                self.matches = [s for s in self.options.keys()]
            elif len(text) != 0:

                if text.count(' ') == 0:
                    self.matches = [s for s in self.options.keys() if s and s.startswith(text)]
                elif text.count(' ') == 1:
                    command, remainder = text.split(' ', 1)
                    if command in self.options.keys():
                        self.matches = [command + " " + s for s in self.options[command] if s and s.startswith(remainder)]
                    else:
                        pass
                else:
                    self.matches = []
            else:
                self.matches = self.options.keys()[:]
        try:
            return self.matches[state] + " "
        except IndexError:
            return None


readline.set_completer(CommandCompleter().complete)
readline.parse_and_bind('tab: complete')
readline.set_completer_delims('\n')


### Data utils


def dict_get_paths(d):
    paths = []
    for key in d.keys():
        if type(d[key]) == dict:
            paths = [[key] + p for p in dict_get_paths(d[key])]
        else:
            paths.append([key])
    return paths


def dict_path_access(d, path):
    for key in path:
        if key in d.keys():
            d = d[key]
        else:
            return None
    return d


def search_for_property_by_name(d, property, path=[]):
    results = []
    for key in d.keys():
        if type(d[key]) == dict:
            results += search_for_property_by_name(d[key], property, path=path + [key])
        elif property.lower() == key.lower():
            results.append({
                "path": path,
                "property": key,
                "value": d[key]
            })
    return results


def search_for_property_by_value(d, value, path=[]):
    results = []
    for key in d.keys():
        if type(d[key]) == dict:
            results += search_for_property_by_value(d[key], value, path=path + [key])
        elif str(value) == str(d[key]):
            results.append({
                "path": path,
                "property": key,
                "value": d[key]
            })
    return results


def parseArgs():
    parser = argparse.ArgumentParser(description="Description message")
    parser.add_argument("-f", "--file", default=None, required=True, help='LDAP json file.')
    parser.add_argument("-d", "--debug", default=False, action="store_true", help='Debug mode.')
    return parser.parse_args()


if __name__ == '__main__':
    options = parseArgs()

    print("[>] Loading %s ... " % options.file, end="")
    sys.stdout.flush()
    f = open(options.file, "r")
    ldapdata = json.loads(f.read())
    f.close()
    print("done.")

    if options.debug == True:
        print("[debug] ")

    base = []
    running = True
    while running:
        try:
            cmd = input("[\x1b[95m%s\x1b[0m]> " % ','.join(base))
            cmd = cmd.strip().split(" ")

            if cmd[0].lower() == "exit":
                running = False

            elif cmd[0].lower() == "object_by_dn":
                _dn = ' '.join(cmd[1:]).split(',')[::-1]
                _data = dict_path_access(ldapdata, _dn)

                if _data is not None:
                    print(json.dumps(_data, indent=4))

            elif cmd[0].lower() == "object_by_property_name":
                _property_name = ' '.join(cmd[1:])

                _results = []
                _data = dict_path_access(ldapdata, base)

                if _data is not None:
                    _results = search_for_property_by_name(_data, _property_name)

                if len(_results) == 0:
                    print("\x1b[91mNo such property found.\x1b[0m")
                else:
                    for result in _results:
                        print("[\x1b[93m%s\x1b[0m] => \x1b[94m%s\x1b[0m\n - \x1b[92m%s\x1b[0m" % (
                            ','.join(result["path"][::-1] + base[::-1]),
                            result["property"],
                            result["value"],
                        ))

            elif cmd[0].lower() == "object_by_property_value":
                _property_value = ' '.join(cmd[1:])

                _results = []
                _data = dict_path_access(ldapdata, base)
                if _data is not None:
                    _results = search_for_property_by_value(_data, _property_value)

                if len(_results) == 0:
                    print("\x1b[91mNo property with specified value found.\x1b[0m")
                else:
                    for result in _results:
                        print("[\x1b[93m%s\x1b[0m] => \x1b[94m%s\x1b[0m\n - \x1b[92m%s\x1b[0m" % (
                            ','.join(result["path"][::-1] + base[::-1]),
                            result["property"],
                            result["value"],
                        ))

            elif cmd[0].lower() == "searchbase":
                _base = ' '.join(cmd[1:])
                _base = _base.split(',')[::-1]
                base = _base

                if options.debug == True:
                    print("[debug] Changed searchbase to %s" % ','.join(base))

            elif cmd[0].lower() == "help":
                print(" - %-15s %s " % ("searchbase", "Sets the LDAP search base."))
                print(" - %-15s %s " % ("object_by_property_name", "Search for an object containing a property by name in LDAP."))
                print(" - %-15s %s " % ("object_by_property_value", "Search for an object containing a property by value in LDAP."))
                print(" - %-15s %s " % ("object_by_dn", "Search for an object by its distinguishedName in LDAP."))
                print(" - %-15s %s " % ("help", "Displays this help message."))
                print(" - %-15s %s " % ("exit", "Exits the script."))
            else:
                print("Unknown command. Type 'help' for help.")
        except KeyboardInterrupt as e:
            print()
            running = False
        except EOFError as e:
            print()
            running = False
