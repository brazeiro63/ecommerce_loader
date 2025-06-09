import json
from collections import Counter
from crewai.tools import tool
from playwright.sync_api import sync_playwright

@tool("Count Repeated HTML Structures")
def count_repeated_html_structures(url: str) -> str:
    """
    Analisa uma página HTML e retorna as estruturas de tags+classes mais repetidas,
    ajudando a identificar listas e grupos de elementos semelhantes (ex: cards, banners).
    Retorna JSON com os 10 mais comuns.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='networkidle')

        # Vamos olhar para as tags mais comuns em cards/listas
        candidate_tags = ['div', 'li', 'article', 'section']

        structure_counter = Counter()

        for tag in candidate_tags:
            elements = page.query_selector_all(tag)
            for el in elements:
                try:
                    # Formata: <tag>.classe1.classe2
                    class_attr = el.get_attribute("class")
                    classes = ""
                    if class_attr:
                        classes = "." + ".".join(
                            c.strip() for c in class_attr.strip().split() if c.strip()
                        )
                    structure_id = f"{tag}{classes}"
                    structure_counter[structure_id] += 1
                except Exception:
                    continue

        # Top 10 mais comuns
        most_common = structure_counter.most_common(10)
        browser.close()

        result = {
            "url": url,
            "unique_structures_found": len(structure_counter),
            "top_structures": [
                {"structure": s, "count": c} for s, c in most_common
            ]
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
