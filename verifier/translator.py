from collections import defaultdict

class Translator:
    _text = {
        # "<key>": {
        #     "<lang-code>": "<translation>"
        # }
    }

    def __init__(self, language="en"):
        self.language = language

    def t(self, key):
        """ Return text objects in the right language """
        return self._text[key].get(self.language, key)

    def bool_to_text(self, bool):
        return self.t("true") if bool else self.t("false")

