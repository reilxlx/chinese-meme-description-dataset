import os
import time
import json
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

chromedriver_path = 'J:\\chromedrive\\chromedriver-win64\\chromedriver.exe'
coze_url = "https://www.coze.com/space/****************/bot/****************"
image_folder = r"J:\\gpt4o\\meme"
processed_image_folder = r"J:\\gpt4o\\processed_meme"
output_file = r"J:\\gpt4o\\descriptions_meme.jsonl"
def check_stop_responding_message(driver):
    try:
        message_element = driver.find_element(By.XPATH, "//span[contains(text(), 'Stop Responding')]")
        return message_element.is_displayed()
    except NoSuchElementException:
        return False
def clear_chat_history(driver):
    try:
        clear_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='bot-edit-debug-chat-clear-button']"))
        )
        clear_button.click()
        print("Chat history cleared.")
    except NoSuchElementException:
        print("Clear button not found.")
    except Exception as e:
        print(f"Error while clearing chat history: {e}")
def main():
    options = Options()
    options.add_argument(
        r"user-data-dir=C:\\Users\\AppData\\Local\\Google\\Chrome\\User Data")
    driver = webdriver.Chrome(executable_path=chromedriver_path, chrome_options=options)
    driver.get(coze_url)
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH,
                                        "//button[@class='semi-button semi-button-primary semi-button-size-small semi-button-borderless jFUFZLij3En6W6yeM2Tc semi-button-with-icon semi-button-with-icon-only']"))
    )
    image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if
                   os.path.isfile(os.path.join(image_folder, f))]
    for i in range(0, len(image_paths), 6):
        batch_image_paths = image_paths[i:min(i + 6, len(image_paths))]

        for j, image_path in enumerate(batch_image_paths):
            file_input = WebDriverWait(driver, 180).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            file_input.send_keys(image_path)
            time.sleep(1)
        WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='bot-home-chart-send-button']"))
        )
        send_button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='bot-home-chart-send-button']")
        is_enabled = send_button.is_enabled()
        if is_enabled:
            send_button.click()
            time.sleep(3)
            pic_name = os.path.basename(image_path)
            print("pic_name:", pic_name)
            while check_stop_responding_message(driver):
                print("Waiting for 'Stop Responding' message to disappear...")
                time.sleep(5)
            paragraphs = WebDriverWait(driver, 60).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'chat-uikit-text-content'))
            )
            if paragraphs:
                last_paragraph = paragraphs[0]
                descriptions = last_paragraph.text
                print("Descriptions:", descriptions)
            else:
                descriptions = ""
                print("No descriptions found.")

            if descriptions == "You have exceeded the daily limit for sending messages to the bot. Please try again later.":
                print("Daily limit exceeded. Stopping the program.")
                driver.quit()
                return
            else:
                try:
                    descriptions_json = json.loads(descriptions)
                    for j, image_path in enumerate(batch_image_paths):
                        pic_name = os.path.basename(image_path)
                        description = descriptions_json.get(str(j + 1), "")
                        with open(output_file, 'a', encoding='utf-8') as f:
                            json.dump({"picName": pic_name, "description": description}, f, ensure_ascii=False)
                            f.write('\n')
                        shutil.move(image_path, os.path.join(processed_image_folder, pic_name))
                        print(f"Moved {pic_name} to {processed_image_folder}")
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    error_folder = "errors"
                    os.makedirs(error_folder, exist_ok=True)
                    shutil.move(image_path, os.path.join(error_folder, pic_name))
                    print(f"Moved {pic_name} to {error_folder} due to error.")
        else:
            print(f"图片 {batch_image_paths} 上传失败！")
            continue
        if (i // 6 + 1) % 24 == 0:
            clear_chat_history(driver)
        time.sleep(5)
    driver.quit()

if __name__ == "__main__":
    main()
