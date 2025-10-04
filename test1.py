from npb_data import fetch_table

url = "https://npb.jp/bis/2024/stats/bat_c.html"
df = fetch_table(url)
print(df.columns)
