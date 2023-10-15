from loguru import logger

import socket
import threading

from PyQt6.QtCore import QCoreApplication

from . import app_globals as ag

HOST = "127.0.0.1"
PORT = 65432

instance_cnt = 0

def new_app_instance():
    is_running, sock = server_is_running('+')
    ag.db.restore = not is_running
    if not is_running:
        setup_server()
        return 0
    else:
        try:
            pid = sock.recv(8).decode()
        except TimeoutError as e:
            logger.info(f'not received: {e}')
            pid = 0
        return pid


def app_instance_closed():
    is_running, sock = server_is_running('-')
    if is_running:
        try:
            sock.recv(8).decode()
        except TimeoutError as e:
            logger.info(f'not received: {e}')


def server_is_running(sign: str) -> tuple[bool, socket.socket|None]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        sock.connect((HOST, PORT))
        sock.send(sign.encode())
        logger.info(f'Server started already; sent sign: "{sign}"')
    except (TimeoutError, ConnectionRefusedError) as e:  # ConnectionRefusedError on linux
        logger.info(e)
        return False, None
    return True, sock

def setup_server():
    serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversock.settimeout(1)
    try:
        serversock.bind((HOST, PORT))
    except OSError as e:
        logger.info(f"server can't bind to {(HOST, PORT)}:{e}")
        server_is_running('-')
        return

    server_thread = threading.Thread(
        target=_server_run,
        args=(serversock, QCoreApplication.applicationPid())
    )
    server_thread.start()

def _server_run(serversock, pid):
    serversock.listen()
    instance_cnt = 1
    logger.info(f"Server running: {instance_cnt=}, {pid=}")
    conn, addr = accept_conn(serversock)
    data = ''
    sent = False

    while True:
        if addr:
            data = conn.recv(1).decode()
        if sent:
            conn.close()
            addr = data = ''
            sent = False
            continue

        if data:
            instance_cnt += 1 if data == '+' else -1
            logger.info(f'send pid: {data=}, {instance_cnt=}')
            if instance_cnt == 0:
                break
            conn.send(str(pid).encode())
            sent = True
            continue

        if not addr:
            conn, addr = accept_conn(serversock)

    logger.info(">>> serversock.close")
    serversock.close()

def accept_conn(serversock: socket.socket):
    conn, addr = None, ''
    try:
        conn, addr = serversock.accept()
    finally:
        if conn:
            logger.info(f'{addr=}')
        return conn, addr
