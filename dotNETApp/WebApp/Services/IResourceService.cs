using Models;
using System.Collections.Generic;
using WebApplication1.Models;

namespace WebApplication1.Services
{
    public interface IResourceService
    {
        List<ResourceModel> FetchData();
        List<ResourceModel>? GetResource(string resourceid);
    }
}
