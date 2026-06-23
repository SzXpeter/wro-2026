import os

log_files = os.listdir("./log")
i = 1
if len(log_files) > 0:
    log_files.sort()
    i = int(log_files[-1][4:7]) 

log_file_name = "./log/log_{0:03d}.txt".format(i)

with open(log_file_name, 'r') as f:
    print(f.readlines())

