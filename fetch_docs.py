import requests, os

urls = [
    "https://docs.stripe.com/payments.md",
    "https://docs.stripe.com/api.md",
]

os.makedirs("docs", exist_ok=True)
for url in urls:
    name = url.split("/")[-1]
    r = requests.get(url)
    with open(f"docs/{name}", "w", encoding="utf-8") as f:
        f.write(r.text)
    print(f"Saved {name}")