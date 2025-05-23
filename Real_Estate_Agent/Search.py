import json
import requests
from KeywordAgent import parse_keywords



def search(keywords,url = "https://google.serper.dev/search"):

  payload = json.dumps({
    "q": keywords,
    "location": "Ankara, Turkey",
    "gl": "tr",
    "num":7
  })
  headers = {
    'X-API-KEY': '62017f0e33239b07f3c4cacb74ab1f691f8ca5fa',
    'Content-Type': 'application/json'
  }

  response = requests.request("POST", url, headers=headers, data=payload)

  return response.json()
def parse_search_links(results):
  links=[]
  for result in results.get("organic", []):
    link=result.get("link")
    if link :
      links.append(link)
  return links

def filter_links(links):
    return [link for link in links if not any(site in link.lower() for site in ["sahibinden.com", "facebook.com", "tiktok.com"])]

