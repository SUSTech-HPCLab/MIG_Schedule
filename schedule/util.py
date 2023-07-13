import subprocess
import socket
import re

MIG_instance_map = {
    '1g.10gb': 19,
    '2g.20gb': 14,
    '3g.40gb': 9,
    '4g.40gb': 5,
    '7g.80gb': 0,
}


Map_table = {

}
def execute_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout.strip() 
    return output

def get_uuid(ip, port, GPU_ID, MIG_Instace):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = (ip, port)
    client_socket.connect(server_address)

    message = "nvidia-smi -L"
    client_socket.sendall(message.encode())
    uuid = client_socket.recv(1024).decode()
    client_socket.close()
    lines = uuid.splitlines()  # 将多行文本分割成行
    uuid_list = []
    for line in lines:
        if MIG_Instace in line:
            uuid_list.append(re.search(r"UUID:\s*([a-zA-Z0-9\-]+)", line).group(1))
    print(uuid_list)


def create_instance(config, ip=0, GPU=0):
    CI = MIG_instance_map.get(config)
    result = execute_command("sudo nvidia-smi mig -i " + str(GPU) + " -cgi "   + str(CI) + " -C")
    print(result)
    return CI

