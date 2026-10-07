import numpy as np
import keyboard
import cv2
import socket

def human_fctn(rgb, depth, temp, search_region_size=30, min_temp_threshold=20,
                   color_threshold=100, depth_threshold=100, temp_threshold=5,
                   color_weight=0.6, depth_weight=0.1, temp_weight=0.3):
    """
    处理RGB、深度和温度图像，输出处理后的闭运算掩膜。
    参数：
    - rgb: RGB图像 (numpy array)
    - depth: 深度图像 (numpy array)
    - temp: 温度图像 (numpy array)
    - search_region_size: 搜索区域的大小
    - min_temp_threshold: 温度阈值
    - color_threshold: 颜色差异阈值
    - depth_threshold: 深度差异阈值
    - temp_threshold: 温度差异阈值
    - color_weight: 颜色差异的权重
    - depth_weight: 深度差异的权重
    - temp_weight: 温度差异的权重
    返回：
    - closed_mask: 经过闭运算后的二值掩膜 (numpy array)
    """
    # RGB图像实际是BGR顺序，将其转换为RGB顺序
    rgb_corrected = rgb[..., [2, 1, 0]]  # 交换BGR到RGB

    # 获取图像的尺寸
    rgb_height, rgb_width = rgb_corrected.shape[:2]
    depth_height, depth_width = depth.shape[:2]
    temp_height, temp_width = temp.shape

    # 确保深度图像和温度图像的尺寸与RGB图像一致
    assert rgb_height == depth_height and rgb_width == depth_width, "RGB and Depth images must have the same dimensions"
    assert rgb_height == temp_height and rgb_width == temp_width, "RGB and Temperature images must have the same dimensions"

    # 寻找温度图像中温度最高的50x50区域
    max_temp_index = np.unravel_index(np.argmax(temp), temp.shape)  # 最大温度的位置

    # 计算初始搜索区域的左上角坐标
    x_start = max(0, max_temp_index[1] - search_region_size // 2)
    y_start = max(0, max_temp_index[0] - search_region_size // 2)

    # 确保搜索区域不超出图像边界
    x_end = min(rgb_width, x_start + search_region_size)
    y_end = min(rgb_height, y_start + search_region_size)

    # 提取初始区域的RGB、深度和温度信息
    initial_region_rgb = rgb_corrected[y_start:y_end, x_start:x_end]
    initial_region_depth = depth[y_start:y_end, x_start:x_end]
    initial_region_temp = temp[y_start:y_end, x_start:x_end]

    # 计算初始区域的平均RGB值、深度值和温度值
    initial_rgb_mean = np.mean(initial_region_rgb, axis=(0, 1))
    initial_depth_mean = np.mean(initial_region_depth)
    initial_temp_mean = np.mean(initial_region_temp)

    # 检查区域的平均温度是否超过20°C
    if initial_temp_mean < min_temp_threshold:
        print(f"Temperature is too low in the initial region (below {min_temp_threshold}°C), skipping further search.")
        return np.zeros(rgb_corrected.shape[:2], dtype=np.uint8)  # 无需进一步处理，直接返回全零掩膜

    # 创建一个二值图像，初始化为全零
    binary_mask = np.zeros(rgb_corrected.shape[:2], dtype=np.uint8)

    # 扩展区域，逐步搜索相似区域
    for y in range(rgb_corrected.shape[0]):
        for x in range(rgb_corrected.shape[1]):
            # 计算当前像素的颜色、深度和温度与初始区域的相似性
            color_diff = np.linalg.norm(rgb_corrected[y, x] - initial_rgb_mean)  # 计算颜色差异
            depth_diff = abs(depth[y, x] - initial_depth_mean)  # 计算深度差异
            temp_diff = abs(temp[y, x] - initial_temp_mean)  # 计算温度差异

            # 计算加权差异值
            weighted_diff = color_weight * color_diff + depth_weight * depth_diff + temp_weight * temp_diff

            # 如果加权差异小于阈值，认为该像素属于人体区域
            if weighted_diff < (color_threshold + depth_threshold + temp_threshold) / 3:
                binary_mask[y, x] = 255  # 标记为人体区域

    # 进行闭运算：先膨胀后腐蚀
    kernel = np.ones((10, 10), np.uint8)  # 定义一个10x10的结构元素
    closed_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)
    human_closed_mask = closed_mask
    return human_closed_mask

def robot_fctn(rgb, depth, temp,
                           color_threshold=100, depth_threshold=100,
                           color_weight=0.7, kernel_size=(15, 15)):
    """
    处理RGB、深度和温度图像，检测机械臂区域并返回经过闭运算后的二值掩膜。
    参数：
    - rgb: RGB图像 (numpy array)
    - depth: 深度图像 (numpy array)
    - temp: 温度图像 (numpy array)
    - x_start, y_start: 初始矩形区域的左上角坐标
    - width, height: 初始矩形区域的宽度和高度
    - color_threshold: 颜色差异阈值
    - depth_threshold: 深度差异阈值
    - color_weight: 颜色差异的权重
    - kernel_size: 结构元素的大小，用于形态学闭运算
    返回：
    - closed_mask: 经过闭运算后的二值掩膜 (numpy array)
    """
    x_start, y_start, width, height = 270, 410, 50, 50   # 根据图像手动调整

    # RGB图像实际是BGR顺序，将其转换为RGB顺序
    rgb_corrected = rgb[..., [2, 1, 0]]  # 交换BGR到RGB

    # 获取初始区域的RGB和深度信息
    initial_region_rgb = rgb_corrected[y_start:y_start + height, x_start:x_start + width]
    initial_region_depth = depth[y_start:y_start + height, x_start:x_start + width]

    # 创建一个二值图像，初始化为全零
    binary_mask = np.zeros(rgb_corrected.shape[:2], dtype=np.uint8)

    # 获取初始区域的平均颜色和深度
    initial_rgb_mean = np.mean(initial_region_rgb, axis=(0, 1))
    initial_depth_mean = np.mean(initial_region_depth)

    # 扩展区域，逐步搜索相似区域
    for y in range(rgb_corrected.shape[0]):
        for x in range(rgb_corrected.shape[1]):
            # 计算当前像素的颜色和深度与初始区域的相似性
            color_diff = np.linalg.norm(rgb_corrected[y, x] - initial_rgb_mean)  # 计算颜色差异
            depth_diff = abs(depth[y, x] - initial_depth_mean)  # 计算深度差异

            # 计算加权差异值
            weighted_diff = color_weight * color_diff + (1 - color_weight) * depth_diff

            # 如果加权差异小于阈值，认为该像素属于机械臂区域
            if weighted_diff < (color_threshold + depth_threshold) / 2:
                binary_mask[y, x] = 255  # 标记为机械臂区域

    # 进行闭运算：先膨胀后腐蚀
    kernel = np.ones(kernel_size, np.uint8)  # 定义结构元素
    closed_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)

    robot_closed_mask = closed_mask
    return robot_closed_mask

