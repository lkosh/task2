""" bank24. BCC system with several counters """
from SimPy.Simulation import *
from random import expovariate, seed

## Model components ------------------------           
num_customers = 0

class Source(Process):
    """ Source generates customers randomly """

    def generate(self,number,meanTBA,resource):          
        for i in range(number):
            c = Customer(name = "Customer%02d"%(i,))
            activate(c,c.visit(b=resource))              
            t = expovariate(1.0/meanTBA)                 
            yield hold,self,t

class Customer(Process):
    """ Customer arrives, is served and leaves """
        
    numBalking = 0                                       

    def visit(self,b):                                   
        arrive = now()
        #print "%8.4f %s: Here I am "%(now(),self.name)
        global num_customers
        num_customers += 1
        
        if num_customers <= maxInSystem:#maxInQueue:     # the test     
            yield request,self,b                         
          
            wait = now()-arrive
            wM.observe(wait) 
            cM.observe(num_customers)
           # print "%8.4f %s: Wait %6.3f"%(now(),self.name,wait)
            tib = expovariate(1.0/timeInBank)            
            yield hold,self,tib                          
            yield release,self,b
           # print "%8.4f %s: Finished  "%(now(),self.name)
            num_customers -=1 
        else:
            Customer.numBalking += 1 
            num_customers -= 1     
            cM.observe(num_customers)
                
           # print "%8.4f %s: BALKING   "%(now(),self.name) 

## Experiment data -------------------------------       

timeInBank = 4.5 # mean, minutes                        
ARRint = 1.0     # mean interarrival time, minutes
numServers = 6	    # servers
maxInSystem = 25   # customers
maxInQueue = maxInSystem - numServers                    

maxNumber = 80000
maxTime = 480.0 # minutes                                      
theseed = 12345                                          

## Model/Experiment ------------------------------
wM = Monitor()   
cM = Monitor() 
seed(theseed)                                            
k = Resource(capacity=numServers,
             name="Counter",unitName="Clerk")            

initialize()
s = Source('Source')
activate(s, s.generate(number=maxNumber,meanTBA=ARRint, 
                         resource=k),at=0.0)             
simulate(until=maxTime)

## Results -----------------------------------------

nb = float(Customer.numBalking)
print "balking number is %8.4f "%(nb)
print  wM[3][0]
result = wM.count(),wM.mean(), max(wM[i][1] for i in range(len(wM))), min(wM[i][1] for i in range(len(wM)))  
#print max(wM[1]), min(wM[1])                      
print "Average wait for %3d completions was %5.3f minutes. Maximum wait was %5.3f minutes. Minimum wait was %5.3f minutes"% result 
print "Average count of clients %3d "%cM.mean()
