import yaml
import os
import sys
import gnupg
import ConfigParser
from constants import *
import logging
logger = logging.getLogger(__name__)


class Config(object):
    def __init__(self):
        location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        config_file = os.path.join(location, CONFIG_FILE)

        self.favoritos_file = os.path.join(location, FAVORITOS_FILE)
        self.products_file = os.path.join(location, ACCOUNTS_FILE)
        self.config = ConfigParser.RawConfigParser()
        try:
            self.config.read(config_file)
        except ConfigParser.MissingSectionHeaderError as ex:
            logger.error("Error leyendo fichero de configuracion (%s): %s", config_file, ex)
            sys.exit(1)

    def write_products(self, products):
        accounts = filter(lambda x: x["type"] == CUENTA_CORRIENTE or x["type"] == CUENTA_NARANJA, products)
        aliases = map(lambda x: x.get("alias") or x.get("name"), accounts)
        yaml.safe_dump(aliases, file(self.products_file,"w"), encoding='utf-8', allow_unicode=True,
                       default_flow_style=False)

    def write_favoritos(self, favoritos):
        only_favoritos = [v for k,v in favoritos.items() if v.get("category") == "favourite"]
        important_data = map(lambda x: {
            "productNumber": x.get("productNumber"),
            "bank": x.get("bank"),
            "iban": x.get("iban"),
            "beneficiary": x.get("beneficiary")
        }, only_favoritos)
        yaml.safe_dump(important_data, file(self.favoritos_file,"w"), encoding='utf-8', allow_unicode=True,
                       default_flow_style=False)
        #with open(self.favoritos_file, "w") as fd:
        #    for k,v in favoritos.iteritems():
        #        if v.get("category") == "favourite":
        #           fd.write("%s # %s\n" % (v.get("beneficiary").encode("utf-8"), v.get("bank").encode("utf-8")))

    def get_dni(self):
        try:
            return self.config.get(CONFIG_SECTION, DNI)
        except ConfigParser.NoSectionError as ex:
            logger.error("Error obteniendo el DNI del fichero de configuracion: %s", ex)
            sys.exit(1)

    def get_pass(self):
        try:
            return self.config.get(CONFIG_SECTION, PASS)
        except ConfigParser.NoSectionError as ex:
            logger.error("Error obteniendo la password del fichero de configuracion: %s", ex)
            sys.exit(1)

    def get_fecha(self):
        try:
            return self.config.get(CONFIG_SECTION, FECHA)
        except ConfigParser.NoSectionError as ex:
            logger.error("Error obteniendo la fecha de nacimiento del fichero de configuracion: %s", ex)
            sys.exit(1)

    def get_coordenada(self, position):
        try:
            pinentry = self.config.get(CONFIG_SECTION, GPG_PINENTRY)
        except ConfigParser.NoSectionError as ex:
            logger.error("Error obteniendo el programa que se debe usar para el pinentry del fichero de configuracion: %s", ex)
            sys.exit(1)

        os.putenv("PINENTRY_USER_DATA", pinentry)
        gpg = gnupg.GPG(use_agent=True)
        try:
            coord = gpg.decrypt_file(file(self.config.get(CONFIG_SECTION, COORDENADAS), "rb"))
            return [x.split(" ")[1] for x in str(coord).split("\n") if x.split(" ")[0]==str(position)][0]
        except (ConfigParser.NoOptionError, IOError):
            # preguntar coordenada al usuario
            return raw_input("Coordenada de la posicion %s: " % position)


    #def existe_movimiento(self,movimiento):
    #    return self.r.sismember(self.key_movimientos,movimiento)

    #def add_movimiento(self,movimiento):
    #    return self.r.sadd(self.key_movimientos,movimiento)

    #def num_movimientos(self):
    #    return self.r.scard(self.key_movimientos)
