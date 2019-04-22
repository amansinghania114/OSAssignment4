#!/usr/bin/env python
# coding: utf-8

# In[1]:


'''   
CS5250 Assignment 4, Scheduling policies simulator  
Sample skeleton program   
Input file:  
    input.txt   
Output files:   
    FCFS.txt   
    RR.txt  
    SRTF.txt  
    SJF.txt  
'''  
import sys
input_file = 'input.txt' 

class Process:
    last_scheduled_time = 0

    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.burst_time_copy = burst_time
        self.predicted_burst_time = 5

    # for printing purpose
    def __repr__(self):
        return '[id %d : arrival_time %d,  burst_time %d]' % (self.id, self.arrive_time, self.burst_time)
       
def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result

def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time        
        
def RR_scheduling(process_list, time_quantum):   
    plistsize  = len(process_list)
    schedule = []
    current_time = 0
    waiting_time = 0
    plcopy = process_list[:]
    queue = []
    queue.append(plcopy[0])
    plcopy.remove(plcopy[0]) 
    while len(queue)!=0:
        current_process = queue.pop(0) 
        if current_process.burst_time < time_quantum:
            executed_time = current_process.burst_time  
        else:
            executed_time = time_quantum
        current_process.burst_time = current_process.burst_time - executed_time           
        if current_time < current_process.arrive_time:
            current_time = current_process.arrive_time
        if len(schedule) == 0 or schedule[len(schedule) - 1][1] != current_process.id:
            schedule.append((current_time, current_process.id))
        current_time = current_time + executed_time
        for process in plcopy:
            if process.arrive_time <= current_time:
                queue.append(process)
        plcopy = [x for x in plcopy if x.arrive_time > current_time]       
        if current_process.burst_time != 0:
            queue.append(current_process)
        else:
            waiting_time = waiting_time + (current_time - current_process.arrive_time - current_process.burst_time_copy)
        if len(queue)==0 and len(plcopy) > 0:
            queue.append(plcopy[0])
            current_time = plcopy[0].arrive_time
            plcopy.remove(plcopy[0])
    average_waiting_time = waiting_time/float(plistsize)
    return schedule, average_waiting_time
        
def SRTF_scheduling(process_list):
    plistsize  = len(process_list)
    schedule = []
    current_time = 0
    waiting_time = 0
    plcopy = process_list[:]
    queue =  []
    current_process = plcopy[0]
    queue.append(plcopy[0])
    plcopy.remove(plcopy[0])
    while len(queue) > 0:
        current_process.burst_time = current_process.burst_time - 1
        if current_time < current_process.arrive_time:
            current_time = current_process.arrive_time
        if len(schedule) == 0 or schedule[len(schedule) - 1][1] != current_process.id:
            schedule.append((current_time, current_process.id))
        current_time += 1
        if current_process.burst_time == 0:
            queue.remove(current_process)
            waiting_time = waiting_time + (current_time - current_process.arrive_time - current_process.burst_time_copy)
        for process in plcopy:
            if process.arrive_time <= current_time:
                queue.append(process)        
        if len(queue)==0 and len(plcopy) > 0:
            current_time = plcopy[0].arrive_time
            queue.append(plcopy[0])
        plcopy = [x for x in plcopy if x.arrive_time > current_time]
#         Whenever two process have the same burst time, the process that arrives first is considered.
        if len(queue) > 0:
            current_process = min(queue, key=lambda p: p.burst_time)
    average_waiting_time = waiting_time/float(plistsize)  
    return schedule, average_waiting_time 
        
    
def SJF_scheduling(process_list, alpha):
    plistsize  = len(process_list)
    schedule = []
    current_time = 0
    waiting_time = 0
    plcopy = process_list[:]
    queue =  []
    current_process = plcopy[0]
    queue.append(plcopy[0])
    plcopy.remove(plcopy[0])
    history = dict()

    while len(queue) > 0:
        queue = sorted(queue, key=lambda p: p.predicted_burst_time)
        current_process = queue.pop(0)
        if current_time < current_process.arrive_time:
            current_time = current_process.arrive_time
        if len(schedule) == 0 or schedule[len(schedule) - 1][1] != current_process.id:
            schedule.append((current_time, current_process.id))
        current_time += current_process.burst_time
        current_process.burst_time = 0
        last_predicted_burst_time = history[
            current_process.id] if current_process.id in history else current_process.predicted_burst_time
        predicted_burst_time = (alpha * current_process.burst_time_copy) + ((1 - alpha) * last_predicted_burst_time)
        history[current_process.id] = predicted_burst_time
        waiting_time = waiting_time + (current_time - current_process.arrive_time - current_process.burst_time_copy)
        for process in plcopy:
            if process.arrive_time <= current_time:
                if process.id in history:
                    process.predicted_burst_time = history[process.id]
                queue.append(process)
        if len(queue)==0 and len(plcopy) > 0:
            current_time = plcopy[0].arrive_time
            queue.append(plcopy[0])
            
        plcopy = [x for x in plcopy if x.arrive_time > current_time]
    average_waiting_time = waiting_time/float(plistsize)
    return schedule, average_waiting_time
    
    
def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    process_list1 = read_input()
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list1,time_quantum = 10)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    process_list2 = read_input()
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list2)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    process_list3 = read_input()
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list3, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )
            
    
if __name__ == '__main__':
    main(sys.argv[1:])

