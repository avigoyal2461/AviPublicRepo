using Microsoft.AspNetCore.Mvc;
using Models;
using System.Collections.Generic;
using System.Reflection.Metadata.Ecma335;
using System.Diagnostics;
using Microsoft.AspNetCore.Authorization;
using WebApplication1.Models;
using Microsoft.Extensions.Logging;
//using WebApplication1.Models;
using WebApplication1.Services;
// For more information on enabling Web API for empty projects, visit https://go.microsoft.com/fwlink/?LinkID=397860

namespace WebApplication1.Controllers
{
    [Route("[controller]")]
    public class ResourceController : Controller
    {
        List<ResourceModel>? resourcelist = new List<ResourceModel>();
        //ResourceModel resource = new ResourceModel();
        private readonly IResourceService _resourceService;

        public ResourceController(IResourceService resourceService)
        {
            _resourceService = resourceService;
        }

        [HttpGet("Resource")]
        public ActionResult Index()
        {
            resourcelist = _resourceService.FetchData();
            return View(resourcelist);
        }

        // GET api/<ResourceController>/5
        [HttpGet("{id}")]
        public IActionResult GetResourceById(string id)
        {
            if (id == null)
            {
                return BadRequest();
            }
            resourcelist = _resourceService?.GetResource(id);
            if (resourcelist == null)
            {
                return NotFound();
            }

            return Ok(resourcelist);
        }

        // POST api/<ResourceController>

        [HttpPost]
        public void Post([FromBody] string value)
        {
        }


        // PUT api/<ResourceController>/5
        [HttpPut("{id}")]
        public void Put(int id, [FromBody] string value)
        {
        }

        // DELETE api/<ResourceController>/5
        [HttpDelete("{id}")]
        public void Delete(int id)
        {
        }
    }
}
