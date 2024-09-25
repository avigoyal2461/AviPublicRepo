using Microsoft.Data.SqlClient;
using Models;
using System;
using System.Collections.Generic;
using System.Data;
using WebApplication1.Models;
using static Microsoft.EntityFrameworkCore.DbLoggerCategory;

namespace WebApplication1.Services
{
	public class WorkQueueService : IWorkQueueService
	{
		//private readonly ISQLService _sqlConnection;
		private readonly ISQLService _sqlConnection;
		List<WorkQueueModel> workQueueList = new List<WorkQueueModel>();
		SqlDataReader? dr;

		public WorkQueueService(ISQLService sqlConnection)
		{
			_sqlConnection = sqlConnection;
		}
		public List<WorkQueueModel> GetAllQueues()
		{
			string query = "select * from dbo.BPAWorkQueue wq inner join dbo.BPAWorkQueueItemAggregate qia on qia.queueIdent = wq.ident";
			dr = _sqlConnection.ExecuteCommand(query, null);

			while (dr.Read())
			{
				workQueueList.Add(new WorkQueueModel()
				{
                    id = dr["id"].ToString(),
					name = dr["name"].ToString(),
                    keyfield = dr["keyfield"].ToString(),
					maxattemps = dr["keyfield"] == DBNull.Value ? 0 : (int)dr["maxattempts"],
                    ident = dr["ident"] == DBNull.Value ? 0 : (int)dr["ident"],
                    processid = dr["processid"] == DBNull.Value ? 0 : (int)dr["processid"],
                    resourcegroupid = dr["resourcegroupid"] == DBNull.Value ? 0 : (int)dr["resourcegroupid"],
                    targetsessions = dr["targetsessions"] == DBNull.Value ? 0 : (int)dr["targetsessions"],
                    activelock = dr["activelock"] == DBNull.Value ? 0 : (int)dr["activelock"],
					activelocktime = DateTime.TryParse(dr["activelocktime"]?.ToString(), out DateTime activelocktime) ? (DateTime?)activelocktime : null,
					activelockname = dr["activelockname"].ToString(),
					encryptid = dr["encryptid"] == DBNull.Value ? 0 : (int)dr["encryptid"],
                    sessionexceptionretry = dr["sessionexceptionretry"] == DBNull.Value ? false : (bool)dr["sessionexceptionretry"],
                    pending = dr["pending"] == DBNull.Value ? 0 : (int)dr["pending"],
                    completed = dr["completed"] == DBNull.Value ? 0 : (int)dr["completed"],
                    exceptioned = dr["exceptioned"] == DBNull.Value ? 0 : (int)dr["exceptioned"],
                    deferred = dr["deferred"] == DBNull.Value ? 0 : (int)dr["deferred"],
                    averageworktime = dr["averageworktime"] == DBNull.Value ? 0 : (int)dr["averageworktime"],
                    totalworktime = dr["totalworktime"] == DBNull.Value ? 0 : (int)dr["totalworktime"],
                    total = dr["total"] == DBNull.Value ? 0 : (int)dr["total"],
                    locked = dr["locked"] == DBNull.Value ? 0 : (int)dr["locked"],
					dateUpdated = DateTime.TryParse(dr["averageWorkTime"]?.ToString(), out DateTime dateUpdated) ? (DateTime?)dateUpdated : null,
					//totalCaseDuration = TimeOnly.TryParse(dr["totalCaseDuration"]?.ToString(), out TimeOnly totalCaseDuration) ? (TimeOnly?)totalCaseDuration : null,
				});
			}
			return workQueueList;
		}
	}
}