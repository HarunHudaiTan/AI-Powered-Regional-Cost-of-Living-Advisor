import json
import requests


class Search():
  def search(self,keywords,url = "https://google.serper.dev/search"):
    # print(keywords)
    payload = json.dumps({
      "q": keywords,
      "gl": "tr",
    })
    headers = {
      'X-API-KEY': '62017f0e33239b07f3c4cacb74ab1f691f8ca5fa',
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    response_json=json.loads(response.text)
    return response_json

  def parse_search_links(self,results):
    links=[]
    for result in results.get("organic", []):
      link=result.get("link")
      if link :
        links.append(link)
    return links

  def filter_links(self,links):
      return [link for link in links if not any(site in link.lower() for site in ["sahibinden.com", "facebook.com", "tiktok.com"])]
