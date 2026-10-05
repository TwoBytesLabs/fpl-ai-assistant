from ddgs import DDGS
import time

try:
    res = DDGS().text("Ivan Toney transfer news loan", max_results=2)
    print(list(res))
except Exception as e:
    print(e)
