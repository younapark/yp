# import ConfigParser
#
# class MyParser(ConfigParser.ConfigParser):
#
#     # def __init__(self):
#     #     self.data=self.read('testdata.ini')
#     #
#
#     def as_dict(self):
#         d = dict(self._sections)
#         for k in d:
#             d[k] = dict(self._defaults, **d[k])
#             d[k].pop('__name__', None)
#         return d
#
#     # def getData(self):
#     #     return self.data
#     #
#
#
# if __name__ == '__main__':
#     MyParser.as_dict()

import ConfigParser

cf=ConfigParser.ConfigParser()

cf.read('testdata.ini')

dictionary = {}
for section in cf.sections():
    dictionary[section] = {}
    for option in cf.options(section):
        dictionary[section][option] = cf.get(section, option)

print dictionary