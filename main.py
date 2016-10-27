#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Adrián López Tejedor <adrianlzt@gmail.com>
#
# Distributed under terms of the GNU GPLv3 license.

"""

"""
from config import Config
from datetime import date
from tabulate import tabulate
from termcolor import cprint
from browser import Browser
from constants import *

import argparse
import json
import sys

import logging

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.WARN)

def movimientos(args):
    """
    Proceso principal que gestiona el login, obtener cuentas y mostrar los movimientos
    """
    logger.info(sys._getframe().f_code.co_name)

    for product in browser.get_products():
        try:
            logger.info("Obteniendo movimientos de %s", product["name"])
            # Tras varias peticiones de movimientos consecutivas, el servidor
            # empieza a meter delays de 30" en las respuestas
            if product.get("type") == TARJETA_CREDITO or product.get("type") == TARJETA_DEBITO:
                continue  # No sacamos a las tarjetas

            if product.get("type") == TARJETA_CREDITO or product.get("type") == TARJETA_DEBITO:
                account_name = "%s - %s" % (product.get("name"), browser.get_card_alias(product))
            else:
                account_name = product.get("alias") or product.get("name")

            if args.cuenta and args.cuenta.decode("utf-8") != account_name:
                continue

            transactions = browser.fetch_last_transactions(product)
            pending_transactions = browser.fetch_pending_transactions(product)
            if len(transactions + pending_transactions) == 0:
                continue

            total_transactions = list(reversed(pending_transactions)) + transactions

            cprint(account_name, 'blue', attrs=["bold"])

            print(tabulate(total_transactions, headers=["Fecha", "Concepto", "Cantidad", "Saldo"], tablefmt="fancy_grid"))
            print("\n\n")
        except Exception as e:
            logger.error("Error analizando movimientos: %s", e)


def favoritos(args):
    logger.info(sys._getframe().f_code.co_name)

    cprint("No implementado", 'red')

def transferencia(args):
    logger.info(sys._getframe().f_code.co_name)

    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    operativa = {"operativeType": "transfers"}
    try:
        res_json = browser.fetch(TRANSFER_ENDPOINT, headers=headers, data=json.dumps(operativa))
    except Exception as ex:
        logger.exception("Error en el primer paso para realizar una transferencia")
        raise ex

    transfer_uuid = res_json.get("id")

    if args.favorito_destino:
        titular_destino, cuenta_destino = browser.get_cuenta_favorito(args.favorito_destino)
    else:
        cuenta_destino = args.cuenta_destino
        titular_destino = args.titular_destino

    cuenta_origen = browser.get_account_from_alias(args.cuenta_origen)

    # PUT para solicitar la transferencia
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    trans_data = {
        "from": {
            "productNumber": cuenta_origen
        },
        "to": {
            "productNumber": cuenta_destino,
            "titular": titular_destino
        },
        "currency": "EUR",
        "amount": args.cantidad,
        "concept": args.concepto,
        "operationDate": date.today().strftime("%d/%m/%Y")
    }

    try:
        res_json = browser.fetch("%s/%s" % (TRANSFER_ENDPOINT, transfer_uuid), headers=headers,
                                 data=json.dumps(trans_data), method="PUT")
    except Exception as ex:
        logger.exception("Error en el segundo paso para realizar una transferencia")
        raise ex

    logger.info("AcceptanceMethods: %s", res_json.get("acceptanceMethods"))
    acceptanceMethod = res_json.get("acceptanceMethods").pop()
    validationType = acceptanceMethod.get("validationType")

    if validationType == "noValidation":
        acceptance = [{"acceptanceValue": ""}]
    elif validationType == "card":
        position = int(acceptanceMethod.get("position"))
        valores = browser.tarjetaCoordenadas(position)
        # Los valores son int, los convertimos a string
        acceptance = [{"acceptanceValue": ",".join(map(str, valores))}]
    else:
        raise Exception("validationType para realizar una transferencia desconocido: %s", validationType)

    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    try:
        res_json = browser.fetch("%s/%s/accept" % (TRANSFER_ENDPOINT, transfer_uuid), headers=headers,
                                 data=json.dumps(acceptance), method="PUT")
    except Exception as ex:
        logger.exception("Error en el tercer paso para realizar una transferencia")
        raise ex

    if res_json.get("acceptanceMethods"):
        logger.error(u"Error enviando la coordenada para aceptar la transferencia: %s",
                     res_json.get("acceptanceMethods").get("message"))
        # TODO: aqui tenemos la opcion de volver a repetir el proceso
        raise Exception("No se ha podido realizar la transferencia")

    transfer = res_json.get("transferTransaction")
    logger.info(u"Transferencia de %s€ desde %s para %s", transfer.get("amount"),
                transfer.get("from").get("productNumber"), transfer.get("to"))

    cprint("Transferencia realizada correctamente", 'white', 'on_cyan', attrs=["bold"])
    cprint("Cantidad: %s" % transfer.get("amount"), 'red')
    cprint(u"Concepto: %s" % transfer.get("concept"), 'yellow')
    cprint("Destino:", 'yellow')
    cprint(u"\t%s" % transfer.get("to").get("titular"), 'yellow')
    cprint(u"\t%s (%s)" % (transfer.get("to").get("bank"), transfer.get("to").get("productNumber")), 'yellow')
    cuenta_origen = browser.get_alias(transfer.get("from").get("productNumber"))
    cprint("Cuenta origen: %s" % cuenta_origen, 'magenta')



