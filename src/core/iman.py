from loguru import logger

import socket
import threading

from . import app_globals as ag

HOST = "127.0.0.1"
PORT = 65432


def new_app_instance() -> int:
    is_running, sock = server_is_running('+')
    ag.db.restore = not is_running
    if not is_running:
        setup_server()
        pid = 0
    else:
        try:
            pid = sock.recv(8).decode()
        except TimeoutError as e:
            pid = 0
    return int(pid)


def app_instance_close():
    server_is_running('-')

def send_message(sign: str = '') -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    sock.connect((HOST, PORT))
    logger.info(f'{ag.PID=}, {sign=}')
    sock.send(f'{ag.PID}/{sign}'.encode())
    return sock

def server_is_running(sign: str) -> tuple[bool, socket.socket|None]:
    try:
        sock = send_message(sign)
    except (TimeoutError, ConnectionRefusedError) as e:  # ConnectionRefusedError on linux
        logger.info(e)
        return False, None
    return True, sock

def setup_server():
    serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversock.settimeout(ag.TIME_CHECK * 2)
    try:
        serversock.bind((HOST, PORT))
    except OSError as e:
        logger.info(f"server can't bind to {HOST}:{PORT}:{e}")
        ''' something went wrong
        "server_is_running" reports that the server is not running, but
        a new server cannot connect, usually because it is already bound.
        so send a signal to remove the instance from the server and
        close it when there are no more instances left. '''
        server_is_running('-')
        return

    server_thread = threading.Thread(
        target=_server_run,
        args=(serversock, ag.PID)
    )
    server_thread.start()

def _server_run(serversock, pid):
    serversock.listen()
    instances = {str(pid): 2}
    conn, addr = accept_conn(serversock)
    data = ''

    STOP = threading.Event()
    def remove_not_active(sec: int):
        while not STOP.wait(sec):
            for key in instances:
                instances[key] = instances[key] // 2

    th = threading.Thread(target=remove_not_active, args=(ag.TIME_CHECK*2,))
    th.start()

    while sum(instances.values()):
        if addr:
            data = conn.recv(8).decode()

            if data:
                dd = data.split('/')
                if dd[1] == '-':
                    instances.pop(dd[0])
                else:
                    instances[dd[0]] = 2
                if dd[1] == '+':
                    conn.send(str(pid).encode())
                continue
            conn.close()

        conn, addr = accept_conn(serversock)

    STOP.set()
    logger.info(">>> serversock.close")
    serversock.close()

def accept_conn(serversock: socket.socket):
    global t1, t2
    conn, addr = None, ''
    try:
        conn, addr = serversock.accept()
    finally:
        if conn:
            logger.info(f'{addr=}')
        return conn, addr
