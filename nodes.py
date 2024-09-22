from transformers import MarianMTModel, MarianTokenizer
import re
import json
import requests
from ollama import Client, Options

# 去这个地址： https://huggingface.co/Helsinki-NLP 可以找到更多语种的模型，用同样的格式添加到如下列表，以便下次选用，翻译模型会被自动下载至本地
marian_list = [
    "opus-mt-zh-en",
    "opus-mt-ru-en",
    "opus-mt-th-en",
    "opus-mt-es-en",
    "opus-mt-fr-en",
    "opus-mt-ar-en",
    "opus-mt-hi-en",
    "opus-mt-bn-en",
    "opus-mt-pt-en",
    "opus-mt-ja-en",
    "opus-mt-de-en",
    "opus-mt-ko-en",
    "opus-mt-vi-en",
    "opus-mt-tr-en",
    "opus-mt-nl-en",
]

class MTCLIPEncode:
    def __init__(self):
        self.default_ollama_url = "http://127.0.0.1:11434"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip": ("CLIP", {}),
                "checkpoint": (marian_list, {"multiline": False, "default": "opus-mt-zh-en"}),
                "text": ("STRING", {"multiline": True, "default": " prefix | translate_part | suffix"}),
                "ollama_url": ("STRING", {"default": "http://127.0.0.1:11434"}),
                "ollama_model": ("STRING", {"default": "mistral-nemo:latest"}),
            }
        }

    # 确保双竖线 `||` 中间的内容为汉字或不少于三个字母的非英文单词
    def is_valid_translate_part(self, text):
        return bool(re.search(r'[\u4e00-\u9fff]|\b\w{3,}\b', text))

    def optimize_with_ollama(self, text, url, model):
        client = Client(host=url)

        prompt = f"""
You are a talented art director with a deep understanding of visual arts. You excel at transforming simple text descriptions into vivid, imaginative images. Now, you will be playing the role of a prompt engineer, providing precise and creative prompts for the Stable Diffusion model.

Please convert the following user input text: {text}, into a detailed and vivid prompt to inspire Stable Diffusion to generate a captivating image.

**Focus on:**
* **Clarity and precision:** Use clear and concise language that Stable Diffusion can easily understand.
* **Visual storytelling:** Create compelling narratives through your descriptions.
* **Artistic techniques:** Employ a variety of artistic techniques like lighting, composition, and perspective.
* **Style and atmosphere:** Convey the desired mood and style using vivid language and metaphors.

**Consider incorporating:**
* **Specific art styles:** e.g., impressionism, surrealism, cyberpunk
* **Cinematographic techniques:** e.g., shallow depth of field, wide-angle shot
* **Descriptive adjectives:** e.g., ethereal, luminous, brooding
* **Compositional elements:** e.g., rule of thirds, golden ratio

**Example:**
* **User input:** A lonely robot sitting on a distant planet
* **Your prompt:** # solitary android, desolate alien planet, distant star, panoramic view, sci-fi aesthetic, melancholic atmosphere, cinematic lighting #

**Remember:** Your goal is to create a prompt that inspires Stable Diffusion to generate a visually stunning and emotionally resonant image.

**Please enclose your prompt within two `#` symbols.**
"""

        response = client.generate(model=model, prompt=prompt)
        return response['response']

    def mtencode(self, clip, checkpoint, text, ollama_url, ollama_model):

        print(f"　　　　　　🫐　🫐　🫐　🫐　🫐　🫐")    # 打印分隔线

        pattern = r"([^|]*)\|([^|]*)\|([^|]*)"    # 需要调用翻译模型的提示词基本格式
        match = re.match(pattern, text)    # 判断是否需要调用翻译模型

        # 若输入 text 中，没有`||`(没有翻译请求)，判断叹号的数量和位置
        ollama_for_original = text.count('!') == 1 and '|' not in text  # 对应的输入格式为："English words English words ! English words"，叹号 `!` 为一个，可以在任意位置
        ollama_for_part_of_original = text.count('!') == 2 and '|' not in text  # 对应格式为："English prefix ! English words for Ollama refine ! English suffix"

        # 有`||`，说明有翻译请求，进行翻译处理
        if match:
            prefix, translate_part, suffix = [re.sub(r'^[\s|,]+|[\s|,]+$', '', part.strip()) for part in match.groups()]    # 被 `||` 双竖线分隔的三个部分
            print(f"　　　　\033[94m{prefix}\033[0m, \033[0;1m|\033[0m \033[92m{translate_part}\033[0m, \033[0;1m|\033[0m \033[94m{suffix}\033[0m")    # 打印用户的原始输入（有`|`），并用颜色区分三个部分

            # ollama_in_translate_part 和 ollama_for_all_3_parts 的判断在解析出 prefix、translate_part 和 suffix 之后
            ollama_in_translate_part = '!' in translate_part  # 判断叹号是否在翻译部分
            ollama_for_all_3_parts = (
                not ollama_in_translate_part and (
                   '!' in prefix or '!' in suffix  # 判断叹号是否在前缀或后缀中
                )
            )

            if not self.is_valid_translate_part(translate_part):
                prompt_text = f"{prefix}, {suffix}"
            else:
                model_name = 'Helsinki-NLP/' + checkpoint
                tokenizer = MarianTokenizer.from_pretrained(model_name)
                model = MarianMTModel.from_pretrained(model_name)

                if ollama_in_translate_part:

                    translate_part = translate_part.replace('!', '')  # 去掉 `!`
                    translated = model.generate(**tokenizer(translate_part, return_tensors="pt", padding=True))
                    translated_text = re.sub(r'^[\s,.]+|[\s,.]+$', '', tokenizer.decode(translated[0], skip_special_tokens=True))
                    print(f"　　　　\033[94m{prefix}\033[0m, \033[92m{translated_text}\033[0m, \033[94m{suffix}\033[0m")    # 打印译文，并与原始的前、后缀合并

                    try:
                        translated_text = self.optimize_with_ollama(translated_text, ollama_url, ollama_model)
                        match = re.search(r'#(.*?)#', translated_text)
                        if match:
                            translated_text = match.group(1)
                            translated_text = re.sub(r'^[\s|,]+|[\s|,]+$', '', translated_text.strip())

                        prompt_text = ", ".join(filter(None, [prefix, translated_text, suffix]))
                        print(f"　　　　\033[94m{prefix}\033[0m, \033[90;1m{translated_text}\033[0m, \033[94m{suffix}\033[0m")    # 打印 Ollama 对译文的处理结果，并与原始的前、后缀合并
                    except Exception as e:
                        print(f"Failed to optimize prompt with Ollama in translated text: {e}")

                else:
                    translated = model.generate(**tokenizer(translate_part, return_tensors="pt", padding=True))
                    translated_text = re.sub(r'^[\s,.]+|[\s,.]+$', '', tokenizer.decode(translated[0], skip_special_tokens=True))

                    prompt_text = ", ".join(filter(None, [prefix, translated_text, suffix]))
                    print(f"　　　　\033[94m{prefix}\033[0m, \033[92m{translated_text}\033[0m, \033[94m{suffix}\033[0m")    # 打印译文，保留原始前、后缀不变，并完成合并

                    if ollama_for_all_3_parts:
                        prompt_text = prompt_text.replace('!', '')  # 去掉 `!`
                        try:
                            prompt_text = self.optimize_with_ollama(prompt_text, ollama_url, ollama_model)
                            match = re.search(r'#(.*?)#', prompt_text)
                            if match:
                                prompt_text = match.group(1)
                                prompt_text = re.sub(r'^[\s|,]+|[\s|,]+$', '', prompt_text.strip())

                            print(f"　　　　\033[90;1m{prompt_text}\033[0m")    # 打印 Ollama 对合并后的提示词（包括前、后缀和译文）整体的处理结果
                        except Exception as e:
                            print(f"Failed to optimize prompt with Ollama in all 3 parts: {e}")
            # 去掉前缀 prefix 为空时，开头会出现的`,`
            prompt_text = prompt_text.lstrip(',')

        else:
            prompt_text = text.strip()
            print(f"　　　　\033[94m{prompt_text}\033[0m")    # 打印无需翻译的原始提示词

            if ollama_for_part_of_original:
                try:
                    # 使用正则提取 `!!` 之间的部分，并移除 `!!`
                    match = re.search(r'^(.*?)!(.*?)!(.*?)$', text)
                    if match:
                        prefix, ollama_part, suffix = [re.sub(r'^[\s|,]+|[\s|,]+$', '', part.strip()) for part in match.groups()]
