from collections import defaultdict
import string

class AhoCorasick:
    def __init__(self, keywords):
        self.words = [word.lower() for word in keywords]
        self.alphabet = string.ascii_lowercase + string.digits + string.punctuation
        self.alpha_size = len(self.alphabet)
        self.char_to_index = {ch: i for i, ch in enumerate(self.alphabet)}
        self.max_states = sum(len(w) for w in self.words) + 1
        self.goto = [[-1] * self.alpha_size for _ in range(self.max_states)]
        self.out = [0] * self.max_states
        self.fail = [-1] * self.max_states
        self.states_count = self.__build_matching_machine()

    def __build_matching_machine(self):
        states = 1
        for idx, word in enumerate(self.words):
            s = 0
            for ch in word:
                i = self.char_to_index.get(ch)
                if i is None:
                    continue
                if self.goto[s][i] == -1:
                    self.goto[s][i] = states
                    states += 1
                s = self.goto[s][i]
            self.out[s] |= (1 << idx)
        for i in range(self.alpha_size):
            if self.goto[0][i] == -1:
                self.goto[0][i] = 0
        queue = []
        for i in range(self.alpha_size):
            nxt = self.goto[0][i]
            if nxt != 0:
                self.fail[nxt] = 0
                queue.append(nxt)
        while queue:
            r = queue.pop(0)
            for i in range(self.alpha_size):
                nxt = self.goto[r][i]
                if nxt != -1:
                    queue.append(nxt)
                    f = self.fail[r]
                    while self.goto[f][i] == -1:
                        f = self.fail[f]
                    self.fail[nxt] = self.goto[f][i]
                    self.out[nxt] |= self.out[self.fail[nxt]]
        return states

    def __find_next_state(self, s, ch):
        i = self.char_to_index.get(ch)
        if i is None:
            return s
        while self.goto[s][i] == -1:
            s = self.fail[s]
        return self.goto[s][i]

    def search(self, text):
        s = 0
        hits = defaultdict(int)
        last_end = -1
        for i, raw_ch in enumerate(text):
            ch = raw_ch.lower()
            s = self.__find_next_state(s, ch)
            if self.out[s] != 0:
                for idx in range(len(self.words)):
                    if self.out[s] & (1 << idx):
                        w = self.words[idx]
                        start = i - len(w) + 1
                        if start > last_end:
                            hits[w] += 1
                            last_end = i
        return hits
