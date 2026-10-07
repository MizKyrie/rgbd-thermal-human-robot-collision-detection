import robotcontrol


# 测试函数
def test_count(test_count):
    # 初始化logger
    robotcontrol.logger_init()

    # 启动测试
    robotcontrol.logger.info("{0} test beginning...".format(robotcontrol.Auboi5Robot.get_local_time()))

    # 系统初始化
    robotcontrol.Auboi5Robot.initialize()

    # 创建机械臂控制类
    robot = robotcontrol.Auboi5Robot()

    # 创建上下文
    handle_move = robot.create_context()

    # 打印上下文
    # logger.info("robot.rshd={0}".format(handle))
    robotcontrol.logger.info("---------------------------------------move robot.rshd={0}".format(handle_move))
    try:

        # 链接服务器
        # ip = 'localhost'
        ip = '192.168.100.10'

        port = 8899
        result = robot.connect(ip, port)

        if result != robotcontrol.RobotErrorType.RobotError_SUCC:
            robotcontrol.logger.info("connect server{0}:{1} failed.".format(ip, port))
        else:
            # 循环测试

            # robot.robot_startup()

            robot.init_profile()
            # 设置关节最大加速度
            robot.set_joint_maxacc((0.5, 0.5, 0.5, 0.5, 0.5, 0.5))

            # robot.set_joint_maxacc((0.5, 0.5, 0.5, 0.5, 0.5, 0.5))

            # 设置关节最大加速度
            robot.set_joint_maxvelc((0.5, 0.5, 0.5, 0.5, 0.5, 0.5))

            joint1 = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

            track_file = "./track_4.txt"

            # robot.set_end_max_line_acc(0.8)
            # robot.set_end_max_line_velc(0.8)

            # 设置关节最大加加速度比率
            # robot.set_jerk_acc_ratio(0.25);
            # robot.set_jerk_angle_acc_ratio(0.25);

            # robot.set_common_jerk_rotio(2);
            while test_count > 0:
                test_count -= 1

                robotcontrol.libpyauboi5.move_joint(handle_move, joint1)

                robotcontrol.libpyauboi5.clear_offline_track(handle_move)

                robotcontrol.libpyauboi5.append_offline_track_file(handle_move, track_file)

                robotcontrol.libpyauboi5.startup_offline_track(handle_move)




    except robotcontrol.RobotError as e:
        robotcontrol.logger.error("{0} robot Event:{1}".format(robot.get_local_time(), e))


    finally:
        # 断开服务器链接
        # if robot.connected:
        # 关闭机械臂
        # robot.robot_shutdown()
        # logger.info("******************************robot_shutdown**********************")
        # 断开机械臂链接
        # robot.disconnect()
        # logger.info("******************************disconnect2**********************")
        # 释放库资源
        # Auboi5Robot.uninitialize()
        robotcontrol.logger.info("{0} test completed.".format(robotcontrol.Auboi5Robot.get_local_time()))


if __name__ == '__main__':


    test_count(1)
   
    robotcontrol.logger.info("test completed")


