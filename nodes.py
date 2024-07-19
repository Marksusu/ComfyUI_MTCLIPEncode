from transformers import MarianMTModel, MarianTokenizer
import re

marian_list = [
    "opus-mt-zh-en",
    "opus-mt-ru-en",
    "opus-mt-th-en",
]
# https://huggingface.co/Helsinki-NLP 在这个地址里可以找到更多语种的模型，添加到如上列表后，下次使用时会自动下载模型

class MTCLIPEncode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip": ("CLIP", {}),
                "checkpoint": (marian_list, {"multiline": False,"default": "opus-mt-zh-en"}),
                "text": ("STRING", {"multiline": True,"default": "prefix | translate_part | suffix"}),
            }
        }

    def is_valid_translate_part(self, text):
        # 简单检查文本是否包含至少一个汉字或一个长度大于2的非英文单词
        return bool(re.search(r'[\u4e00-\u9fff]|\b\w{3,}\b', text))

    def mtencode(self, clip, checkpoint, text):

        # 使用正则表达式修剪首尾可能存在的一个或多个 `,`、[空格]
        text = re.sub(r'^[\s,]+|[\s,]+$', '', text)

        # 使用正则表达式分离出需要翻译和不需要翻译的部分
        pattern = r"([^|]*)\|([^|]*)\|([^|]*)"
        match = re.match(pattern, text)

        if match:
            prefix = match.group(1).strip()
            translate_part = match.group(2).strip()
            suffix = match.group(3).strip()

            # 修剪三个部分的文本，首尾可能存在的一个或多个`|`、`,`、[空格]
            prefix = re.sub(r'^[\s|,]+|[\s|,]+$', '', prefix)
            translate_part = re.sub(r'^[\s|,]+|[\s|,]+$', '', translate_part)
            suffix = re.sub(r'^[\s|,]+|[\s|,]+$', '', suffix)

            # 确保 translate_part 有效
            if not self.is_valid_translate_part(translate_part):
                prompt_text = f"{prefix}, {suffix}"
            else:
                model_name = 'Helsinki-NLP/' + checkpoint
                tokenizer = MarianTokenizer.from_pretrained(model_name)
                model = MarianMTModel.from_pretrained(model_name)

                translated = model.generate(**tokenizer(translate_part, return_tensors="pt", padding=True))
                translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)

                # 修剪 translated_text 首尾可能存在的空格、逗号和句号
                translated_text = re.sub(r'^[\s,.]+|[\s,.]+$', '', translated_text)

                # 合并不需要翻译的部分和翻译后的部分
                if prefix and suffix:
                    prompt_text = f"{prefix}, {translated_text}, {suffix}"
                elif prefix:
                    prompt_text = f"{prefix}, {translated_text}"
                elif suffix:
                    prompt_text = f"{translated_text}, {suffix}"
                else:
                    prompt_text = translated_text

                # ANSI 转义序列用于颜色输出
                color_prefix = f"\033[94m{prefix}\033[0m" if prefix else ""
                color_translate_part = f"\033[92m{translate_part}\033[0m"
                color_translated_text = f"\033[92m{translated_text}\033[0m"
                color_suffix = f"\033[94m{suffix}\033[0m" if suffix else ""

                # 打印格式化输出
                print(f"　　　　　　🫐　🫐　🫐　🫐　🫐　🫐")
                if prefix and suffix:
                    print(f"　　　　{color_prefix}, {color_translate_part}, {color_suffix}")
                elif prefix:
                    print(f"　　　　{color_prefix}, {color_translate_part}")
                elif suffix:
                    print(f"　　　　{color_translate_part}, {color_suffix}")
                else:
                    print(f"　　　　{color_translate_part}")

                if prefix and suffix:
                    print(f"　　　　{color_prefix}, {color_translated_text}, {color_suffix}")
                elif prefix:
                    print(f"　　　　{color_prefix}, {color_translated_text}")
                elif suffix:
                    print(f"　　　　{color_translated_text}, {color_suffix}")
                else:
                    print(f"　　　　{color_translated_text}")

        else:
            prompt_text = text.strip()  # 如果没有匹配项，使用原文本

        # 打印格式化输出
        print(f"　　　　{prompt_text}")

        tokens = clip.tokenize(prompt_text)
        cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)

        return ([[cond, {"pooled_output": pooled}]], prompt_text)

    RETURN_TYPES = (
        "CONDITIONING",
        "STRING",
    )
    FUNCTION = "mtencode"
    CATEGORY = "MTCLIPEncode"

NODE_CLASS_MAPPINGS = {
    "MTCLIPEncode": MTCLIPEncode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MTCLIPEncode": "MTCLIPEncode",
}
