import json
import numpy as np
import time
import sys

values = {
    "r": 0,
    "y": 1,
    "g": 2
}

def pattern_str_to_code(pattern):
    code = 0
    for i, letter in enumerate(pattern):
        code += (3**i) * values[letter]
    
    return code

def pattern_code_to_str(code):
    str_list = []
    chrs = list(values.keys())

    while (code > 0):
        str_list.append(chrs[int(code % 3)])
        code //= 3
        print(code)

    while (len(str_list) < 5):
        str_list.append("r")

    return ''.join(str_list)

def row_entropy(row):
    
    _, counts = np.unique(row, return_counts=True)
    probs = counts / len(row)

    entropies = np.log2(probs) * probs
    
    return - np.sum(entropies)

def pattern_is_valid(pattern):
    allowed = {'r', 'g', 'y'}
    return len(pattern) == 5 and all(char in allowed for char in pattern)

def get_input(prompt_text):
    if sys.stdout.isatty():
        return input(prompt_text)
    else:
        return input()

def best_guess(Matrix, C):

    entropies = [row_entropy(np.array(row)) for row in Matrix[:, C]]

    best_guesses = np.argsort(entropies)[::-1][:10]
    best_entropies = np.sort(entropies)[::-1][10:]

    return [best_guesses, best_entropies]


if __name__ == "__main__":

    with open('words_json/targets_5_letter.json', 'r') as f:
        targets = json.load(f)  # Size A

    with open('words_json/dictionary_5_letter.json', 'r') as f:
        guesses = np.array(json.load(f))  # Size G

    G = len(guesses)
    A = len(targets)


    guess_to_idx = {word: i for i, word in enumerate(guesses)}
    target_to_idx = {word: i for i, word in enumerate(targets)}
    
    Matrix = np.load('matrix.npy')

    active_indices = list(range(len(targets)))

    current_guess_idx = -1
    current_entropy = 0
    found = False
    round_number = 1

    print()
    print("        Wordle Solver | Made By Ali Tarek")
    print()

    while True:

        print(f"-------------------- Round {round_number} ---------------------")
        print(f"[i] Remaining answers: {len(active_indices)}")
        
        new_current_entropy = np.round(np.log2(len(active_indices)), 3)
        entropy_gained = np.round(current_entropy - new_current_entropy, 3)
        current_entropy = new_current_entropy

        print(f"[i] Current entropy: {current_entropy} bits")

        print(f"[i] Actual Information gained (Surprise): {entropy_gained if current_guess_idx != -1 else 0} bits")

        print("--------------------------------------------------")


        print(f"[+] Processing Guesses...")

        if not found:
            start = time.time()

            best_guesses_list = best_guess(Matrix, active_indices)
            best_guesses = guesses[best_guesses_list[0]]
            best_entropies = np.round(best_guesses_list[1], 4)
            
            end = time.time()
            
            print(f"[+] Finished in: {np.round(end - start, 2)}s")
        
        if not found:
            print()
            print(f"Top suggestions:")
            for i in range(10):
                print("    " if i < 9 else "   ", end = "")
                print(f"{i+1}. {best_guesses[i]}    Entropy = {best_entropies[i]}")

            print()

            print(f"[i] Expected Best-Guess Entropy (Information gain): {np.round(best_entropies[0], 3)} bits")
            print(f"[i] Expected posterior entropy using the best-guess: {np.round(current_entropy - best_entropies[0], 3)} bits")

            print()
            print(f"BEST={best_guesses[0]}")

        else:
            print(f"[i] Only one answer remains: {targets[active_indices[0]]}")
            print()
            print(f"BEST={targets[active_indices[0]]}")
            break

        while True:
            guess = get_input("[?] Guess: ").strip().lower()
            if guess in guess_to_idx:
                current_guess_idx = guess_to_idx[guess]
                break
            print(f"[!] Error: '{guess}' is not in the dictionary. Try again.")

        while True:
            feedback_str = get_input("[?] Feedback: ").strip().lower()
            if pattern_is_valid(feedback_str):
                feedback = pattern_str_to_code(feedback_str)
                break
            print("[!] Error: Pattern must be 5 chars using only r, g, y (e.g., rgyrr). Try again.")


        new_active_indices = []
        for i, fb in enumerate(Matrix[current_guess_idx]):
            if fb == feedback and i in active_indices:
                new_active_indices.append(i)

        active_indices = new_active_indices.copy()
        
        if len(active_indices) == 1:
            found = True

        elif len(active_indices) == 0:
            print("\n[!] Contradiction Error")
            print("There are no words in the dictionary that satisfy the feedback for the previous guesses.")
            print("This usually means a previous feedback entry was incorrect.")
            break
        
        round_number += 1
        if round_number > 6:
            print("[!] No more rounds exist.")
            break
        