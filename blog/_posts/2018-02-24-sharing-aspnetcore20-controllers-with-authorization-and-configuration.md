---
title: Sharing ASP.NET Core 2.0 controllers with authorization and configuration
layout: post
---

With ASP.NET Core 2.0 it's easy to publish APIs as libraries and include them in your other projects. This is helpful because it allows you to build end-to-end functionality (e.g. content management) that you can share among different website projects.

This post will walk through a short example of how to build an ASP.NET Core 2.0 controller library which uses ASP.NET Core 2.0 configuration and authorization features. [The code for this post is available on GitHub here](https://github.com/bighuggies/ControllerLibrarySample).


## Contents

* [The example solution structure](#the-example-solution-structure)
* [Using controllers from a class library](#using-controllers-from-a-class-library)
* [Providing services to library controllers](#providing-services-to-library-controllers)
* [Configuring options for the controller library](#configuring-options-for-the-controller-library)
* [Adding authorization to library controllers using policies](#adding-authorization-to-library-controllers-using-policies)

## The example solution structure

To demonstrate how to do this we will create a solution with two projects:

1. An ASP.NET Core 2.0 web project (`ControllerLibrarySample.Web`)
2. A .NET Standard 2.0 class library project (`ControllerLibrarySample.Library`)

![Screenshot of solution structure with two projects](/assets/images/aspnetcoresharingcontrollers/solution_structure.PNG)

For simplicity, the controller class library and web project are in the same solution. In reality, you might publish the library as a nuget package in order to share it among your projects.


## Using controllers from a class library

### Creating the controller

First, we need to create a controller that we want to share in the class library. I'm going to use a simple version of the `ValuesController` that Visual Studio generated in the website project called `OtherValuesController`:

{% highlight csharp %}
using System.Collections.Generic;
using Microsoft.AspNetCore.Mvc;

namespace ControllerLibrarySample.Library.Controllers
{
    [Route("api/[controller]")]
    public class OtherValuesController : Controller
    {
        // GET api/othervalues
        [HttpGet]
        public IEnumerable<string> Get()
        {
            return new string[] { "value1", "value2" };
        }
    }
}
{% endhighlight %}

Notice we are using MVC. For this to build, the library project will need to reference the `Microsoft.AspNetCore.Mvc` package via nuget.

![Nuget reference from the class library project to Microsoft.AspNetCore.Mvc](/assets/images/aspnetcoresharingcontrollers/add_mvc_nuget_reference.PNG)

### Using the controller

For the web project to see and use controllers which are in our class library, we only need to reference the class library project:

![Project reference from the web project to the class library project](/assets/images/aspnetcoresharingcontrollers/add_project_reference.PNG)

In previous versions of ASP.NET you had to write some plumbing code for MVC to see controllers in referenced assemblies. In ASP.NET Core 2.0, it's automatic. For more information on how this works, you can refer to the [documentation on Application Parts](https://docs.microsoft.com/en-us/aspnet/core/mvc/advanced/app-parts).

Now, if we run the Web project and visit `/api/othervalues` we can see that our library controller is working and available:

![Other values controller result of get request](/assets/images/aspnetcoresharingcontrollers/othervalues_controller_working.PNG)

## Providing services to library controllers

We can use controllers from our class library in our web project, but what about services? It's quite likely that our controllers will use constructor injection to retrieve services from the DI container. We could register the services for our library inside of `Startup.cs`, but that's not very reusable since any consumer of the library would have to know about all of the dependencies which our controllers use.

Instead, the class library should encapsulate knowledge of which services are required. To do this, we can create an extension method on `IServiceCollection` in the class library:

{% highlight csharp %}
using Microsoft.Extensions.DependencyInjection;

namespace ControllerLibrarySample.Library
{
    public static class ServiceCollectionExtensions
    {
        public static void AddSampleLibrary(
          this IServiceCollection services
        )
        {
            services.AddTransient<IExampleService, ExampleService>();
        }
    }
}
{% endhighlight %}

And change our `ConfigureServices` method:

{% highlight csharp %}
public void ConfigureServices(IServiceCollection services)
{
  services.AddMvc();
  services.AddSampleLibrary();
}
{% endhighlight %}

Now our library controllers can request services in their constructors and MVC can provide them from its DI container:

{% highlight csharp %}
public class OtherValuesController : Controller
{
    private readonly IExampleService _service;

    public OtherValuesController(IExampleService service)
    {
        _service = service;
    }

    // GET api/othervalues
    [HttpGet]
    public IEnumerable<string> Get()
    {
        return _service.Values();
    }
}
{% endhighlight %}


## Configuring options for the controller library

What if our controllers require some configuration options? ASP.NET Core 2.0 has a lot of nice [ways to provide configuration values](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/configuration/index?tabs=basicconfiguration), but our library shouldn't force consumers to use a particular method.

To abstract our library from the configuration method we need to build two pieces. First, our class library needs to define the options it provides and call `services.Configure<>()` to register these with ASP.NET Core 2.0. Secondly, we need to provide a way for the consumer to pass configuration values to the controller library.

### Creating options used by the library controllers

We can define what options our library exposes by creating a POCO in the library project. We'll add an exciting new option, `Option1`, with the default value of `"default"`:

{% highlight csharp %}
namespace ControllerLibrarySample.Library
{
    public class ExampleOptions
    {
        public string Option1 { get; set; } = "default";
    }
}
{% endhighlight %}

Now, we can use our options in our controller by injecting an `IOptions<ExampleOptions>` in the constructor:

{% highlight csharp %}
[Route("api/[controller]")]
public class OtherValuesController : Controller
{
    private readonly IExampleService _service;
    private readonly ExampleOptions _options;

    public OtherValuesController(
      IExampleService service,
      IOptions<ExampleOptions> options
    )
    {
        _service = service;
        _options = options.Value;
    }

    [HttpGet("option1")]
    public string GetOption1()
    {
        return _options.Option1;
    }

    ...
}
{% endhighlight %}

### Passing options to the controller library

Next we need to build a way for the consumer to provide values for the configuration options of our library.

To do this, we can add a parameter to our configuration extension method which allows the consumer to provide a setup callback which is passed an instance of our options POCO. The consumer can modify this instance to configure the values of `ExampleOptions`:

{% highlight csharp %}
public static class ServiceCollectionExtensions
{
    public static void AddSampleLibrary(
      this IServiceCollection services,
      Action<ExampleOptions> setupAction = null
    )
    {
        services.Configure<ExampleOptions>(
            options => setupAction?.Invoke(options)
        );

        services.AddTransient<IExampleService, ExampleService>();
    }
}
{% endhighlight %}

Now, our consumer can provide the configuration values inside of `Startup.cs`:

{% highlight csharp %}
public void ConfigureServices(IServiceCollection services)
{
    services.AddMvc();

    services.AddSampleLibrary(
        options => Configuration.GetSection("SampleLibrary").Bind(options)
    );
}
{% endhighlight %}

In this example we bind the library options directly to the configuration section "SampleLibrary" inside of `appsettings.json`:

{% highlight json %}
{
  "SampleLibrary": {
    "option1":  "hello world"
  }
}
{% endhighlight %}

Now we have a nice and flexible method of configuring our controller library which lets consumers provide option values using any configuration method they care to use.


## Adding authorization to library controllers using policies

Sometimes you may need to restrict access to certain actions or controllers based on some authorization rules. With ASP.NET Core 2.0, we can use [policies](https://docs.microsoft.com/en-us/aspnet/core/security/authorization/policies) to abstract the required authorization level from how the authorization is actually performed.

For example, let's add a restricted method to the `OtherValuesController`:

{% highlight csharp %}
[HttpGet("secretothervalues")]
[Authorize(Policy = "AdminsOnly")]
public IEnumerable<string> GetSecretValues()
{
    return new[] { "hello world" };
}
{% endhighlight %}

Now when we try to run our web project, we get the following exception:

![The AuthorizationPolicy named: 'AdminsOnly' was not found](/assets/images/aspnetcoresharingcontrollers/policy_exception.PNG)

Inside our `Startup.cs` we can now configure our policy based on some requirement. We could require a specific claim or role, or even some other custom business logic. This could look something like the following (incomplete example, full auth configuration is out of scope of this post):

{% highlight csharp %}
services.AddAuthorization(options =>
{
    options.AddPolicy("AdminsOnly", policy =>
        policy.RequireClaim("admin"));
});
{% endhighlight %}

This is beneficial to us since consumers of our library can now define how they enforce restrictions to particular API methods we have defined, without the library having to know how that particular site performs authorization. This makes the library much more reusable.

## Conclusion

Hopefully this example has demonstrated how ASP.NET Core 2.0 lets us build nicely abstracted controller libraries which use the configuration and authorization features of the framework.

If you know of something I missed or want to ask questions/provide feedback, please open an issue on the [repository which accompanies this example](https://github.com/bighuggies/ControllerLibrarySample).
