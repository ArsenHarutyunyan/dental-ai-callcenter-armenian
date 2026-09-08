import json
import os
import re

from bs4 import BeautifulSoup

INPUT_FILE = "Armenian_Dialects_50050.doc"
OUTPUT_FILE = "app/voice/vocabulary_rag.jsonl"

with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as file:
    content = file.read()

soup = BeautifulSoup(content, "html.parser")

rows = soup.find_all("tr")

seen = set()
items = []

for row in rows:
    cells = row.find_all("td")

    if len(cells) >= 3:
        raw_word = cells[1].get_text(strip=True)
        meaning = cells[2].get_text(strip=True)

        word = re.sub(r"\s*\(տարբերակ\s*\d+\)\s*", "", raw_word).strip()

        if not word or not meaning:
            continue

        key = (word, meaning)

        if key in seen:
            continue

        seen.add(key)

        region = None

        for candidate in ["Շիրակ", "Գյումրի", "Արցախ", "Սյունիք", "Լոռի"]:
            if candidate in meaning:
                region = candidate
                break

        item = {
            "id": len(items) + 1,
            "word": word,
            "meaning": meaning,
            "category": "dialect",
            "region": region,
            "text": (
                f"Բարբառային կամ ժարգոնային բառ՝ {word}։ "
                f"Նշանակությունը՝ {meaning}։ "
                f"Տարածաշրջան՝ {region or 'չնշված'}։"
            ),
        }

        items.append(item)

os.makedirs("app/voice", exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    for item in items:
        file.write(json.dumps(item, ensure_ascii=False) + "\n")

print("Rows found:", len(rows))
print("RAG documents:", len(items))
print("Output:", OUTPUT_FILE)