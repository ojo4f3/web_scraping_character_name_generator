<h1 style="text-align:center">Character Name Generator</h1>
CS361 Project Microservice, Summer 2023<br>
By: Steven Colton Crowther<br>
Version 1.0.1 (19 JAN 2024)

<h2>Description</h2>  
Character name generator is a socket server that takes a client request and sends a reply. It is built for another program requesting names ideas for creating characters. 

<h3>Server</h3>
To connect to the server locally use the below code. The Header defines the default message size between server and client. The header message will be the number of bytes needed for the other end to received the encoded message. The format is the common 'utf-8' format. The port used will be 7567.

```python
import json  
import socket

HEADER = 64
FORMAT = 'utf-8'
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
client.connect(socket.gethostname(), 7567)
```

<h3>Request</h3>
The client's request must be a dictionary that is converted to a JSON string. There are two key=value pairs, one for gender (boy, girl, male, female, m, f) and one for letter (and letter in upper or lower case).

```python
example_request = {'gender': 'boy', 'letter': 'J'}
json_request = json.dumps(example_request)  
encoded_message = json_request.encode(FORMAT)  
message_length = len(encoded_message)  
byte_length = str(message_length).encode(FORMAT)  
byte_length += b' ' * (HEADER - len(byte_length))  
  
# Send size and then message  
client.send(byte_length)  
client.send(encoded_message)  

```  
The message is encoded and the message size is obtained and sent ahead of the encoded message. This way the server knows the size of message about to be sent.

<h3>Response</h3>
There will be two responses for every message. First there is a 'Message received' the server will send once the encoded message arrives. The second message will either be an error message or the response results. The recommended receiving method is below:

```python
listening = True 

# Listen for reply
while listening: 
	# Will first receive a 'Message received' message
	reply_length = int(client.recv(HEADER).decode(FORMAT))  
	if reply_length:  
	print(client.recv(reply_length).decode(FORMAT))  

	# Will now receive the response from the request
	reply_length = int(client.recv(HEADER).decode(FORMAT))  
	if reply_length:  
	received_json = client.recv(reply_length).decode(FORMAT)
	json_data = json.loads(received_json)  
	client.close()  
	listening = False
```

Finally, the `json_data` contains the response information in JSON format which can be parse to get the names and information.

An example response is below:
```python
json_data = [
	{'name': 'Jel', 'origin': 'Swahili'},
	{'name': 'Jensynn', 'origin': 'Finnish,Norwegian'},
	{'name': 'Jem', 'origin': 'English'},
	{'name': 'Jeevansh', 'origin': 'Indian'},
	{'name': 'Jeffey', 'origin': 'English'}, 
	{'name': 'Jenkin', 'origin': 'English'}, 
	{'name': 'Jens', 'origin': 'Hebrew'}, 
	{'name': 'Jenish', 'origin': 'Indian'}, 
	{'name': 'Jeevit', 'origin': 'Indian'}, 
	{'name': 'Jennison', 'origin': 'English'}
]
```

<h3>UML Sequence Diagram</h3>

![UML Sequence Diagram](https://github.com/ojo4f3/character_name_generator/blob/main/uml-sequence.png)
