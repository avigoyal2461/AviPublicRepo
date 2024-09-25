using Microsoft.Data.SqlClient;
using Models;
using System;
using Microsoft.Data.SqlClient;
using System.Collections.Generic;
using System.Data;
using System.Xml.Linq;
using static Microsoft.EntityFrameworkCore.DbLoggerCategory;
using System.Collections;

namespace WebApplication1.Services
{
    public class WorkQueueItemService : IWorkQueueItemService
    {
        private readonly ISQLService _sqlConnection;
        List<WorkQueueItemModel> workQueueItemList = new List<WorkQueueItemModel>();
        private SqlDataReader? dr;
        //List<UserViewModel> userModel = new List<UserViewModel>();
        //private readonly IUserService _userService;

        public WorkQueueItemService(ISQLService sqlConnection) //IUserService userService)
        {
            _sqlConnection = sqlConnection;
            //_userService = userService;
        }
        public List<WorkQueueItemModel> FetchAll()
        {
            //string query = "select top(1000) * from dbo.BPAWorkQueueItem wqi inner join dbo.BPAWorkQueueItemTag wqit on wqi.ident = wqit.queueitemident inner join dbo.BPATag t on wqit.tagid = t.id inner join dbo.BPAWorkQueue wq on wq.id = wqi.queueid order by lastupdated desc";
            string query = "select top(1000) * from dbo.BPAWorkQueueItem wqi inner join dbo.BPAWorkQueue wq on wq.id = wqi.queueid order by lastupdated desc";
            dr = _sqlConnection.ExecuteCommand(query, null);
            workQueueItemList = setData(dr, false);

            return workQueueItemList;
        }
        public List<WorkQueueItemModel> GetQueueByQueueId(string queueId)
        {
            // string query = $"select top(1000) * from dbo.BPAWorkQueueItem wqi inner join dbo.BPAWorkQueueItemTag wqit on wqi.ident = wqit.queueitemident inner join dbo.BPATag t on wqit.tagid = t.id inner join dbo.BPAWorkQueue wq on wq.id = wqi.queueid where wqi.queueid = @queueId order by lastupdated desc";
            string query = $"select top(1000) * from dbo.BPAWorkQueueItem wqi inner join dbo.BPAWorkQueue wq on wq.id = wqi.queueid where wqi.queueid = @queueId order by lastupdated desc";
            
            SqlCommand com = _sqlConnection.GetCommand();
            com.CommandType = CommandType.Text;
            com.Parameters.Add("@queueId", SqlDbType.VarChar).Value = queueId;
            dr = _sqlConnection.ExecuteCommand(query, com);

            workQueueItemList = setData(dr, false);

            return workQueueItemList;
        }
        public List<WorkQueueItemModel> GetTags(string keyValue)
        {
            string query = "select top(1000) * from dbo.BPAWorkQueueItem wqi inner join dbo.BPAWorkQueueItemTag wqit on wqi.ident = wqit.queueitemident inner join dbo.BPATag t on wqit.tagid = t.id inner join dbo.BPAWorkQueue wq on wq.id = wqi.queueid where wqi.keyvalue = @keyValue order by lastupdated desc";
            SqlCommand com = _sqlConnection.GetCommand();
            com.CommandType = CommandType.Text;
            com.Parameters.Add("@keyValue", SqlDbType.VarChar).Value = keyValue;
            dr = _sqlConnection.ExecuteCommand(query, com);

            workQueueItemList = setData(dr, true);
            return workQueueItemList;
        }
        public void DeleteQueueItem(string queueItemId)
        {
            string query = "Delete from dbo.BPAWorkQueueItem where id = @queueItemId";
            SqlCommand com = _sqlConnection.GetCommand();
            com.CommandType = CommandType.Text;
            com.Parameters.Add("@queueItemId", SqlDbType.VarChar).Value = queueItemId;
            dr = _sqlConnection.ExecuteCommand(query, com);
        }
        public void retryItem(string queueItemId)
        {
			string query = "update f set f.status = NULL, f.exception = NULL, f.exceptionreason = NULL from dbo.BPAWorkQueueItem f where f.queueid = @queueItemId";
			SqlCommand com = _sqlConnection.GetCommand();
			com.CommandType = CommandType.Text;
			com.Parameters.Add("@queueItemId", SqlDbType.VarChar).Value = queueItemId;
			dr = _sqlConnection.ExecuteCommand(query, com);
		}
        private static string PrettyPrintWithoutBrackets(XElement element, int indentLevel = 0)
        {
            string indent = new string(' ', indentLevel * 4);
            string result = "";

            // Process child elements
            foreach (var child in element.Elements())
            {
                if (child.Name == "row")
                {
                    result += $"{indent}{child.Name}:\n";
                    result += PrettyPrintRow(child, indentLevel + 1);
                }
                else
                {
                    // Skip over collection or any other tags directly
                    continue;
                }
            }

            return result;
        }

