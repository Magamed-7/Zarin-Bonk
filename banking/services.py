import requests


def get_rates():

    url = (
        'https://api.exchangerate.host/latest'
        '?base=TJS'
        '&symbols=USD,EUR,RUB,TJS'
    )

    try:

        response = requests.get(
            url,
            timeout=5
        )

        data = response.json()

        return data.get(
            'rates',
            {}
        )

    except Exception:

        return {}