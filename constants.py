# Endpoints
BASE_ENDPOINT       = 'https://ing.ingdirect.es/'
LOGIN_ENDPOINT      = BASE_ENDPOINT + 'genoma_login/rest/session'
POST_AUTH_ENDPOINT  = BASE_ENDPOINT + 'genoma_api/login/auth/response'
CLIENT_ENDPOINT     = BASE_ENDPOINT + 'genoma_api/rest/client'
PRODUCTS_ENDPOINT   = BASE_ENDPOINT + 'genoma_api/rest/products'
TRANSFER_ENDPOINT   = BASE_ENDPOINT + 'genoma_api/rest/transfers'
CARD_ENDPOINT       = BASE_ENDPOINT + 'genoma_api/rest/security/card'
FAVORITOS_ENDPOINT  = BASE_ENDPOINT + 'genoma_api/rest/prepare-movemoney-all?operatives=transfer'

# Relacion entre ids y tipo de producto
TARJETA_DEBITO = 1
TARJETA_CREDITO = 3
CUENTA_CORRIENTE = 17
CUENTA_NARANJA = 20

# config
CONFIG_FILE         = "config.cfg"
CONFIG_SECTION      = "default"
ACCOUNTS_FILE       = "accounts.yml"
FAVORITOS_FILE      = "favoritos.yml"
DNI                 = "dni"
PASS                = "pass"
COORDENADAS         = "coordenadas"
FECHA               = "fecha_nacimiento"
FAVORITOS           = "favourites"
GPG_PINENTRY        = "gpg_pinentry"