import time
import csv
import random
import os
import settings

from modules.manipulations import csv_to_results

date = time.strftime("%d/%m/%y")

# print
# print "##############################################################"
# print "#                                                            #"
# print "# This is alloa by Mante Zelvyte and Uli Kraehmer            #"
# print "#                                                            #"
# print "# ulrich.kraehmer@glasgow.ac.uk                              #"
# print "#                                                            #"
# print "# Runtime with 100 agents at each hierarchy is a few minutes #"
# print "#                                                            #"
# print "##############################################################"

# Convert csv files to lists

results1 = csv_to_results(settings.LEVEL1_PATH)
results2 = csv_to_results(settings.LEVEL2_PATH)
results3 = csv_to_results(settings.LEVEL3_PATH)


##################
##################
##################
###### PAUL ######
##################
##################
##################

# 5. Create dictionaries that assign to each agent a number


students = dict(zip([results1[i][1] for i in range(1,len(results1))], [i for i in range(1, len(results1))]))
#print students
# projects=dict(zip([results2[i][1] for i in range(1,len(results2))], [i for i in range(1, len(results2))]))
# supervisors=dict(zip([results3[i][1] for i in range(1,len(results3))], [i for i in range(1, len(results3))]))

# 6. Create dictionaries that store the data in the
# format needed. level1 are the capacities of the
# agenets of hierarchy 1, level1_data are their
# preference lists, level2 the capacities of the agents
# of hierarchy 2, level2_data their preference lists,
# and level3_data (not very consistent...) the
# capacities of the agents of hierarchy 3 

level1=[[i,results1[i][2],results1[i][3]]for i in range(1, len(results1))]
proj=[[projects[results1[i][j]] for j in range(4, len(results1[i]))] for i in range(1, len(results1))]
level1_data=[level1[i]+proj[i] for i in range(0, len(level1))]

print "level1_data", level1_data

level2=[[results2[i][2],results2[i][3]] for i in range(1, len(results2))]
super=[[supervisors[results2[i][j]] for j in range(4, len(results2[i]))] for i in range(1, len(results2))]
level2_data=[level2[i]+super[i] for i in range(0, len(level2))]

level3_data=[[results3[i][2],results3[i][3]] for i in range(1, len(results3))]

# 7. Count the number of agents in each hierarchy and print them out
# str turns an integer into a string
 
num_lines = len(list(csv.reader(open(config["level1_data"]))))-1
num_of_sup = len(list(csv.reader(open(config["level3_data"]))))-1
num_of_proj=len(list(csv.reader(open(config["level2_data"]))))-1

print
print str(num_lines)+" agents of hierarchy 1"
print str(num_of_proj)+" agents of hierarchy 2"
print str(num_of_sup)+" agents of hierarchy 3"


# ??? Determine the maximal length of preferecne lists at hierarchy 2. 
# The lengths of the preference lists will be stoed in a temporary file
 
length_of_supervisor_lists=config['working_files']+'length_of_sup_list_'+date[0]+date[1]+date[3]+date[4]+date[6]+date[7]+'.txt'

outfile = open(length_of_supervisor_lists,"w")
for i in range(0, num_of_proj):
    outtexts ="%(pref)d\n" % dict(pref=len(level2_data[i])-2)
    outfile.write(outtexts)
outfile.close()

f = open(length_of_supervisor_lists, 'r') 
 
data = f.readlines()
data = data[0:]
f.close()
max_alt_sup=int(max(data))

# ??? Dame for preferecne lists at hierarchy 1. 
 
length_of_stud_lists=config['working_files']+'length_of_stud_list_'+date[0]+date[1]+date[3]+date[4]+date[6]+date[7]+'.txt'

outfile = open(length_of_stud_lists,"w")
for i in range(0, num_lines):
    outtexts ="%(pref)d\n" % dict(pref=len(level1_data[i])-2)
    outfile.write(outtexts)
outfile.close()

f = open(length_of_stud_lists, 'r') 
 
data = f.readlines()
data = data[0:]
f.close()
max_alt_proj=int(max(data))

#defining filename of the file to be written
filename0=config['working_files']+'allocation_graph_networkx_'+date[0]+date[1]+date[3]+date[4]+date[6]+date[7]+'.py'

# adding beginning of the code
outfile = open(filename0,"w")
outtext="import networkx as nx\nimport math\nG=nx.DiGraph()\n"
outfile.write(outtext)
outfile.close()

#student node demands +

outfile=open(filename0,"a")
for i in range(0,num_lines):
    outtexts = 'G.add_node(%(stud)d, demand=%(dem)d)\n' % dict(stud=i+1, dem=int(level1_data[i][1])) 
    outfile.write(outtexts)
