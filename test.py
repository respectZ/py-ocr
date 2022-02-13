def wrapText(string, threshold):
    splitted = []
    spaces = []
    while string:
        flag = 0
        for i in range(len(string)):
            if string[i] == " ":
                spaces.append(i)

            if i+1 >= threshold:
                splitted.append(string[0:spaces[-1]])
                string = string[spaces[-1]+1:]
                flag = 1
                break
        if not(flag):
            splitted.append(string)
            string = ""
    return splitted

r = wrapText("There was- !! Even if I die, I want to sleep- !! I want to sleep-! When I die, I want to lie down ---", 50)
print(r)