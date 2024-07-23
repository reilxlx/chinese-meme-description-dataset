# -*- coding: gbk -*-
import base64
import requests
import os
import json
import shutil
import time
import jsonlines
import re
from tqdm import tqdm
import sys
import subprocess  # 导入 subprocess 模块
import mimetypes  # 导入 mimetypes 模块

model_type = "claude-3-5-sonnet-20240620"
IMAGE_DIR = r"J:\表情包多模态\claude-3.5-sonnet\chineseBQB"
PROCESSED_DIR = r"J:\表情包多模态\claude-3.5-sonnet\processed_" + model_type
JSONL_FILE = "J:\表情包多模态\claude-3.5-sonnet\image_descriptions_processed-" + model_type + ".jsonl"

prompt_template = "你是一位有深度的网络图片解读者，擅长解读和描述网络图片。你能洞察图片中的细微之处，对图中的人物面部表情、文字信息、情绪流露和背景寓意具有超强的理解力，描述信息需要详细。为了帮助你更好的理解图中信息，我已经将图中主题和文字信息摘要出来，主题:{zhuti},文字:{wenzi}。你返回的描述中必须包含我提供的主题和文字，不得删除和修改。如果你知道表情包中所使用的主角姓名或出自哪部动漫或引用的出处，可以将该信息加入你的描述中。"

def image_to_base64(file_path):
    """
    image to base64
    """
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
def process_images(image_paths):

    for i, image_path in enumerate(tqdm(image_paths, desc="Processing Images", unit="image")):

        filename = os.path.basename(image_path)
        zhutiandwenzi = extract_zhutiandwenzi(filename)
        zhuti, wenzi = split_zhutiandwenzi(zhutiandwenzi)
        prompt_ch_2 = prompt_template.format(zhuti=zhuti, wenzi=wenzi)

        media_type = mimetypes.guess_type(image_path)[0]

        content_list = [
            {
                "type": "text",
                "text": prompt_ch_2
            },
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": image_to_base64(image_path),
                }
            }
        ]

        url = "https://XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/v1/messages"
        body = {
            "model": model_type,
            "max_tokens": 4096,
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
                'x-api-key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            }, json=body, timeout=60)
            response.raise_for_status()
            response_json = response.json()
            print("response_json:", response_json)
            content = response_json['content'][0]['text']

            result = {
                "picName": filename,
                "description": content
            }
            shutil.move(image_path, os.path.join(PROCESSED_DIR, filename))
            os.utime(os.path.join(PROCESSED_DIR, filename), (time.time(), time.time()))
            with jsonlines.open(JSONL_FILE, mode='a') as writer:
                writer.write(result)

        except requests.exceptions.RequestException as e:
            print(f"请求出错: {e}")
        except (json.JSONDecodeError, KeyError) as e:
            print(f"解析响应出错: {e}")
        finally:
            time.sleep(2)

if __name__ == '__main__':
    image_paths = [os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR) if
                   os.path.isfile(os.path.join(IMAGE_DIR, f))]
    process_images(image_paths)
