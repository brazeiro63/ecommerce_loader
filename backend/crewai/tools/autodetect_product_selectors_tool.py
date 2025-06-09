import re
import json
from crewai.tools import tool
from playwright.sync_api import sync_playwright

@tool("Auto Detect Product Selectors")
def autodetect_product_selectors(url: str) -> str:
    """
    Analisa uma página de e-commerce e sugere seletores para identificar cards de produto,
    nome, preço e link, retornando como JSON em string.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='networkidle')
        
        candidate_tags = ['div', 'li', 'article', 'section']
        candidates = []
        for tag in candidate_tags:
            elements = page.query_selector_all(tag)
            if 10 < len(elements) < 200:
                candidates.append((tag, elements, len(elements)))
        if not candidates:
            browser.close()
            return json.dumps({"erro": "Nenhum possível card de produto detectado."}, ensure_ascii=False)
        
    card_tag, card_elements, card_count = sorted(candidates, key=lambda x: x[2], reverse=True)[0]
    # Tenta encontrar uma classe marcante do card para sugerir
    card_selector = None
    for card in card_elements:
        card_class = card.get_attribute("class")
        if card_class:
            card_selector = f".{card_class.strip().replace(' ','.')}"
            break
    if not card_selector:
        card_selector = card_tag  # fallback para só o nome da tag
    
    name_selector, price_selector, link_selector = None, None, None
    for card in card_elements[:3]:
        children = card.query_selector_all("*")
        for child in children:
            try:
                tag_name = child.evaluate("el => el.tagName").lower()
                if tag_name not in candidate_tags + ['a', 'span', 'h2', 'h3', 'h4', 'p', 'strong']:
                    continue
                text = (child.inner_text() or "").strip()
            except Exception:
                continue
            
            if not name_selector and 5 < len(text) < 100:
                name_class = child.get_attribute("class")
                if name_class:
                    name_selector = f".{name_class.strip().replace(' ','.')}"
            if not price_selector and re.search(r'R\$\s?\d', text):
                price_class = child.get_attribute("class")
                if price_class:
                    price_selector = f".{price_class.strip().replace(' ','.')}"
            if not link_selector:
                href = child.get_attribute("href")
                if href:
                    link_class = child.get_attribute("class")
                    if link_class:
                        link_selector = f".{link_class.strip().replace(' ','.')}"
        if name_selector and price_selector and link_selector:
            break
    browser.close()
    result = {
        "card_tag": card_tag,
        "card_count": card_count,
        "suggested_selectors": {
            "card": card_selector,
            "name": name_selector,
            "price": price_selector,
            "link": link_selector
        }
    }
    return json.dumps(result, ensure_ascii=False, indent=2)
