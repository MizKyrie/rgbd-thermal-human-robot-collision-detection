import threading
import time
import socket
import robotcontrol
# 定义两个任务函数
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
def task1():
    print("任务1开始执行")
    # 初始化logger

    robotcontrol.Auboi5Robot.move_joint(robot, (-1.8217856884002686, 4.286439434508793e-05, 3.0617425181844737e-06, 0.0, 7.336056114581879e-06,3.6680280572909396e-06))
    for i in range(0, 300):
        robotcontrol.Auboi5Robot.move_joint(robot, (-2.9257490634918213, 0.11199241876602173, -0.962587296962738, -0.2975357472896576, -0.07939079403877258,7.33605629648082e-05))
        robotcontrol.Auboi5Robot.move_joint(robot, (-2.7713911533355713, 0.2725012004375458, -1.573270320892334, 1.1650720834732056, -0.7324171662330627,0.0004218232352286577))

    robotcontrol.Auboi5Robot.move_joint(robot, (-1.8217856884002686, 4.286439434508793e-05, 3.0617425181844737e-06, 0.0, 7.336056114581879e-06,3.6680280572909396e-06))
    print("任务1执行结束")

def task2():
    print("任务2开始执行")
    # 创建一个TCP/IP套接字
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 连接到PC1的IP和端口
    client_socket.connect(('192.168.101.76', 12345))  # 替换为PC1的实际IP地址

    # # 发送数据
    # client_socket.sendall(b'Hello from PC2!')

    # 接收数据
    while True:
        data = client_socket.recv(1024)
        print(f"接收到数据: {data.decode('utf-8')}")

        if data.decode('utf-8').count('1')>0:
            robotcontrol.Auboi5Robot.disconnect(robot)


# 创建两个线程
thread1 = threading.Thread(target=task1)
thread2 = threading.Thread(target=task2)

# 启动线程
thread1.start()
thread2.start()

# 等待线程执行完毕
thread1.join()
thread2.join()

print("所有线程执行完毕")