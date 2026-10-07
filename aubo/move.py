import robotcontrol


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
ip = '192.168.100.10'

port = 8899
result = robot.connect(ip, port)
robotcontrol.Auboi5Robot.move_joint(robot,(-1.8217856884002686, 4.286439434508793e-05, 3.0617425181844737e-06, 0.0, 7.336056114581879e-06, 3.6680280572909396e-06))
for i in range(0,300):
    robotcontrol.Auboi5Robot.move_joint(robot,(-2.9257490634918213, 0.11199241876602173, -0.962587296962738, -0.2975357472896576, -0.07939079403877258, 7.33605629648082e-05))
    robotcontrol.Auboi5Robot.move_joint(robot,(-2.7713911533355713, 0.2725012004375458, -1.573270320892334, 1.1650720834732056, -0.7324171662330627, 0.0004218232352286577))

robotcontrol.Auboi5Robot.move_joint(robot,(-1.8217856884002686, 4.286439434508793e-05, 3.0617425181844737e-06, 0.0, 7.336056114581879e-06, 3.6680280572909396e-06))