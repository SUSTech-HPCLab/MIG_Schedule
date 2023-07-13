import socket

# def communicate_with_server(server_ip, server_port, message):
#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#     server_address = (server_ip, server_port)
#     client_socket.connect(server_address)

#     client_socket.sendall(message.encode())

#     client_socket.close()

# server_ip = '0.0.0.0'  # 服务器的IP地址
# server_port = 12345  # 服务器的端口
# message = "Hello, server!"

# communicate_with_server(server_ip, server_port, message)

input = "cd test && CUDA_VISIBLE_DEVICES=MIG-32522c13-1a59-5776-9d30-e0ae7b6a4874  conda run -n test test"
cuda_visible_devices = input.split('CUDA_VISIBLE_DEVICES=')[1].split()[0]
print(cuda_visible_devices)