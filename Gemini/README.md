使用Gemini-1.5-pro、 gemini-pro-vision、gemini-1.5-flash API模型批量生成图片描述，并对处理结果进行分类保存，其核心思想如下：

1. **初始化:**
    - 设置 Gemini API 密钥、模型参数、图片文件夹等。
    - 创建错误图片和已处理图片的文件夹。
2. **定义图片处理函数:**
    - 打开图片，调用 Gemini API 生成描述。
    - 根据 API 返回结果进行分类处理：
        - 成功：保存图片名和描述到 JSONL 文件，并将图片移动到已处理文件夹。
        - 失败：打印错误信息，并将图片移动到错误文件夹。
3. **并发处理图片:**
    - 使用线程池并发处理图片，提高处理效率。
    - 使用 tqdm 显示处理进度。
4. **保存结果:**
    - 将成功生成的图片描述写入 JSONL 文件。

默认情况下API会对图片的内容进行安全性校验，使用以下参数屏蔽。
```json
{
    'HATE': 'BLOCK_NONE',
    'HARASSMENT': 'BLOCK_NONE',
    'SEXUAL' : 'BLOCK_NONE',
    'DANGEROUS' : 'BLOCK_NONE'
}
```

具体图像文本描述信息可从huggingface下载，https://huggingface.co/datasets/REILX/text-description-of-the-meme