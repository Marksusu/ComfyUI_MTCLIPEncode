`MTCLIPEncode` 能用 `Helsinki-NLP` 的本地模型翻译非英语文本，并把翻译后的英文提示词进行编码。

连接位置同默认的 `CLIP Text Encode`。

文字输入框只有一个，这样做的好处是，可以用这里： [Optimized the prompt word module of the plugin](https://github.com/Acly/krita-ai-diffusion/discussions/867) 提到的方法，串接在 `Krita AI Diffusion` 插件中使用。

在单一文字输入框内，约定的文本输入格式为：

`prefix | translate_part | suffix`

可简单解释为：

`[不需翻译的前缀]|[需要翻译的提示词]|[不需要翻译的后缀]`

