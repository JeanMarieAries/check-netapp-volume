# check-netapp-volume
##Nagios plugin for Netapp volume check



check-netapp-volume is a python2.7/nagios plugin that allow you to check volume space, according thresholds defined.
It use SSH connection to connect to the filer, get the entire volumes list, parse and output the result.


    Example of run : 
        check_netapp-2.7.py -H BIGFiler -U supervision -P superpassword -I vol1,vol3 -W 70 -C 95


'-I' allow you to ignore volume from the check (vol name or partial vol name not regexp)

    Example :
        If you want to exclude a volume named 'DataDBOracle', you can use 
        
            -I Data
            or
            -I DBOra
    
    -I is case sensitive.
    
    

###Why using SSH instead of SNMP ?

When Netapp filer is in heavily load, browsing MIB from snmp client does not work very well, because we need to make many requests to the filer to get the stats. The plugin will report UNKNOWN state, because of timed out.

With SSH, we only need one connection, and one remote command execution to get the volume list. (vol size, usage)
Calculation and report are made by the script. 



##Todo before use



#####On the Netapp host

We need a SSH account to connect to the filer, with minimal privileges (for security reason).
This can be done by creating a Netapp role (associated with the 'df' command), a group and a user.

    Example :
        filer# useradmin role add only_ssh -a login-ssh
        filer# useradmin role add df_command -a cli-df*
        filer# useradmin group add ssh_supervision -r only_ssh,df_command
        filer# useradmin user add supervision -g ssh_supervision
        
    now you can use 'supervision' as the SSH user.
    
    
    
#####On the Nagios host

check-netapp-volume is a python script that use a very limited number of modules.
Before running the script, you have to install the 'fabric' module, with pip :

    pip install fabric
  
If you use python version before 2.7.9, you must install pip manually :
    https://pip.pypa.io/en/stable/installing/
  
#####On the script header (optional)

there is a couple of variable that you can define (local directory use to store the SSH stdout, and the file name) 

see the help script for more details
