from pathlib import Path
import copy

from pybo import *


path = Path('../kt-no-tantra')

volumes = [
    '100 དབུ་མ། ཞ_cleaned_cleaned_cleaned.txt',
    '001_cleaned_cleaned_cleaned.txt',
    '044_cleaned_cleaned_cleaned.txt'
]

class AdjustSeg:
    def __init__(self):
        self.tokens = []
        self.ambiguous = None
        self.nonambiguous = None
        self._build_token_list()
        self._classify_ambiguity()

    def _build_token_list(self):
        for p in path.glob("*.*"):
            with open(p) as f:
                _tokens = f.read().split()

        # remove all the tokens which are not word
        non_words = ['#', '￥', 'n', '༄༅', '-', '+', '།']
        for token in _tokens:
            is_word = True
            for char in token:
                if char in non_words:
                    is_word = False
            if is_word:
                self.tokens.append(token)


    def _to_words(self, tokens):
        return ['{}{}'.format(*tk.split('+')) for tk in tokens]


    def _classify_ambiguity(self):
        amb, nonamb = [], []
        for volume in volumes:
            with open(path/volume) as f:
                tokens = f.read().split()
                for token in tokens:
                    if '+' not in token: continue
                    first_tk, second_tk = token.split('+')
                    if f'{first_tk}{second_tk}' in self.tokens:
                        amb.append(token)
                    else:
                        nonamb.append(token)

        self.c_ambiguous, self.c_nonambiguous = list(set(amb)), list(set(nonamb))

        self.ambiguous = self._to_words(self.c_ambiguous)
        self.nonambiguous = self._to_words(self.c_nonambiguous)


    def stats(self):
        print("# of words:", len(self.tokens))
        print("# of Ambiguous:", len(self.ambiguous))
        print("# of Nonambiguos:", len(self.nonambiguous))

        print()
        print("Ambiguous types:")
        print(*self.ambiguous, sep='\n')

        print()
        print("Non ambiguous types:")
        print(*self.nonambiguous[:7], sep='\n')


    def _split_token(self, token, split_idx):

        def __get_syls_split_idx(token, split_idx):
            for i, syl in enumerate(token.syls):
                if syl[-1] >= split_idx:
                    return i

        def __init_syls(syls):
            start_idx = syls[0][0]
            for syl in syls:
                for i in range(len(syl)):
                    syl[i] -= start_idx
            return syls

        def __create_char_groups(char_groups, keys, split_idx=0):
            new_char_groups = {}
            for key in keys:
                new_char_groups[key] = char_groups[key + split_idx]
            return new_char_groups

        def __split_char_groups(token, split_idx):
            keys = list(token.char_groups.keys())
            first_keys = keys[:split_idx]
            second_keys = [k-split_idx for k in keys[split_idx:]]

            first_token_char_groups = __create_char_groups(token.char_groups,
                                                           first_keys)
            second_token_char_groups = __create_char_groups(token.char_groups,
                                                            second_keys,
                                                            split_idx)
            # print(token.char_groups)
            # print(first_token_char_groups)
            # print(second_token_char_groups)

            return first_token_char_groups, second_token_char_groups

        # create an empty tokens
        first_token = Token()
        second_token = Token()

        # split content, syls, char_types and char_groups
        first_token_content = token.content[:split_idx]
        second_token_content = token.content[split_idx:]

        syls_split_idx = __get_syls_split_idx(token, split_idx)
        first_token_syls = token.syls[:syls_split_idx]
        second_token_syls = __init_syls(token.syls[syls_split_idx:])

        first_token_char_types = token.char_types[:split_idx]
        second_token_char_types = token.char_types[split_idx:]

        s = __split_char_groups(token, split_idx)
        first_token_char_groups, second_token_char_groups = s

        # create splited tokens
        first_token.content = first_token_content
        first_token.type = token.type
        first_token.char_groups = first_token_char_groups
        first_token.syls = first_token_syls
        first_token.len = len(token.content)
        first_token.start = token.start

        second_token.content = second_token_content
        second_token.type = token.type
        second_token.char_groups = second_token_char_groups
        second_token.syls = second_token_syls
        second_token.len = len(second_token.content)
        second_token.start = token.start + token.len

        return [first_token, second_token]


    def adjust(self, token_list):
        adjusted_token = []
        for token in token_list:
            # frist adjust all the non ambiguous segmentation
            if token.content in self.nonambiguous or token.content+'་' in self.nonambiguous:
                if not token.content.endswith('་'):
                    matched_idx = self.nonambiguous.index(token.content+'་')
                else:
                    matched_idx = self.nonambiguous.index(token.content)
                split_idx = self.c_nonambiguous[matched_idx].index('+')
                s = self._split_token(token, split_idx)
                adjusted_token.extend(s)
            else:
                adjusted_token.append(token)

        return adjusted_token


if __name__ == "__main__":
    tok = BoTokenizer('POS')
    adj = AdjustSeg()

    string = 'སྒྲུབ་པའི་ཆོས་དང་མི་མཐུན་པའི་ཕྱོགས་ཀྱི་དཔེ་ཡིན་པ་ར་གོ་རིམས་བཞིན་དུ་སྦྱར་རོ་།།'
    token_list = tok.tokenize(string, split_affixes=True)

    print("Before seg adjustment")
    print(*[tk.content for tk in token_list], sep='\n')

    print("After seg adjustment")
    adjusted_tokens = adj.adjust(token_list)
    print(*[tk.content for tk in adjusted_tokens], sep='\n')
