# RGBD-Thermal Human-Robot Collision Detection

基于 RGBD 相机与红外传感器的机器人与人体碰撞检测系统

## 项目简介

本项目通过 **Intel RealSense D435i** 双目相机与 **GYMCU90640** 红外传感器，采集环境的 RGB、深度和温度信息，利用多传感器融合算法识别机械臂AUBO i7与人体，并判断是否发生碰撞，最终通过 TCP 通信触发机械臂急停。

## 系统架构
传感器 → 数据采集 → 人体/机械臂识别 → 碰撞检测 → TCP传输 → 急停控制
<img width="705" height="406.5" alt="image" src="https://github.com/user-attachments/assets/2896656f-a7d3-45cb-92a0-89b491661360" />

## 技术栈

- **编程语言**：Python 3.8 / 3.10
- **相机**：Intel RealSense D435i（pyrealsense2）
- **红外传感器**：GYMCU90640（serial）
- **图像处理**：OpenCV、NumPy
- **通信**：socket、threading
- **机器人控制**：AUBO SDK（robotcontrol.py）

## 硬件清单

| 设备 | 型号 | 用途 |
| :--- | :--- | :--- |
| RGBD相机 | Intel RealSense D435i | RGB + 深度信息采集 |
| 红外传感器 | GYMCU90640 | 温度信息采集 |
| 机械臂 | AUBO i7 | 被控对象 |
| 夹具 | 3D打印 | 固定红外相机 |

## 算法说明

1. **人体检测**：寻找热成像图中温度最高的 50×50 区域，若平均温度 > 20°C，则基于颜色、深度、温度的加权差异扩展区域，生成人体掩膜。
2. **机械臂检测**：手动选定机械臂上的一个 50×50 区域，基于颜色和深度差异扩展区域，生成机械臂掩膜。
3. **碰撞检测**：计算机械臂与人体区域的平均深度差，若小于阈值（实验中为 50），则判定为碰撞。
4. **急停控制**：检测端通过 TCP 发送 '1' 或 '0' 至控制端，控制端收到 '1' 时立即调用 `disconnect` 停止机械臂。

## 团队分工

本项目由三位本科生合作完成：

| 成员 | GitHub | 贡献 |
| :--- | :--- | :--- |
| **MizKyrie** | [@MizKyrie](https://github.com/MizKyrie) | 红外相机配置，目标提取与碰撞检测算法编写，最终项目整理归档 |
| **operatorzhy** | [@operatorzhy](https://github.com/operatorzhy) | 机械臂配置与急停控制算法实现，实验平台设计 |
| **linyuxuantherion** | [@linyuxuantherion](https://github.com/linyuxuantherion) | 双目相机配置，夹具设计与打印，可视化与代码整合  |

## 成果展示

- 演示视频：
https://github.com/user-attachments/assets/d4eaae31-3443-479d-afcc-de608a6239d8
<img width="560" height="372" alt="演示视频_解说" src="https://github.com/user-attachments/assets/05d9e280-42f6-4c94-afd5-8e4528c4bbc4" />



- 系统截图：
- <img width="879" height="452" alt="9338c2a4e23daf59a3948e93424b567a" src="https://github.com/user-attachments/assets/e694ea99-df6b-4b88-88a1-2a6e282d2ba0" />

## 已知局限与后续改进方向

- 当前算法耗时 5~8 秒，实时性有待提升（可引入深度学习或 GPU 加速）
- 仅支持急停响应，可扩展至自动避障、速度调整等
- 单方向摄像头存在遮挡问题，可引入多相机或激光雷达

## 运行说明

1. 安装依赖：`pip install -r requirements.txt`
2. 检测端：依次运行 `shot_depth_img.py`、`thermal_camera.py`、`check_if_collision.py`
3. 控制端：运行 `move.py`
4. 确保两台电脑在同一局域网，并修改 IP 地址

Co-authored-by: operatorzhy <operatorzhy@users.noreply.github.com>
Co-authored-by: linyuxuantherion <linyuxuantherion@users.noreply.github.com>
