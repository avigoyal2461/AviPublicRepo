using System;
using System.ComponentModel.DataAnnotations;
using System.Security.Cryptography.X509Certificates;

namespace Models
{
    public class WorkQueueItemModel
    {
        [Key]
        public string id { get; set; }
        public string queueid { get; set; }
        public string name { get; set; }
        public string? keyvalue { get; set; }
        public string? status { get; set; }
        public int? attempt { get; set; }
        public DateTime? loaded { get; set; }
        public DateTime? completed { get; set; }
        public DateTime? exception { get; set; }
        public string? exceptionreason { get; set; }
        public DateTime? deferred { get; set; }
        public int? worktime { get; set; }
        public string? data { get; set; }
        public int queueident { get; set; }
        public long ident { get; set; }
        public string? sessionid { get; set; }
        public int priority { get; set; }
        public int prevworktime { get; set; }
        public int? attemptworktime { get; set; }
        public DateTime? finished { get; set; }
        public string? exceptionreasonvarchar { get; set; }
        public string? exceptionreasontag { get; set; }
        public int? encryptid { get; set; }
        public DateTime? lastupdated { get; set; }
        public DateTime? locktime { get; set; }
        public long? sla {  get; set; }
        public DateTime? sladatetime { get; set; }
        public string? processname { get; set; }
        public bool issuggested { get; set; }
        public string? tag { get; set; }
    }
}
