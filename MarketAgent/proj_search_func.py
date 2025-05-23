
import json
import requests

def search(keywords,url = "https://google.serper.dev/search"):
  """
  Searches for the given keywords using the Serper API
  and returns the search results.
  """

  payload = json.dumps({
    "q": keywords,
    "location": "Ankara, Turkey",
    "gl": "tr"
  })
  headers = {
    'X-API-KEY': '62017f0e33239b07f3c4cacb74ab1f691f8ca5fa',
    'Content-Type': 'application/json'
  }

  response = requests.request("POST", url, headers=headers, data=payload)

  return response.json()

def parse_search_results(results):
  entries = []
  links=[]
  for result in results.get("organic", []):
    title=result.get("title")
    link=result.get("link")
    snippet=result.get("snippet")
    if title and link and snippet:
      entries.append((title, link, snippet ))
      links.append(link)
  return links



