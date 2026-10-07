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

print(robotcontrol.Auboi5Robot.get_current_waypoint(robot))