import requests

url = "https://data.alpaca.markets"

try:
    response = requests.get(url, timeout=(10, 20))
    print("HTTP status:", response.status_code)
    print(response.text[:500])
except Exception as error:
    print(type(error).__name__, error)