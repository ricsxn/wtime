#!/usr/bin/env python
#
# wtime - Working time class 
#
import sys
import datetime as dt


class wtime:
	start_time=dt.datetime.now()
	current_time=dt.datetime.now()
	working_time=dt.timedelta(hours=7,minutes=12)
	ticket_due=dt.timedelta(hours=6)
	pause_time=dt.timedelta(minutes=30)
	due_time=None
	current_elapse=None
	remaining_time=None
	over_time=None
	ticket_time=None
	ticket_at=None
	ticket_remain=None
	overtime=False
	to_ticket=None
	to_end=None

	def __init__(self):
		self.start_time=dt.datetime.now()
		self.current_time=dt.datetime.now()
		self.working_time=dt.timedelta(hours=7,minutes=12)
		self.ticket_due=dt.timedelta(hours=6)
		self.pause_time=dt.timedelta(minutes=30)
		self.calc()
		
	def __init__(self,hour,minute,second):
		now=dt.datetime.now()
		self.start_time=dt.datetime(now.year,now.month,now.day,hour,minute,second)
		self.current_time=dt.datetime.now()
		self.working_time=dt.timedelta(hours=7,minutes=12)
		self.ticket_due=dt.timedelta(hours=6)
		self.pause_time=dt.timedelta(minutes=30)
		
	def __init__(self,start_time,working_time,ticket_due,pause_time):
		now=dt.datetime.now()
		self.start_time=dt.datetime(now.year,now.month,now.day,start_time[0],start_time[1],start_time[2])
		self.current_time=dt.datetime.now()
		self.working_time=dt.timedelta(hours=working_time[0],minutes=working_time[1],seconds=working_time[2])
		self.ticket_due=dt.timedelta(hours=ticket_due[0],minutes=ticket_due[1],seconds=ticket_due[2])
		self.pause_time=dt.timedelta(hours=pause_time[0],minutes=pause_time[1],seconds=pause_time[2])
		
	def calc(self):
		self.current_time=dt.datetime.now()
		self.due_time=self.start_time+self.working_time+self.pause_time
		self.current_elapse=self.current_time-self.start_time
		if self.current_time > self.due_time:
			self.overtime=True
			self.over_time=self.current_time-self.due_time
			self.to_end=100
		else:
			self.overtime=False
			self.remaining_time=self.due_time-self.current_time
			self.to_end=int(100*(self.start_time-self.current_time).total_seconds()/(self.start_time-self.due_time).total_seconds())
		self.ticket_time=self.ticket_due+self.pause_time
		self.ticket_at=self.start_time+self.ticket_time
		if self.current_time > self.ticket_at:
			self.ticket_remain=dt.timedelta(seconds=0)
			self.to_ticket=100
		else:
			self.ticket_remain=self.ticket_at-self.current_time
			self.to_ticket=int(100*(self.start_time-self.current_time).total_seconds()/(self.start_time-self.ticket_at).total_seconds())

	def getStartTime(self):
		return self.start_time.strftime("%H:%M:%S")
	def getWorkingTime(self):
		return self.printTimeDelta(self.working_time)
	def getPauseTime(self):
		return self.printTimeDelta(self.pause_time)
	def getCurrentTime(self):
		return self.current_time.strftime("%H:%M:%S")
	def getCurrentElapse(self):
		return self.printTimeDelta(self.current_elapse)
	def getDueTime(self):
		return self.due_time.strftime("%H:%M:%S")
	def getRemainingTime(self):
		return self.printTimeDelta(self.remaining_time)
	def getTicketTime(self):
		return self.printTimeDelta(self.ticket_time)
	def getTicketAt(self):
		return self.ticket_at.strftime("%H:%M:%S")
	def getTicketRemain(self):
	 	return self.printTimeDelta(self.ticket_remain)
	def getOverTime(self):
		return self.printTimeDelta(self.over_time)

	def showbar(self,perc,width,pflag=False):
		# perc  - current  percentage
		# width - the bar width
		# pflag - print percentage flag 0/1
		barpt=width*perc/100
		pbar="["
		for i in range(0,width): 
			if (i < barpt):
				pbar+="#"
			else:
				pbar+="-"
		pbar+="]"
		if (pflag):
			pbar+=" %3d%%" % perc
		return pbar

	def printTimeDelta(self,delay):
		if (delay.days > 0):
			out = str(delay).replace(" days, ", ":")
		else:
			out = "0:" + str(delay)
			outAr = out.split(':')
			outAr = ["%02d" % (int(float(x))) for x in outAr[1:]]
			out   = ":".join(outAr)
		return out

	def __str__(self):
		self.calc()
		if self.overtime == True:
			remaining_or_overtime="Overtime      : %s " % self.getOverTime()
		else:
			remaining_or_overtime="Remaining time: %s " % self.getRemainingTime()
		return ("----------------------------\n"
			   +"Reporting your working time \n"
			   +"----------------------------\n"
			   +"Start time    : %s\n" % self.getStartTime()
		       +"Working time  : %s\n" % self.getWorkingTime()
		       +"Pause time    : %s\n" % self.getPauseTime()
		       +"Current time  : %s\n" % self.getCurrentTime()
		       +"Current elapse: %s\n" % self.getCurrentElapse()
		       +"Due time      : %s\n" % self.getDueTime()     
		       +"%s"                   % remaining_or_overtime  + self.showbar(self.to_end,20,True)   +"\n"
		       +"Ticket time   : %s\n" % self.getTicketTime() 
		       +"Ticket at     : %s\n" % self.getTicketAt()     
		       +"Ticket remain : %s "  % self.getTicketRemain()) + self.showbar(self.to_ticket,20,True)+"\n"

