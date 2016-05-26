    # def dateSeq(self) this class is to be deleted..
    #     self.pv.reload_parameters()
    #     self.previousDate = self.pv.get_parameter('DateSeq', 'Date')
    #     self.currentDate = time.strftime('%Y%m%d')
    #     self.seq = self.pv.get_parameter('DateSeq', 'Seq')
    #
    #     if self.previousDate == self.currentDate
    #         self.pv.set_parameter('DateSeq', 'Date', ('string', self.currentDate), True)
    #         print 'Same Date', self.currentDate
    #
    #     else
    #         self.pv.set_parameter('DateSeq', 'Date', ('string', self.currentDate), True)
    #         #  self.seq = 0
    #         print 'New Date'   , self.currentDate, self.seq
    #     self.pv.save_parameters_to_registry()
    #     return self.currentDate