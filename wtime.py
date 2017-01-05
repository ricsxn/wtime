#!/usr/bin/env python
#
# wtime - Working time class 
#
import sys
import datetime as dt

__author__ = "Riccardo Bruno"
__copyright__ = "2017"
__license__ = "Apache"
__maintainer__ = "Riccardo Bruno"
__email__ = "riccardo.bruno@gmail.com"

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


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage wtime <hours> <minutes> [seconds]"
    else:
        # wtime params
        try:
            hours = int(sys.argv[1])
            minutes = int(sys.argv[2])
            if len(sys.argv) == 4:
                seconds = int(sys.argv[3])
            else:
                seconds = 0
        except:
            print "Unable to accept given input"
            sys.exit(10)
        wt = wtime((hours,minutes,seconds),(7,12,0),(6,0,0),(0,30,0))
        print wt
        sys.exit(0)
