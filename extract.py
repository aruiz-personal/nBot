#!/usr/bin/env python3
#_*_ coding: utf8 _*_

# Recibe un texto extrae IOC.. ver https://github.com/renzejongman/iocparser
# Envia a un archivo e invoca metodos que hacen la llamadas a APIs de las soluciones.
# Notas: Optimizar código.


from iocparser import IOCParser
import json
import os.path
import trend

def extraer(texto):    
    extObj = IOCParser(texto)
    results = eliminar_duplicados(extObj.parse())
    results = eliminar_dominios_ips_privadas(results)
    if(len(results)>0):
      send_trend_api(results)
      send_to_file_for_pa(results)
    mostrarResultados(results)
    return results
    
def buscar(texto):    
    extObj = IOCParser(texto)
    results = eliminar_duplicados(extObj.parse())
    results = limpiar(results)
    results = eliminar_dominios_ips_privadas(results)
    if (len(results)==0):
        return ''
    else:
        return generar_salida(results)

def contar(texto):    
    extObj = IOCParser(texto)
    results = eliminar_duplicados(extObj.parse())
    results = limpiar(results)
    results = eliminar_dominios_ips_privadas(results)
    return len(results)

def send_trend_api(results):
    for r in results:
        if(r.kind=="IP"):
           trend.send_ioc_cloud("ip",r.value,"nBot - API IP IOC","log")
        if(r.kind=="sha1"):
            trend.send_ioc_cloud("file_sha1",r.value,"nBot - API SHA1 IOC","log")
        if(r.kind=="uri"):
            trend.send_ioc_cloud("domain",r.value,"nBot - Domain IOC","log")
    
def send_to_file_for_pa(results):
    list_ips=[]
    list_uris=[]
    if(os.path.isfile('/var/archivos_ioc/ip_blacklist.txt')):
        file_ip=open("/var/archivos_ioc/ip_blacklist.txt", "r")
        for line in file_ip:
            list_ips.append(line.rstrip('\n'))
        file_ip.close()
    if(os.path.isfile('/var/archivos_ioc/uri_blacklist.txt')):
        file_uri=open("/var/archivos_ioc/uri_blacklist.txt", "r")
        for line in file_uri:
            list_uris.append(line.rstrip('\n'))
        file_uri.close()

    for r in results:
        if(r.kind=="IP" and r.value not in list_ips):
            list_ips.append(r.value)
        if(r.kind=="uri" and r.value not in list_uris):
            list_uris.append(r.value)

    with open("/var/archivos_ioc/ip_blacklist.txt", "w") as f:
        for ip in list_ips:
            f.write("%s\n" % ip)

    with open("/var/archivos_ioc/uri_blacklist.txt", "w") as f:
        for uri in list_uris:
            f.write("%s\n" % uri)
    
def mostrarResultados(results):
    for res in results:
        print(res.kind + ":" + res.value) 

def eliminar_duplicados(results):
    results_noduplicate = []
    for r in results:
        if (isInList(r.value,results_noduplicate)==False):
            results_noduplicate.append(r)
    
    return results_noduplicate

def isInList(value,results):
    for r in results:
        if(r.value == value):
           return True
    return False

def limpiar(results):
    results_util=[]
    for res in results:
        if(res.kind=='IP' or res.kind=='sha1' or res.kind=='uri'):
            results_util.append(res)
    return results_util

def generar_salida(results):
    sha = []
    ips = []
    URL = []
    for res in results:
        if(res.kind=='IP'):
            ips.append(res)
        if(res.kind=='sha1'):
            sha.append(res)
        if(res.kind=='uri'):
            URL.append(res)
    
    return listToString(ips) + listToString(sha) + listToString(URL) 

def listToString(s):  
    
    # initialize an empty string 
    str1 = ""  
    
    # traverse in the string   
    for ele in s:  
        str1 += ele.kind + " : " + ele.value +"\n" 
    
    # return string   
    return str1  

def eliminar_dominios_ips_privadas(results):
    results_seguro = []
    for r in results:
        if (isPrivado(r)==False):
                results_seguro.append(r)
    
    return results_seguro

def isPrivado(r):
    ip_privados = ['192.168.','10.','0.0.0.0','127.0.0.1','172.16.','172.17.','172.18.','172.19.','172.20.','172.21.','172.22.','172.23.', 
        '172.24.','172.25.''172.26.','172.27.','172.28.','172.29.','172.30.','172.31.']
    dominios_privados = ['mycomapany.com','myfriendcompany.com']

    if (r.kind=='IP'):
        for ip in ip_privados:
            if(r.value.startswith(ip)):
                return True
    
    if (r.kind=='uri'):
        for domain in dominios_privados:
            if(domain in r.value):
                return True

    return False
