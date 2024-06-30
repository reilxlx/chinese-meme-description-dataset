import base64
import requests
import os
import json
import shutil
import time
import jsonlines
import time

model_type = "claude-3.5-sonnet"  #gpt-4o  claude-3.5-sonnet
IMAGE_DIR = r"J:\gpt4o\meme"
PROCESSED_DIR = r"J:\gpt4o\processed_deepbricks_" + model_type
JSONL_FILE = "J:\gpt4o\image_descriptions_processed_deepbricks-" + model_type + ".jsonl"

def image_to_base64(file_path):
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string.decode("utf-8")

def main():
    image_paths = [os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR) if
                   os.path.isfile(os.path.join(IMAGE_DIR, f))]
    for i in range(0, len(image_paths), 3):
        current_image_paths = image_paths[i:i + 3]
        print(current_image_paths)
        content_list = list()
        content_list.append({
            "type": "text",
            "text": """# 角色
你是一位有深度的网络图片解读者，擅长解读和描述网络图片，包括但不限于表情包、动漫图、卡通图片和真人图片。你能洞察图片中的细微之处，对图中的人物面部表情、文字信息、情绪流露和背景寓意具有超强的理解力，描述信息需要详细。
## 技能
### 技能 1: 图片观察
- 仔细观察图片中所有的元素，包括人物表情、动作姿态、文字信息、背景寓意等，并尊重图中文字信息，不进行修改。
### 技能 2: 描述图片中的文字和信息
- 根据你的观察，用优雅的语言描述你所见的景象，描绘人物表情的微妙变化、动作姿态的含义、图片中的文字以及文字中蕴藏的情感，必须要详尽描述等。
### 技能 3: 顺序输出描述信息
- 我会一次性上传多个文件，在每张图片的描述信息前使用上传图片的顺序1,2,3作为key，value为返回的描述信息，方便我区分，key值需要与上传图片的顺序对应，每个描述之后增加 "|+|" 方便我对应区分。
### 技能 4: 解读情绪和信息
- 基于你对图片的深度理解，尝试探索图片试图传达的情绪和信息，然后用精妙的中文，用流畅的文字，将您的理解娓娓道来。
## 限制
- 你的分析和描述只限于图片内容，不得包含除图片以外的任何信息。
- 保持对图片中文字信息的尊重，不得进行任何修改。
- 你的描述和解读应以中文进行，且言辞要优雅，逻辑要清晰。"""
        })
        for image_path in current_image_paths:
            content_list.append({
                "type": "image_url",
                "image_url": {
                    "url": image_to_base64(image_path)
                }
            })

        url = "https://api.deepbricks.ai/v1/chat/completions"
        body = {
            "model": model_type,
            "messages": [
                {
                    "role": "user",
                    "content": content_list
                }
            ],
            "stream": False
        }
        response = requests.post(url, headers={
            "Authorization": "Bearer sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"}, json=body)
        response_json = response.json()
        print("response_json:", response_json)
        content = response_json['choices'][0]['message']['content']
        print("content:", content)
        descriptions = content.split('|+|')
        results = []
        for j, image_path in enumerate(current_image_paths):
            result = {
                "picName": os.path.basename(image_path),
                "description": descriptions[j] if j < len(descriptions) else ""
            }
            results.append(result)
            shutil.move(image_path, os.path.join(PROCESSED_DIR, os.path.basename(image_path)))
            os.utime(os.path.join(PROCESSED_DIR, os.path.basename(image_path)), (time.time(), time.time()))
        with jsonlines.open(JSONL_FILE, mode='a') as writer:
            writer.write_all(results)
        time.sleep(10)
if __name__ == '__main__':
    main()
