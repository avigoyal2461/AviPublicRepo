using Models;
using System.Collections.Generic;

namespace WebApplication1.Services
{
    public interface IWorkQueueItemService
    {
        List<WorkQueueItemModel> FetchAll();
        List<WorkQueueItemModel> GetQueueByQueueId(string queueId);
        List<WorkQueueItemModel> GetTags(string keyvalue);
        void DeleteQueueItem(string queueItemId);
        void retryItem(string queueItemId);

	}
}
