import os
import re

def standardize_svgs():
    folder = r"c:\Users\jaymz\Desktop\oc\f1-collector\assets\flags"
    for filename in os.listdir(folder):
        if filename.endswith(".svg"):
            path = os.path.join(folder, filename)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove width/height if they are 1em
            content = re.sub(r'width="1em"', '', content)
            content = re.sub(r'height="1em"', '', content)
            
            # Ensure viewBox is present
            if 'viewBox' not in content and 'viewbox' not in content:
                 content = content.replace('<svg', '<svg viewBox="0 0 56 56"')
            
            # Clean up colons in IDs (can break some tooling)
            content = content.replace(':Ss:', 'Ss').replace(':S7:', 'S7').replace(':QS2fX', 'QS2fX')
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
    print("Standardized all SVGs in collector assets.")

if __name__ == "__main__":
    standardize_svgs()
