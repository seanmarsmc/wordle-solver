FILE = "words.txt"
WORD_SIZE_LIMIT = 5
ABC_LIST = "abcdefghijklmnopqrstuvwxyz" 
VERBOSE = False

def wordle_solver():
    words = get_words()
    first_call = True

    output_bits = ""
    user_word = ""
    rounds = 0
    while output_bits != "ggggg" and rounds < 6:
        #print stats
        letter_count = count_individual_letters(words)
        if VERBOSE:
            print(f"Round #{rounds} --- Total Words: {len(words)} --- Total Letters: {len(words) * 5}")
            print_frequecy(letter_count,len(words) * 5)

        #print best guess
        if first_call:
            print("Recommended first guess: slate")
        else:
            word_scores = calculate_word_score(words,letter_count)
            best_word,max_score = get_best_scores(word_scores,words)
            if VERBOSE:
                print(f"Best word: {str(best_word).strip()} with score: {max_score}")

        #user input
        output_bits = ""
        user_word = ""
        while len(user_word) != WORD_SIZE_LIMIT: 
            user_word = input("enter a word: ")
        while len(output_bits) != WORD_SIZE_LIMIT:
            if first_call:
                print("b = black = letter dne, y = yellow = letter exists, g = green = correct letter")
                first_call = not first_call
            output_bits = input("enter the bits of information: ")

        #cull words
        if output_bits != "ggggg":
            words = cull_words(words,output_bits,user_word)
        rounds += 1
        #if len(words) == 1:
            #print("The word is",words[0])

    print("GAME OVER\nScore:", rounds)

# CORE FUNCTIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_best_scores(word_scores,possible_words):
        max_score = float("inf")
        best_word = ""
        for word in possible_words:
            if word_scores[word] < max_score:
                max_score = word_scores[word]
                best_word = word
        return best_word.strip(),max_score

def cull_words(possible_words:list,output_bits:str,guess:str):
    """cull words that don't have letters that match the output bits"""
    black_letters = black_letter_finder(output_bits,guess)
    green_letters = green_letter_finder(output_bits,guess)
    yellow_letters = yellow_letter_finder(output_bits,guess)
    passing_letters = []
    for green in green_letters:
        passing_letters.append(green[0])
    for yellow in yellow_letters:
        passing_letters.append(yellow[0])

    if VERBOSE:
        print("Culling words with black letters...")
    passing_words1 = []
    for word in possible_words:
        check = False
        for black_letter in black_letters:
            if black_letter in word:
                if black_letter in passing_letters:
                    pass
                else:
                    check = True
                    break
        if not check:
            passing_words1.append(word)
    if VERBOSE:
        print(f"Culled {len(possible_words)-len(passing_words1)}")

    if VERBOSE:
        print("Culling words that don't have green letters in the correct position...")
    passing_words2 = []
    for word in passing_words1:
        check = False
        for green_letter in green_letters:
            if word[green_letter[1]] != green_letter[0]: 
                check = True
                break
        if not check:
            passing_words2.append(word)
    if VERBOSE:
        print(f"Culled {len(passing_words1)-len(passing_words2)} words")

    if VERBOSE:
        print("Culling words that have yellow letters wrong position...") 
    passing_words3 = []
    for word in passing_words2:
        check = False
        for yellow_letter in yellow_letters:
            if word[yellow_letter[1]] == yellow_letter[0]: 
                check = True
                break
        if not check:
            passing_words3.append(word)
    if VERBOSE:
        print(f"Culled {len(passing_words2)-len(passing_words3)} words")

    if VERBOSE:
        print("Culling words that don't have all the passing letters...") 
    passing_words4 = []
    for word in passing_words3:
        check = False
        for passing_letter in passing_letters:
            if passing_letter not in word:
                check = True
                break
        if not check:
            passing_words4.append(word)
    if VERBOSE:
        print(f"Culled {len(passing_words3)-len(passing_words4)} words")

    if VERBOSE:
        print("Culling words that have black letters when yellow or green letters are in correct position...") 
    passing_words5 = []
    for word in passing_words4:
        check = False
        for black_letter in black_letters:
            if black_letter in passing_letters:
                if word.count(black_letter) != passing_letters.count(black_letter):
                    check = True
                    break
        if not check:
            passing_words5.append(word)
    if VERBOSE:
        print(f"Culled {len(passing_words4)-len(passing_words5)} words")

    return passing_words5

def black_letter_finder(output_bits,guess):
    """Find black letters that do not exist in the guess"""
    black_letters = []
    for idx in range(WORD_SIZE_LIMIT):
        if output_bits[idx] == "b":
            black_letters.append(guess[idx])
    return black_letters

def green_letter_finder(output_bits,guess):
    """Find green letters that are in the correct position"""
    green_letters = []
    for idx in range(WORD_SIZE_LIMIT):
        if output_bits[idx] == "g":
            green_letters.append([guess[idx],idx])
    return green_letters

def yellow_letter_finder(output_bits,guess):
    """Find yellow letters that exist in the guess but are not in the correct position"""
    yellow_letters = []
    for idx in range(WORD_SIZE_LIMIT):
        if output_bits[idx] == "y":
            yellow_letters.append([guess[idx],idx])
    return yellow_letters


#thanks to this https://github.com/sjw269/Wordle-Solver/blob/main/wordle_solver.py
def calculate_word_score(possible_words, frequencies):
    words = {}
    max_freq = [0, 0, 0, 0, 0]
    for c in frequencies:
        for i in range(0, 5):
            if max_freq[i] < frequencies[c][i]:
                max_freq[i] = frequencies[c][i]
    for w in possible_words:
        score = 1
        for i in range(0, 5):
            c = w[i]
            score *= 1 + (frequencies[c][i] - max_freq[i]) ** 2
        words.update({w: score})
        import numpy
        score += numpy.random.uniform(0, 1)     # this will increase expectation from 2.95 to 3.23, but is technically fairer
    return words

# SETUP ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_words():#get all words from FILE
    file = open(FILE,"r")
    words = [word.strip() for word in file.readlines()]
    words.sort()
    file.close()
    return words

def count_individual_letters(words:list):#count the number of letters
    letter_count = {}
    for _, letter in enumerate(ABC_LIST):
        letter_count[letter] = [0,0,0,0,0]

    for word in words:
        word = word.rstrip()
        for idx in range(WORD_SIZE_LIMIT):
            letter = word[idx]
            letter_count[letter][idx] += 1
    letter_count = dict(sorted(letter_count.items(),key=lambda item: sum(item[1]),reverse=True))
    return letter_count

def print_frequecy(dict_of_letters:dict,total_letter_count:int):#print letter, count and frequency
    print("rnk".ljust(4), "ltr".ljust(1),"col 0".ljust(6),"col 1".ljust(6),"col 2".ljust(6),"col 3".ljust(6),"col 4".ljust(9),"ttl".ljust(7),"freq")
    count = 0
    rank = 0
    for key, array in list(dict_of_letters.items()):
        curr_total = 0
        rank += 1
        print(f"{str(rank).ljust(4)} {str(key).ljust(3).capitalize()}",end=" ")
        for idx in array:
            print(f"{str(idx).ljust(6)}",end=" ")
            count+= idx
            curr_total += idx
        if total_letter_count > 0:
            frequency = round(((curr_total/total_letter_count)*100),3)
        else:
            frequency = 0
        print(f"   {str(curr_total).ljust(5)}   {frequency}%")
    return count


if __name__ == "__main__":
    wordle_solver()
