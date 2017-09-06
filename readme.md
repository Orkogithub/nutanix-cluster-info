# Nutanix Cluster Info

"As-built" documentation script for use with Nutanix clusters.

## Disclaimer

This is *not* a production-grade script.  Please make sure you add appropriate exception handling and error-checking before running it in production.

## Author

Chris Rasmussen, Solutions Architect, Nutanix (Melbourne, AU)

## Changes

2017.09.06 - Published new version based on Python 3

## Details

Connect to a Nutanix cluster, grab some high-level details then generate a PDF from it.

The intention is to use this script to generate very high-level and *unofficial* as-built documentation.

The other idea is for you, the user, to take this script and modify it to suit your client requirements.

## Requirements (new/Weasy-based version - Easy)

### Mac

Install [HomeBrew](https://brew.sh/):

```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Install WeasyPrint dependencies:

```
brew install python3 cairo pango gdk-pixbuf libffi
pip3 install requests
```

Install WeasyPrint:

Note: This step may require elevated privileges, depending on your system (i.e. use 'sudo').

```
pip3 install WeasyPrint
```

### Windows

Follow the instructions here: [http://weasyprint.readthedocs.io/en/latest/install.html#windows](http://weasyprint.readthedocs.io/en/latest/install.html#windows)

Sorry, I haven't been able to test any of this on Windows just yet.

## Requirements (old/XHTML2PDF version - Painful, new version recommended)

I'm leaving this section in the script readme, just in case someone needs it later.  I strongly recommend using the new Python3-based version, though.

-   Python 2.7
-   Python 'pip' to install "requests" library
-   Python "requests" library (see below)
-   Python "xhtml2pdf" library (see below)
-   A Nutanix cluster (script has been tested on Acropolis OS >=4.1.4 and will also function quite happily on Nutanix Community Edition)
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

Automatically/easy way:

```
sudo pip install xhtml2pdf
```

Manually:

```
wget -O xhtml2pdf-master.zip https://codeload.github.com/chrisglass/xhtml2pdf/zip/master
unzip xhtml2pdf-master.zip
cd xhtml2pdf-master
sudo python setup.py install
```

### Optional Installation:

When installing xhtml2pdf on Mac OS X Sierra (10.12), I ran into an error that made the script complain about missing 'viewkeys' imports.  To fix the issue I had to install the html5 library, as follows:

```
sudo -H pip install html5lib==1.0b8
```

The commands to do the same thing on Windows will be _similar_ to the above.

## Script Usage (OS X)

```
/usr/local/bin/python3 nutanix-cluster-info.py
```

## Custom Templates

Included with this script is an HTML file called 'templates/nutanix.html'.

### Summary

This is an HTML5 document containing a sample layout that can be used with this script.  If you want to modify the generated PDF's content or layout, edit templates/nutanix.html to suit your requirements.

### Available Fields

_Please make sure the file is saved as 'templates/nutanix.html' when you are finished._

As of the current release, the required fields in templates/nutanix.html are as follows (all are to be prefixed with a '$' symbol, as shown):

-   $cluster_name       [ The name of your Nutanix cluster ]
-   $cluster_ip         [ The cluster's external IP address ]
-   $nodes              [ The number of nodes in the clusters ]
-   $nos                [ The Acropolis (AOS) version ]
-   $nos_full           [ The *full* Acropolis (AOS) version i.e. the complete build number ]
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

### PDF Formatting

As of version 1.2, this script uses 'WeasyPrint' for PDF generation.  Please see the [WeasyPrint docs](http://weasyprint.readthedocs.io/en/latest) for detailed information on the available formatting options.
