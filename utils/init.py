#!/usr/bin/python
import json

data = {}

print('loading...')
with open('skyless.dat') as f:
    for line in f:
        temp = json.loads(line)
        data[temp['key']] = temp['value']

import skyless
skyless.data=data
