from getpass import getpass
from subprocess import Popen, PIPE

password = getpass("Please enter your password: ")
# sudo requires the flag '-S' in order to take input from stdin
# proc = Popen("sudo -S apach2ctl restart".split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
proc = Popen("sudo -S systemctl restart docker.service".split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
# Popen only accepts byte-arrays so you must encode the string
proc.communicate(password.encode())


