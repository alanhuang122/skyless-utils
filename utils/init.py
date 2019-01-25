#!/usr/bin/python
import json

data = {}

print('loading...')
with open('skyless.dat') as f:
    for line in f:
        temp = json.loads(line)
        data[temp['key']] = temp['value']

with open('../locations.json') as f:
    data['locations'] = json.load(f)

import skyless
skyless.data=data
