# wisphub-bqn-sync

Script sencillo de sincronización entre un BQN y un billing de Wisphub.

## Instalación

El script necesita python 3.10 or posterior con el paquete *requests*.

### En Arch Linux:
`$ sudo pacman -S python3`

`$ sudo pip3 install requests`

### En Windows:
1. En una shell de administrador:

`> winget install python`

2. En una shell normal:

`> pip install requests`

#### En Mac OS:
1. Descargas el paquete para MAc del sitio oficial de python:

https://www.python.org/downloads/macos/

2. Instalar el paquete (introduzca la contraseña de Administrator cuando se requiera).

4. En la shell de comandos:

`$ pip3 install requests`

## Configuración

Generar un API token en el billing de Wisphub.

Habilitar la REST API en el BQN.

## Ejecución del script

Cada vez que se requiera una sincronización:

`python3 ./wisphub-bqn-sync.py -b <bqn-ip> <bqn-rest-user> <bqn-rest-password> <wisphub-api-token>`

La primera vez que se ejecuta el script y simepre que haya cambios en los planes, vaya al BQN a Status->Radius/REST/Billing->Policies, mire las políticas de tipo "undefined" y clique en sus nombres para configurare los límites de velocidad de la politica de rate del BQN.

## Limitaciones conocidas

- Los límites de velocidad no se pueden obtener del Wisphub. Deben configurarse en el BQN.
- No se soportan IPs múltiples en un mismo cliente.
- La primera ejecución puede llevar minutos. Las siguientes enviarán al BQN solo los cambios y serán más rápidas.
- Si la sincronización falla, no habrá reintentos (deberán hacerse externamente).
- No incluye programación de la ejecucición periódica del script (deberá hacerse externamente).

## Relación entre entidades del BQN entities con el schema de Wisphub

- Las BQN Rate policies se identifican con el Wisphub "plan_internet"->"nombre", con espacios sustituidos por subrayados.
- Los suscriptores del BQN se identifican con el Wispro "nombre".
- Los clientes con estado == "Suspendido" tienen su tráfico bloqueado por el BQN (política Wisphub_block).