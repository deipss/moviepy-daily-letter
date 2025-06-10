
import gradio as gr

Photo = {
    "image": None,
    "image_path": None,
    "explain_txt": ""
}

# 定义整体数据结构
data_structure = {
    "instructions": {
        "photos": [Photo],
        "commentary": ""
    },
    "frame1": {
        "photos": [Photo],
        "commentary": ""
    },
    "frame2": {
        "photos": [Photo],
        "commentary": ""
    },
    "frame3": {
        "photos": [Photo],
        "commentary": ""
    },
    "frame4": {
        "photos": [Photo],
        "commentary": ""
    },
    "frame5": {
        "photos": [Photo],
        "commentary": ""
    },
    "frame6": {
        "photos": [Photo],
        "commentary": ""
    },
    "frame7": {
        "photos": [Photo],
        "commentary": ""
    },
    "frame8": {
        "photos": [Photo],
        "commentary": ""
    },
    "frame9": {
        "photos": [Photo],
        "commentary": ""
    },
    "end": {
        "photos": [Photo],
        "commentary": ""
    }
}

# 创建 Gradio 接口
def display_frame(frame_name):

    return 'photo_images', 'photo_texts', 'commentary'


if __name__ == '__main__':

    iface = gr.Interface(
        fn=display_frame,
        inputs=gr.Dropdown(choices=list(data_structure.keys())),  # 修改：直接使用 gr.Dropdown
        outputs=[
            gr.Textbox(label="Photos"),  # 修改：直接使用 gr.Image
            gr.Textbox(label="Explain Texts"),  # 修改：直接使用 gr.Textbox
            gr.Textbox(label="Commentary")  # 修改：直接使用 gr.Textbox
        ],
        title="MoviePy Daily Letter Interface",
        description="Select a frame to view photos and commentary."
    )

    # 启动 Gradio 接口
    iface.launch(server_port=8989)
