
def start(lines):
    time = int(lines[3])
    if time < 10:
        return True
    else:
        return False 

def in_vision(lines):
    line = lines[2].split(',')
    if line[0] == "T":
        return True
    else:
        return False

def cant_see(lines):
    line = lines[2].split(',')
    if line[3] == "T":
        return True
    else:
        return False

def can_see(lines):
    line = lines[2].split(',')
    if line[3] == "T":
        return True
    else:
        return False

def footstep_in_direction(lines):
    line = lines[2].split(',')
    if line[6] == "T":
        if int(line[7]) 
    else:
        return False



def footstep_out_direction():

def kill():

def escape():

def initial_pos():


while True:
    f = open("bot.txt", "r+")
    lines = f.readlines()
    f.close()
    if len(lines) != 0:
        if start(lines):
            initial_pos(lines)
        elif in_vision(lines) and cant_see(lines):
            kill(lines)
        elif in_vision(lines) and can_see(lines):
            escape(lines)
        elif footstep_in_direction(lines):
            escape(lines)
        elif footstep_out_direction(lines):
            kill(lines)
        else:
            pass
    else:
        break