def find_keys(text: str):
    keys = []
    for i in range(len(text)):
        if (text[i] not in keys):
            keys.append(text[i])

    return keys

def generate_last_occurence(pattern: str, keys):
    last_occurence = {}
    for key in keys:
        last_occurence[key] = -1

    for i in range(len(pattern)):
        if (pattern[i] in keys):
            last_occurence[pattern[i]] = i

    return last_occurence

def boyer_moore(text:str, pattern: str, last_occurence):
    if (len(text) < len(pattern)): return 0

    i = 0
    count = 0
    found_at_pos = 0
    while(i + len(pattern) <= len(text)):
        j = len(pattern) - 1
        while(j >= 0):
            pos = i + j
            # print(f" pos: {pos}, i: {i}, j: {j}")
            if (text[pos] != pattern[j]):
                to_be_aligned = last_occurence[text[pos]]
                if (to_be_aligned == -1): # kalo gaada di pattern
                    pergeseran = len(pattern)
                elif (to_be_aligned < j): # kalo bisa digeser
                    pergeseran = len(pattern) - 1 - to_be_aligned
                elif (to_be_aligned > j): # kalo gabisa digeser
                    pergeseran = 1
                break
            j -= 1

        if j == -1:
            print(i)
            found_at_pos = i
            count += 1
            pergeseran = len(pattern)

        i += pergeseran

    return count, found_at_pos

def search_using_bm(text: str, pattern: str):
    keys = find_keys(text)
    last_occurence = generate_last_occurence(pattern, keys)
    count, found_at_pos = boyer_moore(text,pattern,last_occurence)
    return count, found_at_pos


