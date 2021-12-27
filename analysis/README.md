# LDAP offline analysis tool

This analysis console offers multiple ways of searching LDAP objects from a JSON file. You can search for objects, property names or property values in the console.

![](./screenshots/analysis.png)

## Commands

| Command | Description |
|---------------------------------|--------------------------------------------------------------|
| [searchbase](./#)               | Sets the LDAP search base.                                   |
| [object_by_property_name](./#)  | Search for an object containing a property by name in LDAP.  |
| [object_by_property_value](./#) | Search for an object containing a property by value in LDAP. |
| [object_by_dn](./#)             | Search for an object by its distinguishedName in LDAP.       |
| [help](./#)                     | Displays this help message.                                  |
| [exit](./#)                     | Exits the script.                                            |

### searchbase command

Sets LDAP search base.

```
$ ./analysis.py -f ../example_output.json 
[>] Loading ../example_output.json ... done.
[]> searchbase DC=LAB,DC=local
[DC=local,DC=LAB]> searchbase CN=Users,DC=LAB,DC=local
[DC=local,DC=LAB,CN=Users]> 
```

### object_by_property_name command

Search for an object containing a property by name in LDAP.

```
$ ./analysis.py -f ../example_output.json 
[>] Loading ../example_output.json ... done.
[]> object_by_property_name admincount
[CN=Administrator,CN=Users,DC=LAB,DC=local] => adminCount
 - 1
[CN=krbtgt,CN=Users,DC=LAB,DC=local] => adminCount
 - 1
[CN=Domain Controllers,CN=Users,DC=LAB,DC=local] => adminCount
 - 1
[CN=Domain Admins,CN=Users,DC=LAB,DC=local] => adminCount
 - 1
...
[]> 
```

### object_by_property_value command

Search for an object containing a property by value in LDAP.

```
$ ./analysis.py -f ../example_output.json 
[>] Loading ../example_output.json ... done.
[]> object_by_property_value 2021-10-17 13:06:46
[CN=user1,CN=Users,DC=LAB,DC=local] => lastLogon
 - 2021-10-17 13:06:46
[]> 
```

### object_by_dn command

Search for an object by its distinguishedName in LDAP.

```
$ ./analysis.py -f ../example_output.json 
[>] Loading ../example_output.json ... done.
[]> object_by_dn CN=krbtgt,CN=Users,DC=LAB,DC=local
{
    "objectClass": [],
    "cn": "krbtgt",
    "description": "Key Distribution Center Service Account",
    "distinguishedName": "CN=krbtgt,CN=Users,DC=LAB,DC=local",
    "instanceType": 4,
    "whenCreated": "2021-10-01 19:46:23",
    "whenChanged": "2021-10-01 20:01:34",
    "uSNCreated": 12324,
    "memberOf": "CN=Denied RODC Password Replication Group,CN=Users,DC=LAB,DC=local",
    "uSNChanged": 12782,
    "showInAdvancedViewOnly": true,
    "name": "krbtgt",
    "objectGUID": "{b6ea7e4f-658e-49ab-bb0b-dd11eca300d3}",
    "userAccountControl": 514,
    "badPwdCount": 0,
    "codePage": 0,
    "countryCode": 0,
    "badPasswordTime": "1601-01-01 00:00:00",
    "lastLogoff": "1601-01-01 00:00:00",
    "lastLogon": "1601-01-01 00:00:00",
    "pwdLastSet": "2021-10-01 19:46:23",
    "primaryGroupID": 513,
    "objectSid": "S-1-5-21-2088580017-2757022071-1782060386-502",
    "adminCount": 1,
    "accountExpires": "9999-12-31 23:59:59",
    "logonCount": 0,
    "sAMAccountName": "krbtgt",
    "sAMAccountType": 805306368,
    "servicePrincipalName": "kadmin/changepw",
    "objectCategory": "CN=Person,CN=Schema,CN=Configuration,DC=LAB,DC=local",
    "isCriticalSystemObject": true,
    "dSCorePropagationData": [
        "2021-10-01 20:01:34",
        "2021-10-01 19:46:24",
        "1601-01-01 00:04:16"
    ],
    "msDS-SupportedEncryptionTypes": 0
}
```

### help command

Displays the help message with all the possible commands:

```
 - searchbase      Sets LDAP search base. 
 - object_by_property_name Search for an object by property name in LDAP. 
 - object_by_property_value Search for an object by property value in LDAP. 
 - object_by_dn    Search for an object by DN in LDAP. 
 - help            Displays this help message. 
 - exit            Exits the script. 
```

### exit command

Exits the analysis console.