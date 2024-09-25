using System.Diagnostics;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using WebApplication1.Models;
using Microsoft.Extensions.Logging;
using Models;
using System.Collections.Generic;
//using System.ComponentModel.Design;
using WebApplication1.Services;

namespace WebApplication1.Controllers;

[Authorize]
public class HomeController : Controller
{
    private readonly ILogger<HomeController> _logger;
	List<ResourceModel> resourceModel = new List<ResourceModel>();
	List<WorkQueueModel> workQueueModel = new List<WorkQueueModel>();
	List<WorkQueueItemModel> workQueueItemModel = new List<WorkQueueItemModel>();
	List<UserViewModel> userModel = new List<UserViewModel>();
    private readonly IResourceService _resourceService;

	public HomeController(ILogger<HomeController> logger, IResourceService resourceService)
    {
        _resourceService = resourceService;
        _logger = logger;
    }

    public IActionResult Index()
    {
        return View();
    }

    public IActionResult Privacy()
    {
        return View();
    }

    [AllowAnonymous]
    [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
    public IActionResult Error()
    {
        return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
    }
}
