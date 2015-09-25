"""

    nutanix-cluster-info.py

    Connect to a Nutanix cluster, grab some high-level details then generate a PDF from it

    The intention is to use this script as very high-level and *informal* as-built documentation

    Thanks to Christian Johannsen for the ridiculously easy Python code used to consume the Nutanix API [http://datatomix.com/?p=146]

"""

__author__ = "Chris Rasmussen @ Nutanix"
__contributors__ = "Christian Johannsen @ Nutanix, http://github.com/xhtml2pdf"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Chris Rasmussen @ Nutanix"
__email__ = "crasmussen@nutanix.com"
__status__ = "Development"

# required modules
import sys
import json
import fpdf
import os.path
import getpass
import requests
import urllib
import xhtml2pdf
from time import localtime, strftime
from xhtml2pdf import pisa
from string import Template

# set the options you'd like to use
# these will apply for the duration of the script
def set_options():
    global center
    global font
    global font_size
    global page_size

    # make changes here, if required
    center=80
    font="Helvetica"
    font_size=12
    page_size='a4'
    # page_size='letter'

#################################################
#                                               #
#                    STOP                       #
#                  EDITING                      #
#                   HERE                        #
#                    :)                         #
#                                               #
#################################################

def get_options():
    global name
    global cluster_ip
    global username
    global password

    name = raw_input('Please enter your name: ')
    cluster_ip = raw_input('CVM IP address: ')
    username = raw_input('Cluster username: ' )
    password = getpass.getpass()

class ApiClient():

    def __init__(self, cluster_ip, request, username, password):
        self.cluster_ip = cluster_ip
        self.username = username
        self.password = password
        self.base_url = "https://%s:9440/PrismGateway/services/rest/v1" % (self.cluster_ip)
        self.request_url = "%s/%s" % (self.base_url, request)

    def get_info(self):
        s = requests.Session()
        s.auth = (self.username, self.password)
        s.headers.update({'Content-Type': 'application/json; charset=utf-8'})
        data = s.get(self.request_url, verify=False).json()
        return data

# load the JSON file
# at this point we have already confirmed that cluster.json exists
# this method isn't currently used
def process_json():
    with open('cluster.json') as data_file:
        return json.load(data_file)

