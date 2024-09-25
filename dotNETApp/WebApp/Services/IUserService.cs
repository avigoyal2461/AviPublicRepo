using WebApplication1.Models;
using Microsoft.Data.SqlClient;
using WebApplication1.Controllers;
using System.Collections.Generic;
using Models;

namespace WebApplication1.Services
{
    public interface IUserService
    {
        List<UserViewModel> FetchData();
        List<UserViewModel> GetUsers();
        List<string> GetAdminUsers();
    }
}
