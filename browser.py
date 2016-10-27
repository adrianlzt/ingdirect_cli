import json
import mechanize
import sys
import logging
import time

import urllib
from constants import *
from excepciones import *
from imagen import *
from datetime import date, timedelta
from termcolor import colored

logger = logging.getLogger(__name__)

class Browser(object):
    def __init__(self, config, login=True):
        WEB_USER_AGENT = 'Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 4 Build/JOP40D) AppleWebKit/535.19 (KHTML, ' \
                         'like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19'

        self.br = mechanize.Browser()
        self.br.set_handle_robots(False)
        self.br.addheaders = [('User-agent', WEB_USER_AGENT)]
        # br.set_proxies({"http": "tcp://0.tcp.ngrok.io:13183", "https": "tcp://0.tcp.ngrok.io:13183"})
        # TODO poner definir un proxy por parametros

        self.products = None
        self.favoritos = None
        self.config = config
        if login:
            self._login()

    def _add_headers(self, header):
        self.br.addheaders = header + self.br.addheaders

    def _convert_headers(self):
        heads = {}
        for h in self.br.addheaders:
            heads[h[0]] = h[1]

        return heads

    def _obtiene_numero_de_imagen(self, imagen):
        if imagen == "iVBORw0KGgoAAAANSUhEUgAAADwAAAA8CAYAAAA6/NlyAAAA80lEQVR42u3XsQ2DMBCFYSZkAA/g3gMwgAdgAHoP4AEYgC0YgB5Hz5IprKSIopBg/pOugO7znXXnLt0sOsCAAQMGDBgwYMCAAQMGDBgwYMCAAX8/9n3PCfgfwSGENAxDzmma0rqu7ba0cy4ZYzJUcGtt/j4TfRo4xpj6vk/Lshz/tm3LYO99e2ChVOE6VG0dRHPgcm+f3WnAgAEDBvxrsMaPZq5mb30QWkCaA2ubUiXHcTzQpbpaSppcLed5zlUWsqTQzT8PtV4q6/bmPXwV8CfvVcC0NOC3ugwwLX3hagKmpQEDBswcBkxLAwYMGDBgwC/iAYRusMooTP73AAAAAElFTkSuQmCC":
            return 0
        if imagen == "iVBORw0KGgoAAAANSUhEUgAAADwAAAA8CAYAAAA6/NlyAAAArklEQVR42u3XwQmFMAwAUCd0ALfoAG7UARyjA3h3AO/Np715/J8viH2B0JJTHySUTDFYTMDAwMDAwMDAwMDAwMDAwMDAwMDAUWvtORz4OI7IOffctu39Lb3ve6zrGsuy9HOYGW5YYGBgYGBgYOBb4zzPKKVESqlnu7faa8ENOM/zJVvNegj8cPCT9t+vwL8+fDiwGQYGBr7r1wDW0sDAwMDAwMDAwH8Ev3HxBx4lPqQ72MOvo8X0AAAAAElFTkSuQmCC":
            return 1
        if imagen == "iVBORw0KGgoAAAANSUhEUgAAADwAAAA8CAYAAAA6/NlyAAABFElEQVR42u3bywmFMBCFYSu0AAtwbwEWYAEpwL0FWIYFuLcA987lBAJ6QXDhi/EfCOLyS84kRDCzl9ayLHGcXRlg5wUYMGDAgAEDBgwYMGDAgAEDBgwY8JvqyIe/W8HzPFvXdVbXdRxt29o0TX7BVVVZURQRKnhZlvH9TPRrIt33veV5buM4blY8TYA7cNM0cYX/K8XbHXgPplhrMtyBFeV1nFXqY8VccXd/LAmv/r0zzo+BtSsLq57WxuUaLKCg6t27sY+A01mc+nkYhtjLLsEhhA12vXG5AyeYnlrVNDQJLsHajQXbG9yWAAMG/Gnw3scAwEQaMGDAgAEDBgwYMGDAgI+Ar/qdBvBF91+3kf4c+Gj9ACFwszHPYVfiAAAAAElFTkSuQmCC":
            return 2
        if imagen == "iVBORw0KGgoAAAANSUhEUgAAADwAAAA8CAYAAAA6/NlyAAABHklEQVR42u3azYmEQBBA4YnQAAzALAzAAAzAuwEYgAGYhQF4t5cnNAwyh2XZ6dmtfgUNc/Sz/lqYR6osHoIF/+84z/M6gi1pwYIFCxYsWLBgwYIFCxYsWLDgn8ayLGkYhtT3fZqmKe37HhcMsGmaNI5jmuc5dV2X2rYtii4GBgUWaI7jOC4wLyIcGChgkM9BaXPCgendVzDKmp4OP6XJNL1M1rdtiw0GCPTe02HBZHdd16uUQfO7mosHfU0fhwOzel6tnzy9w4EpX3bufS0xuEJmmD7Nt6yMztktObiK9jC7mCznCc0pecv66Fri3Mvbz0PBgr8Vz397EPzXHrCKkq4O7NASLFiwYMGCKwe/8/Yj2JIWLPjXwFF6V3At8QUOfbi8RNYGHgAAAABJRU5ErkJggg==":
            return 3
        if imagen == "iVBORw0KGgoAAAANSUhEUgAAADwAAAA8CAYAAAA6/NlyAAAA7klEQVR42u3awQmEMBCFYStMASnALiwgBaQA7xZgARaQAnK3AO+JzECWxduy7K47+QcGRPDwMS+DgkPtrAbAgAEDBgwYMOBPVClFG/CrD5mOdHdglhZgwIABAwYMGPC/gY/jqNM01XVd+wCHEKpzri7LYh+8bZtivff2wRJlgXYz4XmeFSxw8+CUkiIl0lLmweM46mZuZRosMInyvu99gNtWlgm3lnvXqZua8LUFLNhvTvmnr5bdvHjknB8bO8ao16bB7fw+N19LgAEDBgwYMGDAgC2Arf3mAJgzfPN6J4GAiTRgwLc5n4CJNGD7dQIGWLVcNsmv7wAAAABJRU5ErkJggg==":
            return 4
        if imagen == "iVBORw0KGgoAAAANSUhEUgAAADwAAAA8CAYAAAA6/NlyAAAA7ElEQVR42u3ZwQmEMBCFYSu0gBSQuwWkAAuwCwtIARaQArxbQO5mmbAuLrgHFxQz+QcGvH7MYxK1SZVVAxgwYMCAAQMGXBR4XdfcgIk0YMCAnwouZXEBJtKAAQMG/K5xHA9bLbht22StTc65r1YNvnuigO8GD8OQQghpnuc6wPs2xiTvvV7wsiyfZ5lw3/cZPk1TPedw13W5qwHLEpMpqwP/2tBqwRLbo0uG2kjLNt5POcaYjyjVS2uLbzXH0jZZuXhI83p4sv75jgaYDwCAr40cYCIN+DpwSX/6ARNpwIABAwYMGDBgwIABn6kX+cW6dZbwGkoAAAAASUVORK5CYII=":
            return 5
        if imagen == "iVBORw0KGgoAAAANSUhEUgAAADwAAAA8CAYAAAA6/NlyAAABDUlEQVR42u3awQmEMBCFYSu0AAvwngIswAIswLsFWEa6sADvZnmBWdaAxxUy+QcGxNvnJC8odqmx6rzCruvKDZglDRgwYMCAAQMGDBgwYMCAAQMGDBjwc53nmbZtS9M05V7XNR3H4RMsbAghjeOY0WpdD8PwKvo1sIB9399wegi6tyyLP7CWsCZc1r7vuV2C1c2EloE1zXmev6GlZe0WrP2qkBLUfWgZOMZ4Cy2B3YaWJlqWpq0H0Uxo2XHlDmyTLEPq6biqHqxgsv1qaJuuy3NYpcDSPhbSWmj3b0uCq98+g5t5Pfz9/QEwHwAAAwYMGDBgwH8HP/19CpglDRiwW3ANOQDYOxowoQW47voABOCsg8XlTG8AAAAASUVORK5CYII=":
            return 6
        if imagen == "iVBORw0KGgoAAAANSUhEUgAAADwAAAA8CAYAAAA6/NlyAAAA7klEQVR42u3awQmEMBCFYStMARaQuwVYhl2kgBSQAizAuwXkbpYXWJCFPSyyZjfzDwxCLvIxw4wBh2IsBsAX4jiOmnfHJ+8F/Ou4Zi1tDszQAgwYMGDAgC9/jQGmpQEDBgwYMOD+wDHGEkJ4m92B53ku4zjW5zl15pzrE6w8R865gpdlsQFWm6u627b1BxbqFea9L9M02ZjS67rW6qrKJsDPgWViD+/7Xqt75zpqCtZUFljw7sEtVlFTsNpY1dXQMgHWKlKauDyklJqsIm5LgAEDBgwYMGDAgL8J/tc/6wDT0oABAwYMGDBgwIDviQcL3siaH87WMAAAAABJRU5ErkJggg==":
            return 7
        if imagen == "iVBORw0KGgoAAAANSUhEUgAAADwAAAA8CAYAAAA6/NlyAAABKElEQVR42u3awQmDQBCF4VRoARbg3QIswAIswLsFWIAFWIB3C/DuhjewIBIJBLKJs//AHMzJz5kddzGPkFk8AAMGDDgb8L7vloBpacBfi3ddB/jfb9hdS2cHZmgBBgwYMGDAgAF/GsMwhKZpLPu+D9u2+QULWRRF6LrOsGVZWqZEJwNP02RYVTjGuq72m/DuwIIK96rqSnfgcRwNrKoeo6oqa3F3YK3Tuq4thdZ1XMfLsvgcWoIKqErH1Np2OaWPFRZynufQtq3fCsf2Pb+CNLD0ENyBr6bx1fS+PVjtq4l8Dk1oVd4dWGs27rJiW8fqHjcjrqa03sXnKZ1yl/Wz05KqrUx9cOB4mD34jt9/AdPSgAEDBgwYMGDAgDMB88c0WhowYMCAM4on7WCo8wD8C34AAAAASUVORK5CYII=":
            return 8
        if imagen == "iVBORw0KGgoAAAANSUhEUgAAADwAAAA8CAYAAAA6/NlyAAABGUlEQVR42u3ZsQ2DMBCFYSZkAAagZwAGYAAGoGcAxmAAegag56JnyRFCThXFwOU/yUXcfbw7Y5TC/qwKwIABAwYMGDBgwIABAwb8NPC+72EBpqUBAwYMGPD3tW2bDcNgbduGNY6jX/C6rlZVldV1HaCC67fgLsF93wegUo41z7OVZWnTNPkDC6tUz9U0jXVd5w+sJFMzG+fZHVize4apvXPPcTaw5vSYsrCaa+25BKuEFTAupZ5K3tXFQ8nqdF6WxfcMfyq3YLWwZjb1ukrtu7l4qJ3Ph1bccwUWUBeM46GlB5DzlnXJDOtOrURzpsrnIWDAgAEDBgwY8CXgX/xFCZiWBnxv8JPGALDHOgYCmEPrhikB5tAC/K4XTmirmSiKs5wAAAAASUVORK5CYII=":
            return 9

    def _send_pinpad(self, digits):
        logger.info(sys._getframe().f_code.co_name)
        fields = {"pinPositions": digits}
        self._add_headers([('Content-Type', 'application/json; charset=utf-8')])
        req = self.br.request_class(LOGIN_ENDPOINT, headers=self._convert_headers())
        req.get_method = lambda: "PUT"
        try:
            res = self.br.open(req, data=json.dumps(fields))
        except Exception as e:
            msg = "Error en PUT pinpad"
            logger.error("%s\nURL: %s\nData: %s\nHeaders: %s\nResp: %s\nException: %s",
                         msg, req.get_full_url(), fields, req.headers, e.read(), e)
            raise e
        res_json = json.loads(res.read())
        return res_json["ticket"]

    def _post_auth(self, ticket):
        logger.info(sys._getframe().f_code.co_name)
        headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        data = "ticket=%s&device=desktop" % ticket
        req = self.br.request_class(POST_AUTH_ENDPOINT, headers=headers)

        try:
            res = self.br.open(req, data=data)
        except mechanize.HTTPError as e:
            msg = "Error en post_auth"
            logger.error("%s\nURL: %s\nData: %s\nHeaders: %s\nResp: %s\nException: %s",
                         msg, req.get_full_url(), data, req.headers, e.read(), e)
            raise e

    def _login(self):
        logger.info(sys._getframe().f_code.co_name)

        logger.info("dni: %s, fecha: %s, pass: %s" % (self.config.get_dni(), self.config.get_fecha(), self.config.get_pass()))
        if not self.config.get_dni() or not self.config.get_fecha() or not self.config.get_pass():
            raise Exception("Falta cargar los datos: config.yml")

        params = {
            "loginDocument": {
                "documentType": 0,
                "document": self.config.get_dni()
            },
            "birthday": self.config.get_fecha(),
            "companyDocument": None,
            "device": 'desktop'
        }
        data = json.dumps(params)

        self._add_headers([("Accept", 'application/json, text/javascript, */*; q=0.01')])
        self._add_headers([('Content-Type', 'application/json; charset=utf-8')])
        req = self.br.request_class(LOGIN_ENDPOINT, headers=self._convert_headers())
        logger.info("Login headers: %s", self.br.addheaders)
        try:
            res = self.br.open(req, data=data)
        except Exception as e:
            logger.error("Error enviando login. URL: %s. Data: %s", req.get_full_url(), data)
            raise e

        try:
            res_txt = res.read()
            pinData = json.loads(res_txt)
        except ValueError as ex:
            logger.exception("Error obtiniendo el JSON del login: %s", res_txt)
            raise ex

        logger.info("pinPositions: %s", pinData["pinPositions"])

        try:
            pinpad = process_pin_images(pinData["pinpad"])
        except Exception as e:
            logger.error("Exception en process_pin_images: %s", e)
            logger.error(pinData["pinpad"])
            raise e
        logger.info("Pinpad: %s", pinpad)

        password = self.config.get_pass()
        digits = []
        for i in range(0, 3):
            digits.append(int(password[pinData["pinPositions"][i] - 1]))

        logger.info("Digits: %s", digits)

        codecDigits = []
        for i in digits:
            codecDigits.append(pinpad.index(i))

        logger.info("codecDigits: %s", codecDigits)

        try:
            ticket = self._send_pinpad(codecDigits)
        except Exception as e:
            logger.error("Exception en send_pinpad: %s", e)
            raise e
        logger.info("ticket: %s", ticket)

        self._post_auth(ticket)

        return "Ok"

    def _fetch_products(self):
        logger.info(sys._getframe().f_code.co_name)
        self._add_headers([("Accept", '*/*')])
        self._add_headers([('Content-Type', 'application/json; charset=utf-8')])
        req = self.br.request_class(PRODUCTS_ENDPOINT)
        try:
            res = self.br.open(req)
            products = json.loads(res.read())
            return products
        except Exception as e:
            logger.error("Error obteniendo cuentas: %s", e)
            raise e

    def _fetch_favoritos(self):
        logger.info(sys._getframe().f_code.co_name)

        req = self.br.request_class(FAVORITOS_ENDPOINT)

        try:
            res = self.br.open(req)
        except mechanize.HTTPError as e:
            msg = "Error en el get para obtener favoritos"
            logger.error("%s\nURL: %s\nHeaders: %s\nResp: %s\nException: %s",
                         msg, req.get_full_url(), req.headers, e.read(), e)
            raise e

        try:
            res_txt = res.read()
            res_json = json.loads(res_txt)
        except ValueError as ex:
            logger.error("Error obteniendo el JSON del get para obtener favoritos")
            logger.error(res.read())
            raise ex

        return res_json.get("products")

    def get_products(self):
        if self.products is None:
            self.products = self._fetch_products()

        self.config.write_products(self.products)
        return self.products

    def get_favoritos(self):
        if self.favoritos is None:
            self.favoritos = self._fetch_favoritos()

        self.config.write_favoritos(self.favoritos)
        return self.favoritos

    def get_account_from_alias(self, alias):
        """
        Busca en las productos de ing alguna cuenta que su alias o nombre sea como el del parametro
        :param alias: nombre o alias de la cuenta que buscamos
        :return: objecto del producto
        """
        products = self.get_products()
        p = filter(lambda x: x.get("alias") == alias.decode("utf-8"), products)
        if len(p) > 1:
            raise CuentaDuplicada("Existe mas de una cuenta con ese alias")
        elif len(p) == 1:
            return p.pop().get("productNumber")

        p = filter(lambda x: x.get("name") == alias.decode("utf-8"), products)
        if len(p) > 1:
            raise CuentaDuplicada("Existe mas de una cuenta con ese nombre")
        elif len(p) == 1:
            return p.pop().get("productNumber")

        raise CuentaNotFound("No existe ninguna cuenta con ese alias o nombre")

    def get_cuenta_favorito(self, key):
        """
        Devuelve el objeto producto entero a partir de una key.
        Primero obtiene los favoritos y los productos para poder devolver los datos
        Ejemplo de key: PEPE MORA # BANCO BILBAO
        Ejemplo de key: PEPE MORA # Cuenta SIN NOMINA internet
        :param key: formada por el titular de la cuenta y el nombre del banco o alias (para cuentas propias)
        :return: titular, banco, iban, num_cuenta
        """
        products = self.get_products()
        favoritos = self.get_favoritos()

        titular,alias = map(lambda m: m.rstrip().lstrip(), key.split("#"))

        try:
            productNumber = self.get_account_from_alias(alias)
        except CuentaNotFound as e:
            logger.debug(e)
        else:
            return titular, productNumber

        # No hemos encontrado ninguna cuenta propia, por lo que nos deben estar pasando un banco
        banco = alias

        c = [v for k,v in favoritos.iteritems() if v.get(u"bank") == banco.decode("utf-8") and
             v.get(u"beneficiary") == titular.decode("utf-8")]

        if len(c) > 1:
            raise CuentaDuplicada("Se ha encontrado mas de una cuenta favorita para ese nombre y ese banco")
        elif len(c) == 0:
            raise CuentaNotFound("No se ha encontrado ninguna cuenta para el favorito")

        return titular,c.pop().get("productNumber")

    def get_alias(self, productNumber):
        """
        Devuelve el alias o nombre asociado a un productNumber
        :param productNumber: numero de cuenta del que queremos el alias
        :return: nombre o alias de la cuenta asociada
        """
        products = self.get_products()
        try:
            cuenta = filter(lambda x: x.get("productNumber") == productNumber, products).pop()
            if cuenta.has_key("alias"):
                return cuenta.get("alias")
            return cuenta["name"]
        except Exception:
            pass

        return None

    def get_card_alias(self, card):
        """
        A partir de un objeto de tipo tarjeta, devolver el alias, o nombre, de la cuenta asociada
        :param card: objeto tipo card con parametro associatedAccount
        :return: alias de la cuenta asociada o None
        """
        try:
            return self.get_alias(card.get("associatedAccount").get("productNumber"))
        except Exception:
            pass

        return None

    def fetch_last_transactions(self, account):
        logger.info(sys._getframe().f_code.co_name)

        end_date = date.today()
        start_date = date.today() - timedelta(days=30)  # TODO: parametrizar este valor
        params = {
            "fromDate": start_date.strftime('%d/%m/%Y'),
            "toDate": end_date.strftime('%d/%m/%Y'),
            "limit": 6,  # TODO: parametrizar este valor
            "offset": 0
        }
        logger.info("Params para coger transactions: %s", params)

        self._add_headers([("Accept", 'application/json, text/javascript, */*; q=0.01')])
        self._add_headers([('Content-Type', 'application/json; charset=utf-8')])
        req = self.br.request_class("%s/%s/movements?%s" % (
            PRODUCTS_ENDPOINT, account["uuid"], urllib.urlencode(params)))
        logger.info("Query a %s", req.get_full_url())
        try:
            start_time = time.time()
            res = self.br.open(req)
            req_time = time.time() - start_time
        except Exception as e:
            logger.error("Error solicitando movimientos: %s", e)
            raise e

        logger.info("Tiempo de la request: %s", req_time)
        transactions = json.loads(res.read())

        return_transactions = []
        for t in transactions.get("elements", []):
            if t.get("amount") > 0:
                amount = colored(t.get("amount"), 'green')
            else:
                amount = colored(t.get("amount"), 'red')

            if t.get("balance") > 0:
                balance = colored(t.get("balance"), 'green')
            else:
                balance = colored(t.get("balance"), 'red', attrs=["bold"])

            return_transactions.append([t.get("effectiveDate"), t.get("description"), amount, balance])

        return return_transactions

    def fetch_pending_transactions(self, account):
        logger.info(sys._getframe().f_code.co_name)

        try:
            res_json = self.fetch("%s/%s/pending-movements" % (PRODUCTS_ENDPOINT, account["uuid"]))
        except Exception as ex:
            logger.exception("Error al obtener los movimientos pendientes")
            raise ex

        # Obtenemos los detalles para cada transaccion pendiente
        return_transactions = []
        for tr in res_json:
            uuid = tr["uuid"]
            try:
                t = self.fetch("%s/%s/pending-movements/%s" % (PRODUCTS_ENDPOINT, account["uuid"], uuid))
            except Exception as ex:
                logger.exception("Error al obtener los movimientos pendientes")
                raise ex

            if t.get("amount") > 0:
                amount = colored(t.get("amount"), 'green')
            else:
                amount = colored(t.get("amount"), 'red')

            balance = colored("pendiente", 'yellow')
            effectiveDate = colored(t.get("effectiveDate"), 'yellow')
            comment = colored(t.get("comment"), 'yellow')
            return_transactions.append([effectiveDate, comment, amount, balance])

        return return_transactions

    def fetch(self, endpoint, headers=None, data=None, method=None):
        """
        Realiza una peticion a ING el endpoint indicado y devuelve el json parseado
        :param endpoint: url donde realizar la peticion
        :param headers: listado de cabeceras opcional
        :param data: si esta definido este parametro se envia un POST
        :return: JSON parseado a objeto python
        """
        if headers:
            req = self.br.request_class(endpoint, headers=headers)
        else:
            req = self.br.request_class(endpoint)
        if method:
            req.get_method = lambda: method

        try:
            res = self.br.open(req, data=data)
            res_txt = res.read()
            res_json = json.loads(res_txt)
        except mechanize.HTTPError as e:
            logger.error("Error enviando peticion\nURL: %s\nData: %s\nHeaders: %s\nResp: %s\nException: %s",
                         req.get_full_url(), data, req.headers, e.read(), e)
            raise e
        except ValueError as e:
            logger.error("Error obteniendo JSON de la respuesta de ING")
            logger.error(res.read())
            raise e

        return res_json

    def tarjetaCoordenadas(self, position):
        """
        Obtiene el pinpad del endpoint y nos devuelve un array con la respuesta que tenemos que devolver
        :param position: posicion de la tarjeta de coordenadas que nos piden
        :return: array con las posiciones del pinpad que debe enviarse
        """
        # Obtener pinpad
        try:
            res_json = self.fetch(CARD_ENDPOINT)
        except Exception as ex:
            logger.exception("Error obteniendo el pinpad")
            raise ex

        # Obtenemos el pinpad
        try:
            pinpad = process_pin_images(res_json["pinpad"])
        except Exception as e:
            logger.error("Exception en process_pin_images: %s", e)
            logger.error(res_json["pinpad"])
            raise e
        logger.info("Pinpad: %s", pinpad)

        # Obtenemos la coordenada que necesitamos
        coordenada = self.config.get_coordenada(position)

        codecDigits = []
        for i in map(int, str(coordenada)):
            codecDigits.append(pinpad.index(i))

        logger.info("codecDigits: %s", codecDigits)
        return codecDigits

