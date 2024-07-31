import shlex, subprocess
from getpass import getpass

command_line = 'systemctl start docker.service'
restart_nginx = shlex.split(command_line)

proc = subprocess.run(
    restart_nginx,
    stdout=subprocess.PIPE,
    # input=getpass("password: "),
    encoding="ascii",
)


result = subprocess.run(['systemctl', 'is-active', 'docker.service'], capture_output=True, text=True)
print(result.stdout)


# subprocess.call(args, shell=True)

# p = subprocess.Popen(args)
# p.wait()

# proc1 = subprocess.Popen('systemctl restart docker.service',
#                          shell=True,
#                          stdin=subprocess.PIPE,
#                          stdout=subprocess.PIPE,
#                          stderr=subprocess.PIPE)


# ===============================================
# os.system('systemctl restart docker.service')

# output = subprocess.run(['ls', '-l'], capture_output=True, text=True)
# print(output.stdout)