# Nutanix Cluster Info

## Author

Chris Rasmussen, Systems Engineer, Nutanix (Melbourne, AU)

## Details

Connect to a Nutanix cluster, grab some high-level details then generate a PDF from it.

The intention is to use this script to generate very high-level and *informal* as-built documentation.

## Requirements

-   Python  :)
-   Python 'pip' to install "requests" library
-   Python "requests" library (see below)
-   Python "xhtml2pdf" library (see below)
-   A Nutanix cluster (script has been tested on Nutanix OS >=4.1.4)
-   Credentials for that cluster (read-only is fine)

### Python "requests" library

If you don't have the Python "requests" library you'll need to make sure you have the following commands available:

-   pip

### pip on OS X:

```
sudo easy_install pip
```

### pip on Windows:

[Python on Windows FAQ](https://docs.python.org/2/faq/windows.html)

### "requests" Library installation:

```
pip install requests
```

_Note: Depending on your configuration you may need to run the above command with administrative privilege (sudo on OS X or Run as Administrator on Windows)._

### Python "xhtml2pdf" library

This library, if you don't have it, can be installed on OS X with the following commands, in order:

```
wget -O xhtml2pdf-master.zip https://codeload.github.com/chrisglass/xhtml2pdf/zip/master
unzip xhtml2pdf-master.zip
cd xhtml2pdf-master
sudo python setup.py install
```

The commands to do the same thing on Windows will be _similar_ to the above.

## Script Usage

```
python nutanix-cluster-info.py
```

## Custom Templates

Included with this script should be a file called 'template.html'.

This is an HTML5 document containing a sample layout that can be used with this script.  If you want to modify the generated PDF's content or layout, edit template.html to suit your requirements.

_Please make sure the file is still called 'template.html' when you are finished._

As of the current release, the required fields in template.html are as follows (all are to be prefixed with a '$' symbol, as shown):

-   $cluster_name       [ The name of your Nutanix cluster ]
-   $cluster_ip         [ The cluster's external IP address ]
-   $nodes              [ The number of nodes in the clusters ]
-   $nos                [ The Nutanix OS (NOS) version ]
-   $nos_full           [ The *full* Nutanix OS (NOS) version i.e. the complete build number ]
-   $timezone           [ Cluster time zone ]
-   $ntp_servers        [ Configured NTP servers, if any ]
-   $name_servers       [ Configured name/DNS servers, if any ]
-   $desired_rf         [ The cluster's requested RF (replication factor) ]
-   $actual_rf          [ The cluster's actual RF (replication factor) ]
-   $hypervisors        [ A list of the hypervisors running on this cluster ]
-   $models             [ A list of Nutanix node models in this cluster + their serial numbers ]
-   $containers         [ A list of the cluster's containers, including RF, compression & deduplication summary ]
-   $container_count    [ The total number of containers ]
-   $day                [ The date this script was run ]
-   $now                [ The time this script was run ]
-   $name               [ The name you provide when running the script ]
-   $username           [ The username of the current logged-in user ]
-   $computer_name      [ The current local computer name ]

## Example output using included template

![Example Script Output](https://raw.githubusercontent.com/digitalformula/nutanix-cluster-info/master/screenshot.png?raw=true "Example Script Output")

![Example PDF](https://raw.githubusercontent.com/digitalformula/nutanix-cluster-info/master/screenshot-pdf.png?raw=true "Example PDF")

