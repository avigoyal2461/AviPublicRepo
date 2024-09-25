using Microsoft.Data.SqlClient;

namespace WebApplication1.Services
{
    public interface ISQLService
    {
        SqlDataReader ExecuteCommand(string query, SqlCommand? com);
        SqlCommand GetCommand();
        SqlConnection SetConnection();
        void Close();
    }
}
