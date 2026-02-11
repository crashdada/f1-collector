import json
import os

def generate_svg_files():
    collector_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector"
    svg_map_file = os.path.join(collector_dir, "maintenance", "flag_svgs_2026.json")
    output_dir = os.path.join(collector_dir, "assets", "flags")
    
    if not os.path.exists(svg_map_file):
        print(f"SVG map not found: {svg_map_file}")
        return

    with open(svg_map_file, 'r', encoding='utf-8') as f:
        svg_flags = json.load(f)

    os.makedirs(output_dir, exist_ok=True)
    
    # Mapping for cleaner filenames
    filename_map = {
        "People’s Republic of China": "China",
        "United States of America": "USA",
        "United Arab Emirates": "UAE"
    }

    for country, svg_content in svg_flags.items():
        filename = filename_map.get(country, country).replace(" ", "_") + ".svg"
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        print(f"Generated: {filename}")

if __name__ == "__main__":
    generate_svg_files()
