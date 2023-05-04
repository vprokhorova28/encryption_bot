def get_bigrams(input_text, alphabet_set):
    occurrence = {}
    num_all_letters = 0
    for letter in alphabet_set:
        occurrence[letter] = 0
    for character in input_text.lower():
        if character not in alphabet_set:
            continue
        num_all_letters += 1
        if character not in occurrence:
            occurrence[character] = 0
        occurrence[character] += 1
    for letter in occurrence:
        if letter == 'ё':
            occurrence['е'] += (occurrence['ё'] / num_all_letters) * 100
            occurrence['ё'] = 0
        occurrence[letter] = (occurrence[letter] / num_all_letters) * 100
    return occurrence
