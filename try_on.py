import socket


def invoke_image():
    file1 = "./my_model/captured_image.jpg"
    response_filename = "./try_on/response.jpg"

    import socket

    # Read an image file as binary data
    image_filename = file1
    with open(image_filename, "rb") as image_file:
        image_data = image_file.read()

    # Setup client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 9999))  # Connect to server

    # Send the image data to the server
    client_socket.sendall(image_data)  # Use sendall to ensure all data is sent

    # Close the client socket
    client_socket.close()
    start_server()
    return True



def start_server(host='localhost', port=8888):
    # Create a server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}")

    # Accept a client connection
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}")

    try:
        # Receive image data from the client
        image_data = b""
        while True:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            image_data += chunk

        # Save the received image data to a file
        image_filename = "try_on/response.jpg"
        with open(image_filename, "wb") as image_file:
            image_file.write(image_data)

        print(f"Received image and saved as {image_filename}")

    finally:
        # Close the client socket
        client_socket.close()