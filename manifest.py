import requests

MANIFEST_URL = "http://137.131.178.229:8080/manifest"

def load_manifest():
    response = requests.get(MANIFEST_URL)
    response.raise_for_status()
    return response.json()
