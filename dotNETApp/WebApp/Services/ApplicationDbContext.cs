using System.Data;
using System.Data.SqlClient;
using Microsoft.Data.SqlClient;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Diagnostics;

namespace WebApplication1.Services
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions options) : base(options)
        {
        }

        protected ApplicationDbContext()
        {
        }
        public void SetConnection(string connectionString)
        {
            Database.GetDbConnection().ConnectionString = connectionString;
        }
        public SqlDataReader ExecuteRawSqlQuery(string sqlQuery)
        {
            var connection = Database.GetDbConnection() as SqlConnection;
            using (var command = connection.CreateCommand())
            {
                command.CommandText = sqlQuery;
                connection.Open();
                return command.ExecuteReader(CommandBehavior.CloseConnection);
            }
        }

    }
}
