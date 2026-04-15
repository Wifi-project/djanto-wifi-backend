import httpx


async def post_data(url:str,payload:dict,token:str = None,api_key:str = None,sms:bool=False):

    header = {"Content-Type":"application/json"}

    if token and sms is False:
        header["Authorization"] = f"Bearer {token}"

    if sms is True and token:
        header["Authorization"] = f"Basic {token}"

    if api_key:
        header["X-API-KEY"] = api_key

    async with httpx.AsyncClient() as client:
        try:

            response = await client.post(
                url=url,
                headers=header,
                json=payload,
                timeout=10.0)

            response.raise_for_status()
            message = response.json()

            return {"status": "success", "message":message}
        
        except (httpx.ConnectError, httpx.NetworkError) as e:
            print(f"Erreur réseau : {e}")
            return {"status": "failled", "message":"Problème de connexion au serveur"}

        except httpx.TimeoutException:
            print("La requête a expiré")
            return {"status": "failled", "message":"Timeout"}

        except httpx.HTTPStatusError as e:
            return {"status": "failled", "message":f"Statut invalide: {e.response.status_code}"}

        except Exception as e:
            return {"status": "failled", "message":f"Une erreur inconnue est survenue {e}"}
