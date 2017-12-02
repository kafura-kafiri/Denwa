from config import models


def search(kw, page, page_size):
    search_selector = {
        "$or":
            [
                {"$text": {
                    "$search": kw,
                }},
                {'title.en': {'$regex': kw}},
                {'title.fa': {'$regex': kw}},
                {'title.compact': {'$regex': kw}},

            ],
    }
    return models.find(
        {
            **search_selector
        }, {"score": {
            "$meta": "textScore"
        }},
    ).sort([(
            "score", {
                "$meta": "textScore"
            }
        )]).skip(
        page_size * (page - 1)
    ).limit(
        page_size
    )