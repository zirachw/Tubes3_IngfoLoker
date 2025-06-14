from src.algo import bm

text = "preppreppreppreppreparatio"
pattern = "prep"

res, found_at_pos = bm.search_using_bm(text, pattern)

print(f"{pattern} occurence: {res}")
print(f"found at {found_at_pos}")