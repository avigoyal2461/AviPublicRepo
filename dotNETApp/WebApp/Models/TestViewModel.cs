using System;

namespace Models
{
    public class TestViewModel
    {
        public string Message { get; set; }
    }
    public class DateRangeModel
    {
        public DateTime StartTime { get; set; }
        public DateTime EndTime { get; set; }
        public string Process_Name { get; set; }
    }
}
