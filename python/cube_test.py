from tkinter.filedialog import test


test1 = [
            ["kek", "sarga", "kek", "kek"],
            ["sarga", "zold", "sarga", "zold"], 
            ["kek", "sarga", "kek", "kek"], 
        ]    

test2 = [
            ["kek", "sarga", "kek", "kek"],
            ["sarga", "sarga", "sarga", "sarga"], 
            ["kek", "sarga", "kek", "kek"], 
        ]  

test3 = [
            ["kek", "kek", "zold", "kek"],
            ["zold", "zold", "zold", "zold"], 
            ["kek", "kek", "zold", "kek"], 
        ]      

test4 = [
            ["sarga", "kek", "sarga", "kek"],
            ["sarga", "sarga", "sarga", "sarga"], 
            ["kek", "sarga", "kek", "kek"], 
        ] 

test5 = [
            ["zold", "zold", "zold", "zold"],
            ["feher", "feher", "feher", "feher"], 
            ["sarga", "sarga", "sarga", "sarga"], 
        ]      

loaded = [
            ["", "sarga", "kek", "kek"],
            ["sarga", "zold", "sarga", "zold"], 
            ["", "sarga", "kek", "kek"], 
        ]  
def best_order(grid):
    order = []
    for i in range(3):
        yellow_count = 0
        blue_count = 0
        green_count = 0
        for j in range(3, 0, -1):
            if grid[i][j] == "sarga":
                yellow_count += 1
            elif grid[i][j] == "kek":
                blue_count += 1
            elif grid[i][j] == "zold":
                green_count += 1
        sorted_counts = sorted([yellow_count, blue_count, green_count], reverse=True)
        for i in range(3):
            if sorted_counts[i] == yellow_count and not order.count(0):
                order.append(0)   
                break
            elif sorted_counts[i] == blue_count and not order.count(1):
                order.append(1)
                break
            elif sorted_counts[i] == green_count and not order.count(2):
                order.append(2)
                break

        
    return order

def transform(old):
    new = [[], [], [], []]

    for i in range(3, -1, -1):
        new[i].append(old[2][i])
        new[i].append(old[1][i])
        new[i].append(old[0][i])
    return new

transformed = transform(test5)

def best_to_next(test, loaded, now_position):
    picked_yellow = 0
    picked_blue = 0
    picked_green = 0
    picked_white = 0
    for load in loaded:
        picked_yellow += load.count("sarga")
        picked_blue += load.count("kek")
        picked_green += load.count("zold")
        picked_white += load.count("feher")
    d1 = [test[i][j] for i in range(3) for j in range(4) if test[i][j] != loaded[i][j]]
    need_blue = 'kek' in d1
    need_yellow = 'sarga' in d1
    need_white = 'feher' in d1
    need_green = 'zold' in d1
    can_yellow = True
    can_blue = True
    can_green = True
    can_white = True

    if not need_yellow or need_blue and int((picked_yellow -  picked_blue+1)/2)  >= 1:
        can_yellow = False

    if not need_blue or need_green and int((picked_blue -  picked_green+1)/2)  >= 1:
        can_blue = False   
    if not need_blue or need_yellow and int((picked_blue -  picked_yellow+1)/2)  >= 1:
        can_blue = False

    if not need_green or need_white and int((picked_green -  picked_white+1)/2)  >= 1:
        can_green = False
    if not need_green or need_blue and int((picked_green -  picked_blue+1)/2)  >= 1:
        can_green = False

    if not need_white or need_yellow and int((picked_white -  picked_yellow+1)/2)  >= 1:
        can_white = False


    yellow_count = 0
    blue_count = 0
    green_count = 0
    white_count = 0

    for color in ["sarga", "kek", "zold", "feher"]:
        for i in range(3):
            for j in range(3, -1, -1):
                if test[i][j] == color and loaded[i][j] == "":
                    match (color):
                        case "sarga":
                            yellow_count += 1
                        case "kek":
                            blue_count += 1
                        case "zold":
                            green_count += 1
                        case "feher":
                            white_count += 1
                    if test[i][j-1] == color and loaded[i][j-1] == "":
                        match (color):
                            case "sarga":
                                yellow_count += 1
                            case "kek":
                                blue_count += 1
                            case "zold":
                                green_count += 1
                            case "feher":
                                white_count += 1
                    print(f"test[{i}][{j}] = {test[i][j]}, loaded[{i}][{j}] = {loaded[i][j]}")
                    break
                if loaded[i][j] == "":
                    break
                
    
    can_go_to = []
    if can_yellow and yellow_count > 1:
        can_go_to.append(0)
    if can_blue and blue_count > 1:
        can_go_to.append(1)
    if can_green and green_count > 1:
        can_go_to.append(2)
    if can_white and white_count > 1:
        can_go_to.append(3)

    if len(can_go_to) == 0:
        if need_yellow and can_yellow:
            can_go_to.append(0)
        if need_blue and can_blue:
            can_go_to.append(1)
        if need_green and can_green:
            can_go_to.append(2)
        if need_white and can_white:
            can_go_to.append(3)
    final_color = -1
    if now_position in can_go_to:
        final_color = now_position
    elif now_position - 1 in can_go_to:
        final_color = now_position - 1
    elif now_position + 1 in can_go_to:
        final_color = now_position + 1
    elif now_position - 2 in can_go_to:
        final_color = now_position - 2
    elif now_position + 2 in can_go_to:
        final_color = now_position + 2
    else:
        return -1, []
    pos = []
    match (final_color):
        case 0:
            final_color = "sarga"
        case 1:
            final_color = "kek"
        case 2:
            final_color = "zold"
        case 3:
            final_color = "feher"


    for i in range(3):
        for j in range(3, -1, -1):
            if test[i][j] == final_color and loaded[i][j] == "":
                pos.append(i)  
                if j != 0 and test[i][j-1] == final_color: pos.append(i)  
                break
            if loaded[i][j] == "":
                break


    # print(f"d1: {d1}")
    print(f"picked_yellow: {picked_yellow}, picked_blue: {picked_blue}, picked_green: {picked_green}, picked_white: {picked_white}")
    print(f"need_blue: {need_blue}, need_yellow: {need_yellow}, need_white: {need_white}, need_green: {need_green}")
    print(f"can_blue: {can_blue}, can_yellow: {can_yellow}, can_white: {can_white}, can_green: {can_green}")
    print(f"yellow_count: {yellow_count}, blue_count: {blue_count}, green_count: {green_count}, white_count: {white_count}")
    print(f"{can_go_to = }")
    return final_color, pos
    # for i in range(3):



if __name__ == '__main__':
    print(int(1.6))
    print(*test5, sep=',\n')
    print(best_order(test5))

