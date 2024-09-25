using System;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;

namespace Models
{
    public class ResourceModel
    {
        [Key]
        public string resourceid { get; set; }
        public string name { get; set; }
        public int? processesrunning { get; set; }
        public int? actionsrunning { get; set; }
        public int? unitsallocated { get; set; }
        public DateTime? lastupdated { get; set; }
        public int? AttributeID { get; set; }
        public string pool { get; set; }
        public string controller { get; set; }
        public int? diagnostics { get; set; }
        public bool? logtoeventlog { get; set; }
        public string FQDN { get; set; }
        public bool? ssl { get; set; }
        public string userID { get; set; }
        public int? statusid { get; set; }
        public string DisplayStatus { get; set; }
        public string currentculture { get; set; }
        public DateTime? LastTimeLoggedIn { get; set; }

    }
}
