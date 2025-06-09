# 1. 技术方案
在[movie-daily-news](https://github.com/deipss/moviepy-daily-news)项目的基础，将目光放在自己运营的内容上，技术线和上一线项目一致：
大概的方向就是先使用爬虫技术，爬取网站的新闻文本、图片，英文新闻使用机器翻译进行翻译，使用ollama中deepseek进行摘要提取，上述的素材准备好，使用moviepy生成视频。
主要用的技术：

- ~~机器翻译：字节旗下的[火山翻译](https://www.volcengine.com/docs/4640/65067)（每月有免费额度，不够用，已移除，使用deepseek翻译）~~ 
- 摘要提取：ollama 部署了  [deepseek-r1:8b](https://ollama.com/library/deepseek-r1 "点击打开ollama")
- 文字转语音:刚开始打算使用[字节的megaTTS](https://github.com/bytedance/MegaTTS3)，8G的显示不够，使用微软的edge-tts，效果还可以。
- 视频生成：moviepy


> 硬件最好是有GPU，用来运行ollama，当然可以用云服务器代替，取决于个人的资源。

# 2. 信息来源
主要是通过不同的AI平台，提问，自己收集。

# 3. 使用

将每个视频的素材，放在`letters`目录下，每个素材的目录下，有对应的图片和文字素材。
每个素材的目录名，就是视频的名字。
每个素材的目录下，有对应的图片和文字素材。



# 4. 效果

以下生成的视频截图


# 6. todo

- [ ] 主色调确定、头像
- [ ] 主要排版
- [ ] 脚本安排：总-分-总
- [ ] 片头，片尾
- [ ] 音频声色确定：男声
- [ ] Gradio 进行交互界面

# 7. 附件

数据样例：

```json

```