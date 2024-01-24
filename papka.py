import socket
import queue
import threading
from cryptography.fernet import Fernet
import getpass
import socket, threading, time
from pyzbar import pyzbar
import cv2
import re


PORT = 5050
DISCONNECT_MESSAGE = "END"
SEND_FILE_MESSAGE = 'Send file'
SERVER = "192.168.0.6"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

shutdown = False
def draw_barcode(decoded, image):
    # n_points = len(decoded.polygon)
    # for i in range(n_points):
    #     image = cv2.line(image, decoded.polygon[i], decoded.polygon[(i+1) % n_points], color=(0, 255, 0), thickness=5)
    image = cv2.rectangle(image, (decoded.rect.left, decoded.rect.top),(decoded.rect.left + decoded.rect.width, decoded.rect.top + decoded.rect.height),color=(0, 255, 0), thickness=5)
    return image

def decode(image):
    # decodes all barcodes from an image
    decoded_objects = pyzbar.decode(image)
    for obj in decoded_objects:
        # draw the barcode
        image = draw_barcode(obj, image)
        # print barcode type & data
        print("Type:", obj.type)
        print("Data:", obj.data)
        print()
    return image



def receving(name, sock):
    while not shutdown:
        try:
            while True:
                data, addr = sock.recvfrom(1024)
                print(data.decode("utf-8"))
                time.sleep(0.001)
        except:
            pass

def load_key():
    a = open('crypto.key', 'rb').read()
    return a


def encrypt(filename, key):
    f = Fernet(key)
    with open(filename, 'rb') as file:
        file_data = file.read()
        encrypted_data = f.encrypt(file_data)
    with open(filename, 'wb') as file:
        file.write(encrypted_data)


def decrypt(filename, key):
    f = Fernet(key)
    with open(filename, 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = f.decrypt(encrypted_data)
    with open(filename, 'wb') as file:
        file.write(decrypted_data)


#Отправление сообщений
def send(msg):
    f = Fernet(load_key())
    try:
        encrypted_msg = f.encrypt(msg.encode('utf8'))
        client.send(encrypted_msg)
    except:
        encrypted_msg = f.encrypt(msg)
        client.send(encrypted_msg)


def reciver(conn, q):
    f = Fernet(load_key())
    if q == 1:
        encrypted_msg = conn.recv(5335800)
        decrypted_msg = f.decrypt(encrypted_msg)
        decrypted_msg = decrypted_msg.decode('utf8')
        print(decrypted_msg)
    else:
        while not shutdown:
            try:
                encrypted_msg = conn.recv(5335800)
                decrypted_msg = f.decrypt(encrypted_msg)
                decrypted_msg = decrypted_msg.decode('utf8')
                if decrypted_msg:
                    if decrypted_msg == '--Lovi File--':
                        encrypted_name = client.recv(1024)
                        decrypted_name = f.decrypt(encrypted_name)
                        name = decrypted_name.decode('utf8')
                        encrypted_data = client.recv(5335800)
                        decrypted_data = f.decrypt(encrypted_data)
                        data = decrypted_data
                        if type(data) == bytes:
                            with open(f'Filiki/{name}', 'wb') as file:
                                file.write(data)
                        else:
                            with open(f'Filiki/{name}', 'w') as file:
                                file.write(data)
                        print('yah.\n')
                    else:
                        q.put((conn, decrypted_msg))
                        print(decrypted_msg)
            except:
                break


flag = True
 
def insert(type, data):
 
    global flag

    host = socket.gethostbyname(socket.gethostname())
    port = 5432
    hostt = '127.0.0.1'
    userr = 'postgres'
    passwordd = 'zandon2000'
    db_namee = 'tovar'

    conn = PostgresqlDatabase(db_namee, user = userr, password = passwordd, host = hostt)
    charset="utf8"
    
 

    cursor = conn.cursor()
 
    sql = "insert into qrcode(type,data) values(%s,%s)"
    try:
        if cursor.execute(sql, (type, data)) != -1:
            flag = False
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(e)
 
    cursor.close()
    conn.close()
 
 
def decode(image):
    barcodes = pyzbar.decode(image)
    for barcode in barcodes:
                 
        (x, y, w, h) = barcode.rect
                
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
 
        barcodeType = barcode.type
                
        barcodeData = barcode.data.decode("utf-8")
 
        insert(barcodeType, barcodeData)
 
        text = "{} ".format(barcodeType, barcodeData)
        cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    .5, (0, 0, 125), 2)
 
        print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
 
    return image
 

def detect():
        
    camera = cv2.VideoCapture (0)
 
    while flag:
                
        ret, frame = camera.read () 
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                 
        img = decode(gray)
 
            
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
 
                
        cv2.imshow("camera", img)
 
         
    camera.release()
        
    cv2.destroyAllWindows()
 
 
if __name__ == '__main__':
    detect()
