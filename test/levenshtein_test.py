from src.algo.levenshtein import Levenshtein

a = "KITTEN"
b = "SITTING"

lev = Levenshtein(a,b)
lev_dist = lev.compute()

print(f"Levenshtein distance: {lev_dist}")