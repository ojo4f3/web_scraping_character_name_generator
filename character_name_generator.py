"""
Title: character_name_generator
Version: 1.0.1
Description: Microservice socket server that takes requests as JSON strings of gender and first letter and sends a
response with 10 random names scraped from the web that match the criteria.
Last update: 19 JAN 2024
Author: Steven Crowther
"""

# -------------------------- IMPORTS ------------------------------------
import time
import json
import math
import random
import socket
import requests
import threading
from bs4 import BeautifulSoup


# ----------------------- VARIABLES & SETUP -----------------------------
# --------------------- Message format set up ---------------------------
# Default message input size
HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "DISCONNECT"
DEFAULT_ERROR = "No gender key present. Ensure the JSON has connection, gender, and letter keys."

# --------------------  Set up server Host ------------------------------
# Listening on port 7567
PORT = 7567
# Get host device's local IP address
HOST_MACHINE = socket.gethostbyname(socket.gethostname())
HOST = (HOST_MACHINE, PORT)

# -------------------- Create Socket ------------------------------------
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to host address
server.bind(HOST)


# -------------------- FUNCTIONS ----------------------------------------
# ------------ Create and Receive New Connections -----------------------
def start_connection() -> None:
    """
    Create and handle new connections
    """
    server.listen()
    while True:
        # Accept connection and retrieve connection information
        connection, client_address = server.accept()
        # Define and start thread
        thread = threading.Thread(target=comm_thread, args=(connection, client_address))
        thread.start()


# ------------------ Connection Handler ---------------------------------
def comm_thread(connection: socket, address: str) -> None:
    """
    Handles individual connections
    """
    print(f"New connection: {address} connected.")
    # Wait for connection to fully set up
    time.sleep(1)
    # Will wait until a message is received from the client
    # First message will have a size of 64 bytes and message_length is the length of the next message
    message_length = int(connection.recv(HEADER).decode(FORMAT))
    if message_length:
        received_json = connection.recv(message_length).decode(FORMAT)
        json_data = json.loads(received_json)

        # Send confirmation message
        confirm_encoded = "Message received".encode(FORMAT)
        confirm_length = len(confirm_encoded)
        byte_length = str(confirm_length).encode(FORMAT)
        byte_length += b' ' * (HEADER - len(byte_length))
        connection.send(byte_length)
        connection.send(confirm_encoded)

    # Validate request
    try:
        gender_request = json_data['gender']
    except KeyError:
        connection.send(f"Error: No 'gender' key present. {DEFAULT_ERROR}".encode(FORMAT))
        connection.close()
    try:
        letter_request = json_data['letter']
    except KeyError:
        connection.send(f"Error received. No 'letter' key present. {DEFAULT_ERROR}".encode(FORMAT))
        connection.close()

    # Process request and send response
    response = parse_request(gender_request, letter_request)
    if response:
        encoded_response = response.encode(FORMAT)
        response_length = len(encoded_response)
        byte_length = str(response_length).encode(FORMAT)
        byte_length += b' ' * (HEADER - len(byte_length))
        connection.send(byte_length)
        connection.send(encoded_response)
        print("Message sent!")
        time.sleep(3)
    connection.close()


# ------------- Parse and Verify Request --------------------------------
def parse_request(gender: str, letter: str) -> json or str:
    """
    Ensures the request data is valid and calls the web scraping function
    """
    genders = ['girl', 'boy', 'f', 'm', 'female', 'male']
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
               'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    gen = gender.lower()
    let = letter.lower()
    if gen in genders:
        if gen == 'female' or gen == 'f':
            gen = 'girl'
        if gen == 'male' or gen == 'm':
            gen = 'boy'
        if let in letters:
            return scrape_names(gen, let)
        return "Request error. The value in the 'letter' key, is not a letter."
    return "Request error. The value in the 'gender' key, is not a gender."


# ---------------------- Get Names from the Web -------------------------
def scrape_names(gender: str, letter: str) -> json or str:
    """
    Access the internet and scrapes random names based on the gender and first letter.
    Returns an error message or JSON string of results.
    """
    url = f"https://www.momjunction.com/baby-names/{gender}/starting-with-{letter}/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find number of names
        pages = 1
        names_info = []
        total_names = int((soup.title.text.split())[0])
        if total_names > 100:
            pages = math.ceil(total_names / 100)
        # Get random names
        page = random.randint(1, pages)
        # Load the random page
        if page != 1:
            page_url = f"https://www.momjunction.com/baby-names/{gender}/starting-with-{letter}/page/{page}"
            response = requests.get(page_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
            else:
                return'Connection error. Try again.'
        # Collect names
        page_names = soup.find_all('a', class_="baby-name-shlst")
        elements = random.sample(page_names, 10)
        for names in elements:
            name = names['data-name'].capitalize()
            origin = names['data-origin']
            names_info.append({'name': name, 'origin': origin})
        # Return the results as a JSON string
        return json.dumps(names_info)
    else:
        return 'Connection error. Try again.'


# ----------------------------- CODE TO EXECUTE -------------------------
if __name__ == "__main__":
    print("Server is starting. Listening on port 7567...")
    start_connection()
