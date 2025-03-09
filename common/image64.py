import os  
import base64  
from PIL import Image  
  
def image_to_base64(image_path):  
    """  
    将图片文件转换为Base64编码的字符串  
    """  
    with open(image_path, "rb") as image_file:  
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')  
    return f'data:image/{os.path.splitext(image_path)[1][1:]};base64,{encoded_string}'  
  
def convert_images_in_folder(folder_path):  
    """  
    遍历指定文件夹中的所有图片，将它们转换为Base64编码  
    """  
    data = []
    for root, dirs, files in os.walk(folder_path):  
        for file in files:  
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):  
                image_path = os.path.join(root, file)  
                base64_str = image_to_base64(image_path)  
                print(f"Converted {image_path} to Base64:")  
                print(base64_str)  
                data.append(data)
    return data
  


if __name__ == '__main__':
    # 使用示例  
    folder_path = '/Users/xiaoyong/workspace/QAtools/locust_turorials/data/images'  
    convert_images_in_folder(folder_path)
