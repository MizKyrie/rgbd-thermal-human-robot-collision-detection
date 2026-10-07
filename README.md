# RGBD-Thermal Human-Robot Collision Detection

基于 RGBD 相机与红外传感器的机器人与人体碰撞检测系统

## 项目简介

本项目为华中科技大学《机器人》课程设计。通过 **Intel RealSense D435i** 双目相机与 **GYMCU90640** 红外传感器，采集环境的 RGB、深度和温度信息，利用多传感器融合算法识别机械臂（AUBO i7）与人体，并判断是否发生碰撞，最终通过 TCP 通信触发机械臂急停。

## 系统架构
