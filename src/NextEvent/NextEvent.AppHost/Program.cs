using Azure.Provisioning.Storage;
using Azure.Storage.Blobs;
using Microsoft.Extensions.Hosting;

var builder = DistributedApplication.CreateBuilder(args);

//var blobs = builder.AddConnectionString("BlobConnection");

var storage = builder.AddAzureStorage("storage")
    .ConfigureInfrastructure(infra =>
    {
        var storageAccount = infra.GetProvisionableResources()
                                .OfType<StorageAccount>()
                                .Single();      
        storageAccount.AllowBlobPublicAccess = true;
        storageAccount.AllowSharedKeyAccess = true;
        storageAccount.Sku = new StorageSku { Name = StorageSkuName.StandardLrs };                      
    });
var blobs = storage.AddBlobs("BlobConnection");

var web = builder.AddProject<Projects.NextEvent_web>("web")
                    .WithExternalHttpEndpoints()
                    .WithReference(blobs);

builder.Build().Run();
