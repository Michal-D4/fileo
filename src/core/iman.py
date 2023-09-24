from loguru import logger
import socket
import threading

from PyQt6.QtCore import QCoreApplication

from . import app_globals as ag

HOST = "127.0.0.1"
PORT = 65432

instance_cnt = 0

def new_app_instance():
    ag.db.restore, sock = server_is_not_running('+')
    if ag.db.restore:
        setup_server()
        return 0
    else:
        try:
            pid = sock.recv(8).decode()
        except TimeoutError as e:
            logger.info(f'exception: {e}')
            pid = 0
        return pid


def app_instance_closed():
    to_restore, sock = server_is_not_running('-')
    if not to_restore:
        try:
            sock.recv(8).decode()
        except TimeoutError as e:
            logger.info(f'exception: {e}')


def server_is_not_running(sign: str):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        sock.connect((HOST, PORT))
        sock.send(sign.encode())
        logger.info(f'Server running, sent sign: {sign}')
    except socket.timeout as e:
        logger.info(f'exception: {e}')
        return True, None
    return False, sock

def setup_server():
    serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversock.settimeout(2)
    serversock.bind((HOST, PORT))

    server_thread = threading.Thread(
        target=_server_run,
        args=(serversock, QCoreApplication.applicationPid())
    )
    server_thread.start()

def _server_run(serversock, pid):
    serversock.listen()
    instance_cnt = 1
    logger.info(f"Server running: {instance_cnt=}, {pid=}, {type(pid)=}")
    conn, addr = accept_conn(serversock)
    data = ''
    sent = False

    while True:
        if addr:
            data = conn.recv(1).decode()
        if sent:
            conn.close()
            logger.info(f'conn.close <<< {data=}')
            addr = data = ''
            sent = False
            continue

        if data:
            instance_cnt += 1 if data == '+' else -1
            if not instance_cnt:
                break
            conn.send(str(pid).encode())
            logger.info(f'conn.send(str(pid)) <<< {data=}, {instance_cnt=}')
            sent = True
            continue
        # time.sleep(2)

        if not addr:
            conn, addr = accept_conn(serversock)

    logger.info(">>> serversock.close")
    serversock.close()

def accept_conn(serversock):
    conn, addr = None, ''
    try:
        conn, addr = serversock.accept()
    finally:
        return conn, addr