def getTsHMS(ts):
    h = m = s = None
    if ts is not None:
        tv = ts.split(':')
    try:
        h = int(tv[0])
        m = int(tv[1])
        s = int(tv[2])
    except:
        pass
    if s is None: s = 0
    return h, m, s

def printTimeDelta(delay):
    if (delay.days > 0):
        out = str(delay).replace(" days, ", ":")
    else:
        out = "0:" + str(delay)
        outAr = out.split(':')
        outAr = ["%02d" % (int(float(x))) for x in outAr[1:]]
        out   = ":".join(outAr)
    return out

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage wtime2 t1 [[[t2] t3] t4]"
        print "Where tx in the form HH:MM[:SS]"
    else:
        # wtime params
        t1 = t2 = t3 = t4 = None
        try:
            t1 = sys.argv[1]
            t2 = sys.argv[2]
            t3 = sys.argv[3]
            t4 = sys.argv[4]
        except:
            pass

    if t1 is None:
        print "You must specify at least one time stamp in HH:MM:SS format"
        sys.exit(1)
	
    t1h, t1m, t1s = getTsHMS(t1)
    if t1h is None or t1m is None:
        print "t1 does not seem a valid time value, please specify a valit timestamp in HH:MM:SS format"
        sys.exit(1)

    t2h, t2m, t2s = getTsHMS(t2)
    t3h, t3m, t3s = getTsHMS(t3)
    t4h, t4m, t4s = getTsHMS(t4)

#wt = wtime([t1h,t1m,t1s]
#		  ,[t2h,t2m,t2s]
#		  ,[t3h,t3m,t3s]
#		  ,[t4h,t4m,t4s])
#print wt

    now=dt.datetime.now()
    dt1=dt.datetime(now.year,now.month,now.day,t1h,t1m,t1s)
    dt2=dt.datetime(now.year,now.month,now.day,t2h,t2m,t2s)
    dt3=dt.datetime(now.year,now.month,now.day,t3h,t3m,t3s)
    dt4=dt.datetime(now.year,now.month,now.day,t4h,t4m,t4s)

    print printTimeDelta((dt2-dt1)+(dt4-dt3))
    sys.exit(0)

