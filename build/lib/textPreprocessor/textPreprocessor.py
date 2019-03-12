import os
import re
import json
import spacy
import pymorphy2
from polyglot.detect import Detector

import serializableClass

from .textTokenizer import TextTokenizerSpacyBased
from .textTokenizer import TextTokenizerRus

def initLanguagePreprocessorComponents():

    languagePreprocessorComponents = {}
    
    languagePreprocessorComponents["un"] = {}
    languagePreprocessorComponents["un"]["tokenizer"] = TextTokenizerSpacyBased()
    languagePreprocessorComponents["un"]["tokenizer"].setLinguisticProcessor(spacy.load('xx'))
    languagePreprocessorComponents["un"]["stopPos"] = set()
    languagePreprocessorComponents["un"]["stopTokens"] = set()
    languagePreprocessorComponents["un"]["stopLemmas"] = set()

    languagePreprocessorComponents["en"] = {}
    languagePreprocessorComponents["en"]["tokenizer"] = TextTokenizerSpacyBased()
    languagePreprocessorComponents["en"]["tokenizer"].setLinguisticProcessor(spacy.load('en'))
    languagePreprocessorComponents["en"]["stopPos"] = set()
    languagePreprocessorComponents["en"]["stopTokens"] = set()
    languagePreprocessorComponents["en"]["stopLemmas"] = set()

    languagePreprocessorComponents["de"] = {}
    languagePreprocessorComponents["de"]["tokenizer"] = TextTokenizerSpacyBased()
    languagePreprocessorComponents["de"]["tokenizer"].setLinguisticProcessor(spacy.load('de'))
    languagePreprocessorComponents["de"]["stopPos"] = set()
    languagePreprocessorComponents["de"]["stopTokens"] = set()
    languagePreprocessorComponents["de"]["stopLemmas"] = set()

    languagePreprocessorComponents["es"] = {}
    languagePreprocessorComponents["es"]["tokenizer"] = TextTokenizerSpacyBased()
    languagePreprocessorComponents["es"]["tokenizer"].setLinguisticProcessor(spacy.load('es'))
    languagePreprocessorComponents["es"]["stopPos"] = set()
    languagePreprocessorComponents["es"]["stopTokens"] = set()
    languagePreprocessorComponents["es"]["stopLemmas"] = set()

    languagePreprocessorComponents["pt"] = {}
    languagePreprocessorComponents["pt"]["tokenizer"] = TextTokenizerSpacyBased()
    languagePreprocessorComponents["pt"]["tokenizer"].setLinguisticProcessor(spacy.load('pt'))
    languagePreprocessorComponents["pt"]["stopPos"] = set()
    languagePreprocessorComponents["pt"]["stopTokens"] = set()
    languagePreprocessorComponents["pt"]["stopLemmas"] = set()

    languagePreprocessorComponents["fr"] = {}
    languagePreprocessorComponents["fr"]["tokenizer"] = TextTokenizerSpacyBased()
    languagePreprocessorComponents["fr"]["tokenizer"].setLinguisticProcessor(spacy.load('fr'))
    languagePreprocessorComponents["fr"]["stopPos"] = set()
    languagePreprocessorComponents["fr"]["stopTokens"] = set()
    languagePreprocessorComponents["fr"]["stopLemmas"] = set()

    languagePreprocessorComponents["it"] = {}
    languagePreprocessorComponents["it"]["tokenizer"] = TextTokenizerSpacyBased()
    languagePreprocessorComponents["it"]["tokenizer"].setLinguisticProcessor(spacy.load('it'))
    languagePreprocessorComponents["it"]["stopPos"] = set()
    languagePreprocessorComponents["it"]["stopTokens"] = set()
    languagePreprocessorComponents["it"]["stopLemmas"] = set()

    languagePreprocessorComponents["nl"] = {}
    languagePreprocessorComponents["nl"]["tokenizer"] = TextTokenizerSpacyBased()
    languagePreprocessorComponents["nl"]["tokenizer"].setLinguisticProcessor(spacy.load('nl'))
    languagePreprocessorComponents["nl"]["stopPos"] = set()
    languagePreprocessorComponents["nl"]["stopTokens"] = set()
    languagePreprocessorComponents["nl"]["stopLemmas"] = set()

    languagePreprocessorComponents["ru"] = {}
    languagePreprocessorComponents["ru"]["tokenizer"] = TextTokenizerRus()
    languagePreprocessorComponents["ru"]["stopPos"] = set()
    languagePreprocessorComponents["ru"]["stopTokens"] = set()
    languagePreprocessorComponents["ru"]["stopLemmas"] = set()

    return languagePreprocessorComponents