outfile.close()

#student node demands -
outfile=open(filename0,"a")
for i in range(0,num_lines):
    outtexts = 'G.add_node(%(stud)d, demand=%(dem)d)\n' % dict(stud=(num_lines)+i+1, dem=-int(level1_data[i][1])) 
    outfile.write(outtexts)
outfile.close()

#project node demands +
demand1=config['working_files']+'demand1_'+date[0]+date[1]+date[3]+date[4]+date[6]+date[7]+'.py'
outfile=open(demand1,"w")
for i in range(0,num_lines):
    for j in range(3, len(level1_data[i])):
        outtexts = 'G.add_node(%(proj)d, demand=%(dem)d)\n' % dict(proj=int(level1_data[i][j])+(num_lines)*2, dem=int(level2_data[int(level1_data[i][j])-1][0])) 
        outfile.write(outtexts)
outfile.close()

#project node demands -
outfile=open(demand1,"a")
for i in range(0,num_lines):
    for j in range(3,len(level1_data[i])):
        outtexts = 'G.add_node(%(proj)d, demand=%(dem)d)\n' % dict(proj=int(level1_data[i][j])+(num_lines)*2+num_of_proj, dem=-int(level2_data[int(level1_data[i][j])-1][0])) 
        outfile.write(outtexts)
outfile.close()

#removing duplicated nodes
lines_seen = set() # holds lines already seen
outfile = open(filename0, "a")
for line in open(demand1, "r"):
    if line not in lines_seen: # not a duplicate
        outfile.write(line)
        lines_seen.add(line)
outfile.close()

#supervisor node demands +
demand2=config['working_files']+'demand2_'+date[0]+date[1]+date[3]+date[4]+date[6]+date[7]+'.py'
outfile=open(demand2,"w")
for i in range(0,num_lines):
   for j in range(3,len(level1_data[i])):
       for k in range(2, len(level2_data[int(level1_data[i][j])-1])):
        outtexts = 'G.add_node(%(sup)d, demand=%(dem)d)\n' % dict(sup=int(level2_data[int(level1_data[i][j])-1][k])+ (num_lines)*2+num_of_proj*2, dem=int(level3_data[int(level2_data[int(level1_data[i][j])-1][k])-1][0])) 
        outfile.write(outtexts)
outfile.close()

#supervisor node demands -
outfile=open(demand2,"a")
for i in range(0,num_lines):
   for j in range(3,len(level1_data[i])):
       for k in range(2, len(level2_data[int(level1_data[i][j])-1])):
        outtexts = 'G.add_node(%(sup)d, demand=%(dem)d)\n' % dict(sup=int(level2_data[int(level1_data[i][j])-1][k])+ (num_lines)*2+num_of_proj*2+num_of_sup, dem=-int(level3_data[int(level2_data[int(level1_data[i][j])-1][k])-1][0])) 
        outfile.write(outtexts)
outfile.close()

#removing duplicated nodes
lines_seen = set() # holds lines already seen
outfile = open(filename0, "a")
for line in open(demand2, "r"):
    if line not in lines_seen: # not a duplicate
        outfile.write(line)
        lines_seen.add(line)
outfile.close()

#source to students
edges_prerand=config['working_files']+'edges_prerand_'+date[0]+date[1]+date[3]+date[4]+date[6]+date[7]+'.txt'
outtexts = ['G.add_edge(0, %d, weight=0)\n' % (i) for i in range(1,num_lines+1)]
outfile = open(edges_prerand,"w")
outfile.writelines(str("".join(outtexts)))
outfile.close()

#randomization of source to students edges
lines = open(edges_prerand).readlines()
random.shuffle(lines)
open(filename0, 'a').writelines(lines)

#student to student duplicates
outfile=open(filename0,"a")
for i in range(0,num_lines):
    outtexts="G.add_edge(%(stud)d, %(stud_dup)d,capacity=%(cap)d, weight=0)\n" % dict(stud=int(level1_data[i][0]), stud_dup=num_lines+i+1, cap=int(level1_data[i][2])-int(level1_data[i][1]))
    outfile.write(outtexts)
outfile.close()

#students to projects, with option to pick the weighting - input the number of weighted hierarchies - i.e., 0,1 or 2. If 2 - fully generous algorithm. If 1 - generous only for students. If 0 - not generous. 
outfile = open(filename0,"a")
  