def check_collision(rgb, depth, temp, depth_threshold):
    """
    判断机械臂与人体是否发生碰撞
    参数:
    - rgb: 输入的RGB图像
    - depth: 输入的深度图像
    - temp: 输入的温度图像（未使用，可以根据需求调整）
    - robot_params: 机械臂区域参数 (x_start, y_start, width, height)
    - human_params: 人体区域参数 (x_start, y_start, width, height)
    - depth_threshold: 判定碰撞的深度差异阈值
    返回:
    - "Collision Detected" 或 "No Collision"
    """
    # 获取机械臂的闭运算掩膜
    robot_closed_mask = robot_fctn(rgb, depth, temp)

    # 获取人体的闭运算掩膜
    human_closed_mask = human_fctn(rgb, depth, temp)

    # 提取机械臂区域的深度信息
    robot_depth_info = depth[robot_closed_mask == 255]

    # 提取人体区域的深度信息
    human_depth_info = depth[human_closed_mask == 255]

    # 如果机械臂或人体区域没有深度信息，返回0
    if robot_depth_info.size == 0 or human_depth_info.size == 0:
        return 0

    # 计算机械臂和人体区域的平均深度值
    robot_avg_depth = np.mean(robot_depth_info)
    human_avg_depth = np.mean(human_depth_info)

    # 判断两个平均深度值的差是否小于设定的深度阈值
    depth_diff = np.abs(robot_avg_depth - human_avg_depth)

    # 如果深度差小于depth_threshold，判断为碰撞发生，返回1
    if depth_diff < depth_threshold:
        return 1
    else:
        # 反之则无碰撞，返回0
        return 0

if __name__ == "__main__":
    # 由于在实际操作过程中，检测端与机械臂的控制端并非在同一台电脑上
    # 所以需要传输结果（0/1）至控制端，此处采用同局域网下的无限连接传输
    # 创建一个TCP/IP套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 绑定到指定的IP和端口
    server_socket.bind(('0.0.0.0', 12345))  # 绑定所有网络接口，端口号为12345
    # 开始监听
    server_socket.listen(1)
    print("等待连接...")
    # 等待连接
    client_socket, client_address = server_socket.accept()
    print(f"连接来自：{client_address}") # 成功连接后输出控制端地址

    # 加载存放的图像数据
    input_directory1 = r'E:\PycharmProjects\DoubleCam\standard\DM'
    input_filename1 = f"{input_directory1}/{'temp'}.{'npy'}"
    input_directory2 = r'E:\PycharmProjects\DoubleCam\standard\DM'
    input_filename2 = f"{input_directory2}/{'RGB'}.{'npy'}"
    input_directory3 = r'E:\PycharmProjects\DoubleCam\standard\DM'
    input_filename3 = f"{input_directory3}/{'depth'}.{'npy'}"
    while True:
        try:
            # 尝试加载文件，允许 pickle 数据
            temp = np.load(input_filename1, allow_pickle=True)
            rgb = np.load(input_filename2, allow_pickle=True)
            depth = np.load(input_filename3, allow_pickle=True)

            # 若加载成功，通过函数计算是否碰撞
            result = check_collision(rgb, depth, temp, depth_threshold=50)
            # 输出结果（0/1）
            print(result)
            # 传输结果（字符串格式）
            if result == 1:
                client_socket.sendall(b'1')
            elif result == 0:
                client_socket.sendall(b'0')
# 因为读取的数据反复更新，有几率读不到
        except ValueError as e:
            # 如果遇到 ValueError（如加载 pickle 数据失败），重新读取
            continue
        except Exception as e:
            # 如果遇到其他异常也尝试重新读取
            continue
        # 按下'q'键退出
        if keyboard.is_pressed('q'):
            print("程序退出。")
            break

    # 退出并关闭连接
    client_socket.close()
    server_socket.close()
