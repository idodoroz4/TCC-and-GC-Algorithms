
myGraph = {}
global_visited_nodes = {}
circles = []
final_circles = {}
manKeys = {}
womanKeys = {}


def init ():
    # initialize all the Data Structures
    myGraph.clear()
    global_visited_nodes.clear()
    final_circles.clear()
    del circles[:]
    manKeys.clear()
    womanKeys.clear()

def file_to_graph(input_file,saveKeys=None):
    # read from a file and turn the data into key - value elements

    lines = []
    with open(input_file,'r') as f:
        lines = f.readlines()

    for line in lines:
        split1 = line.split('-')
        key = split1[0].strip()

        if saveKeys == 'M':
            manKeys[key] = True
        elif saveKeys == 'W':
            womanKeys[key] = True

        values = split1[1].strip()
        values = values.split('.')[0]
        values = values.split(',')
        if values[-1] is not key:
            values.append(key)

        myGraph[key] = values


def list_to_file (lst,output_file):
    # prints the content of the list into a file
    with open(output_file,'w') as f:
        f.writelines(lst)

def group_to_list(group):
    # transform a group into a list - for TCC only
    lst = []
    for circle in group:
        for i in xrange(len(circle) - 1):
            lst.append("%s - %s\n" % (circle[i],circle[i+1]))

    lst.sort()
    lst[-1] = lst[-1].split('\n')[0] # delete last ENTER
    return lst

def iterate_all_nodes():
    # activating BFS
    not_passed = [node for node in myGraph.keys() if node not in global_visited_nodes]
    while len(not_passed) > 0:
        find_circles([],not_passed[0])
        not_passed = [node for node in myGraph.keys() if node not in global_visited_nodes]


def get_score(node,friend):
    # get score of node to friend
    # examle: node = a, friend = b, a: 'r','f','b','a' ==> returns 1
    # examle: node = a, friend = b, a: 'b','f','r','a' ==> returns 3
    if myGraph[node].count(friend) > 0: # equals indexOf => check if friend is on the list of friends
        return len(myGraph[node]) - myGraph[node].index(friend) - 1
    return 0

def sort_tuple (tpl):
    tmp_list = list(tpl)
    tmp_list.sort()
    return tuple(tmp_list)


def get_circle (list_of_friends):
    # get a list of nodes, one of the nodes appears at the beginning or middle and at the end,
    # return a circle
    visited = []
    is_circle = False
    circle = None
    beginning_of_circle = None
    for friend in list_of_friends:
        if visited.count(friend) > 0:
            beginning_of_circle = friend
            visited.append(friend)
            is_circle = True
            break
        visited.append(friend)
    if is_circle:
        circle=visited[visited.index(beginning_of_circle):]

    return circle

def get_circle_score(circle):
    # get single circle score
    if circle is None:
        return 0
    sum = 0
    for i in xrange(len(circle)):
        if i < len(circle) - 1:
            sum += get_score(circle[i],circle[i+1])
    return sum

def get_group_score (group):
    # get group score
    # group contains one or more circles
    score = 0
    for circle in group:
        score += get_circle_score(circle)

    return score



def find_circles(visited_nodes,current_node):
    # find circles that contains all the visited nodes and the current node

    # register the nodes that we passed
    if not global_visited_nodes.has_key(current_node):
        global_visited_nodes[current_node] = True

    circle = get_circle(visited_nodes)
    if circle:
        if circles.count(circle) == 0:
            circles.append(circle)
        return

    for friend in myGraph[current_node]:
        new_visited_nodes = visited_nodes[:]
        new_visited_nodes.append(friend)
        find_circles(new_visited_nodes, friend)


def remove_bad_circles():
    # remove circles that has the same value: ('a','c','a') vs ('c','a','c')
    sets = {}
    for circle in circles:
        if tuple(set(circle)) in sets:
            if get_circle_score(sets[tuple(set(circle))]) < get_circle_score(circle):
                sets[tuple(set(circle))] = circle
        else:
            sets[tuple(set(circle))] = circle

    return sets.values()

