import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import threading

# Open user's downloaded browser
def get_browser():
    brow = input("Which is your preferred Web Browser? 1: Firefox 2: Chrome 3: Edge 4: Other \n")
    global driver
    try:
        match int(brow):
            case 1:
                driver = webdriver.Firefox()
            case 2:
                driver = webdriver.Chrome()
            case 3:
                driver = webdriver.Edge()
            case 4:
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
    element_other = driver.find_element(By.ID, "dock") 
    for index, value in bin.items():
        if value == 1:
            element_other.send_keys(str(index))

# Finds enemy closest to the ground and returns hex value
def find_lowest_enemy_hex():
    enemies = driver.find_elements(By.CLASS_NAME, "enemy")
    
    if not enemies:
        return None
    
    lowest_number = float('inf')
    lowest_enemy = None
    id_pattern = re.compile(r'enemy-(\d+)')
    
    for enemy in enemies:
        enemy_id = enemy.get_attribute("id")
        match = id_pattern.search(enemy_id)
        if match:
            number = int(match.group(1))
            if number < lowest_number:
                lowest_number = number
                lowest_enemy = enemy
    
    if lowest_enemy:
        return lowest_enemy.text
    return None

# Checks if game has ended yet
def check_running():
    global running, score
    while running:
        time.sleep(0.1)
        if float(driver.find_element(By.ID, "game-over").value_of_css_property("opacity")) != 0:
            score = driver.find_element(By.ID, "score").text
            global game_ended_flag
            game_ended_flag = True
            running = False

# Lets user select what to do once game has ended
def game_ended():
    if score > highscore:
        new = input(f"Game Over! Your score is {score}! You beat your highscore of {highscore}!\nWould you like to play again? Y/N")
        match new.lower():
            case "y":
                pass
            case "n":
                pass
            case _:
                print("Invalid input. Closing game.")

# Plays game and runs game_ended() when complete
def playing():
    global highscore, running, game_ended_flag
    # Loads Highscore
    highscore = driver.find_element(By.ID, "highscore").text
    game_ended_flag = False

    while running and not game_ended_flag:
        enemy_id = find_lowest_enemy_hex()
        if enemy_id is None:
            time.sleep(1)
        else:
            game_inputs(hex_to_bin(enemy_id))
    if game_ended_flag:
        game_ended()

# Opens browser
get_browser()

# Opens website
driver.get("https://flippybitandtheattackofthehexadecimalsfrombase16.com/")

# Waits for game to initialize
time.sleep(6)

# Selects the place to input keys and starts game
element = driver.find_element(By.CLASS_NAME, "tapper")
element.click()

# Initialize game status
global running
running = True

# Start check_running in a separate thread
check_thread = threading.Thread(target=check_running)
check_thread.start()

# Plays game
playing()

# Wait for the check_running thread to finish
check_thread.join()
