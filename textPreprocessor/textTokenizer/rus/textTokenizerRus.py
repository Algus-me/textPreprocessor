import spacy
import pymorphy2

from ..textTokenizer import TextTokenizer

# https://universaldependencies.org/en/pos/index.html
# https://pymorphy2.readthedocs.io/en/latest/user/grammemes.html

correspondenceOfPymorphyAndSpacyPos = {}
correspondenceOfPymorphyAndSpacyPos["PNCT"] = "PUNCT"
correspondenceOfPymorphyAndSpacyPos["UNKN"] = "X"

correspondenceOfPymorphyAndSpacyPos["ADJF"] = "ADJ"
correspondenceOfPymorphyAndSpacyPos["ADJS"] = "ADJ"

correspondenceOfPymorphyAndSpacyPos["ADVB"] = "ADV"

correspondenceOfPymorphyAndSpacyPos["INTJ"] = "INTJ"

correspondenceOfPymorphyAndSpacyPos["NOUN"] = "NOUN"

correspondenceOfPymorphyAndSpacyPos["VERB"] = "VERB"
correspondenceOfPymorphyAndSpacyPos["INFN"] = "VERB"
correspondenceOfPymorphyAndSpacyPos["PRTF"] = "VERB"
correspondenceOfPymorphyAndSpacyPos["PRTS"] = "VERB"
correspondenceOfPymorphyAndSpacyPos["GRND"] = "VERB"

correspondenceOfPymorphyAndSpacyPos["PREP"] = "ADP"

correspondenceOfPymorphyAndSpacyPos["CONJ"] = "CCONJ"

#correspondenceOfPymorphyAndSpacyPos["NPRO"] = "DET"

correspondenceOfPymorphyAndSpacyPos["NUMR"] = "NUM"
correspondenceOfPymorphyAndSpacyPos["NUMB"] = "NUM"

correspondenceOfPymorphyAndSpacyPos["PRCL"] = "PART"

correspondenceOfPymorphyAndSpacyPos["NPRO"] = "PRON"

class tokenClass:
    text = None
    pos_ = None
    lemma_ = None

class TextTokenizerRus(TextTokenizer):
    def tokenize(self, text):
        tokens = self.tokenizer_(text)
        res = []
        i = 0
        while i < len(tokens):
            morphRes = self.morph_.parse(tokens[i].text)[0]
            parsedToken = tokenClass()
            parsedToken.text = tokens[i].text
            posFound = False
            for pos in correspondenceOfPymorphyAndSpacyPos:
                if pos in morphRes.tag:
                    parsedToken.pos_ = correspondenceOfPymorphyAndSpacyPos[pos]
                    posFound = True
                    break
            if posFound == False:
                parsedToken.pos_ = "X"
            parsedToken.lemma_ = morphRes.normal_form
            res.append(parsedToken)
            i += 1

        return res

# Fields:

    tokenizer_ = spacy.load('xx')
    morph_ = pymorphy2.MorphAnalyzer()