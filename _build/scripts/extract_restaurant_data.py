#!/usr/bin/env python3
"""Extract restaurant menu data from existing HTML pages into JSON files."""
import os, re, json, html as html_mod

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
ROOT = os.path.join(REPO_ROOT, 'public_html')
DATA_DIR = os.path.join(ROOT, 'data', 'restaurants')

def find_restaurant_pages():
    pages = []
    for d in sorted(os.listdir(ROOT)):
        idx = os.path.join(ROOT, d, 'index.html')
        if not os.path.isfile(idx):
            continue
        with open(idx, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'restaurant.js' in content or 'initRestaurant' in content:
            pages.append(d)
    return pages

def extract_items_from_html(cat_html):
    items = []
    item_starts = [m.start() for m in re.finditer(r'<div class="menu-item"', cat_html)]
    for i, start in enumerate(item_starts):
        end = item_starts[i+1] if i+1 < len(item_starts) else len(cat_html)
        chunk = cat_html[start:end]
        # Get the opening div attrs
        attr_m = re.match(r'<div class="menu-item"([^>]*)>', chunk)
        if not attr_m:
            continue
        attrs = attr_m.group(1)
        item = {}
        for attr in ['name', 'calories', 'protein', 'carbs', 'fat', 'fiber', 'sodium', 'cholesterol', 'saturated-fat', 'sugars', 'trans-fat', 'price']:
            m = re.search(f'data-{attr}="([^"]*)"', attrs)
            if m:
                val = m.group(1)
                key = attr.replace('-', '_')
                if attr == 'name':
                    item[key] = html_mod.unescape(val)
                else:
                    try:
                        item[key] = float(val)
                    except:
                        pass
        if 'name' in item:
            items.append(item)
    return items

def extract_data(slug):
    filepath = os.path.join(ROOT, slug, 'index.html')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract title
    title_m = re.search(r'<h1[^>]*>(.*?)</h1>', content)
    title = html_mod.unescape(title_m.group(1)) if title_m else slug.replace('-', ' ').title()
    title = re.sub(r'&#\d+;\s*', '', title).strip()
    
    # Extract description
    desc_m = re.search(r'<meta name="description" content="([^"]*)"', content)
    description = desc_m.group(1) if desc_m else ''
    
    # Find all category group boundaries
    cat_starts = [(m.start(), html_mod.unescape(m.group(1))) 
                  for m in re.finditer(r'<div class="rest-cat-group" data-category="([^"]+)"', content)]
    
    categories = []
    for i, (start, cat_name) in enumerate(cat_starts):
        if i + 1 < len(cat_starts):
            end = cat_starts[i+1][0]
        else:
            # Find end of grid
            end_m = re.search(r'<div id="rest-summary"', content[start:])
            end = start + end_m.start() if end_m else len(content)
        
        cat_html = content[start:end]
        items = extract_items_from_html(cat_html)
        categories.append({
            "name": cat_name,
            "items": items
        })
    
    return {
        "slug": slug,
        "title": title,
        "description": description,
        "categories": categories
    }

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    pages = find_restaurant_pages()
    
    print(f'Found {len(pages)} restaurant pages')
    
    for slug in pages:
        data = extract_data(slug)
        out_path = os.path.join(DATA_DIR, f'{slug}.json')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        item_count = sum(len(c['items']) for c in data['categories'])
        print(f'  ✓ {slug}: {len(data["categories"])} categories, {item_count} items')
    
    index = []
    for slug in pages:
        json_path = os.path.join(DATA_DIR, f'{slug}.json')
        with open(json_path, 'r') as f:
            d = json.load(f)
        index.append({
            "slug": d["slug"],
            "title": d["title"],
            "description": d["description"],
            "itemCount": sum(len(c['items']) for c in d['categories'])
        })
    
    with open(os.path.join(DATA_DIR, '_index.json'), 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f'\n✓ Created _index.json with {len(index)} restaurants')

if __name__ == '__main__':
    main()
