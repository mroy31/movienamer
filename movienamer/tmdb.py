import json
import urllib.parse
import requests
import logging

TMDB_API_KEY = '4ec9e70a6068fa052f00fcd4c03b6c46'
TMDB_HOST = 'http://api.themoviedb.org/3'


def search(name, lang, year=None):
    logging.debug("TMDB search for {} - {} - {}".format(lang, name, year))
    if not name:
        raise Exception

    endpoint = TMDB_HOST + '/search/movie'
    payload = {'api_key': TMDB_API_KEY, 'query': urllib.parse.quote_plus(name)}
    if year is not None:
        payload['year'] = year
    if lang is not None:
        payload['language'] = lang

    try:
        response = requests.get(endpoint, params=payload, timeout=5)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise Exception

    try:
        result = json.loads(response.text)
        return result['results']
    except ValueError:
        raise Exception
