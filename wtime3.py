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

# Default values in (H,M,S) format
def_worktime = (7, 12, 0)
def_ticket_due = (6, 30, 0)
def_pausetime = (0, 30, 0)

class wtime:
    start_time = dt.datetime.now()
    current_time = dt.datetime.now()
    working_time = dt.timedelta(hours=def_worktime[0],
                                minutes=def_worktime[1],
                                seconds=def_worktime[2])
    ticket_due = dt.timedelta(hours=def_ticket_due[0],
                              minutes=def_ticket_due[1],
                              seconds=def_ticket_due[2])
    pause_time = dt.timedelta(hours=def_pausetime[0],
                              minutes=def_pausetime[1],
                              seconds=def_pausetime[2])
    due_time = None
    current_elapse = None
    remaining_time = None
    over_time = None
    ticket_time = None
    ticket_at = None
    ticket_remain = None
    overtime = False
    to_ticket = None
    to_end = None
    t1 = None
    t2 = None
    t3 = None
    t4 = None

#   def __init__(self):
#       pass
#       
#   def __init__(self,hour,minute,second):
#       now=dt.datetime.now()
#       self.start_time=dt.datetime(now.year,now.month,now.day,hour,minute,second)
#       self.current_time=dt.datetime.now()
#
#   def __init__(self,start_time,working_time,ticket_due,pause_time):
#       now=dt.datetime.now()
#       self.start_time=dt.datetime(now.year,now.month,now.day,start_time[0],start_time[1],start_time[2])
#       self.current_time=dt.datetime.now()
#       self.working_time=dt.timedelta(hours=working_time[0],minutes=working_time[1],seconds=working_time[2])
#       self.ticket_due=dt.timedelta(hours=ticket_due[0],minutes=ticket_due[1],seconds=ticket_due[2])
#       self.pause_time=dt.timedelta(hours=pause_time[0],minutes=pause_time[1],seconds=pause_time[2])
#
    def __init__(self, **kwargs):
        for arg in kwargs:
            if arg == 'start_time':            
                self.start_time = self.get_datetime(kwargs[arg])
            elif arg =='current_time':
                self.current_time = self.get_datetime(kwargs[arg])
            elif arg == 'working_time':
                self.working_time = self.get_datetime(kwargs[arg])
            elif arg == 'ticket_due':
                self.ticket_due = self.get_datetime(kwargs[arg])
            elif arg == 'pause_time':
                self.pause_time = self.get_datetime(kwargs[arg])
            elif arg == 't1':
                self.t1 = self.get_datetime(kwargs[arg])
            elif arg == 't2':
                self.t2 = self.get_datetime(kwargs[arg])
            elif arg == 't3':
                self.t3 = self.get_datetime(kwargs[arg])
            elif arg == 't4':
                self.t4 = self.get_datetime(kwargs[arg])
    
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
               
    def getTsHMS(self,ts):
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

    def printTimeDelta(self,delay):
        if (delay.days > 0):
            out = str(delay).replace(" days, ", ":")
        else:
            out = "0:" + str(delay)
            outAr = out.split(':')
            outAr = ["%02d" % (int(float(x))) for x in outAr[1:]]
            out   = ":".join(outAr)
        return out
        
    @staticmethod
    def getTimes(wtimecmd):
        t1 = t2 = t3 = t4 = None
        if len(sys.argv) < 1:
            print("Usage %s t1 [[[t2] t3] t4]" % wtimecmd)
            print("Where tx in the form HH:MM[:SS]")
            sys.exit(1)
        # wtime params
        t1 = t2 = t3 = t4 = None
        try:
            t1 = sys.argv[1]
            t2 = sys.argv[2]
            t3 = sys.argv[3]
            t4 = sys.argv[4]
        except:
            pass
        return t1, t2, t3, t4

    def get_datetime(self, timestring):
        if timestring is None:
            return None
        now = dt.datetime.now()
        h, m, s = self.getTsHMS(timestring)
        return dt.datetime(now.year,now.month,now.day,h,m,s) 


    def calc2(self):
        out = {} 
        now=dt.datetime.now()
        if self.t1 is None:
            out["error"]="You must specify at least one time stamp in HH:MM:SS format"
            return out
        t1h = self.t1.hour
        t1m = self.t1.minute
        t1s = self.t1.second
        if t1h is None or t1m is None:
            print("t1 does not seem a valid time value, please specify a valid timestamp in HH:MM:SS format")
            sys.exit(1)
        dt1=dt.timedelta(0,t1h*3600+t1m*60+t1s)
        if self.t2 is not None:
            t2h = self.t2.hour
            t2m = self.t2.minute
            t2s = self.t2.second
        else:
            t2h = now.hour
            t2m = now.minute
            t2s = now.second
        dt2=dt.timedelta(0,t2h*3600+t2m*60+t2s)
        if self.t3 is not None:
            t3h = self.t3.hour
            t3m = self.t3.minute
            t3s = self.t3.second
        else:
            t3h=now.hour
            t3m=now.minute
            t3s=now.second      
        dt3=dt.timedelta(0,t3h*3600+t3m*60+t3s)
        if self.t4 is not None:
            t4h = self.t4.hour
            t4m = self.t4.minute
            t4s = self.t4.second
        else:
            t4h=now.hour
            t4m=now.minute
            t4s=now.second
        dt4=dt.timedelta(0, t4h*3600+t4m*60+t4s)
        dtn=dt.timedelta(0, now.hour*3600+now.minute*60+now.second)
        dtw=dt.timedelta(0, def_worktime[0]*3600 +
                            def_worktime[1]*60 +
                            def_worktime[2]) #  7:12 working time
        dtp=dt.timedelta(0, def_pausetime[0]*3600 +
                            def_pausetime[1]*60 +
                            def_pausetime[2]) #  0:30 default pause time
        dtk=dt.timedelta(0, def_ticket_due[0]*3600 +
                            def_ticket_due[1]*60 +
                            def_ticket_due[2]) #  6:30 ticket threshold
        dtm=dt2-dt1 # delta time morning
        dta=dt4-dt3 # delta time afternoon
        did=dt3-dt2 # delta idle time
        
        out["t1"] = "%02d:%02d:%02d" % (t1h,t1m,t1s)
        out["t2"] = "%02d:%02d:%02d" % (t2h,t2m,t2s)
        out["t3"] = "%02d:%02d:%02d" % (t3h,t3m,t3s)
        out["t4"] = "%02d:%02d:%02d" % (t4h,t4m,t4s)
        out["t2t1"] = self.printTimeDelta(dtm)
        out["t4t3"] = self.printTimeDelta(dta)
        
        total_time=dt.timedelta(seconds=0)
        if did > dt.timedelta(seconds=0):
            out["pause time"] = "%s" % self.printTimeDelta(did)
            out["total time"] = "%s" % self.printTimeDelta(dtm+dta)
            total_time = dtm+dta
        else:
            out["pause time"] = "%s" % self.printTimeDelta(dtp)
            if dtm+dta >= dtp:
                out["total time"] = "%s" % self.printTimeDelta(dtm+dta-dtp)
                total_time = dtp
            else:
                out["consume pause"] = "%s" % self.printTimeDelta(dtp-(dtm+dta))
        if did > dt.timedelta(seconds=0):
            if dtw > (dtm+dta):
                out["time to reach"] = "%s" % self.printTimeDelta(dtw)
                out["time remaining"] = "%s" % self.printTimeDelta(dtw-(dtm+dta))
                out["time remaining at"] = "%s" % self.printTimeDelta(dt1+(dt3-dt2)+dtw)
                time_to_reach = dtw
                time_to_reach_sec = time_to_reach.seconds + time_to_reach.days * 24 * 3600
                time_remaining = dtw-(dtm+dta)
                time_remaining_sec = time_remaining.seconds + time_remaining.days * 24 * 3600
                out["time remaining perc"] = 100*(time_to_reach_sec-time_remaining_sec)/time_to_reach_sec
            else:
                out["overtime"] = "%s" % self.printTimeDelta((dtm+dta)-dtw)
                out["time remaining perc"] = 100
        else:                
            if (dtw+dtp) > (dtm+dta):
                out["time to reach"] = "%s" % self.printTimeDelta(dtw)
                out["time remaining"] = "%s" % self.printTimeDelta((dtw+dtp)-(dtm+dta))
                out["time remaining at"] = "%s" % self.printTimeDelta(dt1+(dt3-dt2)+(dtw+dtp))
                time_to_reach = dtw
                time_to_reach_sec = time_to_reach.seconds + time_to_reach.days * 24 * 3600
                time_remaining = (dtw+dtp)-(dtm+dta)
                time_remaining_sec = time_remaining.seconds + time_remaining.days * 24 * 3600
                out["time remaining perc"] = 100*(time_to_reach_sec-time_remaining_sec)/time_to_reach_sec
            else: 
                out["overtime"] = "%s" % self.printTimeDelta((dtm+dta)-(dtw+dtp))
                out["time to reach"] = "reached"
                out["time remaining perc"] = 100
        if dtm+dta >= dtk:
            out["ticket remaining"] = "reached"
            out["ticket remaining perc"] = 100
        else:
            out["ticket remaining"] = "%s" % self.printTimeDelta(dtk-(dtm+dta))
            out["ticket remaining at"] = "%s" % self.printTimeDelta(dtn+dtk-(dtm+dta))
            tkg = dtk-(dtk-(dtm+dta))
            tkgsec = tkg.seconds + tkg.days * 24 * 3600
            dtksec = dtk.seconds + dtk.days * 24 * 3600
            out["ticket remaining perc"] = 100*tkgsec/dtksec
        out["ticket time"] = "%s" % self.printTimeDelta(dtk)
        return out

    def printout(self,out):
        if 'error' in out.keys():
            print(out['error'])
            return 1
        print("---------------------------------------")
        print(" wtime                                 ")
        print("---------------------------------------")
        print("T1            : %s" % out["t1"])
        print("T2            : %s T2-T1: %s" % (out["t2"],out["t2t1"]))
        print("T3            : %s" % out["t3"])
        print("T4            : %s T4-T3: %s" % (out["t4"],out["t4t3"]))
        print("Pause time    : %s" % out["pause time"])
        consuming = out.get("consume pause", None)
        if consuming is None:
            print("Total time    : %s" % out["total time"])
        else:
            print("Consume pause : %s to go" % consuming)
        overtime = out.get("overtime",None)
        if overtime is not None:
           print("Overtime      : %s" % overtime)
        else:
           print("Time to reach : %s" % out["time to reach"])
           print("Time remaining: %s" % out["time remaining"])
           print("            at: %s" % out["time remaining at"])       
        ticket_time = out["ticket remaining"]        
        if ticket_time == "reached":
            pass
        else:
            print("Ticket remain : %s" % out["ticket remaining"])
            print("           at : %s" % out["ticket remaining at"])
        print("Ticket time   : %s" % out["ticket time"])
        return 0


if __name__ == "__main__":
    t1,t2,t3,t4 = wtime.getTimes("wtime3")
    wt = wtime(t1=t1,t2=t2,t3=t3,t4=t4)
    out = wt.calc2()
    exit_code = wt.printout(out)
    sys.exit(exit_code)
    
    

