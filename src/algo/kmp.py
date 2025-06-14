class KMP:
    def __init__(self, text: str, pattern: str):
        self.text = text
        self.pattern = pattern
        self.border_function = []

    def generate_prefixes(self, text):
        prefixes = []
        for i in range(1, len(text)):
            prefixes.append(text[:i])
        return prefixes

    def generate_suffixes(self, text):
        suffixes = []
        for i in range(len(text) - 1, 0, -1):
            suffixes.append(text[i:])
        return suffixes

    def search_match(self, pattern, idx) -> int:
        text = pattern[:idx]
        suffixes = self.generate_suffixes(text)
        prefixes = self.generate_prefixes(text)
        for i in range(len(suffixes) - 1, -1, -1):
            if suffixes[i] == prefixes[i]:
                return i + 1
        return 0

    def generate_border_function(self):
        self.border_function = []
        for i in range(1, len(self.pattern)):
            self.border_function.append(self.search_match(self.pattern, i))
        self.border_function.append(0)

    def kmp(self):
        if len(self.text) < len(self.pattern):
            return 0, -1

        i = 0
        count = 0
        found = -1
        while i < len(self.text):
            j = 0
            pergeseran = 0
            while j < len(self.pattern):
                pos = i + j
                if pos >= len(self.text) or self.text[pos] != self.pattern[j]:
                    j = self.border_function[j]
                    if self.border_function[j] != 0:
                        pergeseran = len(self.pattern) - j
                    break
                j += 1

            if pergeseran <= 0:
                pergeseran = 1

            if j == len(self.pattern):
                found = i
                count += 1
                pergeseran = len(self.pattern)

            i += pergeseran

        return count, found

    def search(self):
        self.generate_border_function()
        return self.kmp()
