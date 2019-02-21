from ..textTokenizer import TextTokenizer

class TextTokenizerSpacyBased(TextTokenizer):

    def tokenize(self, text):
        return self.nlp_(text)

# Setters and getters:

    def setLinguisticProcessor(self, nlp):
        self.nlp_ = nlp

# Fields:

    nlp_ = None