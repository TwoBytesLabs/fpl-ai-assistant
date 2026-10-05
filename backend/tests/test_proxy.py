import requests
import urllib.parse
url = "https://html.duckduckgo.com/html/"
params = {"q": "Ivan Toney transfer news loan"}
target_url = url + "?" + urllib.parse.urlencode(params)
proxy_url = f"https://api.allorigins.win/get?url={urllib.parse.quote(target_url)}"

try:
    response = requests.get(proxy_url, timeout=10)
    data = response.json()
    if 'contents' in data:
        print(data['contents'][:500])
        if "anomaly-modal" in data['contents']:
            print("Still getting captcha via proxy!")
        else:
            print("Success bypassing captcha via proxy!")
except Exception as e:
    print(e)
