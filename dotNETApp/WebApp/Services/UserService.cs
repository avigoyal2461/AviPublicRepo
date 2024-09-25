using Microsoft.Data.SqlClient;
using Models;
using System;
using System.Collections.Generic;
using WebApplication1.Models;

namespace WebApplication1.Services
{
    public class UserService : IUserService
    {
        private readonly ISQLService _sqlConnection;
        //SqlConnection con = new SqlConnection();
        //SqlCommand com = new SqlCommand();
        SqlDataReader? dr;
        //SqlConnection con;
        List<UserViewModel> userlist = new List<UserViewModel>();
        public UserService(ISQLService sqlConnection)
        {
            _sqlConnection = sqlConnection;
        }
        public List<UserViewModel> FetchData()
        {
            if (userlist.Count > 0)
            {
                userlist.Clear();
            }
            try
            {
                string query = "Select userid,username,useremail,validfromdate,loginattempts,upn from dbo.BPAUser";
                dr = _sqlConnection.ExecuteCommand(query, null);

                while (dr.Read())
                {
                    userlist.Add(new UserViewModel()
                    {
                        userid = dr["userid"].ToString(),
                        username = dr["username"].ToString(),
                        validfromdate = DateTime.TryParse(dr["validfromdate"].ToString(), out DateTime validFromDate) ? (DateTime?)validFromDate : null,
                        useremail = dr["useremail"].ToString(),
                        loginattempts = (int)(dr["loginattempts"])
                    });
                }
            }
            catch (Exception)
            {
            }
            _sqlConnection.Close();
            return userlist;
        }
        public List<UserViewModel> GetUsers()
        {
            return FetchData();
        }
        public List<string> GetAdminUsers()
        {
            List<string> _strOut = new List<string>();
            string query = "select u.username from dbo.bpauser u inner join dbo.BPAUserRoleAssignment ura on ura.userid = u.userid inner join dbo.BPAUserRole ur on ur.id = ura.userroleid where ur.id = 1";
            dr = _sqlConnection.ExecuteCommand(query, null);

            while (dr.Read())
            {
                _strOut.Add(dr["username"].ToString().ToLower());
            }
            _sqlConnection.Close();

            return _strOut;
        }
    }
}
