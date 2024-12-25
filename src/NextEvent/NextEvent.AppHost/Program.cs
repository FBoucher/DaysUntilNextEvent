using Azure.Storage.Blobs;
using Microsoft.Extensions.Hosting;

var builder = DistributedApplication.CreateBuilder(args);

var storage = builder.AddAzureStorage("storage");

// if (builder.Environment.IsDevelopment())
// {
//     storage.RunAsEmulator();
// }

var blobs = storage.AddBlobs("BlobConnection");

var web = builder.AddProject<Projects.NextEvent_web>("web")
                    .WithExternalHttpEndpoints()
                    .WithReference(blobs)
                    .WaitFor(blobs);

builder.Build().Run();
