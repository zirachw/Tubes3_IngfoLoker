class Levenshtein:
    def __init__(self, a: str, b: str):
        self.a = a
        self.b = b
        self.mat = [[0 for _ in range(len(a) + 1)] for _ in range(len(b) + 1)]

    def lev(self, i: int, j: int):
        self.mat[i][j] = min(
            self.mat[i - 1][j] + 1,
            self.mat[i][j - 1] + 1,
            self.mat[i - 1][j - 1] + (1 if self.a[j - 1] != self.b[i - 1] else 0)
        )

    def compute(self) -> int:
        for col in range(len(self.a) + 1):
            self.mat[0][col] = col

        for row in range(len(self.b) + 1):
            self.mat[row][0] = row

        for row in range(1, len(self.b) + 1):
            for col in range(1, len(self.a) + 1):
                self.lev(row, col)

        return self.mat[len(self.b)][len(self.a)]
