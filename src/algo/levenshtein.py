class Levenshtein:
    def __init__(self, text: str, pattern: str):
        self.text = text
        self.pattern = pattern
        self.mat = []

    def lev(self, i: int, j: int):
        self.mat[i][j] = min(
            self.mat[i - 1][j] + 1,
            self.mat[i][j - 1] + 1,
            self.mat[i - 1][j - 1] + (1 if self.pattern[j - 1] != self.text[i - 1] else 0)
        )

    def compute_lev_distance(self, a: str, b: str) -> int:
        self.text = b
        self.pattern = a
        self.mat = [[0 for _ in range(len(a) + 1)] for _ in range(len(b) + 1)]

        for col in range(len(a) + 1):
            self.mat[0][col] = col

        for row in range(len(b) + 1):
            self.mat[row][0] = row

        for row in range(1, len(b) + 1):
            for col in range(1, len(a) + 1):
                self.lev(row, col)

        return self.mat[len(b)][len(a)]

    def compute_similarity(self, threshold: float = 80.0):
        pattern_words = self.pattern.split()
        text_words = self.text.split()
        window_size = len(pattern_words)
        matches = []
        
        for i in range(len(text_words) - window_size + 1):
            window_str = ' '.join(text_words[i:i + window_size])
            distance = self.compute_lev_distance(self.pattern, window_str)
            max_len = max(len(self.pattern), len(window_str))
            similarity = (1 - distance / max_len) * 100
            
            if similarity >= threshold:
                char_start = len(' '.join(text_words[:i]))
                if i > 0:
                    char_start += 1
                matches.append((char_start, window_str, round(similarity, 2)))
        
        return matches
    
    def search_fuzzy_matches(self, threshold: float = 80.0):
        match_details = self.compute_similarity(threshold)
        total_count = len(match_details)
        
        matched_strings_dict = {}
        for match in match_details:
            matched_string = match[1]
            if matched_string in matched_strings_dict:
                matched_strings_dict[matched_string] += 1
            else:
                matched_strings_dict[matched_string] = 1
        return total_count > 0, total_count, matched_strings_dict