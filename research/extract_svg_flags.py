from bs4 import BeautifulSoup
import json
import os

def extract_svg_flags():
    collector_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector"
    html_file = os.path.join(collector_dir, "debug_2026.html")
    output_file = os.path.join(collector_dir, "maintenance", "flag_svgs_2026.json")
    
    if not os.path.exists(html_file):
        print(f"File not found: {html_file}")
        return

    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Find all SVG elements that might be flags
    # Based on user hint: class="CountryFlag-module_flag..." and has a <title>
    flags = {}
    
    # Locate race cards first to associate flags with countries/races
    # The structure likely has a flag near a country name or race title
    
    # Let's search for all SVGs with titles starting with "Flag of"
    svgs = soup.find_all('svg')
    print(f"Found {len(svgs)} SVG elements.")
    
    for svg in svgs:
        title_tag = svg.find('title')
        if title_tag and title_tag.text.startswith('Flag of'):
            country_name = title_tag.text.replace('Flag of ', '').strip()
            # Clean up class names and other attributes if needed
            # We want the inner XML of the SVG (excluding the tag but maybe keeping the viewbox)
            # Or just the whole tag but simplified
            svg_str = str(svg)
            flags[country_name] = svg_str
            print(f"Captured flag for: {country_name}")

    if flags:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(flags, f, ensure_ascii=False, indent=4)
        print(f"Saved {len(flags)} flags to {output_file}")
    else:
        print("No flags found matching the criteria.")

if __name__ == "__main__":
    extract_svg_flags()
