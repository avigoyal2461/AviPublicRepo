using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Authentication.OpenIdConnect;
using Microsoft.AspNetCore.Mvc.Authorization;
using Microsoft.Identity.Web;
using Microsoft.Identity.Web.UI;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.EntityFrameworkCore;
using WebApplication1.Services;
using Microsoft.Extensions.Configuration;

var builder = WebApplication.CreateBuilder(args);
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
// Add services to the container.
builder.Services.AddAuthentication(OpenIdConnectDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApp(builder.Configuration.GetSection("AzureAd"));

builder.Services.AddControllersWithViews(options =>
{
    var policy = new AuthorizationPolicyBuilder()
        .RequireAuthenticatedUser()
        .Build();
    options.Filters.Add(new AuthorizeFilter(policy));
});

builder.Services.AddScoped<ISQLService, SQLService>(provider =>
{
    return new SQLService(connectionString);
});
builder.Services.AddDbContext<ApplicationDbContext>(options => options.UseSqlServer(connectionString));

builder.Services.AddScoped<IUserService>(provider =>
{
    var sqlService = provider.GetRequiredService<ISQLService>();
    return new UserService(sqlService);
});
builder.Services.AddScoped<IResourceService>(provider =>
{
    var sqlService = provider.GetRequiredService<ISQLService>(); //Temp to test, decide whether i want to use this or the DB context
    var dbContext = provider.GetRequiredService<ApplicationDbContext>();
    return new ResourceService(sqlService, dbContext);
});
builder.Services.AddScoped<IWorkQueueItemService>(provider =>
{
    var sqlService = provider.GetRequiredService<ISQLService>();
    //var userService = provider.GetRequiredService<IUserService>();
    return new WorkQueueItemService(sqlService);
});
builder.Services.AddScoped<IWorkQueueService>(provider =>
{
	var sqlService = provider.GetRequiredService<ISQLService>();
	//var workQueueItem = provider.GetRequiredService<IWorkQueueItemService>(); //TODO load into service
    return new WorkQueueService(sqlService);
});

builder.Services.AddScoped<IResourceService, ResourceService>();

builder.Services.AddRazorPages()
    .AddMicrosoftIdentityUI();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseStaticFiles();

app.UseRouting();

app.UseAuthorization();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");
app.MapRazorPages();

app.Run();