hierarchy_weight= int(config["weighted_hierarchies"])
if hierarchy_weight==0:
# POTENTIAL BUG WHEN REPLACING n BY num_lines
    for i in range(0,num_lines):
       for j in range(3,len(level1_data[i])):
          outtexts = "G.add_edge(%(number)d, %(proj)d, weight=0)\n" % dict(number=int(level1_data[i][0])+(num_lines), proj=int(level1_data[i][j])+(num_lines)*2)
          outfile.write(outtexts)    
elif hierarchy_weight==1:
    for i in range(0,n):
       for j in range(3,len(level1_data[i])):
          outtexts = "G.add_edge(%(number)d, %(proj)d, weight=%(cost1)d)\n" % dict(number=int(level1_data[i][0])+(num_lines), proj=int(level1_data[i][j])+(num_lines)*2, cost1=(num_lines)**(j-3))
          outfile.write(outtexts)
else:
    for i in range(0,num_lines):
       for j in range(3,len(level1_data[i])):
          outtexts = "G.add_edge(%(number)d, %(proj)d, weight=%(cost2)d)\n" % dict(number=int(level1_data[i][0])+(num_lines), proj=int(level1_data[i][j])+(num_lines)*2, cost2=(num_lines)**(j-3+max_alt_sup-1))
          outfile.write(outtexts)
        
outfile.close()

#projects to project duplicates
edges1=config['working_files']+'edges1_'+date[0]+date[1]+date[3]+date[4]+date[6]+date[7]+'.py'

outfile = open(edges1,"w")

for i in range(0,num_lines):
   for j in range(3,len(level1_data[i])):
      outtexts = "G.add_edge(%(proj)d,%(proj_dup)d, capacity=%(cap)d, weight=0)\n" % dict(proj=int(level1_data[i][j])+(num_lines)*2, proj_dup=(num_lines)*2+num_of_proj+int(level1_data[i][j]), cap=int(level2_data[int(level1_data[i][j])-1][1])-int(level2_data[int(level1_data[i][j])-1][0]))
      outfile.write(outtexts)
        
outfile.close()

#removing duplicated lines

lines_seen = set() 
outfile = open(filename0, "a")
for line in open(edges1, "r"):
    if line not in lines_seen: 
        outfile.write(line)
        lines_seen.add(line)
outfile.close()

#projects duplicated to supervisors, with option to pick the weighting

edges2=config['working_files']+'edges2_'+date[0]+date[1]+date[3]+date[4]+date[6]+date[7]+'.py'
outfile = open(edges2,"w")
if hierarchy_weight==0:
# POTENTIAL BUG
    for i in range(0,num_lines):
       for j in range(3,len(level1_data[i])):
           for k in range(2, len(level2_data[int(level1_data[i][j])-1])):
              outtexts = "G.add_edge(%(number)d, %(super)d, weight=0)\n" % dict(number =(num_lines)*2+num_of_proj+int(level1_data[i][j]), super=int(level2_data[int(level1_data[i][j])-1][k])+ (num_lines)*2+num_of_proj*2)
              outfile.write(outtexts)             
elif hierarchy_weight==1:
# POTENTIAL BUG
    for i in range(0,num_lines):
       for j in range(3,len(level1_data[i])):
           for k in range(2, len(level2_data[int(level1_data[i][j])-1])):
              outtexts = "G.add_edge(%(number)d, %(super)d, weight=0)\n" % dict(number =(num_lines)*2+num_of_proj+int(level1_data[i][j]), super=int(level2_data[int(level1_data[i][j])-1][k])+ (num_lines)*2+num_of_proj*2)
              outfile.write(outtexts)       
else:
      for i in range(0,num_lines):
       for j in range(3,len(level1_data[i])):
           for k in range(2, len(level2_data[int(level1_data[i][j])-1])):
              outtexts = "G.add_edge(%(number)d, %(super)d, weight=%(cost)d)\n" % dict(number =(num_lines)*2+num_of_proj+int(level1_data[i][j]), super=int(level2_data[int(level1_data[i][j])-1][k])+ (num_lines)*2+num_of_proj*2, cost=(num_lines)**(k-2))
              outfile.write(outtexts)
        
outfile.close()

#removing duplicate edges

lines_seen = set() 
outfile = open(filename0, "a")
for line in open(edges2, "r"):
    if line not in lines_seen: 
        outfile.write(line)
        lines_seen.add(line)
outfile.close()


#supervisors to supervisor duplicates

edges3=config['working_files']+'edges3_'+date[0]+date[1]+date[3]+date[4]+date[6]+date[7]+'.py'

