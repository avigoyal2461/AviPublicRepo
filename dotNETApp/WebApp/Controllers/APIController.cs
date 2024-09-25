using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System.Diagnostics;
using WebApplication1.Models;

namespace WebApplication1.Controllers
{
    public class APIController : Controller
    {
        private readonly ILogger<HomeController> _logger;

        public APIController(ILogger<HomeController> logger)
        {
            _logger = logger;
        }
    }
}
