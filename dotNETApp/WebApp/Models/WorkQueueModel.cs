using System;
using System.ComponentModel.DataAnnotations;

namespace Models
{
    public class WorkQueueModel
    {
        [Key]
        public string id { get; set; }
        public string name { get; set; }
        //public string status { get; set; }
        //public bool? isEncrypted { get; set; }

        public string? keyfield { get; set; }
        public bool? running { get; set; }
        public int? maxattemps { get; set; }
        public int? ident { get; set; }
        public int? processid { get; set; }
        public int? resourcegroupid { get; set; }
        public int? targetsessions { get; set; }
        public int? activelock { get; set; }
        public DateTime? activelocktime { get; set; }
        public string? activelockname { get; set; }
        public int? encryptid { get; set; }
        public bool sessionexceptionretry { get; set; }
        public int? pending { get; set; }
        public int? completed { get; set; }
        public int? exceptioned { get; set; }
        public int? deferred { get; set; }
        public int? averageworktime { get; set; }
        public int? totalworktime { get; set; }
        public int? locked { get; set; }
        public int? total { get; set; }
        public DateTime? dateUpdated { get; set; }
    }
}
