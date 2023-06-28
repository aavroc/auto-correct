# class to validate a text based on a string of words
# any word must appear in order in the text all words are checked and the last match is the position pos (pos starts with the value 0)
# any !word may not appear after pos
# any group of words in between () is a any-order-group this group can appear in any order after pos
# any group of words in between [] is a or-group, this group is an or-group any words that matched validates.
# note a word match means that the given search string portial matches a word in teh text, match is cae insensitive

# self.match (Turue or False depending of teh validation)
# self.matchedWords numer of words that matched (=validated)

# Technical Info
# The string is first parsed in a list of lists with two elements, the command and the argument
# The commands are ?, !, a, o for match one word, negative match, any order group (), or group []
# example output from parser is: [['?', 'word1'], ['!', 'word2'], ['?', 'word3'], ['a', 'word4 word6 word5']]
# After this parsing this list of lists is parsed per command-argument couple. Each commnd has its own method
# This "command-method" returned the new position of where we are at the text. -1 one means we failed to match
# The validation method keeps a tab on the number of matched words and returns true/flase and teh number of words matched.


class TextValidation:
    def __init__(self, text, words):
        self.parsedCommand = self.parseWords(words)
        print(f"Parsed result: {self.parsedCommand}")
        result = self.validate(text, self.parsedCommand)
        print(f"Validated result: {result}")
        (self.match, self.wordsMatched) = result

    def parseWords(self, words):
        output = []
        status = "normal"
        for word in words:
            if word == "":
                continue
            if word.startswith("(") or word.startswith("["):
                status = "group"
                group = word[1:]
            elif word.endswith(")"):
                status = "normal"
                group += " " + word[:-1]
                output.append(["a", group])
            elif word.endswith("]"):
                status = "normal"
                group += " " + word[:-1]
                output.append(["o", group])
            elif word[0] == "!":
                output.append(["!", word[1:]])
            else:
                if status == "normal":
                    output.append(["?", word])
                elif status == "group":
                    group += " " + word

        return output  # example output: [['?', 'word1'], ['!', 'word2'], ['?', 'word3'], ['a', 'word4 word6 word5']]

    def validate(self, text, words):
        pos = 0
        wordsMatched = 0

        for item in words:
            thisCommand = item[0]
            thisArgument = item[1].split()

            if thisCommand == "?":  # positive word seach
                pos = self.checkPositveWord(text, pos, thisArgument[0])
                if pos >= 0:
                    wordsMatched += 1
                else:
                    break

            if thisCommand == "!":  # negative word search
                pos = self.checkNegativeWord(text, pos, thisArgument[0])
                if pos >= 0:
                    wordsMatched += 1
                else:
                    break

            if thisCommand == "a":  # any order group
                pos = self.checkAnyOrderGroup(text, pos, thisArgument)
                if pos >= 0:
                    wordsMatched += len(thisArgument)
                else:
                    break

            if thisCommand == "o":  # or group
                pos = self.checkOrGroup(text, pos, thisArgument)
                if pos >= 0:
                    wordsMatched += len(thisArgument)
                else:
                    break

        if pos >= 0:
            return (True, wordsMatched)
        else:
            return (False, wordsMatched)

    # Case insensitive partial search and returns -1 if no match, otherwise return position just after the match in the text.
    def findLastPos(self, text, word, pos):
        pos = text.lower().find(word.lower(), pos)
        if pos < 0:
            return pos
        return pos + len(word)

    def checkPositveWord(self, text, pos, word):
        pos = self.findLastPos(text, word, pos)
        return pos

    def checkNegativeWord(self, text, pos, word):
        negative_search_pos = self.findLastPos(text, word, pos)
        if negative_search_pos > 0:
            return -1
        else:
            return pos

    def checkOrGroup(self, text, pos, words):
        max_pos = -1
        for word in words:
            temp_pos = self.findLastPos(text, word, pos)
            max_pos = max(max_pos, temp_pos)
        if max_pos < 0:
            return pos
        return max_pos

    def checkAnyOrderGroup(self, text, pos, words):
        max_pos = -1
        for word in words:
            temp_pos = self.findLastPos(text, word, pos)
            max_pos = max(max_pos, temp_pos)
            if temp_pos < 0:
                return temp_pos

        return max_pos