# import httpx


# async def call_api_post(url:str,payload:dict,token:str = None):

#     header = {"Content-Type":"application/json"}

#     if token:
#         header["Authorization"] = f"Bearer {token}"

    
#     async with httpx.AsyncClient as client:
#         try:
#             response = await client.post()
        
#         except httpx

#         response.raise_for_status() 
    
#     return response.json()
