using Microsoft.AspNetCore.Mvc;
using Models;
using System.Collections.Generic;
using System.ComponentModel.Design;
using WebApplication1.Services;

namespace WebApplication1.Controllers
{
    [Route("[controller]")]
    public class WorkQueueController : Controller
    {
        List<WorkQueueModel>? workqueueList = new List<WorkQueueModel>();
        private readonly IWorkQueueService _workQueueService;

        public WorkQueueController(IWorkQueueService workQueueService)
        {
            _workQueueService = workQueueService;
        }
        [HttpGet("WorkQueue")]
        public IActionResult Index()
        {
            workqueueList = _workQueueService.GetAllQueues();
            return View(workqueueList);
        }
    }
}