# do the actual PDF generation
def generate_pdf(data_in):
    # the current time right now
    day=strftime("%d-%b-%Y", localtime())
    time=strftime("%H%M%S", localtime())
    now="%s_%s" % (day, time)

    # the name of the PDF file to generate
    pdf_file="%s_%s_cluster.pdf" % (now, data_in["name"])

    #
    # the next block parses some of the cluster info that currently exists as arrays
    #

    ntp_servers = ""
    for ntp_server in data_in["ntpServers"]:
        ntp_servers = ntp_servers + ", " + ntp_server
    ntp_servers = ntp_servers.strip(',')

    name_servers = ""
    for name_server in data_in["nameServers"]:
        name_servers = name_servers + ", " + name_server
    name_servers = name_servers.strip(',')

    hypervisors = ""
    for hypervisor in data_in["hypervisorTypes"]:
        if hypervisor == "kKvm":
            hypervisor_name = "Acropolis"
        elif hypervisor == "kVMware":
            hypervisor_name = "ESXi"
        elif hypervisor == "kHyperv":
            hypervisor_name = "Hyper-V"
        hypervisors = hypervisors + ", " + hypervisor_name
    hypervisors = hypervisors.strip(',')

    node_models = ""
    for model in data_in["rackableUnits"]:
            node_models = node_models + ", " + model["model"] + " [S/N " + model["serial"] + "]"
    node_models = node_models.strip(',')

    # specify the HTML page template
    source_html_test = Template("""<!doctype html>

                                <html lang="en-us">

                                <head>
                                    <meta charset="utf-8">
                                    <title>Nutanix Cluster Details</title>
                                </head>

                                <body>

                                <p>Nutanix cluster details :: Generated on <strong>$day</strong> at <strong>$now</strong> by <strong>$name</strong> (logged in as $username)</p>

                                <table>
                                   <tr>
                                       <td>Cluster Name</td>
                                       <td>Cluster IP address</td>
                                       <td># Nodes</td>
                                       <td>NOS Version</td>
                                   </tr>
                                   <tr>
                                       <td>$cluster_name</td>
                                       <td>$cluster_ip</td>
                                       <td>$nodes</td>
                                       <td>$nos</td>
                                   </tr>
                                </table>

                                <hr>

                                <table>
                                   <tr>
                                       <td>Hypervisors</td>
                                   </tr>
                                   <tr>
                                       <td>$hypervisors</td>
                                   </tr>
                                </table>

                                <hr>

                                <table>
                                   <tr>
                                       <td>Models</td>
                                   </tr>
                                   <tr>
                                       <td>$models</td>
                                   </tr>
                                </table>

                                <hr>

                                <table>
                                   <tr>
                                       <td>Cluster Timezone</td>
                                       <td>NTP Servers</td>
                                       <td>Name Servers</td>
                                   </tr>
                                   <tr>
                                       <td>$timezone</td>
                                       <td>$ntp_servers</td>
                                       <td>$name_servers</td>
                                   </tr>
                                </table>

                                <hr>

                                <table>
                                    <tr>
                                        <td>Desired RF</td>
                                        <td>Actual RF</td>
                                    </tr>
                                    <tr>
                                        <td>$desired_rf</td>
                                        <td>$actual_rf</td>
                                    </tr>
                                 </table>

                                </body>

                                </html>
    """)

    # substitute the template variables for actual cluster data
    template = source_html_test.safe_substitute(
        day=day,
        now=time,
        name=name,
        username=getpass.getuser(),
        cluster_name=data_in["name"],
        cluster_ip=data_in["clusterExternalIPAddress"],
        nodes=data_in["numNodes"],
        nos=data_in["version"],
        hypervisors=hypervisors,
        models=node_models,
        timezone=data_in["timezone"],
        ntp_servers=ntp_servers,
        name_servers=name_servers,
        desired_rf=data_in["clusterRedundancyState"]["desiredRedundancyFactor"],
        actual_rf=data_in["clusterRedundancyState"]["currentRedundancyFactor"]
    )

    # enable logging so we can see what's going on, then generate the final PDF file
    pisa.showLogging()
    convert_html_to_pdf(template, pdf_file)

    print """
Finished generating PDF file:

%s
""" % pdf_file

# utility function for HTML to PDF conversion
def convert_html_to_pdf(source_html, output_filename):
    # open output file for writing (truncated binary)
    result_file = open(output_filename, "w+b")

    # convert HTML to PDF
    pisaStatus = pisa.CreatePDF(
        source_html,
        dest=result_file)

    # close output file
    result_file.close()

    # return True on success and False on errors
    return pisaStatus.err

def show_intro():
    print """
%s:

Connect to a Nutanix cluster, get some detail about the cluster and generate a basic PDF from those details.

Intended to generate a very high-level and *informal* as-built document.

This script is GPL and there is *no warranty* provided with this script ... AT ALL.
Formal documentation should be generated using best-practice methods that suit your environment.
""" % sys.argv[0]

def main():

    show_intro()

    # first we must make sure the cluster JSON file exists in the currect directory
    # if os.path.isfile( 'cluster.json' ) == True:

    # get the cluster connection info
    get_options()

    # set the script's options, as specified above
    set_options()

    # disable warnings
    # don't do this in production scripts but will disable annoying warnings here
    requests.packages.urllib3.disable_warnings()

    # make sure all required info has been provided
    if not name:
        raise Exception("Name cannot be empty.")
    elif not cluster_ip:
        raise Exception("Cluster IP is required.")
    elif not username:
        raise Exception("Username is required.")
    elif not password:
        raise Exception("Password is required.")
    else:
        # all required info has been provided - we can continue
        # setup the connection info
        client = ApiClient(cluster_ip, "cluster", username, password)
        # connect to the cluster and get the cluster details
        cluster_json = client.get_info()
        # process the JSON data and create the PDF file
        generate_pdf(cluster_json)

if __name__ == "__main__":
    main()