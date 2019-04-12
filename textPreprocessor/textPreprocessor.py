import os
import re
import json
from nltk.corpus import stopwords
import spacy
import pymorphy2
from polyglot.detect import Detector

import serializableClass

from .textTokenizer import TextTokenizerSpacyBased
from .textTokenizer import TextTokenizerRus

initializeFollowingLanguageProcessors = ["un", "en", "de", "es", "pt", "fr", "it", "nl", "ru"]

def initLanguageTokenizers(listOfSupportedLanguages):
    languageTokenizers = {}

    for lang in listOfSupportedLanguages:
        if lang == "un":
            languageTokenizers["un"] = TextTokenizerSpacyBased()
            languageTokenizers["un"].setLinguisticProcessor(spacy.load('xx'))
        elif lang == "ru":
            languageTokenizers["ru"] = TextTokenizerRus()
        else:
            languageTokenizers[lang] = TextTokenizerSpacyBased()
            languageTokenizers[lang].setLinguisticProcessor(spacy.load(lang))

    return languageTokenizers

def getParametersDict():
    parametersDict = {}
    parametersDict["caseSensitive"] = False
    parametersDict["stopPos"] = set()
    parametersDict["stopTokens"] = set()
    parametersDict["stopTokensLower"] = set()
    parametersDict["stopLemmas"] = set()

    return parametersDict

def initLanguageTokenizeParameters(listOfSupportedLanguages):
    languageTokenizeParameters = {}

    for lang in listOfSupportedLanguages:
        languageTokenizeParameters[lang] = getParametersDict()

    return languageTokenizeParameters

class TextPreprocessor(serializableClass.SerializableClass):
    def __init__(self):
        self.languageTokenizeParameters_ = initLanguageTokenizeParameters(initializeFollowingLanguageProcessors)
    
    def getFilteredTokens(self, text, lang):
        tokens = self.languageTokenizers_[lang].tokenize(text)
        res = []
        for t in tokens:
            if re.search(r"[\W\d]", t.text):  # if token is not a word (not consist of letters) then skip
                continue
            if t.lemma_ == "-PRON-":
                t.lemma_ = t.text.lower()
            if t.pos_ in self.languageTokenizeParameters_[lang]["stopPos"]:
                continue
            if self.languageTokenizeParameters_[lang]["caseSensitive"] == False:
                if t.text.lower() in self.languageTokenizeParameters_[lang]["stopTokensLower"]:
                    continue
            else:
                if t.text in self.languageTokenizeParameters_[lang]["stopTokens"]:
                    continue
            if t.lemma_ in self.languageTokenizeParameters_[lang]["stopLemmas"]:
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
        if lang not in self.languageTokenizers_ or lang=="un":
            lettersFromText = re.sub("[\W\d_]", "", text)
            if len(lettersFromText) == 0:
                if defaultLangIfNotDetected is not None:
                    lang = defaultLangIfNotDetected
                else:
                    lang = "en"
            elif re.match("^[A-Za-z]*$", lettersFromText):
                lang = "en"
            elif re.match("^[А-Яа-я]*$", lettersFromText):
                lang = "ru"
            elif defaultLangIfNotDetected is not None:
                lang = defaultLangIfNotDetected
            else:
                lang = "un"
        return lang

    def setInitialParametersAutomatically(self):
        self.setAllowedPos(["ADJ", "ADV", "INTJ", "NOUN", "PROPN", "VERB"])
        self.setStopLemmas(set(stopwords.words("russian")), "ru")
        self.setStopLemmas(set(stopwords.words("english")), "en")

