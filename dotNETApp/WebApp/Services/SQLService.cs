using Microsoft.AspNetCore.SignalR.Protocol;
using Microsoft.Data.SqlClient;
using System;

namespace WebApplication1.Services
{
    public class SQLService : ISQLService
    {
        private readonly string _connectionString;
        private SqlCommand _com = new SqlCommand();
        private SqlDataReader? dr;
        private SqlConnection? con;
        //System.Collections.IEnumerable s
        public SQLService(string connectionString)
        {
            _connectionString = connectionString;
            //con = SetConnection();
        }
        public SqlCommand GetCommand()
        {
            //_com = new SqlCommand();
            return _com;
        }
        public SqlDataReader ExecuteCommand(string query, SqlCommand? com)
        {
            if (com != null)
            {
                _com = com;
            }
            con = SetConnection();
            _com.Connection = con;
            _com.CommandText = query;
            dr = _com.ExecuteReader();

            return dr;
        }

        public SqlConnection SetConnection()
        {
            con = new SqlConnection(_connectionString);
            con.Open();
            return con;
        }
        public void Close()
        {
            con.Close();
        }
    }
}