if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="ingdirect", description='Gestionar cuentas ING-Direct')
    parser.add_argument('-v', '--verbose', dest='verbose', action='count', default=0,
                        help='verbose output. specify twice for debug-level output.')

    subparsers = parser.add_subparsers(title='Acciones')

    parser_favoritos = subparsers.add_parser('favoritos', help='Guardar un favoritos"')
    parser_favoritos.set_defaults(func=favoritos)
    parser_favoritos.add_argument('-t', '--titular', action='store', dest='guardar_favorito_titular',
                                  help="Nombre del titular del favorito a guardar", default=None, required=True)
    parser_favoritos.add_argument('-c', '--cuenta', action='store', dest='guardar_favorito_cuenta',
                                  help="Numero de cuenta del favorito a guardar", default=None, required=True)

    parser_movimientos = subparsers.add_parser('movimientos', help='Obtener movimientos')
    parser_movimientos.set_defaults(func=movimientos)
    parser_movimientos.add_argument('-c', '--cuenta', action='store', dest='cuenta',
                                    help="Solo obtener los movimientos de esta cuenta.", default=None)

    parser_transferencia = subparsers.add_parser('transferencia', help='Realizar una transferencia')
    parser_transferencia.set_defaults(func=transferencia)
    group = parser_transferencia.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--cuenta_destino', action='store', dest='cuenta_destino',
                       help="Cuenta a donde se realiza la transferencia.", required=False)
    group.add_argument('-f', '--favorito_destino', action='store', dest='favorito_destino',
                       help="Cuenta conocida a donde se realiza la transferencia.", required=False)
    parser_transferencia.add_argument('-o', '--cuenta_origen', action='store', dest='cuenta_origen',
                                      help="Cuenta desde la que se realiza la transferencia.", required=True)
    parser_transferencia.add_argument('-p', '--titular', action='store', dest='titular_destino',
                                      help="Titular de la cuenta destino.", required=False)
    parser_transferencia.add_argument('-c', '--cantidad', action='store', dest='cantidad',
                                      help="Euros que queremos transferir.", required=True)
    parser_transferencia.add_argument('-m', '--concepto', action='store', dest='concepto',
                                      help="Concepto de la transferencia.", required=True)

    args = parser.parse_args()

    if args.verbose > 1:
        logger.setLevel(logging.DEBUG)
    elif args.verbose > 0:
        logger.setLevel(logging.INFO)

    if hasattr(args, "cuenta_destino") and args.cuenta_destino and args.titular_destino is None:
        parser.error("Si especificas una cuenta destino debes especificar un titular")

    config = Config()
    browser = Browser(config)
    args.func(args)
