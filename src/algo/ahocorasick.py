from collections import defaultdict

class AhoCorasick:
    def __init__(self, keywords):
        self.words = [word.lower() for word in keywords]
        self.max_states = sum(len(word) for word in self.words)
        self.max_characters = 26
        self.out = [0] * (self.max_states + 1)
        self.fail = [-1] * (self.max_states + 1)
        self.goto = [[-1] * self.max_characters for _ in range(self.max_states + 1)]
        self.states_count = self.__build_matching_machine()

    def __build_matching_machine(self):
        states = 1
        for i, word in enumerate(self.words):
            current_state = 0
            for character in word:
                ch = ord(character) - 97
                if self.goto[current_state][ch] == -1:
                    self.goto[current_state][ch] = states
                    states += 1
                current_state = self.goto[current_state][ch]
            self.out[current_state] |= (1 << i)
        for ch in range(self.max_characters):
            if self.goto[0][ch] == -1:
                self.goto[0][ch] = 0
        queue = []
        for ch in range(self.max_characters):
            if self.goto[0][ch] != 0:
                self.fail[self.goto[0][ch]] = 0
                queue.append(self.goto[0][ch])
        while queue:
            state = queue.pop(0)
            for ch in range(self.max_characters):
                if self.goto[state][ch] != -1:
                    failure = self.fail[state]
                    while self.goto[failure][ch] == -1:
                        failure = self.fail[failure]
                    failure = self.goto[failure][ch]
                    self.fail[self.goto[state][ch]] = failure
                    self.out[self.goto[state][ch]] |= self.out[failure]
                    queue.append(self.goto[state][ch])
        return states

    def __find_next_state(self, current_state, next_input):
        if not next_input.isalpha() or not next_input.isascii():
            return current_state
        ch = ord(next_input.lower()) - 97
        while self.goto[current_state][ch] == -1:
            current_state = self.fail[current_state]
        return self.goto[current_state][ch]

    def search(self, text):
        current_state = 0
        result = defaultdict(int)
        text = text.lower()
        last_match_end = -1
        for i in range(len(text)):
            current_state = self.__find_next_state(current_state, text[i])
            if self.out[current_state] == 0:
                continue
            for j in range(len(self.words)):
                if self.out[current_state] & (1 << j):
                    word = self.words[j]
                    start_idx = i - len(word) + 1
                    end_idx = i
                    if start_idx > last_match_end:
                        result[word] += 1
                        last_match_end = end_idx
        return result

