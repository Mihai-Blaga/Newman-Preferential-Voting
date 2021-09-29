# Written by Mihai Blaga on behalf of all Returning Officers of 2021.
# For questions about maintenance or functionality, please contact Mihai via the appropriate repository tools:
# https://github.com/Mihai-Blaga/Newman-Preferential-Voting

import pandas as pd
from numpy.core.numeric import NaN

# Used to convert GC votes into ones that exclude president, treasurer and international representative
# and which, when summed, provide the candidates in order of highest to lowest preference.
#   
# Given a row of valid votes and the indexes of whom to exclude,
# returns row with adjusted votes where larger indicates higher preference
def shuffle_gc_scores(row, excluded, num, mx):
    for i in range(len(row)):
        if i not in excluded:
            cpy = row[i]
            for j in excluded:
                if cpy < row[j]:
                    row[i] = row[i] + 1
            
            if row[i] <= (mx - num):
                row[i] = NaN
    
    for i in excluded:
        row[i] = NaN
        
    for i in range(len(row)):
        if row[i] != NaN:
            row[i] = row[i] - (mx - num)     

    return row

# PLEASE CHANGE THE BELOW CONSTANTS TO ADJUST FOR CHANGES IN FORMATTING
# TODO: **Please make sure that all names are spelt consistently throughout ballots. This includes whitespaces around names.**
VOTE_FILE_LOCATION = ".\\example-vote.csv"

# For each of the positions, the corresponding place in spaces stores how many spaces before the start of the respective count
pos = ['president', 'treasurer', 'international representative', 'gc']
# Specifies the number of empty lines before the beginning of any ballot tables
# If this is incorrect, the program will not be able to ingest the ballot information.
spaces = [2, 6, 10, 14]

# Number of candidates which must be voted for vs number of candidates for which the preference is kept
# i.e. in 2021 everyone had to vote for 11 (num_with_safety) people but of those, when pres, tres and 
# intl were excluded, only the first 8 (num_without_safety) were kept. 
num_with_safety = 11
num_without_safety = 8


#--------------------------------PARSING BALLOT INFORMATION#--------------------------------
votes = open(VOTE_FILE_LOCATION).readlines()

# Will store the start and end line numbers for each of the counts
start = []
end = []

# Gets the line number for all spaces denoted by '\n'
space_list = [i for i, n in enumerate(votes) if n == '\n']

# Calculates the start and end line numbers and stores them in start and end
for i in range(len(pos)):
    p = pos[i]
    s = spaces[i]
    start.append(space_list[s - 1] + 1)
    end.append(space_list[s])

# Converting everything to dataframes
proc_votes = []
for i in range(4):
    proc_votes.append(votes[start[i]:end[i]])
    proc_votes[i] = [s.strip() for s in proc_votes[i]]
    proc_votes[i] = [s.replace('\t', '') for s in proc_votes[i]]
    proc_votes[i] = [s.split(',') for s in proc_votes[i]]
    proc_votes[i] = pd.DataFrame(proc_votes[i][1:], columns = proc_votes[i][0])
    proc_votes[i] = proc_votes[i].set_index('Ballot')
    proc_votes[i] = proc_votes[i].apply(pd.to_numeric, errors='coerce')

pres_votes = proc_votes[0]
tres_votes = proc_votes[1]
intl_votes = proc_votes[2]
gc_votes = proc_votes[3]

#Printing processed votes without any additional processing done on them.
print("----PRES VOTES----")
print(pres_votes)
print("Presidential vote results:")
print(pres_votes.sum().sort_values(ascending = False))

print("----TRES VOTES----")
print(tres_votes)
print("Treasurer vote results:")
print(tres_votes.sum().sort_values(ascending = False))

print("----INTL VOTES----")
print(intl_votes)
print("International representative vote results:")
print(intl_votes.sum().sort_values(ascending = False))

print("----GC VOTES----")
print(gc_votes)

# Calculating the winners of the presidential, treasurer and international representative seats
excluded_members = []
for i in range(3):
    sorted_results = proc_votes[i].sum().sort_values(ascending = False)

    print("Excluding ", excluded_members)

    while (sorted_results.index[0] in excluded_members):
        print(sorted_results.index[0], " has already been elected into a better position and is being excluded")
        sorted_results = sorted_results[1:]
    
    print()
    print(sorted_results)

    winner = ""
    if sorted_results[0] != sorted_results[1]:
        suggested = sorted_results.index[0]
        print("Suggested ", pos[i],   " = ", suggested)
        winner = suggested
    else:
        print("Tie detected, please calculate ", pos[i], " by hand")
        winner = input("Please enter the manually calculated " + str(pos[i]) + ": ")

    excluded_members.append(winner)
    print("\n")


#Calculating the scores of each person running for GC.
num_candidates = len(gc_votes.columns)
print("Number of candidates running for GC: ", num_candidates)

#Specify the structure a valid ballot should have and compare to all ballots to filter for only legitimate ones
temp = gc_votes.apply(pd.Series.value_counts, axis = 1).fillna(0)

correct_vote = temp.head(1)
for i in correct_vote.columns:
    if i in range(num_candidates, num_candidates-num_with_safety, -1):
        correct_vote[i] = 1
    else:
        correct_vote[i] = 0

correct_vote = correct_vote.iloc[0]

# Filter away all incorrect votes
gc_votes = gc_votes[(temp == correct_vote).all(1)]

i_excluded_members = []
for mem in excluded_members:
    ls = list(gc_votes.columns.values)
    if mem in ls:
        i_excluded_members.append(ls.index(mem))

print("Excluding the following positions: ", i_excluded_members)
final_gc = [shuffle_gc_scores(x, i_excluded_members, num_without_safety, num_candidates) for x in gc_votes.to_numpy()]
final_gc = pd.DataFrame(final_gc, columns = gc_votes.columns)
print("---UPDATED GC TABLE---")

# Uncomment this section for verbose gc table with adjusted vote scores.
#with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
#    print(final_gc)

print(final_gc)

sorted_results = final_gc.sum().sort_values(ascending = False)
print("---FINAL GC SCORES---")
print(sorted_results)