# 1. 技术方案
在[movie-daily-news](https://github.com/deipss/moviepy-daily-news)项目的基础，将目光放在自己运营的内容上，技术线和上一线项目一致。
将md文件转换成视频，

- ~~机器翻译：字节旗下的[火山翻译](https://www.volcengine.com/docs/4640/65067)（每月有免费额度，不够用，已移除，使用deepseek翻译）~~ 
- 使用`markdown`包，将md解析出来
- 文字转语音:刚开始打算使用[字节的megaTTS](https://github.com/bytedance/MegaTTS3)，8G的显示不够，使用微软的edge-tts，效果还可以。
- 视频生成：moviepy


# 2. 信息来源
主要是通过不同的AI平台，提问，自己收集。

# 3. 使用

将每个视频的素材，放在`letters`目录下，每个素材的目录下，有对应的图片和文字素材。
每个素材的目录名，就是视频的名字。
每个素材的目录下，有对应的图片和文字素材。


# 4. 效果

以下生成的视频截图

![img.png](assets/img.png)

# 6. todo

- [ ] 主色调确定、头像
- [x] 主要排版
- [x] 脚本安排：总-分-总
- [x] 片头，片尾
- [x] 音频声色确定：男声
- [ ] Gradio 进行交互界面
- [ ] 字幕
- [x] 找一个完全的素材，进行测试
- [x] 视频的预览
- [ ] ~~对于一些素材，需要手动修改，比如图片的尺寸，看html5的自适应是如何实现的。~~

# 7. 附件

数据样例：

```json
[
  {
    "idx": 1,
    "letter": "林则徐致维多利亚女王的信:",
    "description": "林则徐致维多利亚女王的信:",
    "generated": false,
    "is_deleted": false,
    "date": "20250610"
  }
]

```