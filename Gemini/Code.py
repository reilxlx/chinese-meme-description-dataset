# -*- coding: gbk -*-
import google.generativeai as genai
import PIL.Image
import os
import json
import shutil
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
genai.configure(api_key='')
model = genai.GenerativeModel(
    'gemini-1.5-pro-latest',  #gemini-pro-vision、gemini-1.5-flash
    generation_config=genai.GenerationConfig(
        max_output_tokens=2000,
        temperature=1,
        top_p=0.99
    ))
image_folder = '/emo'
output_file = 'image_descriptions.jsonl'
error_folder = '/emo_error'
processed_folder = '/emo_processed'
for folder in [error_folder, processed_folder]:
    if not os.path.exists(folder):
        os.makedirs(folder)

prompt_ch_2 = "请您静心品鉴此表情包，它或许蕴含着文字的韵味、动漫的灵动、卡通的趣味抑或是真人的神态。您需细细观察图中所有元素，无论是人物的眉眼、文字的深意抑或是背景的寓意，皆不可忽视，且请尊重图中文字信息，勿作改动。恳请您用优雅的笔触描绘您所见的景象，例如人物表情的微妙变化、动作姿态的含义以及文字中蕴藏的情感等，并尝试解读此表情包试图传递的情绪或信息。请您用精妙的中文，以流畅的文字，将您的理解娓娓道来，以便我能清晰地领悟此表情包的奥妙之处。"
image_files = [
    f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.jpeg', '.png'))
]
def process_image(filename):
    image_path = os.path.join(image_folder, filename)
    try:
        img = PIL.Image.open(image_path)
        response = model.generate_content([prompt_ch_2, img], safety_settings={
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL' : 'BLOCK_NONE',
        'DANGEROUS' : 'BLOCK_NONE'
    })
        if response and hasattr(response, 'text') and response.text:
            data = {
                "picName": filename,
                "description": response.text
            }
            img.close()
            os.rename(os.path.join(image_folder, filename),
                      os.path.join(processed_folder, filename))
            return data
        else:
            print(f"Error processing {filename}: Gemini API returned no text. Skipping...")
            img.close()
            os.rename(os.path.join(image_folder, filename),
                      os.path.join(error_folder, filename))
            return None
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        img.close()
        shutil.move(os.path.join(image_folder, filename),
                    os.path.join(error_folder, filename))
        return None
with ThreadPoolExecutor(max_workers=5) as executor, open(output_file, 'a', encoding='utf-8') as outfile:
    futures = {executor.submit(process_image, filename): filename for filename in image_files}
    for future in tqdm(as_completed(futures), total=len(futures), desc="Processing Images"):
        result = future.result()
        if result:
            outfile.write(json.dumps(result, ensure_ascii=False) + '\n')
print("Image processing complete.")
