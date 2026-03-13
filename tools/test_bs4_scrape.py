from bs4 import BeautifulSoup
import re

with open('f1_2026.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

# Search for any tag that contains 'schedule-card' in class
cards = soup.find_all(lambda tag: tag.name == 'a' and any('schedule-card' in c for c in tag.get('class', [])))
print(f"Found {len(cards)} schedule cards")

for i, card in enumerate(cards):
    href = card.get('href', '')
    text = card.get_text(separator='|', strip=True)
    print(f"Card {i}: {href} | {text[:150]}...")