outfile = open(edges3,"w")
for i in range(0,num_lines):
   for j in range(3,len(level1_data[i])):
       for k in range(2, len(level2_data[int(level1_data[i][j])-1])):
        outtexts = "G.add_edge(%(super)d, %(super_dup)d, capacity=%(cap)d, weight=0)\n" % dict(super=int(level2_data[int(level1_data[i][j])-1][k])+ (num_lines)*2+num_of_proj*2, super_dup=int(level2_data[int(level1_data[i][j])-1][k])+ (num_lines)*2+num_of_proj*2+num_of_sup, cap=int(level3_data[int(level2_data[int(level1_data[i][j])-1][k])-1][1])-int(level3_data[int(level2_data[int(level1_data[i][j])-1][k])-1][0]))
        outfile.write(outtexts)
outfile.close()

#removing duplicate projects
lines_seen = set() # holds lines already seen
outfile = open(filename0, "a")
for line in open(edges3, "r"):
    if line not in lines_seen: # not a duplicate
        outfile.write(line)
        lines_seen.add(line)
outfile.close()
 
#calculate the sink
sink = (num_lines)*2 + num_of_proj*2 + num_of_sup*2+1

#supervisors to sink
edges4=config['working_files']+'edges4_'+date[0]+date[1]+date[3]+date[4]+date[6]+date[7]+'.py'
outfile = open(edges4,"w")
for i in range(0,num_lines):
   for j in range(3,len(level1_data[i])):
       for k in range(1, len(level2_data[int(level1_data[i][j])-1])):
        outtexts = "G.add_edge(%(super_dup)d, %(node_sink)d, weight=0)\n" % dict(node_sink=sink, super_dup=int(level2_data[int(level1_data[i][j])-1][k])+ (num_lines)*2+num_of_proj*2+num_of_sup)
        outfile.write(outtexts)
outfile.close()

lines_seen = set() # holds lines already seen
outfile = open(filename0, "a")
for line in open(edges4, "r"):
    if line not in lines_seen: # not a duplicate
        outfile.write(line)
        lines_seen.add(line)
outfile.close()

#adding ending of the code
outfile = open(filename0,"a")
outtext="import sys\ntry:\n J=nx.max_flow_min_cost(G,0,%(node_sink)d)\nexcept nx.NetworkXUnfeasible:\n  print('Allocation satisfying the lower bounds is not possible. Try reducing lower bounds.')\n  sys.exit(1)\nexcept nx.NetworkXError:\n  print('The input graph is not directed or not connected. Please check the data if all the choices on the level 1 list are included in the level 2 list and the choices on the level 2 list are included in the level 3 list.')\n  sys.exit(1)\nexcept nx.NetworkXUnbounded:\n  print('Allocation is not possible because some upper capacity bounds at level 1 have not been set up. Please check the data.')\n  sys.exit(1)" %dict(node_sink=sink)
outfile.write(outtext)
outfile.close()

#deleting temporary files: 'Yes' to delete files (in alloa.conf for delete_files) or 'No' to leave them.
delete_files=config["delete_files"]
if delete_files=='Yes':
    os.remove(file1)
    os.remove(file2)
    os.remove(file3)
    os.remove(edges1)
    os.remove(edges2)
    os.remove(demand1)
    os.remove(demand2)
    os.remove(edges_prerand)
    os.remove(edges3)
    os.remove(edges4)
    os.remove(length_of_supervisor_lists)
    os.remove(length_of_stud_lists)
   



#inverse dictionary mapping
#print supervisors
inv_supervisors = {v:k for k, v in supervisors.items()}
inv_students = {v:k for k, v in students.items()}
inv_projects = {v:k for k, v in projects.items()}

#executing min cost max flow algorithm using networkx
exec(open(filename0).read())


    
#return the total flow from sink to source, i.e., number of level 1 items with their allocations. 
flow = nx.max_flow(G, 0, sink)
#return the cost of flow
C=nx.cost_of_flow(G,J)

#deleting graph file : 'Yes' to delete files (in alloa.conf for delete_files) or 'No' to leave them.
if delete_files=='Yes':
   os.remove(filename0)

#results

if hierarchy_weight==0:
    allocation_results=[[inv_students[u], inv_projects[v-n*2], inv_supervisors[s-n*2-num_of_proj*2], 'N/A', 'N/A'] for u in J if u>0 if u<n+1 for m in J[u] if m>n if m<n*2+1 for v in J[m] if v>n*2 if v<n*2+num_of_proj+1 if J[m][v]>0 for l in J[v] if l>n*2+num_of_proj if l<n*2+num_of_proj*2+1 if J[v][l]>0 for s in J[l] if s>n*2+num_of_proj*2 if s<n*2+num_of_proj*2+num_of_sup+1 if J[l][s]>0]
