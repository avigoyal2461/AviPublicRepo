using Models;
using System.Collections.Generic;

namespace WebApplication1.Models
{
	public class HomeViewModel
	{
		public List<ResourceModel> ResourceList { get; set; }
		public List<WorkQueueModel> WorkQueue { get; set; }
		public List<WorkQueueItemModel> WorkQueueItem { get; set; }
	}
}