# SETTERS AND GETTERS:

    def setCaseSensitive(self, caseSensitive, lang=None):
        if lang is None:
            for l in self.languageTokenizeParameters_:
                self.languageTokenizeParameters_[l]["caseSensitive"] = caseSensitive
        else:
            self.languageTokenizeParameters_[lang]["caseSensitive"] = caseSensitive
    def getCaseSensitive(self, lang):
        return self.languageTokenizeParameters_[lang]["caseSensitive"]

    def setStopPos(self, stopPos, lang=None):
        stopPos = set(stopPos)
        if lang is None:
            for l in self.languageTokenizeParameters_:
                self.languageTokenizeParameters_[l]["stopPos"] = stopPos
        else:
            self.languageTokenizeParameters_[lang]["stopPos"] = stopPos
    def setAllowedPos(self, allowed, lang=None):
        allowed = set(allowed)
        if lang is None:
            for l in self.languageTokenizeParameters_:
                self.languageTokenizeParameters_[l]["stopPos"] = self.allPos_ - allowed
        else:
            self.languageTokenizeParameters_[lang]["stopPos"] = self.allPos_ - allowed
    def getStopPos(self, lang):
        return self.languageTokenizeParameters_[lang]["stopPos"]

    def setStopTokens(self, stopTokens, lang):
        self.languageTokenizeParameters_[lang]["stopTokens"] = stopTokens
        for st in stopTokens:
            self.languageTokenizeParameters_[lang]["stopTokens"].add(st.lower())
    def getStopTokens(self, lang):
        return self.languageTokenizeParameters_[lang]["stopTokens"]

    def setStopLemmas(self, stopLemmas, lang, normalize=False):
        if normalize == True:
            normalized = []
            for sl in stopLemmas:
                morphRes = self.morph_.parse(sl)[0]
                normalized.append(morphRes.normal_form.lower())
            stopLemmas = set(normalized)
        else:
            stopLemmas = set([sl.lower() for sl in stopLemmas])
        self.languageTokenizeParameters_[lang]["stopLemmas"] = stopLemmas
    def getStopLemmas(self, lang):
        return self.languageTokenizeParameters_[lang]["stopLemmas"]

# SAVE AND LOAD:

    def saveThisObjectDataOnly_(self, folder):
        dataToSave = self.changeSetsToListsInLanguageTokenizeParametersDict(self.languageTokenizeParameters_)
        with open(os.path.join(folder, "data.json"), "w") as fp:
            json.dump(dataToSave, fp)

    def loadThisObjectDataOnly_(self, folder):
        dataToLoad = None
        with open(os.path.join(folder, "data.json"), "r") as fp:
            dataToLoad = json.load(fp)

        self.languageTokenizeParameters_ = self.changeListsToSetsInLanguageTokenizeParametersDict(dataToLoad)

        for lang in initializeFollowingLanguageProcessors:
            if lang not in self.languageTokenizeParameters_:
                self.languageTokenizeParameters_[lang] = getParametersDict()

# PRIVATE FUNCTIONS:

    def changeSetsToListsInLanguageTokenizeParametersDict(self, languageTokenizeParameters):
        res = {}
        for lang in languageTokenizeParameters:
            res[lang] = {}
            for param in languageTokenizeParameters[lang]:
                if type(languageTokenizeParameters[lang][param]) == set:
                    res[lang][param] = list(languageTokenizeParameters[lang][param])
                else:
                    res[lang][param] = languageTokenizeParameters[lang][param]

        return res

    def changeListsToSetsInLanguageTokenizeParametersDict(self, languageTokenizeParameters):
        res = {}
        for lang in languageTokenizeParameters:
            res[lang] = {}
            for param in languageTokenizeParameters[lang]:
                if type(languageTokenizeParameters[lang][param]) == list:
                    res[lang][param] = set(languageTokenizeParameters[lang][param])
                else:
                    res[lang][param] = languageTokenizeParameters[lang][param]

        return res

# FIELDS:

    languageTokenizers_ = initLanguageTokenizers(initializeFollowingLanguageProcessors)

    languageTokenizeParameters_ = None

    # https://universaldependencies.org/u/pos/index.html
    allPos_ = set(["ADJ", "ADV", "INTJ", "NOUN", "PROPN", "VERB",
                   "ADP", "AUX", "CCONJ", "DET", "NUM", "PART",
                   "PRON", "SCONJ", "PUNCT", "SYM", "X"])

    morph_ = pymorphy2.MorphAnalyzer()
    
    
TextPreprocessor.initNewRootOfInheritance()
TextPreprocessor.registerClass()

