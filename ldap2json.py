#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name          : ldap2json.py
# Author             : Podalirius (@podalirius_)
# Date created       : 22 Dec 2021


from sectools.windows.ldap import init_ldap_session, raw_ldap_query
import argparse
import datetime
import json
import sys


def cast_to_dict(cid):
    out = {}
    for key, value in cid.items():
        if type(value) == bytes:
            out[key] = str(value)
        elif type(value) == list:
            newlist = []
            for element in value:
                if type(element) == bytes:
                    newlist.append(str(element))
                elif type(element) == datetime.datetime:
                    newlist.append(element.strftime('%Y-%m-%d %T'))
                elif type(element) == datetime.timedelta:
                    # Output format to change
                    newlist.append(element.seconds)
                else:
                    newlist.append(str(element))
            out[key] = newlist
        elif type(value) == datetime.datetime:
            out[key] = value.strftime('%Y-%m-%d %T')
        elif type(value) == datetime.timedelta:
            # Output format to change
            out[key] = value.seconds
        else:
            out[key] = value
    return out


def bytessize(data):
    """
    Function to calculate the size of data in bytes and convert it to a human-readable format.

    Args:
        data (bytes): The data for which the size needs to be calculated.

    Returns:
        str: The human-readable format of the data size.
    """
    l = len(data)
    units = ['B','kB','MB','GB','TB','PB']
    for k in range(len(units)):
        if l < (1024**(k+1)):
            break
    return "%4.2f %s" % (round(l/(1024**(k)),2), units[k])


def parseArgs():
    parser = argparse.ArgumentParser(add_help=True, description="The ldap2json script allows you to extract the whole LDAP content of a Windows domain into a JSON file.")
    parser.add_argument("--use-ldaps", action="store_true", help="Use LDAPS instead of LDAP.")
    parser.add_argument("-q", "--quiet", dest="quiet", action="store_true", default=False, help="Show no information at all.")
    parser.add_argument("--debug", dest="debug", action="store_true", default=False, help="Debug mode.")
    parser.add_argument("-o", "--outfile", dest="jsonfile", default="ldap.json", help="Output JSON file. (default: ldap.json).")
    parser.add_argument("-b", "--base", dest="searchbase", default=None, help="Search base for LDAP query.")

    authconn = parser.add_argument_group("authentication & connection")
    authconn.add_argument("--dc-ip", action="store", metavar="ip address", help="IP Address of the domain controller or KDC (Key Distribution Center) for Kerberos. If omitted it will use the domain part (FQDN) specified in the identity parameter.")
    authconn.add_argument("--kdcHost", dest="kdcHost", action="store", metavar="FQDN KDC", help="FQDN of KDC for Kerberos.")
    authconn.add_argument("-d", "--domain", dest="auth_domain", metavar="DOMAIN", action="store", help="(FQDN) domain to authenticate to.")
    authconn.add_argument("-u", "--user", dest="auth_username", metavar="USER", action="store", help="user to authenticate with.")

    secret = parser.add_argument_group()
    cred = secret.add_mutually_exclusive_group()
    cred.add_argument("--no-pass", action="store_true", help="Don't ask for password (useful for -k).")
    cred.add_argument("-p", "--password", dest="auth_password", metavar="PASSWORD", action="store", help="Password to authenticate with.")
    cred.add_argument("-H", "--hashes", dest="auth_hashes", action="store", metavar="[LMHASH:]NTHASH", help="NT/LM hashes, format is LMhash:NThash.")
    cred.add_argument("--aes-key", dest="auth_key", action="store", metavar="hex key", help="AES key to use for Kerberos Authentication (128 or 256 bits).")
    secret.add_argument("-k", "--kerberos", dest="use_kerberos", action="store_true", help="Use Kerberos authentication. Grabs credentials from .ccache file (KRB5CCNAME) based on target parameters. If valid credentials cannot be found, it will use the ones specified in the command line.")
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    options = parser.parse_args()
    
    if options.auth_password is None and options.no_pass == False and options.auth_hashes is None:
        print("[+] No password of hashes provided and --no-pass is '%s'" % options.no_pass)
        from getpass import getpass
        if options.auth_domain is not None:
            options.auth_password = getpass("  | Provide a password for '%s\\%s':" % (options.auth_domain, options.auth_username))
        else:
            options.auth_password = getpass("  | Provide a password for '%s':" % options.auth_username)

    return options


if __name__ == '__main__':
    options = parseArgs()

    print("[+]======================================================")
    print("[+]    LDAP2JSON v1.1                  @podalirius_      ")
    print("[+]======================================================")
    print()

    auth_lm_hash = ""
    auth_nt_hash = ""
    if options.auth_hashes is not None:
        if ":" in options.auth_hashes:
            auth_lm_hash = options.auth_hashes.split(":")[0]
            auth_nt_hash = options.auth_hashes.split(":")[1]
        else:
            auth_nt_hash = options.auth_hashes

    print("[>] Connecting to remote LDAP host '%s' ... " % options.dc_ip, end="", flush=True)
    ldap_server, ldap_session = init_ldap_session(
        auth_domain=options.auth_domain, 
        auth_username=options.auth_username, 
        auth_password=options.auth_password, 
        auth_lm_hash=auth_lm_hash, 
        auth_nt_hash=auth_nt_hash, 
        auth_key=options.auth_key, 
        use_kerberos=options.use_kerberos, 
        kdcHost=options.kdcHost, 
        use_ldaps=options.use_ldaps, 
        auth_dc_ip=options.dc_ip
    )
    configurationNamingContext = ldap_server.info.other["configurationNamingContext"]
    defaultNamingContext = ldap_server.info.other["defaultNamingContext"]
    print("done.")

    if options.debug:
        print("[>] Authentication successful!")

    print("[>] Extracting all objects from LDAP ...")
    
    data = {}
    for naming_context in ldap_server.info.naming_contexts:
        if options.debug:
            print("[>] Querying (objectClass=*) to LDAP on %s ..." % naming_context)

        response = raw_ldap_query(
            auth_domain=options.auth_domain,
            auth_dc_ip=options.dc_ip,
            auth_username=options.auth_username,
            auth_password=options.auth_password,
            auth_hashes=options.auth_hashes,
            auth_key=options.auth_key,
            searchbase=naming_context,
            use_ldaps=options.use_ldaps,
            use_kerberos=options.use_kerberos,
            kdcHost=options.kdcHost,
            query="(objectClass=*)",
            attributes=["*"]
        )

        if options.debug:
            print("  | LDAP query (objectClass=*) returned %d objects" % len(response))

        for cn in response:
            path = cn.split(',')[::-1]
            tmp = data
            for key in path[:-1]:
                if key in tmp.keys():
                    tmp = tmp[key]
                else:
                    tmp[key] = {}
                    tmp = tmp[key]
            tmp[path[-1]] = cast_to_dict(response[cn])

    json_data = json.dumps(data, indent=4)
    if options.debug:
        print("[>] JSON data generated.")

    print("[>] Writing json data to %s" % options.jsonfile)
    f = open(options.jsonfile, 'w')
    f.write(json_data)
    f.close()
    print("[>] Written %s bytes to %s" % (bytessize(json_data), options.jsonfile))
