using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using WebApplication1.Models;

//using System.Web.Http;
using WebApplication1.Services;

namespace WebApplication1.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class UserAPIController : ControllerBase
    {
        private readonly IUserService _userService;
        private readonly ILogger<UserController> _logger;
        //private readonly List<UserViewModel> userlist = new List<UserViewModel>();

        public UserAPIController(ILogger<UserController> logger, IUserService userService)
        {
            _userService = userService;
            _logger = logger;
        }
        [HttpGet]
        public IActionResult Get()
        {
            return Ok(_userService.GetUsers());
        }
        [HttpGet("{Username}")]
        public IActionResult Get(string Username)
        {
            if (Username == null) 
            {
                return BadRequest();
            }

            foreach (var user in _userService.GetUsers())
            {
                if (user.username?.ToLower() == Username.ToLower())
                {
                    return Ok(user);
                }
            }
            return NotFound();
        }
    }
}
