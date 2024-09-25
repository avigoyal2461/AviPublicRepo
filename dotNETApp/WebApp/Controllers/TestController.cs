using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Models;
//using WebApplication1.Models;

namespace WebApplication1.Controllers
{
    [Route("Test")]
    public class TestController : Controller
    {

        private readonly ILogger<HomeController> _logger;

        public TestController(ILogger<HomeController> logger)
        {
            _logger = logger;
        }
        
        public IActionResult Index()
        {
            return View();
        }
        
        [HttpGet("Test")]
        public IActionResult Test()
        {
            return View(new TestViewModel { Message = "Test Message 2" });
        }
        
        [HttpPost("Submit")]
        public IActionResult Submit(DateRangeModel model)
        {
            //return View(new TestViewModel { Message = $"Start: {model.StartTime}, End: {model.EndTime}" });
            var message = $"Start: {model.StartTime.ToString("MM/dd/yyyy")}, End: {model.EndTime.ToString("MM/dd/yyyy")}. Selected process: {model.Process_Name}";
            return View("Test", new TestViewModel { Message = message });
        }
        
    }
}
