import socket

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
    print(f"接收到数据: {type(data.decode('utf-8'))}")

# 关闭连接
# client_socket.close()