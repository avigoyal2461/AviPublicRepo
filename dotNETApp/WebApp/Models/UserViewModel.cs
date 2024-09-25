using Newtonsoft.Json;
using System.ComponentModel.DataAnnotations.Schema;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel;
using System;

namespace Models
{
    public class UserViewModel
    {
        [DisplayName("User ID")]
        public string userid { get; set; }
        [DisplayName("Username")]
        public string username { get; set; }
        [DisplayName("Valid From")]
        public DateTime? validfromdate { get; set; }
        [DisplayName("passwordexpirydate")]
        public DateTime? passwordexpirydate { get; set; }
        [DisplayName("User Email")]
        public string useremail { get; set; }
        [DisplayName("isdeleted")]
        public bool? isdeleted { get; set; }
        [DisplayName("UseEditSummaries")]
        public bool? UseEditSummaries { get; set; }
        [DisplayName("preferredStatisticsInterval")]
        public string preferredStatisticsInterval { get; set; }
        [DisplayName("SaveToolStripPositions")]
        public bool? SaveToolStripPositions { get; set; }
        [DisplayName("PasswordDurationWeeks")]
        public int? PasswordDurationWeeks { get; set; }
        [DisplayName("AlertEventTypes")]
        public int? AlertEventTypes { get; set; }
        [DisplayName("AlertNotificationTypes")]
        public int? AlertNotificationTypes { get; set; }
        [DisplayName("LogViewerHiddenColumns")]
        public double? LogViewerHiddenColumns { get; set; }
        [DisplayName("systemusername")]
        public string systemusername { get; set; }
        [DisplayName("loginattempts")]
        public int? loginattempts { get; set; }
        [DisplayName("lastsignedin")]
        public DateTime? lastsignedin { get; set; }
        [DisplayName("authtype")]
        public int? authtype { get; set; }
        [DisplayName("authenticationServerClientId")]
        public string authenticationServerClientId { get; set; }
        [DisplayName("authenticationServerUserId")]
        public string authenticationServerUserId { get; set; }
        [DisplayName("deletedLastSynchronizationDate")]
        public DateTimeOffset? deletedLastSynchronizationDate { get; set; }
        [DisplayName("hasBluePrismApiScope")]
        public bool hasBluePrismApiScope { get; set; }
        [DisplayName("updatedLastSynchronizationDate")]
        public DateTimeOffset? updatedLastSynchronizationDate { get; set; }
        [DisplayName("authServerName")]
        public string authServerName { get; set; }
        [DisplayName("Upn")]
        public string Upn { get; set; }
        [DisplayName("Sid")]
        public string Sid { get; set; }
        [DisplayName("Dn")]
        public string Dn { get; set; }
        [DisplayName("Full User")]
        public string FullUser
        {
            get { return username + " " + Upn; }
        }
    }
}
