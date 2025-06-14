from src.algo import levenshtein as l

a = "KITTEN"
b = "SITTING"

lev_dist = l.levenshtein_distance(a,b)

print(f"Levenshtein distance: {lev_dist}")