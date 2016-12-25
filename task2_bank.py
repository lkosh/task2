""" bank24. BCC system with several counters """
from SimPy.Simulation import *
from random import expovariate, seed

## Model components ------------------------           
num_customers = 0
def bank_empty():
	return num_customers ==0
class Source(Process):
	""" Source generates customers randomly """
	def generate(self,number,interval,counters):          
		for i in range(number):
			c = Customer(name = "Customer%02d"%(i,))
			activate(c,c.visit(counters))   
			           
			t = expovariate(1.0/interval)                 
			yield hold,self,t
def NoInSystem(R):                                                  
    """ Total number of customers in the resource R"""
    return (len(R.waitQ)+len(R.activeQ))                            

class Customer(Process):
	""" Customer arrives, is served and leaves """
        
	numBalking = 0                                       
	def visit(self,counters):                                   
		arrive = now()
        #print "%8.4f %s: Here I am "%(now(),self.name)
		
		
		global num_customers
		num_customers += 1
		
		if num_customers <= maxInSystem:#maxInQueue:     # the test     
			Qlength = [NoInSystem(counters[i]) for i in range(Nc)] 
			for i in range(Nc):                                         
				if Qlength[i] == 0 or Qlength[i] == min(Qlength):
					choice = i  # the chosen queue number                
					break
			#some signalling
			event1 = SimEvent('Event-1')
			signal = Signaller()
			activate(signal, signal.sendSignals(counters = kk, choice = choice, event = event1))   
			yield request,self,counters[choice]
			#yield queueevent, self, event1                         
			#self.interrupt()
			wait = now()-arrive
			wM.observe(wait) 
			cM.observe(num_customers)
			#print b.waitQ
			print num_customers
           # print "%8.4f %s: Wait %6.3f"%(now(),self.name,wait)
			tib = expovariate(1.0/timeInBank)            
			yield hold,self,tib                          
			yield release,self,counters[choice]
           # print "%8.4f %s: Finished  "%(now(),self.name)
			num_customers -=1 
		else:
			Customer.numBalking += 1 
			num_customers -= 1     
			cM.observe(num_customers)
                
           # print "%8.4f %s: BALKING   "%(now(),self.name) 
class Signaller(Process):
	def sendSignals(self,counters, choice, event):
		tmp = choice
		Qlength = [NoInSystem(counters[i]) for i in range(Nc)] 
		for i in range(Nc):  
			if i == choice:
				continue                                       
			if Qlength[i] < Qlength[choice]:
				choice = i  # the chosen queue number                
		if choice != tmp:
			event.signal()
			print "signal!"
		yield hold, self, 0
			
		
## Experiment data -------------------------------       

timeInBank = 4.5 # mean, minutes                        
ARRint = 1.0     # mean interarrival time, minutes
numServers = 5	    # servers
maxInSystem = 25   # customers
maxInQueue = maxInSystem - numServers                    

maxNumber = 80000
maxTime = 480.0 # minutes                                      
theseed = 12345                                          
Nc = 7

    
## Model/Experiment ------------------------------

sE = SimEvent(name='Change lines')
wM = Monitor()   
cM = Monitor() 
seed(theseed)                                            
kk = [Resource(name="Clerk" + str(i)) for i in range(Nc)]   
initialize()    
s = Source('Source')
activate(s,s.generate(number=maxNumber,interval=ARRint,   
                      counters=kk),at=0.0) 

simulate(until=maxTime)

## Results -----------------------------------------

nb = float(Customer.numBalking)
print "balking number is %8.4f "%(nb)
print  wM[3][0]
result = wM.count(),wM.mean(), max(wM[i][1] for i in range(len(wM))), min(wM[i][1] for i in range(len(wM)))  
#print max(wM[1]), min(wM[1])                      
print "Average wait for %3d completions was %5.3f minutes. Maximum wait was %5.3f minutes. Minimum wait was %5.3f minutes"% result 
print "Average count of clients %3d "%cM.mean()
