def create_swap_map(list1, list2):
        swap_map = {}
        #lijst 1 is 1 en list2 is 2
        if len(list1) == 1 and len(list2) > 1:
            for element in list2:
                swap_map[element] = list1[0]
                swap_map[list1[0]] = element
            #lijst 2 is 1 en list2 is 1
        elif len(list2) == 1 and len(list1) > 1:
            for element in list1:
                swap_map[element] = list2[0]
                swap_map[list2[0]] = element
        else:
            #allebij even groot
            for i in range(len(list1)):
                swap_map[list1[i]] = list2[i]
                swap_map[list2[i]] = list1[i]

        return swap_map

x = ['a', 'b']
y = ['c', 'd']

test = create_swap_map(x, y)

ahjlsd = 1