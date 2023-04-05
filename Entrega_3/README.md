Video de Sustentación 

[Video de Sustentación](https://uniandes-my.sharepoint.com/:v:/g/personal/c_huertasc_uniandes_edu_co/EVzV2Rd1vLRMgS2BsgDBxUYBmzWYtspjLgJ08nKpefZ_nQ?e=8MxiaS)

El despliegue de la arquitectura se realizó de dos maneras que llevan al mismo resultado, solo ejecute una de las siguientes opciones para crear la infraestructura que contendrá la aplicación:

* [Despliegue de Infraestructura por Cloud Shell](#despliegue-de-infraestructura-por-cloud-shell)
* [Despliegue de infraestructura con Terraform](#despliegue-de-infraestructura-con-terraform)

La arquitectura que se establecio crear es mostrada en la siguiente imagen.

![Infraestructura File Compresor GCP.](https://github.com/camandhuercue/Entrega-1---Sistema-de-Conversi-n-Cloud/blob/main/Entrega_3/imgs/Infraestructura_GCP.jpg "Infraestructura File Compresor GCP.")

Antes del despliegue se realiza una breve introducción a conocer cada uno de los archivos (Usados para despliegue Terraform) y comandos (Despliegue Cloud Shell) que son usados para el despliegue del compresor de archivos.

# **Descripcion de Archivos y Comandos**

Los archivos que contiene Terraform están estructurados de la siguiente manera.

```bash
Terraform/
├── instance
│   └── main.tf
├── sql-instance
│   └── main.tf
├── variables.tf
├── cloud-sql.tf
├── privatenet.tf
└── provider.tf
```

A continuación se da una breve explicación de lo que contiene cada uno y su propósito.

## ***1. Variables***

Como su nombre lo dice tiene variables que seran usadas en otros archivos ***.tf*** Especificamente las variables que se pueden ver en este archivo contiene los comandos iniciales necesarios para dejar preparadas cada una de las maquinas.

### ***1.1 Variable "file-server-sh" / Configuración del NFS*** 
---
Esta variable tiene los comando necesarios para la configuracion del NFS a continuacion una explicacion de cada comando.


Para configurar el sistema de archivos compartidos, es necesario configurar el servicio en la máquina que se designó para tal rol (**file-server**). Utilizaremos nfs-kernel-server, para ello ejecutamos el siguiente comando en la consola como root

```bash
sudo apt-get update -y && sudo apt-get install nfs-kernel-server -y
```

Creamos la carpeta que se hará visible para las otras instancias:

```bash
sudo mkdir -p /shared/files
```

Cambiamos los permisos del directorio para que se ajusten a lo solicitado por el servicio:

```bash
sudo chown nobody:nogroup /shared/files/
```

Ahora, limitamos el acceso al NFS a los servidores locales:

```bash
echo "/shared/files/   172.16.0.0/24(rw,sync,no_root_squash,no_subtree_check)" >> /etc/exports
```

Por último, reiniciamos el servicio para que apliquen los cambios:

```bash
systemctl restart nfs-server
```

Si se desea se puede entrar a la instancia que contiene el file-server y probar que el servicio se encuentre corriendo:


Revisamos que el servicio se encuentre corriendo:

```bash
systemctl status nfs-server
```

Tambien se pueden hacer pruebas desde otras maquinas para comprobar que se estan montando los archivos en la maquina ***file-server***

Del lado del cliente (***backend***, ***worker*** o ***frontend***) instalamos los paquetes necesarios con el siguiente comando:

```bash
sudo apt-get update -y && sudo apt-get install nfs-common -y
```

Montamos las unidades compartidas en el cliente y comprobamos que cuando se crea un archivo en un lado es accesible en el otro

```bash
cd
mkdir test
sudo mount 172.16.0.7:/shared/files ./test/
cd ./test
echo "esto es una prueba" >> prueba.txt
```

### ***1.2 Variable "metadata" / Instalación de docker*** 
---

Esta variable se debe ejecutar en las maquinas ***backend***, ***worker*** o ***frontend*** con la finalidad de instalar en cada una de ellas docker y dejar el repositorio base en cada una de ellas.

Con estos comando se garantiza la instalacion de Docker en Debian:

```bash
sudo apt-get update && apt-get install ca-certificates curl gnupg
mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --yes --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
"deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
"$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update && sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
```

Descargamos las configuraciones del repositorio 

```bash
git clone https://github.com/camandhuercue/Entrega-1---Sistema-de-Conversi-n-Cloud.git
```

### ***1.3 Variable "backend-worker-sh" / Paquetes necesarios monteje de archivos NFS*** 
---

Esta variable se debe ejecutar en las maquinas ***backend***, ***worker***, instalamos los paquetes necesarios para que funcione el NFS con el siguiente comando:

```bash
apt-get update && apt-get install nfs-common -y
```

### ***1.4 Variable "backend-sh" / Instalacion de docker*** 
---

Esta variable se debe ejecutar en la maquina del ***backend***, nos ubicamos en la carpeta correspondiente:

```bash
cd Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_3/Backend/
mkdir files
```

Montamos la carpeta compartida en la ruta creada:

```bash
mount 172.16.0.7:/shared/files ./files/
```

> **Nota:** 
Desde este punto se debe ejecutar tanto al desplegar con Cloud Shell como con Terraform.

Se debe de modificar la IP de la base de datos:

```bash
nano Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_3/Backend/BackEnd/Dockerfile
```

Se debe de modificar la IP de la base de datos en la sección **DB_HOST**, luego ejecutar lo siguiente:

```bash
cd Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_3/Backend/
docker compose up
```

El servicio queda Levantado.

### ***1.5 Variable "worker-sh" / Instalacion de docker*** 
---

Esta variable se debe ejecutar en la maquina del ***worker***, nos ubicamos en la carpeta correspondiente:

```bash
cd Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_3/Worker
mkdir files
```

Montamos la carpeta compartida en la ruta creada:

```bash
mount 172.16.0.7:/shared/files ./files/
```

> **Nota:** 
Desde este punto se debe ejecutar tanto al desplegar con Cloud Shell como con Terraform.

Se debe de modificar la IP de la base de datos:

```bash
nano Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_3/Worker/Queue/queue_api/__init__.py
```

Allí ponemos en el string de la base de datos la IP que nos haya asignado el servicio.

Luego ejecutamos lo siguiente:

```bash
cd Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_3/Worker
docker compose up
```

El servicio queda Levantado.

### ***1.6 Variable "frontend-sh" / Instalacion de docker*** 
---

Esta variable se debe ejecutar en la maquina del ***frontend***, nos ubicamos en la carpeta correspondiente y se levanta el servicio con ayuda de docker compose.

```bash
cd Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_3/Frontend/
docker compose up
```



# **Despliegue de Infraestructura por Cloud Shell**

Ejecute los siguientes comando configurar la region y zona:

```bash
gcloud config set project {project_name}
```

```bash
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a
```

Cree las variables de entorno con el id del poyecto, la region y la zona.

```bash
export PROJECT_ID=$(gcloud config get-value project)
export REGION=$(gcloud config get-value compute/region)
export ZONE=$(gcloud config get-value compute/zone)
export PRIVATENET='net-pruebas'
export PRIVATESUBNET='subnet-pruebas'
export FIREWALL_ALLOW_SSH='privatenet-allow-ssh'
export FIREWALL_ALLOW_INTERNAL='privatenet-allow-internal'
export FRONTEND='frontend'
export BACKEND='backend'
export WORKER='worker'
export FILE_SERVER='file-server'

```

## **Creacion de VPC**
---

Ejecute el siguiente comando para crear una red privada

```bash
gcloud compute networks create $PRIVATENET --subnet-mode=custom
```

Ejecutar el sigueinte comando para crear una subred privada **<name_privatesubnet>** 

```bash
gcloud compute networks subnets create $PRIVATESUBNET \
--network=$PRIVATENET \
 --region=$REGION \
 --range=172.16.0.0/24
```

## **Creacion de reglas de Firewall**
---

Ejecute el siguiente comando para permitir el acceso a todas las maquinas desde local.

```bash
gcloud compute firewall-rules create $FIREWALL_ALLOW_SSH \
--direction=INGRESS \
--priority=1000 \
--network=$PRIVATENET \
--action=ALLOW \
--rules=tcp:22,tcp:8080,tcp:5001 \
--source-ranges=0.0.0.0/0
```

Ejecute el siguiente comando para permitir todas las comunicaciones entre las redes internas.

```bash
gcloud compute firewall-rules create $FIREWALL_ALLOW_INTERNAL \
 --direction=INGRESS \
 --priority=1000 \
 --network=$PRIVATENET \
 --action=ALLOW \
 --rules=tcp:0-65535,udp:0-65535,icmp \
 --source-ranges=172.16.0.0/24
```

## **Creacion de Maquinas Virtuales**
---

Ejecute el siguiente comando para crear las máquinas virtuales necesarias para la ejecución de la aplicación.

```bash
gcloud compute instances create $FRONTEND \
--subnet $PRIVATESUBNET \
--zone $ZONE \
--private-network-ip 172.16.0.4 \
--machine-type f1-micro

gcloud compute instances create $BACKEND \
--subnet $PRIVATESUBNET \
--zone $ZONE \
--private-network-ip 172.16.0.5 \
--machine-type f1-micro

gcloud compute instances create $WORKER \
--subnet $PRIVATESUBNET \
--zone $ZONE \
--private-network-ip 172.16.0.6 \
--machine-type f1-micro \
--no-address


gcloud compute instances create $FILE_SERVER \
--subnet $PRIVATESUBNET \
--zone $ZONE \
--private-network-ip 172.16.0.7 \
--machine-type f1-micro \
--no-address
```

# **Despliegue de infraestructura con Terraform**

Dentro de la Cloud Shell de GCP se deben ejecutar los siguientes pasos para el despliegue de la infraestructura que soportara el compresor de archivos.

Descargar terraform corriendo el siguiente comando:

```bash
wget https://releases.hashicorp.com/terraform/1.2.7/terraform_1.2.7_linux_amd64.zip
```

Para descomprimir terraform utilice el siguiente comando:

```bash
unzip terraform_1.2.7_linux_amd64.zip
rm -rf terraform_1.2.7_linux_amd64.zip
```

Establezca la variable de entorno PATH para los binarios de Terraform:

```bash
export PATH="$PATH:$HOME/terraform"
cd /usr/bin
sudo ln -s $HOME/terraform
cd $HOME
source ~/.bashrc
```

Confirme la instalación de Terraform ejecutando el siguiente comando:

```bash
terraform --version
```

Exporte el proyecto de Google Cloud a una variable de entorno ejecutando el siguiente comando en Cloud Shell:

```bash
export PROJECT_ID=$(gcloud config get-value project)
```

Descargamos el repositorio de terraform que contiene los archivos necesarios para desplegar la infraestructura requerida.

```bash
git clone https://github.com/camandhuercue/Entrega-1---Sistema-de-Conversi-n-Cloud.git
mv Entrega-1---Sistema-de-Conversi-n-Cloud/Entrega_3/Terraform/ ~/
rm -rf Entrega-1---Sistema-de-Conversi-n-Cloud
```

* ***Habilite el Compute Engine API.***
* ***Habilite el Cloud Resource Manager API.***
* ***Habilite el Cloud SQL Admin API.***

Una vez estemos en ubicados dentro de la carpeta Terraform

```bash
cd Terraform
```

Para realizar el despliegue primero se reescribe los archivos de configuración de Terraform a un formato y estilo canónico ejecutando el siguiente comando:

```bash
terraform fmt
```

Inicialice Terraform ejecutando el siguiente comando:

```bash
terraform init
```

Cree un plan de ejecución ejecutando el siguiente comando:

```bash
terraform plan
```

Aplique los cambios deseados ejecutando el siguiente comando:

```bash
terraform apply
```

Revise:

* **Compute Engine:** Deben aparecer las instancias necesarias para la ejecución de la aplicación.
* **Redes VPC:**
    * **Redes VPC:** Se debe crear una red VPC con una Sub red perteneciente a la Zona ***"us-central1-a"***
    * **Firewall:** Se deben crear 2 reglas dse Firewall que afectan a la VPC creada.

# **Configuración de SQL**

Dentro de los archivos de Terraform tambien se deja la opcion de crear la instancia que soportara a Cloud SQL sin embargo este proceso tarda alrededor de 18 Minutos a comparacion de lo 5 Minutos que tarda al crearse por consola. En caso de querer probar que se puede desplegar la instancia SQL con Terraform descomnete el modulo que se encuentra en el archivo ***cloud-sql.tf***

Con respecto a la instancia de SQL, se crea con el servio de Cloud SQL de Google, seleccionando como motor Postgres. Las características son las siguientes:

- Versión: 14.
- Ambiente: Desarrollo.
- Region y Zona: US Central 1 - a.
- VCPU: 1
- RAM: 4
- SSD: 10GB sin aumentos automáticos.
- Sin IP pública y se crea una conexión privada entre Google y nuestra VPC con rango 172.16.2.0/14.
- Sin Copias de seguridad ni protección de eliminación.
- Se deja el restante por defecto.

> **Nota:** 
Desde este punto se debe ejecutar tanto al desplegar con Cloud Shell como con Terraform.

Mientras se crea la instancia de SQL, se instala el cliente de postgres en cualquiera de las instancias de Compute Engine, con la finalidad de entrar al abase de datos y poder crear la base de datos y el esquema a utilizar por el desarrollo. Para ello en la consola como root se ejecuta lo siguiente:

```bash
apt-get update && apt-get install postgresql-client -y
```

Una vez instalado el cliente, conectarse a la base de datos con el siguiente comando:


```bash
psql -h {ip-db} -U postgres
```

La contraseña que estamos utilizando para la base de datos es SuP3r$3cUr#P$$!!

Una vez en la base de datos ejecutamos lo siguiente para poder configurarla según se necesita en el desarrollo:

```bash
CREATE DATABASE compress_database;
\connect compress_database;
CREATE SCHEMA compress_schema;
```