class TextPreprocessor(serializableClass.SerializableClass):
    
    def getFilteredTokens(self, text, lang):
        tokens = self.languagePreprocessorComponents_[lang]["tokenizer"].tokenize(text.lower())
        res = []
        for t in tokens:
            if t.pos_ in self.languagePreprocessorComponents_[lang]["stopPos"]:
                continue
            if t.text in self.languagePreprocessorComponents_[lang]["stopTokens"]:
                continue
            if t.lemma_ in self.languagePreprocessorComponents_[lang]["stopLemmas"]:
                continue
            res.append(t)
        return res

    def getFilteredTokensAndDetectedLanguage(self, text, defaultLangIfNotDetected=None):
        lang = self.detectLanguage(text)
        lang = self.chooseKnownLanguageOfTextIfPossible(text, lang, defaultLangIfNotDetected)
        filteredTokens = self.getFilteredTokens(text, lang)
        res = {"filteredTokens" : filteredTokens, "lang" : lang}
        return res
    
    def detectLanguage(self, text):
        try:
            detectionResult = Detector(text)
            lang = detectionResult.language.code
        except:
            lang = "un"
        return lang
    
    def chooseKnownLanguageOfTextIfPossible(self, text, lang, defaultLangIfNotDetected=None):
        if lang not in self.languagePreprocessorComponents_ or lang=="un":
            lettersFromText = re.sub("[\W\d_]", "", text)
            if len(lettersFromText) == 0:
                if defaultLangIfNotDetected is not None:
                    lang = defaultLangIfNotDetected
                else:
                    lang = "en"
            elif re.match("^[A-Za-z]*$", text):
                lang = "en"
            elif re.match("^[А-Яа-я]*$", text):
                lang = "ru"
            elif defaultLangIfNotDetected is not None:
                lang = defaultLangIfNotDetected
            else:
                lang = "un"
        return lang

# SETTERS AND GETTERS:

    def setStopPos(self, stopPos, lang):
        self.languagePreprocessorComponents_[lang]["stopPos"] = stopPos
    def setAllowedPos(self, allowed, lang):
        self.languagePreprocessorComponents_[lang]["stopPos"] = self.allPos_ - allowed
    def getStopPos(self, lang):
        return self.languagePreprocessorComponents_[lang]["stopPos"]

    def setStopTokens(self, stopTokens, lang):
        self.languagePreprocessorComponents_[lang]["stopTokens"] = stopTokens
    def getStopTokens(self, lang):
        return self.languagePreprocessorComponents_[lang]["stopTokens"]

    def setStopLemmas(self, stopLemmas, lang, normalize=False):
        if normalize == True:
            normalized = []
            for sl in stopLemmas:
                morphRes = self.morph_.parse(sl)[0]
                normalized.append(morphRes.normal_form)
            stopLemmas = set(normalized)
        self.languagePreprocessorComponents_[lang]["stopLemmas"] = stopLemmas
    def getStopLemmas(self, lang):
        return self.languagePreprocessorComponents_[lang]["stopLemmas"]

# SAVE AND LOAD:

    def saveThisObjectDataOnly_(self, folder):
        dataToSave = {}
        for lang in self.languagePreprocessorComponents_:
            dataToSave[lang] = {}
            for comp in self.languagePreprocessorComponents_[lang]:
                if comp == "tokenizer":
                    continue
                dataToSave[lang][comp] = list(self.languagePreprocessorComponents_[lang][comp])
        with open(os.path.join(folder, "data.json"), "w") as fp:
            json.dump(dataToSave, fp)

    def loadThisObjectDataOnly_(self, folder):
        dataToLoad = None
        with open(os.path.join(folder, "data.json"), "r") as fp:
            dataToLoad = json.load(fp)
        for lang in dataToLoad:
            for comp in dataToLoad[lang]:
                self.languagePreprocessorComponents_[lang][comp] = set(dataToLoad[lang][comp])

# FIELDS:

    languagePreprocessorComponents_ = initLanguagePreprocessorComponents()

    allPos_ = set(["ADJ", "ADV", "INTJ", "NOUN", "PROPN", "VERB",
                   "ADP", "AUX", "CCONJ", "DET", "NUM", "PART",
                   "PRON", "SCONJ", "PUNCT", "SYM", "X"])

    morph_ = pymorphy2.MorphAnalyzer()
    
    
TextPreprocessor.initNewRootOfInheritance()
TextPreprocessor.registerClass()

