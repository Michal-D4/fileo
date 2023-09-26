import subprocess

def activate(pid):
    temp = subprocess.Popen(
        ['wmctrl', '-p', '-l'], stdout = subprocess.PIPE
    )
    rr = temp.communicate()
    pp = str(rr[0]).split(r'\n')
    p_id = get_win_id(pp, str(pid))
    if p_id:
        subprocess.Popen(
            ['wmctrl', '-i', '-R', f'{p_id}'], stdout = subprocess.PIPE
        )

def get_win_id(comm: list, pid: str) -> str:
    for cc in comm:
        if pid in cc:
            p = cc.find('0x')
            return cc[p:p+10]
    return ''
