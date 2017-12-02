from config import models, keywords
from ast import literal_eval


def add_keyword(kw):
    try:
        result = keywords.update_one(
            {'word': kw},
            {'$inc': {'count': 1}}
        )
        if not result.raw_result['updatedExisting']:
            raise Exception
    except:
        keywords.insert_one({
            'word': kw,
            'count': 1,
        })


def update_compact_titles():
    for model in models.find():
        keys = model['title']['compact']
        _key = ''
        _max = 0
        _count = float('inf')
        for key in keys:
            key = keywords.find_one({'word': key})
            if key['count'] < _count or (key['count'] == _count and len(key['word']) >= _max):
                _max = len(key['word'])
                _count = key['count']
                _key = key['word']
        model['title']['compact'] = _key
        models.save(model)


models.delete_many({})
keywords.delete_many({})
with open('models.txt') as f:
    lines = f.readlines()
    lines = [line.rstrip('\n') for line in lines]
    for line in lines:
        _ = literal_eval(line)
        keys = [key.lower() for key in _['title']['en'].split(' ')]
        if len(keys) > 1:
            keys = [keys[i] + ' ' + keys[i + 1] for i in range(len(keys) - 1)]
        _['title']['compact'] = keys
        for key in keys:
            add_keyword(key)
        models.insert_one(_)
    update_compact_titles()

    for model in models.find():
        print(model)