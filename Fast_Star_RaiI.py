import traceback
import time
import ctypes
import pyuac
import requests
import tkinter as tk
import os
import hashlib
import sys
import questionary
from PIL import ImageTk, Image
from utils.log import log, webhook_and_log, fetch_php_file_content
from get_width import get_width, check_mult_screen
from utils.config import read_json_file, modify_json_file, init_config_file, CONFIG_FILE_NAME
from utils.map import Map
from utils.switch_window import switch_window
from utils.exceptions import Exception

def filter_content(content, keyword):
    # 将包含指定关键词的部分替换为空字符串
    return content.replace(keyword, "")

def calculate_image_hash(image_path):
    with open(image_path, 'rb') as f:
        data = f.read()
        hash_value = hashlib.md5(data).hexdigest()
    return hash_value

def show_popup():
    root = tk.Tk()
    root.withdraw()

    # 加载自定义图标
    icon_path = os.path.join(os.getcwd(), "picture", "1.ico")  # 图标文件路径
    icon = ImageTk.PhotoImage(Image.open(icon_path))

    # 创建弹窗
    popup = tk.Toplevel(root)
    popup.title("不许倒卖！倒卖的曱甴冚家铲")
    popup.iconphoto(True, icon)
    popup.geometry("540x470")

    # 加载图片
    image_path = os.path.join(os.getcwd(), "picture", "2.png")  # 图片文件路径
    image = ImageTk.PhotoImage(Image.open(image_path))

    # 校验图片MD5值
    expected_hash = "73d2c76cd9ec02710faf21322cabf9eb"
    image_hash = calculate_image_hash(image_path)
    if image_hash != expected_hash:
        log.error("？你小子，改我东西")
        return

    # 显示图片
    image_label = tk.Label(popup, image=image)
    image_label.pack()

    # 显示文本
    text_label = tk.Label(popup, text="开源软件，倒狗biss！不如您不幸购买到本软件，请立刻退款，退款失败请差评！", padx=10, pady=10)
    text_label.pack()

    # 确定按钮回调函数
    def on_ok():
        popup.destroy()
        continue_script()

    # 倒计时和确定按钮
    remaining_time = 10  # 倒计时时间
    ok_button = tk.Button(popup, text="确定（{}秒）".format(remaining_time), command=on_ok)
    ok_button.pack()

    # 更新倒计时
    def update_counter():
        nonlocal remaining_time
        if remaining_time > 0:
            remaining_time -= 1
            ok_button.config(text="确定（{}秒）".format(remaining_time))
            popup.after(1000, update_counter)
        elif remaining_time == 0:
            on_ok()

    # 开始倒计时
    update_counter()

    # 设置弹窗居中显示
    popup.update_idletasks()
    width = popup.winfo_width()
    height = popup.winfo_height()
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    popup.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    # 运行弹窗
    popup.mainloop()

def continue_script():
    try:
        main()
    except ModuleNotFoundError as e:
        print(traceback.format_exc())
        os.system("pip install -r requirements.txt")
        print("请重新运行")
    except NameError as e:
        print(traceback.format_exc())
        os.system("pip install -r requirements.txt")
        print("请重新运行")
    except:
        log.error(traceback.format_exc())

def choose_map(map_instance: Map):
    title_ = "请选择起始星球："
    options_map = {"空间站「黑塔」": "1", "雅利洛-VI": "2", "仙舟「罗浮」": "3"}
    option_ = list(options_map.keys())[0]
    main_map = options_map.get(option_)
    title_ = "请选择起始地图："
    options_map = map_instance.map_list_map.get(main_map)
    if not options_map:
        return
    keys = list(options_map.keys())
    values = list(options_map.values())
    option_ = list(options_map.values())[0]
    side_map = keys[values.index(option_)]
    return f"{main_map}-{side_map}"

def main():
    main_start()
    map_instance = Map()
    start = choose_map(map_instance)
    if start:
        php_content = fetch_php_file_content()  # 获取PHP文件的内容
        filtered_content = filter_content(php_content, "舔狗日记")  # 过滤关键词
        log.info("\n" + filtered_content)  # 将过滤后的内容输出到日志
        log.info("")  # 添加一行空行
        log.info("切换至游戏窗口，请确保跑图角色普攻为远程")
        check_mult_screen()
        switch_window()
        time.sleep(0.5)
        log.info("开始运行，请勿移动鼠标和键盘.向着星...呃串台了")
        log.info("1.2版本，均衡6锄满单角色收益62900经验")
        log.info("免费软件，倒卖的曱甴冚家铲，请尊重他人的劳动成果")
        map_instance.auto_map(start)  # 读取配置
    else:
        log.info("错误编号，请尝试检查更新")
        webhook_and_log("运行完成")
def main_start():
    CONFIG_FILE_NAME = "config.json"  

    config_data = read_json_file(CONFIG_FILE_NAME, False)
    if not config_data.get('start'):
        title = "你游戏里开启了连续自动战斗吗？："
        options = ['没打开', '打开了', '这是什么']
        option = questionary.select(title, options).ask()

        if option == '打开了':
            modify_json_file(CONFIG_FILE_NAME, "auto_battle_persistence", options.index(option))
            modify_json_file(CONFIG_FILE_NAME, "start", True)

            new_option_title = "想要跑完自动关机吗？"
            new_option_choices = ['不想', '↑↑↓↓←→←→BABA']
            new_option_choice = questionary.select(new_option_title, new_option_choices).ask()
            new_option_value = new_option_choice == '↑↑↓↓←→←→BABA'
            modify_json_file(CONFIG_FILE_NAME, "auto_shutdown", new_option_value)

if __name__ == "__main__":
    try:
        if not pyuac.isUserAdmin():
            pyuac.runAsAdmin()
        else:
            show_popup()  # 显示弹窗
    except:
        log.error(traceback.format_exc())
