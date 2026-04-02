# Activer l'API SSL (port sécurisé 8729)
/ip service enable api-ssl
/ip service set api-ssl address=VOTRE_IP_VPS disabled=no

# Créer un certificat SSL (si pas déjà fait)
/certificate add name=api-cert common-name=api.mikrotik.local

# Assigner le certificat à l'API SSL
/ip service set api-ssl certificate=api-cert

# Créer un groupe avec permissions CRUD complètes
/user group add name=api_full policy=api,read,write,policy,test

# Créer un utilisateur API avec le groupe
/user add name=api_user group=api_full password=MonPasswordSecurise123

# Vérifier la configuration
/ip service print
/user print
/user group print