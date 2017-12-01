import json
import requests
api_url = 'https://maps.googleapis.com/maps/api/place/autocomplete/json'


def filter_places(predictions, filters, place_id=False):
    _ = []
    for p in predictions:
        for f in filters:
            if set(p).issuperset(f):
                _.append(p)

    return _

def sug(query):

    parameters = {
        'key': 'AIzaSyBOT_LUhiW6ckODDTRMXvptoMBuipKLVFM',
        'input': 'نقش جهان',
    }

    _local = [
        set("locality"),
        set("neighborhood"),
        set("political"),
        set("establishment"),
        set("point_of_interest"),
        set("transit_station"),
    ]

    _global = [
        set("geocode")
    ]

    _json = requests.get(api_url, params=parameters).content
    _json = _json.decode('utf-8')
    _json = json.loads(_json)
    if _json['status'] == "ZERO_RESULTS":
        return [], []
    if _json['status'] == "OK":
        return filter_places(_json['predictions'], _local, place_id=True), filter_places(_json['predictions'], _global)
    print('network error')
    return [], []

# do ta array doros mikonim yeki type hayee ke kolii an yeki type haayee ke jozee an
# age jozee yeki bud > [yes, no]
# age jozee chanta dasht va chantash kam bud > [items]
# age jozee hash kheili bud > complete it +
# else age koli dasht > complete it +
# jozE nadarim koli nadarim wtf try again
#"ZERO_RESULTS" > wtf try again