using Models;
using System.Collections.Generic;

namespace WebApplication1.Services
{
    public interface IWorkQueueService
    {
        List<WorkQueueModel> GetAllQueues();
    }
}
