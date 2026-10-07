import serial
import numpy as np
import cv2

def find_frame_head(data, frame_head_pattern):
    # 在数据流中查找帧头的起始位置
    # 返回帧头起始位置的索引，如果未找到帧头，返回-1
    return data.find(frame_head_pattern)

def parse_frame(raw_data):
    # 输入的数据帧总长是否达到应有的1544字节
    if len(raw_data) != 1544:
        return
    # 校验帧头是否有效
    if raw_data[0] != 0x5A or raw_data[1] != 0x5A:
        return
    # 解析目标温度数据（从 Byte 4 到 Byte 1539，768 个目标温度数据）
    temperatures = []
    for i in range(0, 1536, 2):
        temp_data_low = raw_data[4 + i]
        temp_data_high = raw_data[5 + i]
        temp_value = (temp_data_high << 8) | temp_data_low  # 合并低高字节
        actual_temp_value = temp_value / 100.0  # 除以100得到实际温度
        temperatures.append(actual_temp_value)
    # 将 768 个温度数据转换为 24x32 的矩阵
    temp_matrix = np.array(temperatures).reshape(24, 32)
    # 对矩阵进行左右镜像，因为读取的数据是反的
    temp_matrix_flipped = np.fliplr(temp_matrix)
    # 返回结果
    return temp_matrix_flipped

# OpenCV的图像显示中拖动条的回调函数
# (从深度读取的函数里复制的所以部分变量没改)
def on_trackbar_change1(min_val):
    global depth_min
    depth_min = cv2.getTrackbarPos('Min Temp', 'Thermal Image')

def on_trackbar_change2(min_val):
    global depth_max
    depth_max = cv2.getTrackbarPos('Max Temp', 'Thermal Image')

def main():
    global depth_min, depth_max
    depth_min = 5  # 默认温度阈值区间
    depth_max = 25
    global checkquit # 用于结束程序
    checkquit = 1
    try:
        # 打开串口，配置波特率、数据位、停止位、校验位等参数
        ser = serial.Serial('COM4', 115200, timeout=1, bytesize=8, stopbits=1, parity='N')
        print("串口打开成功!")
        buffer = b""  # 用于缓存接收到的数据

        # 创建OpenCV显示窗口和拖动条
        cv2.namedWindow('Thermal Image')
        cv2.createTrackbar('Min Temp', 'Thermal Image', depth_min, 50, on_trackbar_change1)
        cv2.setTrackbarMin('Min Temp', 'Thermal Image',-10)
        cv2.createTrackbar('Max Temp', 'Thermal Image', depth_max, 50, on_trackbar_change2)
        cv2.setTrackbarMin('Max Temp', 'Thermal Image', -10)

        while checkquit == 1:
            # 持续读取数据
            data = ser.read(ser.in_waiting)  # 读取串口缓冲区中的所有数据
            buffer += data  # 将新读取的数据添加到缓存中

            # 尝试找到帧头
            frame_head_pattern = b'\x5A\x5A'  # 假设帧头是两个字节: 0x5A, 0x5A
            while len(buffer) >= 1544:
                frame_head_index = find_frame_head(buffer, frame_head_pattern)

                if frame_head_index != -1:  # 找到帧头
                    # 提取从帧头开始的1544字节数据
                    raw_data = buffer[frame_head_index:frame_head_index + 1544]
                    buffer = buffer[frame_head_index + 1544:]  # 从缓存中移除已经处理的帧

                    # 调用解析函数逐帧解析并显示数据
                    temp_matrix_flipped = parse_frame(raw_data)

                    # 由于初始分辨率仅有32*24，故将其扩展为与深度图和RGB图相同的640*400，使用线性插值
                    thermal_image = cv2.resize(temp_matrix_flipped, (32*20, 24*20), interpolation=cv2.INTER_LINEAR)

                    # 应用设定的温度阈值
                    thermal_display = np.clip(thermal_image, depth_min, depth_max)
                    thermal_display = np.where((thermal_image >= depth_min) & (thermal_image <= depth_max), thermal_display, 0)

                    # 映射温度到彩色梯度（便于显示）
                    thermal_display_normalized = cv2.normalize(thermal_display, None, 0, 255, cv2.NORM_MINMAX)
                    thermal_colormap = cv2.applyColorMap(thermal_display_normalized.astype('uint8'), cv2.COLORMAP_JET)
                    # 显示
                    cv2.imshow('Thermal Image', thermal_colormap)

                    # 保存红外热成像图像至指定路径，便于检测程序读取
                    output_directory = r'E:\PycharmProjects\DoubleCam\standard\DM'
                    output_filename = f"{output_directory}/{'temp'}.{'npy'}"
                    np.save(output_filename, thermal_display)
                    # 按 'q' 或 ESC 退出
                    key = cv2.waitKey(1)
                    if key & 0xFF == ord('q') or key & 0xFF == 27:
                        checkquit = 0
                        break
                else:
                    # 如果找不到帧头，则退出循环等待更多数据
                    break
        # 退出，关闭串口
        ser.close()
        print("串口已关闭.")
    except serial.SerialException as e:
        print("打开串口失败:", e)
    except Exception as e:
        print("发生错误:", e)

if __name__ == "__main__":
    main()