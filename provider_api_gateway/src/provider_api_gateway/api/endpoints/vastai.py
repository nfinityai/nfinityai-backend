# from typing import Optional
# from fastapi import APIRouter, Depends, HTTPException, Response
# from provider_api_gateway.schemas.vastai import offers, instances
# from provider_api_gateway.providers.vastai import get_vastai_client, VastAiClient
# from typing_extensions import Annotated
# from fastapi import Query
# from pydantic import BaseModel, Field
# from enum import Enum

# router = APIRouter()


# class ListAvailableInstancesQuery(BaseModel):
#     gpu_name: Optional[str] = Query(None, description="GPU name")


#     def get_item_query_dict(self) -> offers.ItemQuery:
#         fields = [offers.ItemField(
#             field=field,
#             value=getattr(self, field)
#         ) for field in self.model_fields_set if getattr(self, field) is not None]

#         return offers.ItemQuery(
#             no_default=False,
#             fields=fields
#         ).model_dump(exclude_none=True)
    
# class CreateInstanceLaunchRunType(str, Enum):
#     SSH = "ssh"
#     JUPYTER = "jupyter"

# class CreateInstanceQuery(BaseModel):
#     ID: int = Field(..., description='id of instance type to launch (returned from search offers)')
#     disk: float = Field(10, description='size of local disk partition in GB')
#     image: Optional[str] = Field("pytorch/pytorch:latest", description='docker container image to launch')
#     login: Optional[str] = Field(None, description="docker login arguments for private repo authentication, surround with ''")
#     run_type: CreateInstanceLaunchRunType = Field(CreateInstanceLaunchRunType.SSH, description='Launch as an ssh instance type.')
#     env: Optional[str] = Field(None, description="env variables and port mapping options, surround with ''")


#     def get_launch_options(self) -> instances.LaunchOptions:

#         return instances.LaunchOptions(
#             ID=self.ID,
#             disk=self.disk,
#             image=self.image,
#             login=self.login,
#             ssh=True if self.run_type == CreateInstanceLaunchRunType.SSH else False,
#             jupyter=True if self.run_type == CreateInstanceLaunchRunType.JUPYTER else False,
#             env=self.env
#         )


# @router.get("/instances")
# async def list_available_instances(
#     query: Annotated[ListAvailableInstancesQuery, Depends()],
#     client: Annotated[VastAiClient, Depends(get_vastai_client)],
# ):
#     query_model = offers.SearchOffersQuery(
#         query=query.get_item_query_dict()
#     )
#     try:
#         df = await client.search_offers(query_model)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
#     return Response(df.to_json(orient='records'), media_type='application/json')


# @router.get("/instances/me")
# async def list_my_instances(
#     client: Annotated[VastAiClient, Depends(get_vastai_client)],
# ):
#     try:
#         df = await client.show_my_instances()
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
#     return Response(df.to_json(orient='records'), media_type='application/json')


# @router.post("/instance")
# async def create_instance(
#     params: CreateInstanceQuery,
#     client: Annotated[VastAiClient, Depends(get_vastai_client)],
# ):
#     try:
#         result = await client.create_instance(params.get_launch_options())
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
#     return {'success': result.success}


# @router.delete("/instance/{instance_id}")
# async def delete_instance(
#     instance_id: int,
#     client: Annotated[VastAiClient, Depends(get_vastai_client)],
# ):
#     try:
#         result = await client.delete_instance(instance_id)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
#     return {'success': result.success}
