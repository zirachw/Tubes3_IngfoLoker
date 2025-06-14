class BoyerMoore:
    def __init__(self, text: str, pattern: str):
        self.text = text
        self.pattern = pattern
        self.last_occurence = {}

    def find_keys(self):
        keys = []
        for i in range(len(self.text)):
            if self.text[i] not in keys:
                keys.append(self.text[i])
        return keys

    def generate_last_occurence(self, keys):
        self.last_occurence = {}
        for key in keys:
            self.last_occurence[key] = -1

        for i in range(len(self.pattern)):
            if self.pattern[i] in keys:
                self.last_occurence[self.pattern[i]] = i

    def boyer_moore(self):
        if len(self.text) < len(self.pattern): return 0, -1

        i = 0
        count = 0
        found_at_pos = -1
        while(i + len(self.pattern) <= len(self.text)):
            j = len(self.pattern) - 1
            while(j >= 0):
                pos = i + j
                if (self.text[pos] != self.pattern[j]):
                    to_be_aligned = self.last_occurence.get(self.text[pos], -1)
                    if (to_be_aligned == -1):
                        pergeseran = len(self.pattern) - 1
                    elif (to_be_aligned < j):
                        pergeseran = len(self.pattern) - 1 - to_be_aligned
                    elif (to_be_aligned > j):
                        pergeseran = 1
                    break
                j -= 1

            if j == -1:
                found_at_pos = i
                count += 1
                pergeseran = len(self.pattern)

            i += pergeseran

        return count, found_at_pos

    def search(self):
        keys = self.find_keys()
        self.generate_last_occurence(keys)
        return self.boyer_moore()