elif hierarchy_weight==1:
    allocation_results=[[inv_students[u], inv_projects[v-n*2], inv_supervisors[s-n*2-num_of_proj*2], int(round(math.log(G[m][v]['weight'], n),0)+1), 'N/A'] for u in J if u>0 if u<n+1 for m in J[u] if m>n if m<n*2+1 for v in J[m] if v>n*2 if v<n*2+num_of_proj+1 if J[m][v]>0 for l in J[v] if l>n*2+num_of_proj if l<n*2+num_of_proj*2+1 if J[v][l]>0 for s in J[l] if s>n*2+num_of_proj*2 if s<n*2+num_of_proj*2+num_of_sup+1 if J[l][s]>0]
else:
    allocation_results=[[inv_students[u],inv_projects[v-num_lines*2],inv_supervisors[s-num_lines*2-num_of_proj*2],int(round(math.log(G[m][v]['weight'],num_lines),0)-int(max_alt_sup)+2),int(round(math.log(G[l][s]['weight'], num_lines),0)+1)] for u in J if u>0 if u<num_lines+1 for m in J[u] if m>num_lines if m<num_lines*2+1 for v in J[m] if v>num_lines*2 if v<num_lines*2+num_of_proj+1 if J[m][v]>0 for l in J[v] if l>num_lines*2+num_of_proj if l<num_lines*2+num_of_proj*2+1 if J[v][l]>0 for s in J[l] if s>num_lines*2+num_of_proj*2 if s<num_lines*2+num_of_proj*2+num_of_sup+1 if J[l][s]>0] 

#allocation=[[u,v-n*2, k-n*2-num_of_proj*2] for u in J for m in J[u] for v in J[m] for j in J[v] for k in J[j] if J[j][k]>0 if J[u][m]>0 if J[m][v]>0 if J[v][j]>0 if u>0 if u<n+1 if m>n if m<n*2+1 if v>n*2 if v<num_of_proj+n*2+1 if j>num_of_proj+n*2 if j<num_of_proj*2+n*2+1 if k>num_of_proj*2+n*2 if k<num_of_proj*2+n*2+num_of_sup]

allocation_results2=[[inv_supervisors[u-num_lines*2-num_of_proj*2-num_of_sup], J[u][v]] for u in J for v in J[u] if J[u][v]>=0 if u>num_lines*2+num_of_proj*2+num_of_sup if u<num_of_sup*2+num_lines*2+num_of_proj*2+1]
allocation_results3=[[inv_projects[u-num_lines*2], J[u][v]] for u in J for v in J[u] if J[u][v]>=0 if u>num_lines*2 if u<num_of_proj+num_lines*2+1]

#data for counting student preferences
prefs=[allocation_results[i][3] for i in range(0, len(allocation_results))]
if hierarchy_weight>=1:
    for j in range(0, len(results1)):
        num_of_prefs=[prefs.count(i) for i in range(1, len(results1[j])-3)]
else:
    num_of_prefs='N/A'


#data for counting supervisor preferences

supervisor_prefs=[allocation_results[i][4] for i in range(0, len(allocation_results))]
if hierarchy_weight>=2:
    num_of_super_prefs=[supervisor_prefs.count(i) for i in range(1, max_alt_sup+1)]
else:
    num_of_super_prefs='N/A'



# ??? Generate filename for main output file

filename=config['allocation_results']+'allocation_'+date[0]+date[1]+date[3]+date[4]+date[6]+date[7]+'.csv'

#writing allocation results in the file 'allocation.csv'

# Here are the tags for the aganets, e.g. student,
# project, academic, specified in config=alloa.conf
 
level1_name=config['level1']
level2_name=config['level2']
level3_name=config['level3']


outfile = open(filename,"w")
outtext="%(lev1)s, %(lev2)s, %(lev3)s,  %(lev1)s preference, %(lev2)s preference\n\n" %dict(lev1=level1_name,lev2=level2_name,lev3=level3_name) 
outfile.write(outtext)
outfile.close()

# FOR ME allocation_results contaisn now the allocation, either we alter this or we alter the next step

outfile = open(filename,"a")
for i in range(0, len(allocation_results)):
    outtext2="%(arg)s, %(arg2)s, %(arg3)s, %(arg4)s, %(arg5)s \n" %dict(arg=allocation_results[i][0], arg2=allocation_results[i][1],arg3=allocation_results[i][2],arg4=allocation_results[i][3], arg5=allocation_results[i][4])
    outfile.write(outtext2)
outfile.close()