        private static string PrettyPrintRow(XElement row, int indentLevel)
        {
            string indent = new string(' ', indentLevel * 4);
            string result = "";

            foreach (var field in row.Elements("field"))
            {
                string name = field.Attribute("name")?.Value;
                string value = field.Attribute("value")?.Value;

                result += $"{indent}    {name}: {value}\n";
            }

            return result;
        }
        private List<WorkQueueItemModel> setData(SqlDataReader dr, bool runTag = false)
        {
            workQueueItemList.Clear();
            while (dr.Read())
            {
                XDocument xDocument = XDocument.Parse(dr["data"]?.ToString() ?? "");
                //string xmlData = xDocument.ToString();
                string xmlData = PrettyPrintWithoutBrackets(xDocument.Root);
                if (runTag)
                {
                    workQueueItemList.Add(new WorkQueueItemModel()
                    {
                        id = dr["id"].ToString(),
                        queueid = dr["queueid"].ToString(),
                        name = dr["name"].ToString(),
                        keyvalue = dr["keyvalue"]?.ToString() ?? "",
                        status = dr["status"]?.ToString() ?? "",
                        attempt = dr["attempt"] == DBNull.Value ? 0 : (int)dr["attempt"],
                        loaded = DateTime.TryParse(dr["loaded"]?.ToString(), out DateTime loaded) ? (DateTime?)loaded : null,
                        completed = DateTime.TryParse(dr["completed"]?.ToString(), out DateTime completed) ? (DateTime?)completed : null,
                        exception = DateTime.TryParse(dr["exception"]?.ToString(), out DateTime exception) ? (DateTime?)exception : null,
                        deferred = DateTime.TryParse(dr["deferred"]?.ToString(), out DateTime deferred) ? (DateTime?)deferred : null,
                        finished = DateTime.TryParse(dr["finished"]?.ToString(), out DateTime finished) ? (DateTime?)finished : null,
                        exceptionreason = dr["exceptionreason"]?.ToString() ?? "",
                        data = xmlData,
                        worktime = dr["worktime"] == DBNull.Value ? 0 : (int)dr["worktime"],
                        queueident = dr["queueident"] == DBNull.Value ? 0 : (int)dr["queueident"],
                        ident = dr["ident"] == DBNull.Value ? 0 : (long)dr["ident"],
                        sessionid = dr["sessionid"]?.ToString() ?? "",
                        priority = dr["priority"] == DBNull.Value ? 0 : (int)dr["priority"],
                        prevworktime = dr["prevworktime"] == DBNull.Value ? 0 : (int)dr["prevworktime"],
                        attemptworktime = dr["attemptworktime"] == DBNull.Value ? 0 : (int)dr["attemptworktime"],
                        exceptionreasonvarchar = dr["exceptionreasonvarchar"]?.ToString() ?? "",
                        exceptionreasontag = dr["exceptionreasontag"]?.ToString() ?? "",
                        encryptid = dr["encryptid"] == DBNull.Value ? 0 : (int)dr["encryptid"],
                        lastupdated = DateTime.TryParse(dr["lastupdated"]?.ToString(), out DateTime lastupdated) ? (DateTime?)lastupdated : null,
                        locktime = DateTime.TryParse(dr["locktime"]?.ToString(), out DateTime locktime) ? (DateTime?)locktime : null,
                        sla = dr["sla"] == DBNull.Value ? 0 : (long)dr["sla"],
                        sladatetime = DateTime.TryParse(dr["sladatetime"]?.ToString(), out DateTime sladatetime) ? (DateTime?)sladatetime : null,
                        processname = dr["processname"]?.ToString() ?? "",
                        issuggested = dr["issuggested"] == DBNull.Value ? false : (bool)dr["issuggested"],
                        tag = dr["tag"]?.ToString() ?? "",
                    });
                }
                else
                {
                    workQueueItemList.Add(new WorkQueueItemModel()
                    {
                        id = dr["id"].ToString(),
                        queueid = dr["queueid"].ToString(),
                        name = dr["name"].ToString(),
                        keyvalue = dr["keyvalue"]?.ToString() ?? "",
                        status = dr["status"]?.ToString() ?? "",
                        attempt = dr["attempt"] == DBNull.Value ? 0 : (int)dr["attempt"],
                        loaded = DateTime.TryParse(dr["loaded"]?.ToString(), out DateTime loaded) ? (DateTime?)loaded : null,
                        completed = DateTime.TryParse(dr["completed"]?.ToString(), out DateTime completed) ? (DateTime?)completed : null,
                        exception = DateTime.TryParse(dr["exception"]?.ToString(), out DateTime exception) ? (DateTime?)exception : null,
                        deferred = DateTime.TryParse(dr["deferred"]?.ToString(), out DateTime deferred) ? (DateTime?)deferred : null,
                        finished = DateTime.TryParse(dr["finished"]?.ToString(), out DateTime finished) ? (DateTime?)finished : null,
                        exceptionreason = dr["exceptionreason"]?.ToString() ?? "",
                        data = xmlData,
                        worktime = dr["worktime"] == DBNull.Value ? 0 : (int)dr["worktime"],
                        queueident = dr["queueident"] == DBNull.Value ? 0 : (int)dr["queueident"],
                        ident = dr["ident"] == DBNull.Value ? 0 : (long)dr["ident"],
                        sessionid = dr["sessionid"]?.ToString() ?? "",
                        priority = dr["priority"] == DBNull.Value ? 0 : (int)dr["priority"],
                        prevworktime = dr["prevworktime"] == DBNull.Value ? 0 : (int)dr["prevworktime"],
                        attemptworktime = dr["attemptworktime"] == DBNull.Value ? 0 : (int)dr["attemptworktime"],
                        exceptionreasonvarchar = dr["exceptionreasonvarchar"]?.ToString() ?? "",
                        exceptionreasontag = dr["exceptionreasontag"]?.ToString() ?? "",
                        encryptid = dr["encryptid"] == DBNull.Value ? 0 : (int)dr["encryptid"],
                        lastupdated = DateTime.TryParse(dr["lastupdated"]?.ToString(), out DateTime lastupdated) ? (DateTime?)lastupdated : null,
                        locktime = DateTime.TryParse(dr["locktime"]?.ToString(), out DateTime locktime) ? (DateTime?)locktime : null,
                        sla = dr["sla"] == DBNull.Value ? 0 : (long)dr["sla"],
                        sladatetime = DateTime.TryParse(dr["sladatetime"]?.ToString(), out DateTime sladatetime) ? (DateTime?)sladatetime : null,
                        processname = dr["processname"]?.ToString() ?? "",
                        issuggested = dr["issuggested"] == DBNull.Value ? false : (bool)dr["issuggested"],
                        //tag = dr["tag"]?.ToString() ?? "",
                    });
                }
            }
            _sqlConnection.Close();
            return workQueueItemList;
        }
    }
}