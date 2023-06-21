import re

def validate_text(text, words):
    pattern = r"\b{}\b".format(r"\b|\b".join(map(re.escape, words)))
    matches = re.findall(pattern, text)

    print(pattern)
    print (matches)
    
    # Validate the order of words
    index = 0
    for match in matches:
        if match == words[index]:
            index += 1
            if index == len(words):
                return True
    return False

# Example usage
text = "xxxx word1 xxx xxxx word2 xxx word4 xxx word3 word5"
word_list = ["word1", "word2", "(word3 word4)", "word5"]

valid = validate_text(text, word_list)
print(valid)  # Output: True