filename2=config['allocation_results']+'allocation_profile_'+date[0]+date[1]+date[3]+date[4]+date[6]+date[7]+'.csv'

#writing profile results
outfile = open(filename2,"w")
outtextcount="Total number of assigned level 1 agents is %(flow)d\nTotal cost of assginment is %(cost)d\n\nLevel 1 preference count\n\n"%dict(flow=flow, cost=C)
outfile.write(outtextcount)
outfile.close()

if hierarchy_weight>=1:
    outfile = open(filename2,"a")
#    for i in range(0, len(results1[i])-4):
    for i in range(0, max_alt_proj-1):
        outtextpref="%(pref)s,%(pref2)d\n"%dict(pref=level2_name+' that was choice no.'+str(i+1), pref2=num_of_prefs[i])
        outfile.write(outtextpref)
    outfile.close()
else:
    outfile = open(filename2,"a")
    outtextpref="N/A \n"
    outfile.write(outtextpref)
    outfile.close()


outfile = open(filename2,"a")
outtextcount2="\nLevel 2 preference count\n\n"
outfile.write(outtextcount2)
outfile.close()


if hierarchy_weight>=2:
    outfile = open(filename2,"a")
    for i in range(0, max_alt_sup):
        outtextpref="%(pref)s, %(pref2)d \n"%dict(pref=level3_name+' that was choice no.'+str(i+1), pref2=num_of_super_prefs[i])
        outfile.write(outtextpref)
    outfile.close()
else:
    outfile = open(filename2,"a")
    outtextcount3="N/A \n"
    outfile.write(outtextcount3)
outfile.close()

filename3=config['allocation_results']+'allocation_workloads_capacities_'+date[0]+date[1]+date[3]+date[4]+date[6]+date[7]+'.csv'

#allocation results - supervisor workloads/project capacities taken
outfile = open(filename3,"w")
outtext3="%(lev3)s, %(lev3)s workload\n\n" %dict(lev3=level3_name)
outfile.write(outtext3)
outfile.close()

outfile = open(filename3,"a")
for j in range(0, len(allocation_results2)):
    outtext4="%(arg)s, %(arg2)s \n" %dict(arg=allocation_results2[j][0], arg2=allocation_results2[j][1])
    outfile.write(outtext4)
outfile.close()

outfile = open(filename3,"a")
outtext5="\n%(lev2)s, %(lev2)s capacity taken\n\n"  %dict(lev2=level2_name)
outfile.write(outtext5)
outfile.close()

outfile = open(filename3,"a")
for k in range(0, len(allocation_results3)):
    outtext6="%(arg)s,  %(arg2)s \n" %dict(arg=allocation_results3[k][0], arg2=allocation_results3[k][1])
    outfile.write(outtext6)
outfile.close()

#SECOND MARKERS
level4_allocation=config["level4_allocation"]
if level4_allocation=='No':
    sys.exit(0)
 #specifying what is the level  data (from 'alloa.conf' file)   
level4_name=config['level4']

#Reading level 4 data from the file specified in the configuration file 'alloa.conf' specify the input file; r - read
file4=config['working_files']+'result4_'+date[0]+date[1]+date[3]+date[4]+date[6]+date[7]+'.txt'
infile=open(config["level4_data"], 'r')
lines=infile.readlines()
infile.close()
outtext = ['%d%s%s' % (i, config["user_delimiter4"], row) for i, row in enumerate(lines,0) ]
outfile = open(file4,"w")
outfile.writelines(str("".join(outtext)))
outfile.close()

#creating list of lists of level 4 data
results4 = []
with open(file4) as inputfile:
    for line in inputfile:
        results4.append(line.strip().split(config["user_delimiter4"]))


#putting level 4 data into the right format
level4=[[supervisors[results4[i][1]],results4[i][2],results4[i][3]] for i in range(1, len(results4))]
projec=[[projects[results4[i][j]] for j in range(4, len(results4[i]))] for i in range(1, len(results4))]
level4_data=[level4[i]+projec[i] for i in range(0, len(results4)-1)]

