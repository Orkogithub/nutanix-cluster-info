# Nutanix Cluster Info

## Author

Chris Rasmussen, Systems Engineer, Nutanix (Melbourne, AU)

## Details

Connect to a Nutanix cluster, grab some high-level details then generate a PDF from it

The intention is to use this script as very high-level and *informal* as-built documentation

## Requirements

-   Python  :)
-   A Nutanix cluster (script has been tested on Nutanix OS >=4.1.4)
-   Credentials for that cluster (read-only is fine)

## Usage

```
python ./nutanix-cluster-info.py
```

## Example Output

![Example Script Output](https://raw.githubusercontent.com/digitalformula/nutanix-cluster-info/master/screenshot.png?raw=true "Example Script Output")

![Example PDF](https://raw.githubusercontent.com/digitalformula/nutanix-cluster-info/master/screenshot-pdf.png?raw=true "Example PDF")
