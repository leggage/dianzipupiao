import asyncio
import os
import threading
import cv2
import csv
from bleak import BleakClient
import re
import numpy as np

# 全局变量用于存储蓝牙数据
bluetooth_data_file = r'C:\Users\leggage\Desktop\DATA\accl_data2.csv'
# 文件夹用于存储图片
image_folder = r'C:\Users\leggage\Desktop\DATA\IMG1'
os.makedirs(image_folder, exist_ok=True)
# 创建线程事件，用于通知线程何时停止
stop_event = threading.Event()

# 摄像头对象
cap = cv2.VideoCapture(0)
# 全局变量用于存储BleakClient对象
client = None


async def close_bluetooth_connection():
    if client:
        await client.disconnect()
        print("蓝牙连接已关闭")


async def handle_notification(sender, data):
    # 这个回调函数将在接收到通知时被调用
    # 将每个字节转换为十六进制字符串，每个字节占一列
    hex_data = [format(byte, '02x') for byte in data]
    print(f"收到通知: {hex_data}")

    my_list.append(data)

    # 将数据写入文件
    if len(my_list) == 10:
        with open(bluetooth_data_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            # 写入六字节的数据到CSV文件的六列
            for byte_group in my_list:
                writer.writerow(byte_group)

        print(f"列表已保存为CSV文件 {bluetooth_data_file}")
    if len(my_list) <= 10:
        # 在这里拍摄图片并保存到文件夹
        global image_capture_count
        while image_capture_count < 20:  # 每次录制期间最多拍摄5张图片
            image_filename = os.path.join(image_folder, f"image_{len(os.listdir(image_folder))}.jpg")
            ret, frame = cap.read()
            if ret:
                cv2.imwrite(image_filename, frame)
                print(f"保存图片至 {image_filename}")
                image_capture_count += 1
        image_capture_count = 0  # 重置计数器

    # 如果收到停止事件，停止蓝牙数据接收线程
    if stop_event.is_set():
        await close_bluetooth_connection()
        return


async def subscribe_to_characteristic(device_address, characteristic_uuid):
    global client
    try:
        client = BleakClient(device_address)
        await client.connect()

        # 启用特征的通知
        await client.start_notify(characteristic_uuid, handle_notification)

        print(f"已经开始监听特征 {characteristic_uuid} 的通知...")

        while True:
            await asyncio.sleep(1)  # 持续监听，这里可以根据需要调整频率
            # 如果收到停止事件，停止蓝牙数据接收线程
            if stop_event.is_set():
                break

    except asyncio.TimeoutError:
        print("连接超时，请检查设备是否可用或重新尝试连接")
    finally:
        if client:
            await client.disconnect()


def truncate_string(input_string, n):
    """截断输入的字符串，只返回前n个字符或遇到空字符。"""
    for i in range(min(n, len(input_string))):
        if input_string[i] == '\0':
            return input_string[:i]
    return input_string[:n]


if __name__ == "__main__":
    #ESP32的BLE地址
    # device_address = "FC:B4:67:50:E0:2A"  # 你的ESP32的蓝牙地址
    # characteristic_uuid = "0000ee01-0000-1000-8000-00805f9b34fb"  # 要监听的特征的UUID
    #STM32蓝牙地址
    device_address = "FF:23:07:20:80:0C"  # 你的STM32的蓝牙地址
    characteristic_uuid = "0000fff1-0000-1000-8000-00805f9b34fb"  # 要监听的特征的UUID
    my_list = []
    image_capture_count = 0  # 图片计数器

    # 创建一个线程来运行蓝牙数据接收的代码
    bluetooth_thread = threading.Thread(
        target=lambda: asyncio.run(subscribe_to_characteristic(device_address, characteristic_uuid)))

    # 启动线程
    bluetooth_thread.start()

    # 等待用户输入以停止程序
    input("按 Enter 键停止程序...")

    # 发送停止事件，通知线程停止
    stop_event.set()
    # 关闭蓝牙连接
    asyncio.run(close_bluetooth_connection())
    # 释放摄像头资源
    cap.release()
    cv2.destroyAllWindows()