#edges allocated - need to be removed
taken_edges=[[projects[allocation_results[i][1]], supervisors[allocation_results[i][2]]] for i in range(0, len(allocation_results))]
possible_edges=[[[level4_data[i][j],level4_data[i][0]] for j in range(4, len(level4_data[i]))] for i in range(0, len(level4_data))]
possible_edges_pref=[[[level4_data[i][j],level4_data[i][0],j] for j in range(4, len(level4_data[i]))] for i in range(0, len(level4_data))]
#merging lists of a list into a one list of lists. 
possible_edges1=sum(possible_edges, [])
possible_edges_pref1=sum(possible_edges_pref,[])
#possible_edges1 minus taken edges
marker_edges=[x for x in possible_edges1 if x not in taken_edges]
#workloads after allocation
workloads_taken=[[supervisors[allocation_results2[i][0]],allocation_results2[i][1]] for i in range(0, len(allocation_results2))]
#marking capacities left after allocation (lecturer, lower capacity, upper capacity)
marking_capacities=[[level4_data[i][0], int(level4_data[i][1]),int(level4_data[i][2])-workloads_taken[i][1]] for i in range(0, len(level4_data))]
project_numbers_taken=[[projects[allocation_results3[i][0]], allocation_results3[i][1]] for i in range(0,len(allocation_results3)) if allocation_results3[i][1]>0]

#creating input graph for second markers

#adding beginning of the code
filename_markers=config['working_files']+'allocation_graph_networkx_second_markers_'+date[0]+date[1]+date[3]+date[4]+date[6]+date[7]+'.py'
outfile = open(filename_markers,"w")
outtext="import networkx as nx\nimport math\nM=nx.DiGraph()\n"
outfile.write(outtext)
outfile.close()

#supervisor node demands +
outfile=open(filename_markers,"a")
for i in range(0,len(marking_capacities)):
    outtexts = 'M.add_node(%(super)d, demand=%(dem)d)\n' % dict(super=marking_capacities[i][0]+num_of_proj*2, dem=marking_capacities[i][1]) 
    outfile.write(outtexts)
outfile.close()

#supervisor node demands -

outfile=open(filename_markers,"a")
for i in range(0,len(marking_capacities)):
    outtexts = 'M.add_node(%(super)d, demand=%(dem)d)\n' % dict(super=marking_capacities[i][0]+len(marking_capacities)+num_of_proj*2, dem=-marking_capacities[i][1]) 
    outfile.write(outtexts)
outfile.close()

#source to projects

markers1=config['working_files']+'markers1_'+date[0]+date[1]+date[3]+date[4]+date[6]+date[7]+'.py'

outfile = open(markers1,"w")
for i in range(0,len(taken_edges)):
    outtexts = 'M.add_edge(0, %(proj)d, weight=0)\n' %dict(proj=taken_edges[i][0])
    outfile.writelines(str("".join(outtexts)))
outfile.close()
                
#removing duplicated lines

lines_seen = set() 
outfile = open(filename_markers, "a")
for line in open(markers1, "r"):
    if line not in lines_seen: 
        outfile.write(line)
        lines_seen.add(line)
outfile.close()



#projects to project duplicates
markers2=config['working_files']+'markers2_'+date[0]+date[1]+date[3]+date[4]+date[6]+date[7]+'.py'
outfile=open(markers2,"w")
for i in range(0,len(project_numbers_taken)):
    outtexts="M.add_edge(%(proj)d, %(proj_dup)d, capacity=%(cap)d, weight=0)\n" % dict(proj=project_numbers_taken[i][0], proj_dup=project_numbers_taken[i][0]+num_of_proj, cap=project_numbers_taken[i][1])
    outfile.write(outtexts)
outfile.close()

#removing duplicated lines

lines_seen = set() # holds lines already seen
outfile = open(filename_markers, "a")
for line in open(markers2, "r"):
    if line not in lines_seen: # not a duplicate
        outfile.write(line)
        lines_seen.add(line)
outfile.close()


#projects to markers 
outfile = open(filename_markers,"a")
for i in range(0,len(marker_edges)):
    outtexts = "M.add_edge(%(proj)d, %(mark)d, weight=0, capacity=1)\n" % dict(proj=marker_edges[i][0]+num_of_proj, mark=marker_edges[i][1]+num_of_proj*2)
    outfile.write(outtexts)        
outfile.close()

#markers to marker duplicates

outfile = open(filename_markers,"a")
for i in range(0,len(marking_capacities)):
      outtexts = "M.add_edge(%(mark)d,%(mark_dup)d, capacity=%(cap)d, weight=0)\n" % dict(mark=marking_capacities[i][0]+num_of_proj*2, mark_dup=marking_capacities[i][0]+num_of_proj*2+len(marking_capacities), cap=marking_capacities[i][2]-marking_capacities[i][1])
      outfile.write(outtexts)
        
outfile.close()

 
#calculate the sink2
sink2 = num_of_proj*2 + num_of_sup*2+1

#second markers to sink2

