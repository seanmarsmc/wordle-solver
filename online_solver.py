from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import argparse
from wordle_solver import *

parser = argparse.ArgumentParser(description="Play Wordle Automagically")
parser.add_argument("--headless", help="Run in headless mode", action="store_true")
parser.add_argument("--guess", type=str, help="Guess a first word",default="slate")
args = parser.parse_args()
HEADLESS = not args.headless

def setup_online_solver():
    url = "https://www.nytimes.com/games/wordle/index.html"
    play_button_xpath = "/html/body/div[2]/div/div/div/div/div[2]/button[2]"
    x_button_xpath = "/html/body/div[2]/div/dialog/div/div/button"
    chrome_options = Options()
    if HEADLESS:
        chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    button = driver.find_element(By.XPATH, play_button_xpath)
    button.click()
    sleep(1)
    button = driver.find_element(By.XPATH, x_button_xpath)
    button.click()
    sleep(1)
    return driver

def play_game(driver: webdriver.Chrome):
    guess = args.guess.lower()
    game_board = driver.find_element(By.TAG_NAME, "body")
    possible_words = get_words()
    for i in range(1,7):
        row_xpath = f"/html/body/div[2]/div/div[4]/main/div[1]/div/div[{i}]"
        game_board.send_keys(guess)
        game_board.send_keys(Keys.RETURN)
        sleep(3)
        colors = get_color(driver,row_xpath)
        if colors == "ggggg":
            print("Answer:",guess.upper())
            break
        print(f"Guessing {guess.upper()} {colors.upper()}")
        possible_words = cull_words(possible_words,colors,guess)
        frequencies = count_individual_letters(possible_words)
        word_scores = calculate_word_score(possible_words, frequencies)
        guess,max_score = get_best_scores(word_scores,possible_words)
    driver.quit()

def get_color(driver: webdriver.Chrome,row_xpath):
    #guess = driver.find_element(By.XPATH, row_xpath).text
    #guess = guess.replace("\n","").strip().lower()
    #print(guess)
    colors = ""
    for i in range (1,6):
        tile_xpath = row_xpath + f"/div[{i}]/div"
        tile = driver.find_element(By.XPATH, tile_xpath)
        data_state = tile.get_attribute("data-state")
        #print(data_state)
        if data_state == "correct":
            colors = colors + "g"
        elif data_state == "present":
            colors = colors + "y"
        elif data_state == "absent":
            colors = colors + "b"
        else:
            print("Error")
    return colors #byyby

if __name__ == "__main__":
    driver = setup_online_solver()
    play_game(driver)