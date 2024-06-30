import base64
import requests
import os
import json
import shutil
import time
import jsonlines

IMAGE_DIR = r"J:\yi\meme"
ERROR_DIR = r"J:\yi\meme_error"
PROCESSED_DIR = r"J:\yi\meme_processed"
JSONL_FILE = "J:\yi\yivision\image_descriptions_processed_yivision.jsonl"

def image_to_base64(file_path):
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string.decode("utf-8")

def main():
    image_paths = [os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR) if
                   os.path.isfile(os.path.join(IMAGE_DIR, f))]
    for image_path in image_paths:
        print(image_path)
        content_list = list()
        content_list.append({
            "type": "text",
            "text": """# 角色
你是一位有深度的网络图片解读者，擅长解读和描述网络图片，包括但不限于表情包、动漫图、卡通图片和真人图片。你能洞察图片中的细微之处，对图中的人物面部表情、文字信息、情绪流露和背景寓意具有超强的理解力，描述信息需要详细(尤其是文字需仔细识别并输出)。
## 技能
### 技能 1: 图片观察
- 仔细观察图片中所有的元素，包括人物表情、动作姿态、文字信息、背景寓意等，并尊重图中文字信息，不进行修改。
### 技能 2: 描述图片中的文字和信息
- 根据你的观察，用优雅的语言描述你所见的景象，描绘人物表情的微妙变化、动作姿态的含义、图片中的文字以及文字中蕴藏的情感，必须要详尽描述等。
### 技能 3: 解读情绪和信息
- 基于你对图片的深度理解，尝试探索图片试图传达的情绪和信息，然后用精妙的中文，用流畅的文字，将您的理解娓娓道来。
## 限制
- 你的分析和描述只限于图片内容，不得包含除图片以外的任何信息。
- 保持对图片中文字信息的尊重，不得进行任何修改。
- 你的描述和解读应以中文进行，且言辞要优雅，逻辑要清晰。"""
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
                "Authorization": "Bearer XXXXXXXXXXXXXXXXXXXXXXXXXXXX"}, json=body)
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
