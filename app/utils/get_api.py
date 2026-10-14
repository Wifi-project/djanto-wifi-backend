import httpx
from typing import Any
from enum import Enum

class StatusRequest(str, Enum):
    success = 'success'
    failled = 'failled'



async def post_data(url:str,payload:dict, headers: dict = None, is_data:bool=False):
    if headers is None:
        headers = {"Content-Type":"application/json"}

    async with httpx.AsyncClient() as client:
        try:
            response = None
            if is_data is True:
                response = await client.post(
                    url=url,
                    headers=headers,
                    data=payload,
                    timeout=10.0
                ) 
            else:
                response = await client.post(
                    url=url,
                    headers=headers,
                    json=payload,
                    timeout=10.0
                ) 

            response.raise_for_status()
            message = response.json()

            return {"status": "success", "message": message}
        
        except (httpx.ConnectError, httpx.NetworkError) as e:
            return {"status": "failled", "message":"Problème de connexion au serveur"}

        except httpx.TimeoutException:
            return {"status": "failled", "message":"Timeout"}

        except httpx.HTTPStatusError as e:
            return {"status": "failled", "message":f"Statut invalide: {e.response.status_code} {e}"}

        except Exception as e:
            return {"status": "failled", "message":f"Une erreur inconnue est survenue {e}"}




async def get_data(
    url: str,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: float = 15.0,
) -> dict:
    
    default_headers = {"Content-Type": "application/json"}
    if headers:
        default_headers.update(headers)

    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.get(
                url=url,
                params=params,
                headers=default_headers,
            )
            response.raise_for_status()  
            message = response.json()

            return {"status": "success", "message":message}
        
        except (httpx.ConnectError, httpx.NetworkError) as e:
            return {"status": "failled", "message":"Problème de connexion au serveur"}

        except httpx.TimeoutException:
            return {"status": "failled", "message":"Timeout"}

        except httpx.HTTPStatusError as e:
            return {"status": "failled", "message":f"Statut invalide: {e.response.status_code}"}

        except Exception as e:
            return {"status": "failled", "message":f"Une erreur inconnue est survenue {e}"}


#####################################################################
# LES APPELS SYNCRONE
#####################################################################


def post_data_sync(url: str,payload: dict,headers: dict = None) -> dict:
    if headers is None:
        headers = {"Content-Type": "application/json"}

    with httpx.Client() as client:
        try:
            response = client.post(
                url=url,
                headers=headers,
                json=payload,
                timeout=10.0,
            )
            response.raise_for_status()
            message = response.json()

            return {"status": "success", "message": message}

        except (httpx.ConnectError, httpx.NetworkError):
            return {"status": "failled", "message": "Problème de connexion au serveur"}

        except httpx.TimeoutException:
            return {"status": "failled", "message": "Timeout"}

        except httpx.HTTPStatusError as e:
            return {"status": "failled", "message": f"Statut invalide: {e.response.status_code}"}

        except Exception as e:
            return {"status": "failled", "message": f"Une erreur inconnue est survenue {e}"}


def get_data_sync(url: str,params: dict | None = None,headers: dict | None = None) -> dict:
    default_headers = {"Content-Type": "application/json"}
    if headers:
        default_headers.update(headers)

    with httpx.Client() as client:
        try:
            response = client.get(
                url=url,
                params=params,
                headers=default_headers,
                timeout=10.0
            )
            response.raise_for_status()
            message = response.json()

            return {"status": "success", "message": message}

        except (httpx.ConnectError, httpx.NetworkError):
            return {"status": "failled", "message": "Problème de connexion au serveur"}

        except httpx.TimeoutException:
            return {"status": "failled", "message": "Timeout"}

        except httpx.HTTPStatusError as e:
            return {"status": "failled", "message": f"Statut invalide: {e.response.status_code}"}

        except Exception as e:
            return {"status": "failled", "message": f"Une erreur inconnue est survenue {e}"}