outfile = open(filename_markers,"a")
for i in range(0,len(marking_capacities)):
    outtexts = "M.add_edge(%(mark_dup)d, %(node_sink2)d, weight=0)\n" % dict(node_sink2=sink2, mark_dup=marking_capacities[i][0]+num_of_proj*2+len(marking_capacities))
    outfile.write(outtexts)
outfile.close()


#adding ending of the code
outfile = open(filename_markers,"a")
outtext="import sys\ntry:\n K=nx.max_flow_min_cost(M,0,%(node_sink2)d)\nexcept nx.NetworkXUnfeasible:\n  print('Second allocation satisfying the level 4 lower bounds is not possible. Try reducing lower bounds.')\n  sys.exit(1)\nexcept nx.NetworkXError:\n  print('The input graph is not directed or not connected. Please check the data if all the choices on the level 1 list are included in the level 2 list and the choices on the level 2 list are included in the level 3 list.')\n  sys.exit(1)\nexcept nx.NetworkXUnbounded:\n  print('Allocation is not possible because some upper capacity bounds at level 1 have not been set up. Please check the data.')\n  sys.exit(1)" %dict(node_sink2=sink2)
outfile.write(outtext)
outfile.close()

#deleting temporary level 4 allocation files
if delete_files=='Yes':
    os.remove(markers1)
    os.remove(markers2)
    os.remove(file4)

#executing min cost max flow algorithm using networkx
exec(open(filename_markers).read())

#return the total flow from sink to source, i.e., number of level 1 items with their allocations. 
flow_markers = nx.max_flow(M, 0, sink2)
#return the cost of flow
C_markers=nx.cost_of_flow(M,K)

#deleting temporary level 4 allocation files
if delete_files=='Yes':
    os.remove(filename_markers)
 
#results for marking (level4)

allocation_results_markers=[[inv_projects[m-num_of_proj], inv_supervisors[v-num_of_proj*2]] for u in K if u>0 if u<num_of_proj+1 for m in K[u] if m>num_of_proj if m<num_of_proj*2+1 for v in K[m] if v>num_of_proj*2 if v<num_of_proj*2+num_of_sup+1 if K[m][v]>0 ]
allocation_results_markers_workload=[[inv_supervisors[u-num_of_proj*2-num_of_sup], K[u][sink2]] for u in K if u> num_of_proj*2+num_of_sup if u<sink2]



filename_markers_results=config['allocation_results']+'allocation_second_markers_'+date[0]+date[1]+date[3]+date[4]+date[6]+date[7]+'.csv'
#writing allocation results in the file 'allocation.csv'
outfile = open(filename_markers_results,"w")
outtextcount="Total number of assigned level 2 items is %(flow)d\n\n"%dict(flow=flow_markers)
outfile.write(outtextcount)
outfile.close()


outfile = open(filename_markers_results,"a")
outtext="%(lev2)s, %(lev4)s\n\n" %dict(lev2=level2_name, lev4=level4_name)
outfile.write(outtext)
outfile.close()


outfile = open(filename_markers_results,"a")
for i in range(0, len(allocation_results_markers)):
    outtext2="%(arg)s, %(arg2)s\n" %dict(arg=allocation_results_markers[i][0], arg2=allocation_results_markers[i][1])
    outfile.write(outtext2)
outfile.close()



filename_markers_results2=config['allocation_results']+'allocation_markers_workloads_'+date[0]+date[1]+date[3]+date[4]+date[6]+date[7]+'.csv'
#allocation results - marker workloads
outfile = open(filename_markers_results2,"w")
outtext3="%(lev4)s, %(lev4)s workload\n\n" %dict(lev4=level4_name)
outfile.write(outtext3)
outfile.close()

outfile = open(filename_markers_results2,"a")
for j in range(0, len(allocation_results_markers_workload)):
    outtext4="%(arg)s, %(arg2)s \n" %dict(arg=allocation_results_markers_workload[j][0], arg2=allocation_results_markers_workload[j][1])
    outfile.write(outtext4)
outfile.close()


filename_total_results=config['allocation_results']+'allocation_total_workloads_'+date[0]+date[1]+date[3]+date[4]+date[6]+date[7]+'.csv'
#allocation results - marker workloads
outfile = open(filename_total_results,"w")
outtext3="%(lev3)s, Total workload\n\n" %dict(lev3=level3_name)
outfile.write(outtext3)
outfile.close()

outfile = open(filename_total_results,"a")
for j in range(0, len(allocation_results2)):
    outtext4="%(arg)s, %(arg2)s \n" %dict(arg=allocation_results_markers_workload[j][0], arg2=allocation_results_markers_workload[j][1]+allocation_results2[j][1])
    outfile.write(outtext4)
outfile.close()

