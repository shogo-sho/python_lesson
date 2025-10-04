import requests

url = 'https://news.yahoo.co.jp'
response = requests.get(url)

response.text[:500]