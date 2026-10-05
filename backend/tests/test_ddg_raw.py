import requests
url = "https://html.duckduckgo.com/html/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
params = {"q": "Ivan Toney transfer news loan"}
response = requests.get(url, headers=headers, params=params, timeout=10)
print(response.text)
