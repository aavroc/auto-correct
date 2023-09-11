# class to validate a text based on a string of words
# any word must appear in order in the text all words are checked and the last match is the position pos (pos starts with the value 0)
# any !word may not appear after pos
# any group of words in between () is a any-order-group this group can appear in any order after pos
# any group of words in between [] is a or-group, this group is an or-group any words that matched validates.
# note a word match means that the given search string portial matches a word in teh text, match is cae insensitive

# self.match (Turue or False depending of teh validation)
# self.matchedWords numer of words that matched (=validated)

class Validation:
    def __init__(self, text, words):
        self.parsedCommand = self.parseWords(words)
        result = self.validate(text, self.parsedCommand)
        (self.match, self.wordsMatched) = result
    
    def parseWords(self, words):
        output=[]
        status='normal'
        for word in words:
            if ( word.startswith( "(" ) or word.startswith( "[" ) ):
                status='group'
                group=word[1:]
            elif ( word.endswith( ")" ) ):
                status='normal'
                group+=' '+word[:-1]
                output.append(['a',group])
            elif ( word.endswith( "]" ) ):
                status='normal'
                group+=' '+word[:-1]
                output.append(['o',group])
            elif ( word[0] == '!' ):
                output.append(['!',word[1:]])
            else:
                if status == 'normal':
                    output.append(['?',word])
                elif status == 'group':
                    group+=' '+word
       
        return output  # example output: [['?', 'word1'], ['!', 'word2'], ['?', 'word3'], ['a', 'word4 word6 word5']]


    def validate(self, text, words):

        pos=0
        wordsMatched=0

        for item in words:
            thisCommand = item[0]
            thisArgument = item[1].split()

            if thisCommand == '?' : # positive word seach
                pos = self.checkPositveWord(text,pos,thisArgument[0])
                if pos > 0 :
                    wordsMatched+=1
                else:
                    break

            if thisCommand == '!' : # negative word search
                pos = self.checkNegativeWord(text,pos,thisArgument[0])
                if pos > 0 :
                    wordsMatched+=1
                else:
                    break

            if thisCommand == 'a' : # any order group
                pos = self.checkAnyOrderGroup(text,pos,thisArgument)
                if pos > 0 :
                    wordsMatched+=len(thisArgument)
                else:
                    break

            if thisCommand == 'o' : # or group
                pos = self.checkOrGroup(text,pos,thisArgument)
                if pos > 0 :
                    wordsMatched+=len(thisArgument)
                else:
                    break
       
        if pos > 0:
            return (True, wordsMatched)
        else:
            return (False, wordsMatched)

    def checkPositveWord(self, text, pos, word):
        pos = text.lower().find(word.lower(), pos)
        return pos

    def checkNegativeWord(self, text, pos, word):
        negative_search_pos = text.lower().find(word.lower(), pos)
        if ( negative_search_pos > 0 ):
            return -1
        else:
            return pos

    def checkOrGroup(self, text, pos, words):
        max_pos = -1
        for word in words:
            temp_pos = text.lower().find(word.lower(), pos)
            max_pos=max(max_pos, temp_pos)
        return max_pos

    def checkAnyOrderGroup(self, text, pos, words):
        max_pos = -1
        for word in words:
            temp_pos = text.lower().find(word.lower(), pos)
            max_pos=max(max_pos, temp_pos)
            if temp_pos < 0:
                return temp_pos

        return max_pos





def validateWords(words, text):
    pos = 0
    negative_search = -1
    words_correct = 0

    for word in words:

        if ( word.startswith("(") and word.endswith(")") ):
            word=word[1:-1]
            anyorder_words = word.split()
            maxpos=0
            for anyorder_word in anyorder_words:
                temp_pos = text.lower().find(anyorder_word.lower(), pos)
                if ( temp_pos == -1 ):
                    maxpos = -1
                    break;
                maxpos = max(maxpos, temp_pos)
            pos = maxpos

        elif word and word[0] == '!':
            negative_search = text.lower().find(word[1:].lower(), pos)
        else:
            pos = text.lower().find(word.lower(), pos)

        if pos == -1 or negative_search != -1:
            # Word not found, stop searching
            pos = -1
            break
        else:
            words_correct+=1

    return words_correct, pos

# Test1
text = "xxxx word1 xxx xxxx word2 xxx word3 xxx word4 word 5 word 4 word word5 word6"

word_list = ["word1", "word2", "word3", "word4", "word5"]
valid = validateWords(word_list, text)
if ( valid != (3,-1) ):
    print(f'Test failed, {valid}')

word_list = ["word1", "word2", "word4", "word3", "word5"]
valid = validateWords(word_list, text)
if ( valid[0] != (5) ):
    print(f'Test failed, {valid}')

word_list = ["word1", "word2", "(word3 word4)", "word5"]
valid = validateWords(word_list, text)
if ( valid[0] != (4) ):
    print(f'Test failed, {valid}')

word_list = ["!word1", "word2", "(word3 word4)", "word5"]
valid = validateWords(word_list, text)
if ( valid[1] != (-1) ):
    print(f'Test failed, {valid}')

word_list = ["word1", "word2", "(word5 word3 word4)"]
valid = validateWords(word_list, text)
if ( valid[0] != (3) ):
    print(f'Test with {word_list} failed, output {valid}')

word_list = ["word1", "word2", "(word5 wordje3 word4)"]
valid = validateWords(word_list, text)
if ( valid[1] != (-1) ):
    print(f'Test with {word_list} failed, output {valid}')

word_list = ["word1", "!word2","word3", "(word4", "word6", "word5)"]
validation = Validation(text, word_list)

array_word_lists=[]
array_word_lists.append(["word1", "word2","word4"])
array_word_lists.append(["word1", "!word2","word3", "(word4", "word6", "word5)"])
array_word_lists.append(["word1", "word2","word3", "(w", "word6", "word5)"])
array_word_lists.append([])

for word_list in array_word_lists:
    validation = Validation(text, word_list)
    print()
    print(f"{text}")
    print(f"Word list: {word_list} \nParsed:{validation.parsedCommand}")
    print(f"Result: {validation.match}")
    print(f"Word Matched: {validation.wordsMatched}")
    print()