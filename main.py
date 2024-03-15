import base64
import os
import sys
from io import BytesIO
import PIL.ImageOps
from PIL import Image, ImageDraw, ImageFont
import exifread
import tkinter as tk
from tkinter import filedialog
import tkinter.messagebox


def get_params(the_photo_path):
    if the_photo_path.endswith('png') or the_photo_path.endswith('PNG'):
        params_text = "24mm  f3.2  1/240s  ISO100"
        return params_text

    with open(the_photo_path, 'rb') as photo:
        tags = exifread.process_file(photo)
        try:
            focal_length = tags['EXIF FocalLengthIn35mmFilm']
        except Exception as e:
            params_text = "24mm  f3.2  1/240s  ISO100"
            return params_text
        if focal_length is None:
            params_text = "24mm  f3.2  1/240s  ISO100"
            return params_text

        FNumber = str(tags['EXIF FNumber'])
        F = FNumber.split('/')
        f = float(F[0]) / float(F[1])

        exposure_time = str(tags['EXIF ExposureTime']) + 's'

        ISO = tags['EXIF ISOSpeedRatings']

        params_text = f"{focal_length}mm  f{f}  {exposure_time}  ISO{ISO}"
        return params_text


def resize_image_with_aspect_ratio(image, target_width):
    # 打开图片
    original_image = image

    # 计算调整后的高度，保持原始长宽比
    original_width, original_height = original_image.size
    aspect_ratio = original_width / original_height
    target_height = int(target_width / aspect_ratio)

    # original_image.info['dpi'] = (240, 240)

    # 调整图片大小
    resized_image = original_image.resize((target_width, target_height))
    return resized_image


def add_text_to_image(resized_bg, text, position=(10, 10), font_size=20, font_color=(255, 255, 255), font_path=None):
    # 打开图片
    # img = Image.open(bg_path)
    img = resized_bg

    # 创建Draw对象
    draw = ImageDraw.Draw(img)

    # 设置字体
    if font_path is not None:
        font = ImageFont.truetype(font_path, font_size)
    else:
        font = ImageFont.load_default()

    # 添加文字
    draw.text(position, text, font=font, fill=font_color)

    # 保存图片
    return img


def concatenate_images_vertically(hasselblad_boarder, original_photo, output_path):
    # 打开两张图片
    image2 = hasselblad_boarder.convert("RGB")
    image1 = original_photo.convert("RGB")

    # 获取图片的宽度和高度
    width, height1 = image1.size
    _, height2 = image2.size

    # 选择最大的高度作为新图片的高度
    new_height = height1 + height2

    # 创建一个新的画布，高度为两张图片的总和
    new_image = Image.new("RGB", (width, new_height))

    # 在新画布上粘贴第一张图片
    # new_image.paste(image1, (0, 0, width, height1))
    new_image.paste(image1, (0, 0))

    # 在新画布上粘贴第二张图片，位置为第一张图片的底部
    # new_image.paste(image2, (0, height1, width, new_height))
    new_image.paste(image2, (0, height1))
    # 保存拼接后的图片
    if photo_path.endswith('png') or photo_path.endswith('PNG'):
        new_image.save(output_path, format="PNG", quality=100, dpi=(300, 300))
    else:
        new_image.save(output_path, format="JPEG", quality=100, dpi=(300, 300))


if __name__ == "__main__":
    # 实例化
    root = tk.Tk()
    root.withdraw()


    def err_messagebox():
        tk.messagebox.showerror(title='错误', message='文件读取出错')
        root.quit()
        root.destroy()


    # 获取图片路径
    global photo_path
    photo_path = filedialog.askopenfilename()
    try:
        original_photo = PIL.Image.open(photo_path)
    except Exception as e:
        err_messagebox()
        sys.exit()
    photo_width, photo_height = original_photo.size

    # 指定background图片路径
    with open('./resources/image_base64.txt', 'rb') as base64_data:
        base64_image = base64_data.read()
    image_data = base64.b64decode(base64_image)

    # 使用Pillow库打开图片
    bg_image = Image.open(BytesIO(image_data))
    # bg_path = r".\hasselblad.jpg"

    # 指定输出图片路径
    output_path = os.path.dirname(photo_path) + '\\' + os.path.split(photo_path)[-1].split('.')[0] + '-Hasselblad.' + \
                  os.path.split(photo_path)[-1].split('.')[1]

    # 自定义文字信息
    text = get_params(photo_path)

    left_ratio = 175 / 3840
    upper_ratio = 250 / 445
    left_position = round(left_ratio * photo_width)
    upper_position = round(upper_ratio * photo_height)
    # print(left_position, upper_position)

    # 自定义文字位置（离边框的像素距离）
    position = (178, 250)  # left boarder, upper boarder
    # position = (left_position, 250)   # left boarder, upper boarder

    # 自定义字体大小
    font_size = 65

    # 自定义字体颜色（RGB格式）
    font_color = (169, 169, 169)

    # 自定义字体路径（如果有特定字体文件）
    font_path = r"./resources/AvenirNext-Regular.ttf"  # 替换为你的字体文件路径

    user_profile = os.environ.get('USERPROFILE')
    pictures_path = os.path.join(user_profile, 'Pictures')
    save_path = pictures_path + '\\' + os.path.split(photo_path)[-1].split('.')[0] + '-Hasselblad.' + \
                os.path.split(photo_path)[-1].split('.')[1]
    # print(save_path)

    # 调用函数添加文字
    hasselblad_boarder = add_text_to_image(bg_image, text, position, font_size, font_color, font_path)

    resized_bg = resize_image_with_aspect_ratio(hasselblad_boarder, target_width=photo_width)

    concatenate_images_vertically(resized_bg, original_photo, save_path)
