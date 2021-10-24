from ui.nonblock import nbinput
from utils import clear_screen

displayed = []
max = 10
nbinput = nbinput()
error = None
running = True
while running:
    clear_screen()
    dis_len = len(displayed)
    if dis_len > max:
        dis = displayed[-max:]
    else:
        dis = displayed
    for t in dis:
        print(t)

    if dis_len < max:
        for i in range(max - dis_len):
            print()

    nbinput.get_input()
    input_list = nbinput.input_list()
    total = "".join(input_list)
    if len(input_list) > 5:
        nbinput.flush()
        displayed.append(total)
    print(total)
