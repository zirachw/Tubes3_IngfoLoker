from typing import List, Tuple
import random

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

    def search_fuzzy_matches(self, threshold: float = 61.0):
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


def fuzzy_match(pattern: str, text: str, threshold: float) -> bool:
    lev = Levenshtein(text, pattern)
    found, _, _ = lev.search_fuzzy_matches(threshold)
    return found


DATA: List[Tuple[str, str, bool]] = [
    ("React", "React", True),
    ("React", "Reac", True),
    ("React", "Reaact", True),
    ("React", "Raect", True),
    ("React", "Rxact", True),
    ("React", "Reacter", False),
    ("React", "Angular", False),
    ("Express", "Express", True),
    ("Express", "Exprss", True),
    ("Express", "Expresss", True),
    ("Express", "Exrpess", True),
    ("Express", "Exprees", True),
    ("Express", "Expresion", False),
    ("Express", "Spring", False),
    ("Python", "Python", True),
    ("Python", "Pythn", True),
    ("Python", "Pythonn", True),
    ("Python", "Pyhton", True),
    ("Python", "Ptyhon", True),
    ("Python", "Pyythonn", False),
    ("Python", "Java", False),
    ("Django", "Django", True),
    ("Django", "Djanog", True),
    ("Django", "Diango", True),
    ("Django", "Djiango", False),
    ("Django", "Flask", False),
    ("HTML", "HTML", True),
    ("HTML", "HTMl", True),
    ("HTML", "HTM", True),
    ("HTML", "HMTL", True),
    ("HTML", "HMLT", False),
    ("HTML", "CSS", False),
    ("CSS", "CSS", True),
    ("CSS", "CSSS", True),
    ("CSS", "CS", True),
    ("CSS", "C S", False),
    ("CSS", "HTML", False),
    ("JavaScript", "JavaScript", True),
    ("JavaScript", "JavScript", True),
    ("JavaScript", "JavaScriptt", True),
    ("JavaScript", "JavaScrpt", True),
    ("JavaScript", "JavaScipt", True),
    ("JavaScript", "JvaaScript", True),
    ("JavaScript", "TypeScript", False),
    ("SQL", "SQL", True),
    ("SQL", "SQl", True),
    ("SQL", "SQQL", True),
    ("SQL", "SLQ", True),
    ("SQL", "NoSQL", False),
]

def f1_score_manual(y_true: List[bool], y_pred: List[bool]) -> float:
    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt and yp)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if not yt and yp)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt and not yp)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    return (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

def find_best_threshold(data, k_folds=5, seed=42):
    random.seed(seed)
    n = len(data)
    indices = list(range(n))
    random.shuffle(indices)
    fold_size = n // k_folds
    folds = [indices[i * fold_size : (i + 1) * fold_size] for i in range(k_folds - 1)]
    folds.append(indices[(k_folds - 1) * fold_size :])
    best_t, best_score = None, -1.0
    for thresh in range(50, 101):
        f1_scores = []
        for i in range(k_folds):
            val_idx = folds[i]
            y_true = [data[j][2] for j in val_idx]
            y_pred = [fuzzy_match(data[j][0], data[j][1], thresh) for j in val_idx]
            f1_scores.append(f1_score_manual(y_true, y_pred))
        avg_f1 = sum(f1_scores) / len(f1_scores)
        if avg_f1 > best_score:
            best_score, best_t = avg_f1, thresh
    return best_t, best_score

if __name__ == "__main__":
    best_threshold, best_f1 = find_best_threshold(DATA)
    print(f"Best threshold: {best_threshold}%  (cross-validated F1={best_f1:.3f})")