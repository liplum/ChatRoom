import platform

system_type = platform.system()


def init_keys():
    import keys
    if system_type == "Windows":
        import chars
        keys.k_up = chars.c_up
        keys.k_down = chars.c_down
        keys.k_left = chars.c_left
        keys.k_right = chars.c_right
        keys.k_pgdown = chars.c_pgdown
        keys.k_pgup = chars.c_pgup
        keys.k_end = chars.c_end
        keys.k_home = chars.c_home
        keys.k_insert = chars.c_insert
        keys.k_delete = chars.c_delete
        keys.k_f1 = chars.c_f1
        keys.k_f2 = chars.c_f2
        keys.k_f3 = chars.c_f3
        keys.k_f4 = chars.c_f4
        keys.k_f5 = chars.c_f5
        keys.k_f6 = chars.c_f6
        keys.k_f7 = chars.c_f7
        keys.k_f8 = chars.c_f8
        keys.k_f9 = chars.c_f9
        keys.k_f10 = chars.c_f10

        keys.k_f12 = chars.c_f12
        keys.k_backspace = chars.c_backspace
        keys.k_enter = chars.c_carriage_return
        keys.k_quit = chars.c_esc

        keys.ctrl_a = chars.ctrl_a
        keys.ctrl_b = chars.ctrl_b
        keys.ctrl_c = chars.ctrl_c
        keys.ctrl_d = chars.ctrl_d
        keys.ctrl_e = chars.ctrl_e
        keys.ctrl_f = chars.ctrl_f
        keys.ctrl_g = chars.ctrl_g
        keys.ctrl_h = chars.ctrl_h
        keys.ctrl_i = chars.ctrl_i
        keys.ctrl_j = chars.ctrl_j
        keys.ctrl_k = chars.ctrl_k
        keys.ctrl_l = chars.ctrl_l
        keys.ctrl_m = chars.ctrl_m
        keys.ctrl_n = chars.ctrl_n
        keys.ctrl_o = chars.ctrl_o
        keys.ctrl_p = chars.ctrl_p
        keys.ctrl_r = chars.ctrl_r
        keys.ctrl_t = chars.ctrl_t
        keys.ctrl_u = chars.ctrl_u
        keys.ctrl_v = chars.ctrl_v
        keys.ctrl_w = chars.ctrl_w
        keys.ctrl_x = chars.ctrl_x
        keys.ctrl_y = chars.ctrl_y

    elif system_type == "Linux":
        import linuxchars
        keys.k_up = linuxchars.lc_up
        keys.k_down = linuxchars.lc_down
        keys.k_left = linuxchars.lc_left
        keys.k_right = linuxchars.lc_right
        keys.k_pgdown = linuxchars.lc_pgdown
        keys.k_pgup = linuxchars.lc_pgup
        keys.k_end = linuxchars.lc_end
        keys.k_home = linuxchars.lc_home
        keys.k_insert = linuxchars.lc_insert
        keys.k_delete = linuxchars.lc_delete
        keys.k_f1 = linuxchars.lc_f1
        keys.k_f2 = linuxchars.lc_f2
        keys.k_f3 = linuxchars.lc_f3
        keys.k_f4 = linuxchars.lc_f4
        keys.k_f5 = linuxchars.lc_f5
        keys.k_f6 = linuxchars.lc_f6
        keys.k_f7 = linuxchars.lc_f7
        keys.k_f8 = linuxchars.lc_f8
        keys.k_f9 = linuxchars.lc_f9
        keys.k_f10 = linuxchars.lc_f10

        keys.k_f12 = linuxchars.lc_f12
        keys.k_backspace = linuxchars.lc_backspace
        keys.k_enter = linuxchars.lc_line_end
        keys.k_quit = linuxchars.lc_eot

        keys.ctrl_a = linuxchars.lctrl_a
        keys.ctrl_b = linuxchars.lctrl_b
        keys.ctrl_c = linuxchars.lctrl_c
        keys.ctrl_d = linuxchars.lctrl_d
        keys.ctrl_e = linuxchars.lctrl_e
        keys.ctrl_f = linuxchars.lctrl_f
        keys.ctrl_g = linuxchars.lctrl_g
        keys.ctrl_h = linuxchars.lctrl_h
        keys.ctrl_i = linuxchars.lctrl_i
        keys.ctrl_j = linuxchars.lctrl_j
        keys.ctrl_k = linuxchars.lctrl_k
        keys.ctrl_l = linuxchars.lctrl_l
        keys.ctrl_m = linuxchars.lctrl_m
        keys.ctrl_n = linuxchars.lctrl_n
        keys.ctrl_o = linuxchars.lctrl_o
        keys.ctrl_p = linuxchars.lctrl_p
        keys.ctrl_r = linuxchars.lctrl_r
        keys.ctrl_t = linuxchars.lctrl_t
        keys.ctrl_u = linuxchars.lctrl_u
        keys.ctrl_v = linuxchars.lctrl_v
        keys.ctrl_w = linuxchars.lctrl_w
        keys.ctrl_x = linuxchars.lctrl_x
        keys.ctrl_y = linuxchars.lctrl_y


def init_colors():
    import ui.Renders
    BK = ui.Renders.BK
    FG = ui.Renders.FG
    if system_type == "Windows":
        from win32console import BACKGROUND_RED, BACKGROUND_BLUE, BACKGROUND_GREEN, FOREGROUND_BLUE, FOREGROUND_RED, \
            FOREGROUND_GREEN
        BK.Blue = BACKGROUND_BLUE
        BK.Green = BACKGROUND_GREEN
        BK.Red = BACKGROUND_RED
        BK.Yellow = BACKGROUND_RED | BACKGROUND_GREEN
        BK.Violet = BACKGROUND_RED | BACKGROUND_BLUE
        BK.Cyan = BACKGROUND_BLUE | BACKGROUND_GREEN
        BK.Black = 0
        BK.White = BACKGROUND_RED | BACKGROUND_BLUE | BACKGROUND_GREEN

        FG.Blue = FOREGROUND_BLUE
        FG.Green = FOREGROUND_GREEN
        FG.Red = FOREGROUND_RED
        FG.Yellow = FOREGROUND_RED | FOREGROUND_GREEN
        FG.Violet = FOREGROUND_RED | FOREGROUND_BLUE
        FG.Cyan = FOREGROUND_GREEN | FOREGROUND_BLUE
        FG.Black = 0
        FG.White = FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_RED
    elif system_type == "Linux":
        from curses import COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_WHITE, COLOR_BLACK, COLOR_YELLOW, COLOR_CYAN
        BK.Blue = COLOR_BLUE
        BK.White = COLOR_WHITE
        BK.Yellow = COLOR_YELLOW
        BK.Green = COLOR_GREEN
        BK.Cyan = COLOR_CYAN
        BK.Red = COLOR_RED
        BK.Violet = COLOR_RED | COLOR_BLUE
        BK.Black = COLOR_BLACK

        FG.Blue = COLOR_BLUE
        FG.White = COLOR_WHITE
        FG.Yellow = COLOR_YELLOW
        FG.Green = COLOR_GREEN
        FG.Cyan = COLOR_CYAN
        FG.Red = COLOR_RED
        FG.Violet = COLOR_RED | COLOR_BLUE
        FG.Black = COLOR_BLACK
        print(BK.__dict__.items())
        print(FG.__dict__.items())


init_keys()
init_colors()
