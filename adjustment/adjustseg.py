from pathlib import Path
from pybo import *


class AdjustSeg:

    def __init__(self, path, volumes):
        self.path = path
        self.volumes = volumes
        self.token_corpus = []
        self.ambiguous = None
        self.c_ambiguos = None
        self.nonambiguous = None
        self.c_nonambiguous = None
        self._build_token_list()
        self._classify_ambiguity()


    def _build_token_list(self):
        for p in self.path.glob("*.*"):
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
                self.token_corpus.append(token)


    def _classify_ambiguity(self):

        def __to_words(corrected_tokens):
            token_words = []
            for tk in corrected_tokens:
                if '+' in tk:
                    token_words.append('{}{}'.format(*tk.split('+')))
                else:
                    token_words.append('{}{}'.format(*tk.split('-')))
            return token_words

        amb, nonamb = [], []
        prev_token = None
        for volume in self.volumes:
            with open(self.path/volume) as f:
                tokens = f.read().split()
                for token in tokens:
                    if '+' in token:
                        first_tk, second_tk = token.split('+')
                        if f'{first_tk}{second_tk}' in self.token_corpus:
                            amb.append(token)
                        else:
                            nonamb.append(token)
                    elif '-' in token:
                        if f'{prev_token}' in self.token_corpus and f'{token[1:]}' in self.token_corpus:
                            amb.append(f'{prev_token}{token}')
                        else:
                            nonamb.append(f'{prev_token}{token}')
                    prev_token = token

        self.c_ambiguous, self.c_nonambiguous = list(set(amb)), list(set(nonamb))

        self.ambiguous = __to_words(self.c_ambiguous)
        self.nonambiguous = __to_words(self.c_nonambiguous)


    def stats(self):
        print("# of words:", len(self.token_corpus))
        print("# of Ambiguous:", len(self.c_ambiguous))
        print("# of Nonambiguos:", len(self.c_nonambiguous))

        print()
        print("Ambiguous types:")
        print(*self.c_ambiguous, sep='\n')

        print()
        print("Non ambiguous types:")
        print(*self.c_nonambiguous[:7], sep='\n')


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
        first_token.len = len(first_token_char_groups)
        first_token.start = token.start

        second_token.content = second_token_content
        second_token.type = token.type
        second_token.char_groups = second_token_char_groups
        second_token.syls = second_token_syls
        second_token.len = len(second_token.content)
        second_token.start = token.start + split_idx

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
                try:
                    print(token.content)
                    print(self.nonambiguous[matched_idx])
                    print(self.c_nonambiguous[matched_idx])
                    split_idx = self.c_nonambiguous[matched_idx].index('+')
                    s = self._split_token(token, split_idx)
                except:
                    pass
                adjusted_token.extend(s)
            else:
                adjusted_token.append(token)

        return adjusted_token


if __name__ == "__main__":

    path = Path('../kt-no-tantra')

    volumes = [
        '100 དབུ་མ། ཞ_cleaned_cleaned_cleaned.txt',
        '001_cleaned_cleaned_cleaned.txt',
        '044_cleaned_cleaned_cleaned.txt'
    ]

    tok = BoTokenizer('POS')
    adj = AdjustSeg(path, volumes)

    string = 'སྒྲུབ་པའི་ཆོས་དང་མི་མཐུན་པའི་ཕྱོགས་ཀྱི་དཔེ་ཡིན་པ་ར་གོ་རིམས་བཞིན་དུ་སྦྱར་རོ་།།'
    token_list = tok.tokenize(string, split_affixes=True)

    print("Before seg adjustment")
    print(*[tk.content for tk in token_list], sep=' ')

    print("After seg adjustment")
    adjusted_tokens = adj.adjust(token_list)
    print(*[tk.content for tk in adjusted_tokens], sep=' ')
