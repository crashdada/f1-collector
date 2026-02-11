import re

file_path = r'c:\Users\jaymz\Desktop\oc\f1-collector\debug_2026.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 匹配所有可能的媒体 URL
urls = re.findall(r'https?://[^\s\"\'<>]+?\.(?:png|jpg|svg|webp)', content)
unique_urls = sorted(list(set(urls)))

# 过滤出包含国旗相关关键词的 URL
flag_urls = [u for u in unique_urls if 'flag' in u.lower() or 'country' in u.lower() or 'circle' in u.lower()]

print(f"Total unique media URLs: {len(unique_urls)}")
print(f"Potential flag URLs: {len(flag_urls)}")
for u in flag_urls:
    print(u)

# 打印一些示例以观察路径结构
print("\nExample URLs:")
for u in unique_urls[:20]:
    print(u)