#                        prefix, ollama_part, suffix = match.groups()
                        ollama_part = self.optimize_with_ollama(ollama_part.strip(), ollama_url, ollama_model)
                        ollama_match = re.search(r'#(.*?)#', ollama_part)
                        if ollama_match:
                            ollama_part = ollama_match.group(1)
                            ollama_part = re.sub(r'^[\s|,]+|[\s|,]+$', '', ollama_part.strip())

                        prompt_text = f"{prefix.strip()}, {ollama_part.strip()}, {suffix.strip()}"
                        print(f"　　　　\033[32m{prefix}\033[0m, \033[90;1m{ollama_part}\033[0m, \033[32m{suffix}\033[0m")    # 打印 Ollama 对无需翻译的原始提示词的处理结果，并保留原始前、后缀
                except Exception as e:
                    print(f"Failed to optimize prompt with Ollama in part of original prompt: {e}")

            elif ollama_for_original:
                prompt_text = text.replace('!', '')  # 去掉 `!`
                try:
                    prompt_text = self.optimize_with_ollama(prompt_text, ollama_url, ollama_model)
                    match = re.search(r'#(.*?)#', prompt_text)
                    if match:
                        prompt_text = match.group(1)
                        prompt_text = re.sub(r'^[\s|,]+|[\s|,]+$', '', prompt_text.strip())

                    print(f"　　　　\033[90;1m{prompt_text}\033[0m")    # 打印无需翻译但需要 Ollama 处理的提示词
                except Exception as e:
                    print(f"Failed to optimize prompt with Ollama in original prompt: {e}")

            # 去掉前缀 prefix 为空时，开头会出现的`,`
            prompt_text = prompt_text.lstrip(',')

        # 最终输出
        print(f"　　　　\033[32m{prompt_text}\033[0m")    # 打印进入 CLIP 编码流程的提示词

        tokens = clip.tokenize(prompt_text)
        cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)

        return ([[cond, {"pooled_output": pooled}]], prompt_text)

    RETURN_TYPES = ("CONDITIONING", "STRING",)
    FUNCTION = "mtencode"
    CATEGORY = "MTCLIPEncode"

NODE_CLASS_MAPPINGS = {
    "MTCLIPEncode": MTCLIPEncode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MTCLIPEncode": "MTCLIPEncode",
}
