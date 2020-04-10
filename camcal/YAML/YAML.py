# -*- coding: utf-8 -*-
import yaml
import numpy as np
import io


# Define data
data = {'a list': [1, 42, 3.141, 1337, 'help', u'€'],
        'a string': 'bla',
        'another dict': {'foo': 'bar',
                         'key': 'value',
                         'the answer': 42}}

data = {'a':(2345.2424, 242.23423, 2342342.23423)}

# Write YAML file
with io.open('data.yaml', 'w', encoding='utf8') as outfile:
    yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)

# Read YAML file
with open("/home/daniil/camcal/NextStep/data.yaml", 'r') as stream:
    a = yaml.load(stream)

print(a['tl'])

al = a['trd']
print(al)


'''
with open("data.yaml", 'r') as stream:
    try:
        sheet = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)
    print(sheet)
'''
