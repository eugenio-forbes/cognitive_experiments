import socket
import threading
import json
from datetime import datetime


server_ip = '192.168.1.1'
server_port = 8888
datetime_format = 

### Message types for which Elemem sends a response back to client
message_types_with_response = {'CONNECTED', 'CONFIGURE', 'READY', 'HEARTBEAT'}

def prepare_response(client_message):
    server_response = {
        'type': f"{client_message['type']}_OK",
        'id': client_message['id'],
        'time': datetime.now(),
        'data': client_message['data']
    }
    return server_response

def handle_client(client, client_address):
    
    message_buffer = ''
    receiving_from_client = True
    try:
        while receiving_from_client:
            
            new_bytes = client.recv(1024)
            
            if not new_bytes:
                break

            message_buffer += new_bytes.decode('utf-8')

            while '\n' in message_buffer:
                message_string, message_buffer = message_buffer.split('\n', 1)
     
                message = json.loads(message_string)
                
                message_type = message['type']

                if message_type in message_types_with_response:
                    server_response = prepare_response(message)
                    response_string = json.dumps(server_response) + '\n'
                    client.sendall(response_string.encode('utf-8'))

    except ConnectionResetError:
        print("Connection reset by client.")
    finally:
        client.close()
        print(f"Client disconnected.")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((server_ip, server_port))
        server_socket.listen(1)

        while True:
            client, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client, client_address))
            client_thread.start()

if __name__ == "__main__":
    start_server()