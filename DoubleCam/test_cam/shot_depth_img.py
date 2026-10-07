import pyrealsense2 as rs
import numpy as np
import cv2

# 添加相机图像滤波器
spatial = rs.spatial_filter()
temporal = rs.temporal_filter()
hole_filling = rs.hole_filling_filter()

# 此处列表用于缓存数据
# 由于红外相机存在延迟，需要手动为双目相机设置延迟来确保两处图像一致
color_list = []
depth_list = []
delay = 10


# OpenCV的图像显示中拖动条的回调函数
# 深度图像的阈值
def on_trackbar_change1(min_val):
    global depth_min
    depth_min = cv2.getTrackbarPos('Min Depth', 'Depth Image')


def on_trackbar_change2(min_val):
    global depth_max
    depth_max = cv2.getTrackbarPos('Max Depth', 'Depth Image')


# 以下为调节两个相机显示误差时使用的拖动条，实际操作时不再使用

# def on_trackbar_changeDX(min_val):
#     global DX
#     DX = cv2.getTrackbarPos('X', 'Depth Image')

# def on_trackbar_changeDY(min_val):
#     global DY
#     DY = cv2.getTrackbarPos('Y', 'Depth Image')

# def on_trackbar_changeDS(min_val):
#     global DS
#     DS = cv2.getTrackbarPos('S', 'Depth Image')

# def on_trackbar_changeRX(min_val):
#     global RX
#     RX = cv2.getTrackbarPos('X', 'Depth Image')

# def on_trackbar_changeRY(min_val):
#     global RY
#     RY = cv2.getTrackbarPos('Y', 'Depth Image')

# def on_trackbar_changeRS(min_val):
#     global RS
#     RS = cv2.getTrackbarPos('S', 'Depth Image')

