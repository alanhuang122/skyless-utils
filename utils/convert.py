import json

with open('skyless.dat', 'w') as f:
    for name in ['areas', 'bargains', 'domiciles', 'events', 'exchanges', 'personae', 'prospects', 'qualities', 'settings']:
        with open(f'{name}.txt') as g:
                data = json.loads(g.read())
                for line in data:
                    f.write(f"{{\"key\": \"{name}:{line['Id']}\", \"value\": {json.dumps(line)}}}\n")
