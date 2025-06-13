def generate_border_function(pattern: str):
    border_function = []
    for i in range(1,len(pattern)):
        border_function.append(search_match(pattern, i))
    return border_function

def generate_prefixes(text):
    prefixes = []
    for i in range(1,len(text)):
        prefixes.append(text[:i])
    return prefixes

def generate_suffixes(text):
    suffixes = []
    for i in range(len(text)-1, 0, -1):
        suffixes.append(text[i:])
    return suffixes
        
def search_match(pattern, idx) -> int:
    text = pattern[:idx]
    suffixes = generate_suffixes(text)
    prefixes = generate_prefixes(text)
    for i in range(len(suffixes)-1, -1, -1):
        if (suffixes[i] == prefixes[i]):
            return i+1
    return 0

def kmp(text: str, pattern:str, border_function):
    if (len(text) < len(pattern)): return 0

    i = 0
    count = 0
    found = 0
    while(i < len(text)):
        j = 0
        pergeseran = 0
        #loop untuk bandingin pattern
        while(j < len(pattern)):
            pos = i + j
            if (text[pos] != pattern[j]):
                j = border_function[j]
                if border_function[j] != 0: # kalo border_function nya ga 0
                    pergeseran = len(pattern) - j # pergeserannya sesuain
                break
            j += 1

        #kalo border_function nya 0 geser 1 aja
        if pergeseran <= 0: pergeseran = 1

        if j == len(pattern):
            found = i
            count += 1
            pergeseran = len(pattern)

        i += pergeseran

    return count, found

text = "abacaabaccabacabaabb"
pattern = "abacab"
border_function = generate_border_function(pattern)
border_function.append(0)
res, found_at_pos = kmp(text, pattern, border_function)
print(f"{res} {found_at_pos}")