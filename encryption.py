import frequency_analysis
import russian_language_data


def get_shifted_letter(
        letter: str, shift: int, *,
        mapping: dict, alphabet: str, upper_alphabet: str,
        upper_lower_mapping: dict) -> str:
    if letter == '\xa0':
        return ' '
    # Assign lowered_letter = letter if letter is not in mapping
    lowered_letter = upper_lower_mapping.get(letter, letter)
    letter_index = mapping.get(lowered_letter)
    if letter_index is None:
        return letter
    new_letter_index = (letter_index + shift) % len(alphabet)
    if letter in upper_lower_mapping:
        return upper_alphabet[new_letter_index]
    return alphabet[new_letter_index]


def caesar_cipher(input_text: str, *,
                  shift: int, mode: int) -> str:
    # mode = 1 -> cipher
    # mode = -1 -> decipher
    if mode == -1:
        shift = -shift
    new_text = ''
    for character in input_text:
        character = \
            get_shifted_letter(character,
                               shift,
                               mapping=russian_language_data.RUSSIAN_ALPHABET_MAPPING,
                               alphabet=russian_language_data.RUSSIAN_ALPHABET,
                               upper_alphabet=russian_language_data.RUSSIAN_UPPER_ALPHABET,
                               upper_lower_mapping=russian_language_data.RUSSIAN_ALPHABET_UPPER_TO_LOWER_MAPPING
                               )
        new_text += character
    return new_text


def get_delta(
        distribution: dict,
        usual_distribution=russian_language_data.RUSSIAN_LETTERS_OCCURRENCE
) -> float:
    delta = 0
    usual_occurrence = sorted(usual_distribution.items(), key=lambda x: x[0])
    current_occurrence = sorted(distribution.items(), key=lambda x: x[0])
    for i in range(len(usual_occurrence)):
        delta += abs(usual_occurrence[i][1] - current_occurrence[i][1]) ** 2
    return delta


def get_shift(input_text: str):
    deltas_for_each_shift = []
    for i in range(russian_language_data.RUSSIAN_LETTERS_NUMBER):
        shifted_text = caesar_cipher(input_text, shift=i, mode=1)
        occurrence = frequency_analysis.get_bigrams(shifted_text,
                                                    russian_language_data.RUSSIAN_ALPHABET_SET)
        deltas_for_each_shift.append(get_delta(occurrence))
    min_delta = min(deltas_for_each_shift)
    return deltas_for_each_shift.index(min_delta)


def decipher(input_text: str) -> str:
    shift = get_shift(input_text)
    return caesar_cipher(input_text, shift=shift, mode=1)


def letter_shifted_with_vigener(
        letter: str, key: str, mode: int, *,
        mapping: dict, alphabet: str, upper_alphabet: str,
        upper_lower_mapping: dict) -> str:
    # mode = -1 -> decipher
    # mode = 1 -> cipher
    lowered_letter = upper_lower_mapping.get(letter, letter)
    letter_index = mapping.get(lowered_letter)
    key_letter_index = mapping.get(key)
    new_letter_index = \
        (letter_index + mode * key_letter_index) % len(alphabet)
    if letter in upper_lower_mapping:
        return upper_alphabet[new_letter_index]
    return alphabet[new_letter_index]


def vigener_cipher(input_text: str, *, key: str, mode: int) -> str:
    # mode = 1 -> cipher
    # mode = -1 -> decipher
    key = key.lower()
    key_character = 0
    new_text = ''
    for character in input_text:
        if not character.isalpha():
            new_text += character
            continue
        if character.isalpha() and \
                character.lower() not in russian_language_data.RUSSIAN_ALPHABET_SET:
            new_text += character
            continue
        new_text += letter_shifted_with_vigener(character,
                                                key[key_character],
                                                mode,
                                                mapping=russian_language_data.RUSSIAN_ALPHABET_MAPPING,
                                                alphabet=russian_language_data.RUSSIAN_ALPHABET,
                                                upper_alphabet=russian_language_data.RUSSIAN_UPPER_ALPHABET,
                                                upper_lower_mapping=russian_language_data.RUSSIAN_ALPHABET_UPPER_TO_LOWER_MAPPING)
        key_character += 1
        key_character %= len(key)
    return new_text

