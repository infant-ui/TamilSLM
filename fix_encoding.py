import sys
garbled = "α«òα«úα«┐α«ñα«òα»ì"
with open("test_out.txt", "w", encoding="utf-8") as f:
    try:
        f.write("cp437: " + garbled.encode("cp437").decode("utf-8") + "\n")
    except Exception as e:
        f.write(f"cp437 failed: {e}\n")
    try:
        f.write("latin-1: " + garbled.encode("latin-1").decode("utf-8") + "\n")
    except Exception as e:
        f.write(f"latin-1 failed: {e}\n")
    try:
        f.write("cp1252: " + garbled.encode("cp1252").decode("utf-8") + "\n")
    except Exception as e:
        f.write(f"cp1252 failed: {e}\n")
