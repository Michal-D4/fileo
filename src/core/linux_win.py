import subprocess

def activate(res):
    temp = subprocess.Popen(
        ['wmctrl', '-p', '-l'], stdout = subprocess.PIPE
    )
    rr = temp.communicate()
    pp = str(rr[0]).split(r'\n')
    id = get_win_id(pp, str(res[1]))
    if id:
        subprocess.Popen(
            ['wmctrl', '-i', '-R', f'{id}'], stdout = subprocess.PIPE
        )

def get_win_id(comm: list, pid: str) -> str:
    for cc in comm:
        if pid in cc:
            p = cc.find('0x')
            return cc[p:p+10]
    return ''
