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


init_keys()
