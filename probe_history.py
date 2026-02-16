import requests
import re
import json

def probe():
    # 1. Try historical API
    print("Probing historical API...")
    try:
        resp = requests.get("https://api.tickertape.in/mmi/history", headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if resp.status_code == 200:
            print("Found history endpoint!")
            print(resp.json())
        else:
            print(f"History endpoint failed: {resp.status_code}")
    except Exception as e:
        print(f"History endpoint error: {e}")

    # 2. Inspect HTML
    print("\nFetching main page HTML...")
    try:
        resp = requests.get("https://www.tickertape.in/market-mood-index", headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            html = resp.text
            # Look for JSON-like structures or "history" keywords
            # specifically looking for Next.js data
            match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
            if match:
                data = json.loads(match.group(1))
                print("Found NEXT_DATA!")
                # traverse to find MMI history
                # printing keys to avoid huge output
                print(data.keys())
                # Just checking if we can find 'mmi' or 'history' in the props
                if 'props' in data:
                    print(data['props'].keys())
                    if 'pageProps' in data['props']:
                        print(data['props']['pageProps'].keys())
            else:
                print("No NEXT_DATA found.")
        else:
            print(f"Main page fetch failed: {resp.status_code}")
    except Exception as e:
        print(f"Main page fetch error: {e}")

if __name__ == "__main__":
    probe()
