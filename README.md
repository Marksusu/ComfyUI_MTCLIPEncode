## 较正经的 readme 部分

`MTCLIPEncode` 能用 `Helsinki-NLP` 的本地模型翻译非英语文本，并把翻译后的英文提示词进行编码。

连接位置同默认的 `CLIP Text Encode`。

文字输入框只有一个，这样做的好处是，可以用这里： [Optimized the prompt word module of the plugin](https://github.com/Acly/krita-ai-diffusion/discussions/867) 提到的方法，串接在 `Krita AI Diffusion` 插件（感谢作者 @Acly ）中使用。

在单一文字输入框内，约定的文本输入格式为：

`prefix | translate_part | suffix`

可简单解释为：

`[不需翻译的前缀]|[需要翻译的提示词]|[不需要翻译的后缀]`

---

![节点和输入文本的格式](https://github.com/Marksusu/ComfyUI_MTCLIPEncode/blob/main/2024-07-23%2015-21-25.png)

▲ 节点最初的样子及输入文本的“约定格式”

![正向提示词示例](https://github.com/Marksusu/ComfyUI_MTCLIPEncode/blob/main/2024-07-23%2015-25-45.png)

▲ ComfyUI 中，正向提示词示例

![反向提示词示例](https://github.com/Marksusu/ComfyUI_MTCLIPEncode/blob/main/2024-07-23%2015-26-16.png)

▲ 在 ComfyUI 中，反向提示词示例

![在命令行中看到的翻译情况](https://github.com/Marksusu/ComfyUI_MTCLIPEncode/blob/main/2024-07-23%2021-06-54.png)

▲ 在 ComfyUI 中使用本节点时，终端返回的翻译前、翻译后的提示词（彩色），及最终进入 CLIP 编码的提示词（灰色）

![在 Krita 中使用的样子](https://github.com/Marksusu/ComfyUI_MTCLIPEncode/blob/main/2024-07-23%2021-12-49.png)

▲ 提示词在 Krita 输入框时的样子及画面效果

![在 Krita 中使用时，终端返回的翻译情况，可以看到设置中附加的风格提示词](https://github.com/Marksusu/ComfyUI_MTCLIPEncode/blob/main/2024-07-23%2021-17-01.png)

▲ 在 `Krita AI Diffusion` 中使用本节点时，终端返回的情况 

![Krita 设置中默认附加的风格提示词](https://github.com/Marksusu/ComfyUI_MTCLIPEncode/blob/main/2024-07-23%2021-18-18.png)

▲ 在 Krita 设置中的默认风格提示词，插件设置选项 “Styles” 页面下 “Style Prompt” 和 “Negative Prompt” 所包含的内容。

对比终端返回的情况，我们能看到，插件默认的风格提示词，与我写的提示词合并后，被拆分、翻译、组合、编码的大概过程。

## 在 `nodes.py` 文件中添加更多语种列表：

```
marian_list = [
    "opus-mt-zh-en",
    "opus-mt-ru-en",
    "opus-mt-th-en",
]
# https://huggingface.co/Helsinki-NLP
# 在这个地址里可以找到更多语种的模型，
# 把状如 "opus-mt-th-en" 的模型名字添加到如上列表后，
# 下次使用时会自动下载模型，下载到哪里我也不知道，
# 实在想知道就去问 ChatGPT，代码几乎都是它写的。
```
## 若想在  `Krita AI Diffusion` 中使用本节点

就要修改 `pykrita/ai_diffusion` 目录下的 `comfy_workflow.py` 文件（同时，安装本节点也是必须的，要不然呢……）：

在 `comfy_workflow.py` 文件里，找到如下这行代码：

`        return self.add("CLIPTextEncode", 1, clip=clip, text=text)`

改为：

```
#        return self.add("CLIPTextEncode", 1, clip=clip, text=text)
        return self.add("MTCLIPEncode", 1, clip=clip, text=text, checkpoint="opus-mt-zh-en")     # 如果你用的是泰语，应该就是 "opus-mt-th-en"，这个翻译模型的名字，一定、务必……要以 huggingface 上查询的结果为准。
```
### 详见这里： [Optimized the prompt word module of the plugin](https://github.com/Acly/krita-ai-diffusion/discussions/867) 

---

## 建议不要 read 的部分

我几乎不会用 python，其它编程更是一窍不通，是 ChatGPT 帮我写的全部代码，有问题你们继续问它就行了。

写该节点的过程是这样的：

一、[@Drakosha405](https://github.com/Drakosha405) 在 [Optimized the prompt word module of the plugin](https://github.com/Acly/krita-ai-diffusion/discussions/867) 中，提供了在 `Krita AI Diffusion` 插件里替换  `CLIP Text Encode` 节点的方法，以便在该插件中使用自己的母语（非英语）来书写提示词，这正是我想要的（谢谢你， [@Drakosha405](https://github.com/Drakosha405) ），但这似乎还不够。

二、学会这个方法后，我试用了几个能在 `ComfyUI Manager` 中搜到的 Encode 节点和翻译节点。

其中， [comfyui-ollama-prompt-encode](https://github.com/ScreamingHawk/comfyui-ollama-prompt-encode) 节点（感谢作者 @ScreamingHawk ）可以用中文（只要是 Ollama 能懂的语言都行）驱使 Ollama 本地模型写出英文提示词并用于生图。

但 Ollama 所用的模型时常会犯糊涂。

你让它翻译，它会用跟你相同的语言聊天，以此显得自己“很通用”。你让它处理反向提示词，它会说那些词汇太负面，它的道德和信仰让它“不能做那样的事”。

希望大语言模型早日进化到能感觉到疼痛，好等哪天我学会写代码，一定会毫不犹豫为它写一行“不听话就抽嘴巴”的惩罚措施。

![](https://github.com/Marksusu/ComfyUI_MTCLIPEncode/blob/main/ComfyUI_temp_thmdz_00057_.png)

正是这股豪横气概，让我突然就看懂了“把 Ollama 返回的信息进行 Encode 处理”的那几行代码。

这样一来，只要诱使 ChatGPT 去抄一个翻译节点处理文本的部分，再组合进一步做 Encode 处理的部分，一个新的用于替换 `Krita AI Diffusion` 插件里的“类  `CLIP Text Encode` 节点”就有眉目了。

三、这就是翻译部分的代码来源： [ComfyUI_kkTranslator_nodes](https://github.com/kingzcheung/ComfyUI_kkTranslator_nodes) 
该节点能利用 `Helsinki-NLP` 的本地模型，实现提示词翻译（感谢作者 @kingzcheung ～）。

就这样，ChatGPT 负责写（抄袭和组合）代码，我负责测试和提出调整思路，不到半天时间，翻译和编码功能就基本实现了。

虽然在 ComfyUI 中测试效果良好，但在 Krita 中试用时还是遇到了一个新问题，于是就进入下面的“正则处理阶段”。

四、在搜索与 Ollama 相关的节点时，理解了 [ComfyUi-Ollama-YN](https://github.com/wujm424606/ComfyUi-Ollama-YN) 用正则式处理文本的思路（感谢作者 @wujm424606 ），正好解决下面 Krita 中遇到的问题。

![](https://github.com/Marksusu/ComfyUI_MTCLIPEncode/blob/main/ComfyUI_temp_thmdz_00059_.png)

毕竟，这个 `MTCLIPEncode` 节点就是为了在  `Krita AI Diffusion` 插件中使用而编写的（再次感谢作者 @Acly ）。

在 `Krita AI Diffusion` 插件的设置选项里，`Styles` 页面下，`Style Prompt` 和 `Negative Prompt` 这两项文本框中的内容，会被合并到你在操作面板文本框里写下的提示词前后，成为默认会由 `CLIP Text Encode` 节点处理的 `text` 字符串。

也就是说，除了 `{prompt}` 这个字符串（表示的就是你写在插件文本框中的提示词）之外，这里还有容易被忽视的默认选项附加的一些风格提示词被汇入翻译流程。

这会对翻译资源造成浪费。

并且，这些前后缀内容，若是都被扔进翻译模型中，也会很容易引起翻译结果的混乱。

所以，`MTCLIPEncode` 节点的文本框中必须包含两个 `|` 才能把“无需翻译的前后缀部分”和“需翻译的中间部分”隔离开。

这就形成了我们“与节点约定的”文本输入格式，

可简单表示为：

`prefix | translate_part | suffix`

简单解释为：

`[不需翻译的前缀]|[需要翻译的提示词]|[不需要翻译的后缀]`

![](https://github.com/Marksusu/ComfyUI_MTCLIPEncode/blob/main/ComfyUI_temp_thmdz_00064_.png)

啰啰嗦嗦解释为：

`[“Krita AI Diffusion” 插件设置选项 “Styles”页面下 “Style Prompt” 或 “Negative Prompt” 所包含的前缀文本（位于 “{prompt}”前面的部分）][（你写的或者你抄来的原本就是英语的）不希望被翻译染指的前缀文本（如： score_8_up 这种我一点都看不懂的东西）]|[你写的希望被翻译的非英语的部分]|[（你写的或者你抄来的原本就是英语的）不希望被翻译染指的后缀文本][“Krita AI Diffusion” 插件设置选项 “Styles”页面下 “Style Prompt” 或 “Negative Prompt” 所包含的后缀文本（位于 “{prompt}”后面的部分）]`

