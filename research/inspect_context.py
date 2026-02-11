with open("reconstructed_2026.txt", "r", encoding="utf-8") as f:
    text = f.read()

pos = text.find("13 - 15 MAR")
if pos != -1:
    print("Found '13 - 15 MAR' at pos:", pos)
    print("Context around 13-15 MAR:")
    print(text[pos-500 : pos+500])

# Search for Japan
pos_japan = text.lower().find("japan")
if pos_japan != -1:
    print("\nFound 'Japan' at pos:", pos_japan)
    print("Context around Japan:")
    print(text[pos_japan-500 : pos_japan+500])
else:
    print("\n'Japan' not found in the reconstructed text.")
