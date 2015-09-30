"""

    nutanix-cluster-info.py

    Connect to a Nutanix cluster, grab some high-level details then generate a PDF from it

    The intention is to use this script as very high-level and *informal* as-built documentation

    Thanks to Christian Johannsen for the ridiculously easy Python method used to consume the Nutanix API [http://datatomix.com/?p=146]

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
import os.path
import socket
import getpass
import requests
import urllib
import xhtml2pdf
from time import localtime, strftime
from xhtml2pdf import pisa
from string import Template

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
# this method isn't used right now
def process_json():
    with open('cluster.json') as data_file:
        return json.load(data_file)

# load JSON data from an on-disk file
def load_json(file):
    with open(file) as data_file:
        return json.load(data_file)

# do the actual PDF generation
def generate_pdf(cluster_in, container_in):
    # the current time right now
    day=strftime("%d-%b-%Y", localtime())
    time=strftime("%H%M%S", localtime())
    now="%s_%s" % (day, time)

    # the name of the PDF file to generate
    pdf_file="%s_%s_cluster.pdf" % (now, cluster_in["name"])

    #
    # the next block parses some of the cluster info that currently exists as arrays
    #

    ntp_servers = ""
    for ntp_server in cluster_in["ntpServers"]:
        ntp_servers = ntp_servers + ", " + ntp_server
    ntp_servers = ntp_servers.strip(',')

    name_servers = ""
    for name_server in cluster_in["nameServers"]:
        name_servers = name_servers + ", " + name_server
    name_servers = name_servers.strip(',')

    hypervisors = ""
    for hypervisor in cluster_in["hypervisorTypes"]:
        if hypervisor == "kKvm":
            hypervisor_name = "Acropolis"
        elif hypervisor == "kVMware":
            hypervisor_name = "ESXi"
        elif hypervisor == "kHyperv":
            hypervisor_name = "Hyper-V"
        hypervisors = hypervisors + ", " + hypervisor_name
    hypervisors = hypervisors.strip(',')

    node_models = ""
    for model in cluster_in["rackableUnits"]:
        node_models = node_models + ", " + model["model"] + " [ S/N " + model["serial"] + " ]"
    node_models = node_models.strip(',')

    containers = ""
    for container in container_in["entities"]:
        containers = containers + container["name"] + " [ RF: " + str(container["replicationFactor"]) + ", compression: " + str(container["compressionEnabled"]) + ", deduplication: " + str(container["onDiskDedup"]) + " ]<br>"
    containers = containers.strip(',')

    # specify the HTML page template
    with open( "template.html", "r") as data_file:
        source_html = Template( data_file.read() )

    # substitute the template variables for actual cluster data
    template = source_html.safe_substitute(
        day=day,
        now=time,
        name=name,
        username=getpass.getuser(),
        cluster_name=cluster_in["name"],
        cluster_ip=cluster_in["clusterExternalIPAddress"] if cluster_in["clusterExternalIPAddress"] else "Not set",
        nodes=cluster_in["numNodes"],
        nos=cluster_in["version"],
        hypervisors=hypervisors,
        models=node_models,
        timezone=cluster_in["timezone"],
        ntp_servers=ntp_servers,
        name_servers=name_servers,
        desired_rf=cluster_in["clusterRedundancyState"]["desiredRedundancyFactor"],
        actual_rf=cluster_in["clusterRedundancyState"]["currentRedundancyFactor"],
        nos_full=cluster_in["fullVersion"],
        containers=containers,
        computer_name=socket.gethostname()
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

This script is GPL and there is *no warranty* provided with this script ... AT ALL.  You can use and modify this script as you wish, but please make sure the changes are appropriate for the intended environment.

Formal documentation should always be generated using best-practice methods that suit your environment.
""" % sys.argv[0]

def main():

    if os.path.isfile("template.html"):
        show_intro()

        # first we must make sure the cluster JSON file exists in the currect directory
        # if os.path.isfile( 'cluster.json' ) == True:

        # get the cluster connection info
        get_options()

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
            cluster_client = ApiClient(cluster_ip, "cluster", username, password)
            container_client = ApiClient(cluster_ip, "containers", username, password)
            # connect to the cluster and get the cluster details
            cluster_json = cluster_client.get_info()
            container_json = container_client.get_info()

            # if you have data in a JSON file you can load them this way instead
            # this section would likely only be used in modified versions of this script where a live Nutanix cluster is not available
            # with open('cluster.json') as data_file:
                # cluster_json = json.load(data_file)
            # with open('container.json') as data_file:
                # container_json = json.load(data_file)

            # process the JSON data and create the PDF file
            generate_pdf(cluster_json, container_json)

    else:
        print "\nUnfortunately template.html was not found in the current directory.  You'll need this file to continue.\n"

if __name__ == "__main__":
    main()

