using Azure.Storage.Blobs;
using Microsoft.Extensions.Hosting;

var builder = DistributedApplication.CreateBuilder(args);

var blobs = builder.AddConnectionString("BlobConnection");

//var storage = builder.AddAzureStorage("storage");
//var blobs = storage.AddBlobs("BlobConnection");

var web = builder.AddProject<Projects.NextEvent_web>("web")
                    .WithExternalHttpEndpoints()
                    .WithReference(blobs);

builder.Build().Run();