def get_new_suggested_groups(suggested_groups, myCircles):
    # building a dictionary that contains all possible groups
    group_was_added = False
    circles_to_be_removed = []
    for circle1 in suggested_groups.keys(): # key = tuple of tuples : ( ('a','b','a') , ('c','d','c') )
        group_was_changed = False
        for circle2 in myCircles:

            if not [node for node in suggested_groups[circle1] if node in circle2]:
                group = list(circle1)
                group.append(tuple(circle2))
                group = sort_tuple(tuple(group))
                # we get new group as tuple of tuples : ( ('a','b','a') , ('c','d','c') )
                # the new group contains circles that doesn't have same elements in 2 groups or more
                # a.k.a: all the circles in a group are Foreign Groups

                if group not in suggested_groups:
                    group_was_changed = True
                    group_was_added = True
                    suggested_groups[group] = list(set([node for circle in group for node in circle]))

        if not group_was_changed:
            final_circles[circle1] = True
            circles_to_be_removed.append(circle1)

    # if group was *not* added it is final group! need to put it in final_group dic and remove from suggested
    for circle in set(circles_to_be_removed):
        suggested_groups.pop(circle)

    return suggested_groups, group_was_added

def group_foreign_circles (myCircles):
    # get all foreign groups
    suggested_groups = {}
    for circle in myCircles:
        suggested_groups[(tuple(circle), )] = circle

    group_was_added = True # if a group was added, need to iterate again
    while group_was_added:
        suggested_groups, group_was_added = get_new_suggested_groups(suggested_groups, myCircles)


def remove_big_groups (groups):
    # get a list of groups
    # remove groups that have circles that contains more then 3 elements
    # return the new list of groups
    new_groups = []
    for group in groups:
        conatain_large_circle = False
        for circle in group:
            if len(circle) > 3:
                conatain_large_circle = True
                break

        if not conatain_large_circle:
            new_groups.append(group)

    return new_groups

def get_GC_output(best_group):
    manTXT = []
    womanTXT = []

    for circle in best_group:
        if circle[0] != circle[1]: # persons are man and a woman
            if circle[0] in manKeys: # circle[0] is a man circle[1] is a woman
                manTXT.append("%s - %s\n" % (circle[0],circle[1]))
                womanTXT.append("%s - %s\n" % (circle[1],circle[0]))
            else: #  circle[1] is a man circle[0] is a woman
                manTXT.append("%s - %s\n" % (circle[1],circle[0]))
                womanTXT.append("%s - %s\n" % (circle[0],circle[1]))
        else: # persons are 2 men or 2 women
            if circle[0] in manKeys: # circle[0] is a man circle[1] is a woman
                manTXT.append("%s - %s\n" % (circle[0],circle[1]))
            else: #  circle[1] is a man circle[0] is a woman
                womanTXT.append("%s - %s\n" % (circle[0],circle[1]))

    manTXT.sort()
    womanTXT.sort()

    manTXT[-1] = manTXT[-1].split('\n')[0] # delete last ENTER
    womanTXT[-1] = womanTXT[-1].split('\n')[0] # delete last ENTER
    return  manTXT, womanTXT


def run_TCC ():
    file_to_graph('input.txt')
    iterate_all_nodes() # BFS
    single_circles = remove_bad_circles() # remove similar circles
    group_foreign_circles(single_circles) # combain foreign circles to groups

    # calculate group's total score for all foreign groups
    final_groups_score = [(group,get_group_score(group)) for group in final_circles.keys()]

    # sort all the groups by score
    final_groups_score_sorted = sorted(final_groups_score, key=lambda l: l[1])[::-1]

    # output the first group - with the highest score
    group_to_list(final_groups_score_sorted[0][0])

    list_to_file(group_to_list(final_groups_score_sorted[0][0]),'output.txt')


def run_GC ():
    init() # clear all data structures
    file_to_graph('inputM.txt', 'M') # put all man preferences in the graph
                                     # save the man names on a 'man' list

    file_to_graph('inputW.txt', 'W') # put all woman preferences in the graph
                                     # save the woman names on a 'woman' list

    iterate_all_nodes() # BFS
    single_circles = remove_bad_circles() # remove similar circles
    group_foreign_circles(single_circles) # combain foreign circles to groups

    final_circles_lst = remove_big_groups(final_circles.keys())

    # calculate group's total score for all foreign groups
    final_groups_score = [(group,get_group_score(group)) for group in final_circles_lst]


    # sort all the groups by score
    final_groups_score_sorted = sorted(final_groups_score, key=lambda l: l[1])[::-1]


    man_text, woman_text = get_GC_output(final_groups_score_sorted[0][0])

    list_to_file(man_text,'outputM.txt')
    list_to_file(woman_text,'outputW.txt')



def main():
    run_TCC()
    run_GC()
    exit()

main()
