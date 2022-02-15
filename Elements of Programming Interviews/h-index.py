#returns the greatest number in a list that also has the most representation in that list
#(i.e) [1,1,1,2,3,4,4,5,6] would return 4, because there are 4 numbers that are greater than or equal to 4
#in the list

#Time complexity O(nlogn)| Space complexity O(n)

from random import randint, randrange


def h_index(citations: list[int]) -> int:
    
    #sort the list in ascending order
    citations = sorted(citations) #O(n) time operation
    
    n = len(citations)
    for i, c in enumerate(citations):
        if c >= n - i:
            return n - i
    return 0

my_list = []

for i in range(randrange(0,15)):
    my_list.append(randint(0,10))
    
print(f"The h-index is: {h_index(my_list)}")
            