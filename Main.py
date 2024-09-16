from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import re
import threading

# Initialize global variables
highest = 0
processed_enemies = set()
running = False
score = 0
game_ended_flag = False

# Open user's downloaded browser
def get_browser():
    brow = input("Which is your preferred Web Browser? 1: Firefox 2: Chrome 3: Edge 4: Safari 5: Other \n")
    global driver
    try:
        match int(brow):
            case 1:
                print("Initializing Firefox")
                driver = webdriver.Firefox()
            case 2:
                print("Initializing Chrome")
                driver = webdriver.Chrome()
            case 3:
                print("Initializing Edge")
                driver = webdriver.Edge()
            case 4:
                print("Initializing Safari")
                driver = webdriver.Safari()
            case 5:
                print("Only these three browsers are currently supported. Check back at a later time or switch browsers.")
            case _:
                print("Invalid input. Please enter a number 1-4")
    except:
        print("Invalid input. Please enter a number 1-4")

# Converts hexadecimal values to binary
def hex_to_bin(hex):
    return {index: value for index, value in enumerate([int(n) for n in bin(int(hex, 16))[2:].zfill(8)])}

# Inputs the corresponding key for each binary value
def game_inputs(bin):
    element_other = driver.find_element(By.TAG_NAME, "body")
    
    # Iterate through the binary dictionary and send keys
    for index, value in bin.items():
        if value == 1:
            element_other.send_keys(str(index+1))

# Finds enemy closest to the ground and returns hex value
def find_lowest_enemy_hex():
    id_pattern = re.compile(r'enemy-(\d+)' )
    enemies = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "enemy"))
    )
    if not enemies:
        return None

    lowest_number = float('inf')
    lowest_enemy = None

    for enemy in enemies:
        try:
            enemy_id = enemy.get_attribute("id")
            match = id_pattern.search(enemy_id)
            if match:
                number = int(match.group(1))
                if number not in processed_enemies and number < lowest_number:
                    lowest_number = number
                    lowest_enemy = enemy
        except:
            continue

    if lowest_enemy:
        processed_enemies.add(lowest_number)
        return lowest_enemy.text


# Checks if game has ended yet
def check_running():
    global running, score, game_ended_flag
    while running:
        end = input("Press Q to end the script\n")
        try:
            score = int(driver.find_element(By.ID, "score").text)
        except:
            pass
        if end.lower() == "q" or score == "99" or score == "100":
            running = False
            game_ended()
        if float(driver.find_element(By.ID, "game-over").value_of_css_property("opacity")) != 0:
            game_ended_flag = True
            running = False

def start_game():
    time.sleep(5.6)
    element = driver.find_element(By.CLASS_NAME, "tapper")
    element.click()

def restart_game():
    global processed_enemies
    processed_enemies = set()
    global running
    running = True


def update_highscore(new_score):
    global highest
    highest = max(highest, new_score)

# Lets user select what to do once game has ended
def game_ended():
    global highest
    if score >= 99:
        new = input(f"Congratulations! You beat the game with a score of {score}!\nWould you like to play again? Y/N")
        match new.lower():
            case "y":
                driver.refresh()
                time.sleep(6)
                start_game()
                restart_game()
            case "n":
                driver.quit()
            case _:
                print("Invalid input. Closing game.")
                driver.quit()
    elif score > highest:
        new = input(f"Game Over! Your score is {score}! You beat your highscore of {highest}!\nWould you like to play again? Y/N")
        update_highscore(score)
        match new.lower():
            case "y":
                driver.refresh()
                time.sleep(6)
                start_game()
                restart_game()
            case "n":
                driver.quit()
            case _:
                print("Invalid input. Closing game.")
                driver.quit()
    else:
        new = input(f"Game Over! Your score is {score}!\nWould you like to play again? Y/N")
        match new.lower():
            case "y":
                driver.refresh()
                time.sleep(6)
                start_game()
                restart_game()
            case "n":
                driver.quit()
            case _:
                print("Invalid input. Closing game.")
                driver.quit()

# Plays game and runs game_ended() when complete
def playing():
    global running, game_ended_flag
    game_ended_flag = False

    while running and not game_ended_flag:
        enemy_id = find_lowest_enemy_hex()
        if enemy_id is None:
            # Use WebDriverWait to pause only until a new enemy appears
            try:
                WebDriverWait(driver, 0.1).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "enemy"))
                )
            except TimeoutException:
                pass
        else:
            game_inputs(hex_to_bin(enemy_id))

    if game_ended_flag:
        game_ended()


# Opens browser
get_browser()

# Opens website
driver.get("https://flippybitandtheattackofthehexadecimalsfrombase16.com/")

# Selects the place to input keys and starts game
start_game()
running = True

# Start check_running in a separate thread
check_thread = threading.Thread(target=check_running)
check_thread.start()

# Plays game
playing()

# Wait for the check_running thread to finish
check_thread.join()
