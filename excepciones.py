class CuentaNotFound (Exception):
    def __init__(self, message='Cuenta no encontrada'):
        super(CuentaNotFound, self).__init__(message)

class CuentaDuplicada(Exception):
    def __init__(self, message='Varias cuentas iguales'):
        super(CuentaDuplicada, self).__init__(message)
