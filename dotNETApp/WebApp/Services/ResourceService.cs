using Microsoft.Data.SqlClient;
using Models;
using System;
using System.Collections.Generic;
using System.Threading;
using WebApplication1.Models;

namespace WebApplication1.Services
{
    public class ResourceService : IResourceService
    {
        private readonly ISQLService _sqlConnection;
        private readonly ApplicationDbContext _dbContext;
        List<ResourceModel> resourceList = new List<ResourceModel>();
        SqlDataReader? dr;

		public ResourceService(ISQLService sqlConnection, ApplicationDbContext dbContext)
        {
            _sqlConnection = sqlConnection;
            _dbContext = dbContext;
        }
        public List<ResourceModel> FetchData()
        {
            string query = "select * from dbo.BPAResource where AttributeID = 0";
            //dr = _sqlConnection.ExecuteCommand(query);
            dr = _dbContext.ExecuteRawSqlQuery(query);

            while (dr.Read())
            {
                resourceList.Add(new ResourceModel()
                {
                    resourceid = dr["resourceid"].ToString(),
                    name = dr["name"].ToString(),
                    processesrunning = (int)dr["processesrunning"],
                    actionsrunning = (int)dr["actionsrunning"],
                    unitsallocated = (int)dr["unitsallocated"],
                    DisplayStatus = dr["DisplayStatus"].ToString(),
                    AttributeID = (int)dr["AttributeID"],
                    statusid = (int)dr["statusid"],
					//lastupdated = TimeZoneInfo.ConvertTimeFromUtc(DateTime.TryParse(dr["lastupdated"]?.ToString(), out DateTime lastUpdated) ? (DateTime?)lastUpdated : null, easternZone)
					lastupdated = DateTime.TryParse(dr["lastupdated"]?.ToString(), out DateTime lastUpdated) ? (DateTime?)lastUpdated : null
                });
            }
            return resourceList;
        }
        public List<ResourceModel>? GetResource(string resourceid)
        {
            string query = $"select * from dbo.BPAResource where resourceid = '{resourceid}'";
            dr = _sqlConnection.ExecuteCommand(query, null);

            if (!dr.HasRows)
            {
                return null;
            }
            while (dr.Read())
            {
                try
                {
                    resourceList.Add(new ResourceModel()
                    {
                        resourceid = dr["resourceid"].ToString(),
                        name = dr["name"].ToString(),
                        processesrunning = (int)dr["processesrunning"],
                        actionsrunning = (int)dr["actionsrunning"],
                        unitsallocated = (int)dr["unitsallocated"],
                        AttributeID = (int)dr["AttributeID"],
                        statusid = (int)dr["statusid"],
                        FQDN = dr["FQDN"].ToString(),
                        lastupdated = DateTime.TryParse(dr["lastupdated"]?.ToString(), out DateTime lastUpdated) ? (DateTime?)lastUpdated : null,
                        LastTimeLoggedIn = DateTime.TryParse(dr["LastTimeLoggedIn"].ToString(), out DateTime lastloggedin) ? (DateTime?)lastloggedin : null,
                        pool = dr["pool"].ToString(),
                        controller = dr["controller"].ToString()
                    });
                }
                catch(Exception ex) 
                {
                    Console.WriteLine(ex.Message);
                }   
            }
            _sqlConnection.Close();
            return resourceList;
        }
    }
}
