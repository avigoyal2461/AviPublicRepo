using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Logging;
using Models;
using Newtonsoft.Json.Linq;
using System.Collections.Generic;

//using System.Net;
//using System.Net.Http;
//using System.Net.Http.Headers;
using System.Text;

//using System.Net.Http;
//using System.Web.Http;
using WebApplication1.Models;
using WebApplication1.Services;

namespace WebApplication1.Controllers
{
    [Route("User")]
    public class UserController : Controller
    {
        List<UserViewModel> userlist = new List<UserViewModel>();
        private readonly IUserService _userService;
        private readonly ILogger<UserController> _logger;

        public UserController(ILogger<UserController> logger, IUserService userService)
        {
            _logger = logger;
            _userService = userService;
        }
        // GET: ProcessTableController
        [HttpGet("User")]
        public ActionResult Index()
        {
            //var users = _context.BPAUsers.ToList();
            userlist = _userService.FetchData();
            return View(userlist);
        }

        // GET: ProcessTableController/Details/5
        [HttpGet("Details")]
        public ActionResult Details(int id)
        {
            return View();
        }

        // GET: ProcessTableController/Create
        [HttpGet("Create")]

        public IActionResult Create()
        {
            return View();
        }

        // POST: ProcessTableController/Create
        [HttpPost]
        [ValidateAntiForgeryToken]
        public ActionResult Create(IFormCollection collection)
        {
            try
            {
                return RedirectToAction(nameof(Index));
            }
            catch
            {
                return View();
            }
        }

        // GET: ProcessTableController/Edit/5
        [HttpGet("Edit")]

        public ActionResult Edit(int id)
        {
            userlist = _userService.FetchData();
            return View(userlist);
        }

        // POST: ProcessTableController/Edit/5
        [HttpPost]
        [ValidateAntiForgeryToken]
        public ActionResult Edit(int id, IFormCollection collection)
        {
            try
            {
                return RedirectToAction(nameof(Index));
            }
            catch
            {
                return View();
            }
        }

        // GET: ProcessTableController/Delete/5
        [HttpGet("Delete")]

        public ActionResult Delete(int id)
        {
            return View();
        }

        // POST: ProcessTableController/Delete/5
        [HttpPost]
        [ValidateAntiForgeryToken]
        public ActionResult Delete(int id, IFormCollection collection)
        {
            try
            {
                return RedirectToAction(nameof(Index));
            }
            catch
            {
                return View();
            }
        }
    }
}