def main():
    global depth_min, depth_max
    depth_min = 500  # 默认深度区间
    depth_max = 2000
    default_depth_max = 10000  # 两个深度区间拖动条的最大值

    # 同上，用于调节图像误差，实际操作时不使用

    # global DX, DY, DS
    # DX = 0
    # DY = 0
    # DS = 100

    # global RX, RY, RS
    # RX = 0
    # RY = 0
    # RS = 100

    # 配置深度流和颜色流
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    # 启动通道管道
    pipeline.start(config)
    # 获取对齐对象
    align_to = rs.stream.color
    align = rs.align(align_to)

    try:
        # 创建OpenCV显示窗口和拖动条
        cv2.namedWindow('Depth Image')
        cv2.namedWindow('RGB Image')
        cv2.createTrackbar('Min Depth', 'Depth Image', depth_min, default_depth_max, on_trackbar_change1)
        cv2.createTrackbar('Max Depth', 'Depth Image', depth_max, default_depth_max, on_trackbar_change2)

        # 同上，用于调节图像误差，实际操作时不使用
        # cv2.createTrackbar('X', 'Depth Image', DX, 640, on_trackbar_changeDX)
        # cv2.setTrackbarMin('X', 'Depth Image', -480)
        # cv2.createTrackbar('Y', 'Depth Image', DY, 640, on_trackbar_changeDY)
        # cv2.setTrackbarMin('Y', 'Depth Image', -480)
        # cv2.createTrackbar('S', 'Depth Image', DS, 300, on_trackbar_changeDS)
        # cv2.setTrackbarMin('S', 'Depth Image', 1)

        # cv2.createTrackbar('X', 'RGB Image', RX, 320, on_trackbar_changeRX)
        # cv2.setTrackbarMin('X', 'RGB Image', -320)
        # cv2.createTrackbar('Y', 'RGB Image', RY, 240, on_trackbar_changeRY)
        # cv2.setTrackbarMin('Y', 'RGB Image', -240)
        # cv2.createTrackbar('S', 'RGB Image', RS, 200, on_trackbar_changeRS)
        # cv2.setTrackbarMin('S', 'RGB Image', 1)

        while True:
            # 尝试获取相机数据
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)
            # 读取深度信息
            depth_frame = aligned_frames.get_depth_frame()
            # 应用滤波器
            depth_frame = frames.get_depth_frame()
            depth_frame = spatial.process(depth_frame)
            depth_frame = temporal.process(depth_frame)
            depth_frame = hole_filling.process(depth_frame)
            # 读取RGB信息
            color_frame = aligned_frames.get_color_frame()

            # 有几率读不到，重新读取
            if not depth_frame:
                continue

            # 转换为numpy格式
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # 由于两个相机之间的显示误差，需要重新调节图片尺寸
            # 并且因为红外相机分辨率和检测范围都最小，故选择裁剪深度图和热成像图
            # 右侧注释表示调节时使用的变量，实操更换为调节结果
            # 裁剪比例 (S表示裁剪出图像中心的S%)
            crop_ratio1 = 0.50  # DS
            crop_ratio2 = 0.76  # RS
            # 获取图像的高度和宽度
            depth_height, depth_width = depth_image.shape[:2]
            color_height, color_width = color_image.shape[:2]
            # 计算裁剪区域的大小
            depth_crop_width = int(depth_width * crop_ratio1)
            depth_crop_height = int(depth_height * crop_ratio1)
            color_crop_width = int(color_width * crop_ratio2)
            color_crop_height = int(color_height * crop_ratio2)

            # 计算裁剪区域的左上角坐标（使裁剪框从图像中心开始）
            depth_x = (depth_width - depth_crop_width) // 2 - 15  # DX
            depth_y = (depth_height - depth_crop_height) // 2 + 0  # DY

            color_x = (color_width - color_crop_width) // 2 - 10  # RX
            color_y = (color_height - color_crop_height) // 2 + 0  # RY

            # 对两幅图像进行裁剪并将裁剪结果更新到原变量中
            depth_image = depth_image[depth_y:depth_y + depth_crop_height, depth_x:depth_x + depth_crop_width]
            color_image = color_image[color_y:color_y + color_crop_height, color_x:color_x + color_crop_width]

            # 调整图像大小回原始尺寸
            color_image = cv2.resize(color_image, (640, 480), interpolation=cv2.INTER_LINEAR)
            depth_image = cv2.resize(depth_image, (640, 480), interpolation=cv2.INTER_LINEAR)

            # 由于红外相机存在延迟，需要手动为双目相机设置延迟来确保两处图像一致
            # 存入当前图像至列表
            color_list.append(color_image)
            depth_list.append(depth_image)
            if len(color_list) <= delay:
                continue
            # 输出前第delay个图像
            color_image = color_list.pop(0)
            depth_image = depth_list.pop(0)

            # 应用深度阈值（手动调节）
            depth_display = np.clip(depth_image, depth_min, depth_max)
            depth_display = np.where((depth_image >= depth_min) & (depth_image <= depth_max), depth_display, 0)

            # 映射深度到彩色梯度（便于显示）
            depth_display_normalized = cv2.normalize(depth_display, None, 0, 255, cv2.NORM_MINMAX)
            depth_colormap = cv2.applyColorMap(depth_display_normalized.astype('uint8'), cv2.COLORMAP_JET)

            # 显示
            cv2.imshow('Depth Image', depth_colormap)
            cv2.imshow('RGB Image', color_image)

            # 保存图像（包括RGB与深度）至指定路径，便于检测程序读取
            output_directory = r'E:\PycharmProjects\DoubleCam\standard\DM'
            output_filename = f"{output_directory}/{'depth'}.{'npy'}"
            np.save(output_filename, depth_display)
            output_directory = r'E:\PycharmProjects\DoubleCam\standard\DM'
            output_filename = f"{output_directory}/{'RGB'}.{'npy'}"
            np.save(output_filename, color_image)

            # 按 'q' 或 ESC 退出
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q') or key & 0xFF == 27:
                break

    finally:
        # 退出
        pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()