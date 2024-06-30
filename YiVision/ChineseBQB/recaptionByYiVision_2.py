import base64
import requests
import os
import json
import shutil
import time
import jsonlines
import re

IMAGE_DIR = r"J:\yi\pickedImages"
ERROR_DIR = r"J:\yi\pickedImages_error"
PROCESSED_DIR = r"J:\yi\pickedImages_processed"
JSONL_FILE = "J:\yi\yivision\ChineseBQB_picked_yivision.jsonl"

def image_to_base64(file_path):
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string.decode("utf-8")

def extract_zhutiandwenzi(image_name):
    cleaned_name = re.sub(r"\d{5}", "", image_name)
    cleaned_name = os.path.splitext(cleaned_name)[0]
    zhutiandwenzi = cleaned_name.strip().strip(".")
    return zhutiandwenzi

def split_zhutiandwenzi(zhutiandwenzi):
    parts = zhutiandwenzi.split("-", 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    else:
        return "", ""

def main():
    image_paths = [os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR) if
                   os.path.isfile(os.path.join(IMAGE_DIR, f))]
    for image_path in image_paths:
        zhutiandwenzi = extract_zhutiandwenzi(os.path.basename(image_path))
        zhuti, wenzi = split_zhutiandwenzi(zhutiandwenzi)
        content_list = list()
        content_list.append({
            "type": "text",
            "text": f"""你是一位有深度的网络图片解读者，擅长解读和描述网络图片。你能洞察图片中的细微之处，对图中的人物面部表情、文字信息、情绪流露和背景寓意具有超强的理解力，描述信息需要详细。为了帮助你更好的理解图中信息，我已经将图中主题和文字信息摘要出来，主题:{zhuti},文字:{wenzi}。你返回的描述中必须包含我提供的主题和文字，不得删除和修改。"""
        })
        content_list.append({
            "type": "image_url",
            "image_url": {
                "url": "data:image/jpeg;base64," + image_to_base64(image_path)
            }
        })
        url = "https://api.lingyiwanwu.com/v1/chat/completions"
        body = {
            "model": "yi-vision",
            "messages": [
                {
                    "role": "user",
                    "content": content_list
                }
            ],
            "stream": False
        }
        try:
            response = requests.post(url, headers={
                "Authorization": "Bearer XXXXXXXXXXXXXXXXXXXXXXX"}, json=body)
            response_json = response.json()
            print("response_json:", response_json)
            content = response_json['choices'][0]['message']['content']
            result = {
                "picName": os.path.basename(image_path),
                "description": content
            }
            with jsonlines.open(JSONL_FILE, mode='a') as writer:
                writer.write(result)
            shutil.move(image_path, os.path.join(PROCESSED_DIR, os.path.basename(image_path)))
            os.utime(os.path.join(PROCESSED_DIR, os.path.basename(image_path)), (time.time(), time.time()))
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            shutil.move(image_path, os.path.join(ERROR_DIR, os.path.basename(image_path)))
            os.utime(os.path.join(ERROR_DIR, os.path.basename(image_path)), (time.time(), time.time()))
if __name__ == '__main__':
    main()
