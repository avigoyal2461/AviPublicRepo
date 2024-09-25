using Microsoft.AspNetCore.Mvc;
using Models;
using System;
using System.Collections.Generic;
using System.ComponentModel.Design;
using WebApplication1.Services;

namespace WebApplication1.Controllers
{
    [Route("[controller]")]
    public class WorkQueueItemController : Controller
    {
        List<WorkQueueItemModel>? workqueueItemList = new List<WorkQueueItemModel>();
        private readonly IWorkQueueItemService _workQueueItemService;
        private readonly IUserService _userService;
        List<string> adminUsers = new List<string>();

        public WorkQueueItemController(IWorkQueueItemService workQueueItemService, IUserService userService)
        {
            _workQueueItemService = workQueueItemService;
            _userService = userService;
	    adminUsers = _userService.GetAdminUsers();
	}
	[HttpGet("WorkQueueItems")]
        public IActionResult Index()
        {
            workqueueItemList = _workQueueItemService.FetchAll();
            return View(workqueueItemList);
        }
        [HttpGet("Post")]
        public IActionResult Post(Guid id)
        {
            workqueueItemList = _workQueueItemService.GetQueueByQueueId(id.ToString());
            Console.WriteLine("Pasting queue id");
            Console.WriteLine(id);
            //adminUsers = _userService.GetAdminUsers();
            var model = Tuple.Create(workqueueItemList, adminUsers);
            return View("Index", model);
        }
        [HttpGet("Tags")]
        public IActionResult Tags(string id)
        {
            workqueueItemList = _workQueueItemService.GetTags(id);
            return View(workqueueItemList);
        }
        [HttpGet("Delete")]
        public IActionResult Delete(string id, Guid queueId)
        {
			//add check for User.Identity.Name
            if (adminUsers.Contains(User.Identity.Name.ToLower()))
            {
				_workQueueItemService.DeleteQueueItem(id);
			}
            return Post(queueId);
        }
        [HttpGet("Retry")]
        public IActionResult Retry(string id, Guid queueId)
        {
			//add check for User.Identity.Name
			if (adminUsers.Contains(User.Identity.Name.ToLower()))
			{
				_workQueueItemService.retryItem(id);
			}
			return Post(queueId);
        }
    }
}
