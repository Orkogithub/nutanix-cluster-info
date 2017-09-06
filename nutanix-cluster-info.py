"""

    nutanix-cluster-info.py

    Connect to a Nutanix cluster, grab some high-level details then generate a PDF from it

    The intention is to use this script as very high-level and *unofficial* as-built documentation

    You would need to *heavily* modify this script for use in a production environment so that it contains appropriate error-checking, exception handling and data collection

"""

__author__ = "Chris Rasmussen @ Nutanix"
__version__ = "1.2"
__maintainer__ = "Chris Rasmussen @ Nutanix"
__email__ = "crasmussen@nutanix.com"
__status__ = "Development/Demo"

# required modules
import sys
import json
import os.path
import socket
import getpass
from time import localtime, strftime
from string import Template

import urllib.request
import urllib.parse
import urllib3
import requests
from requests.auth import HTTPBasicAuth
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration

def get_options():
    global name
    global cluster_ip
    global username
    global password

    name = input('Please enter your name: ')
    cluster_ip = input('CVM IP address: ')
    username = input('Cluster username: ' )
    password = getpass.getpass()

class ApiClient():

    def __init__(self, cluster_ip, request, username, password):
        self.cluster_ip = cluster_ip
        self.username = username
        self.password = password
        self.base_url = "https://%s:9440/api/nutanix/v2.0" % (self.cluster_ip)
        self.request_url = "%s/%s" % (self.base_url, request)

    def get_info(self):
        
        urllib3.disable_warnings()
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        try:
            r = requests.get(self.request_url, verify=False, headers=headers, auth=HTTPBasicAuth(self.username, self.password), timeout=5)
        except requests.ConnectTimeout:
            print('Connection timed out while connecting to %s. Please check your connection, then try again.' % self.cluster_ip)
            sys.exit()
        except requests.ConnectionError:
            print('An error occurred while connecting to %s. Please check your connection, then try again.' % self.cluster_ip)
            sys.exit()
        except requests.HTTPError:
            print('An HTTP error occurred while connecting to %s. Please check your connection, then try again.' % self.cluster_ip)
            sys.exit()
        
        if r.status_code >= 500:
            print('An HTTP server error has occurred (%s)' % r.status_code ) 
        else:
            if r.status_code == 401:
                print('An authentication error occurred while connecting to %s. Please check your credentials, then try again.' % self.cluster_ip)
                sys.exit()
            if r.status_code >= 401:
                print('An HTTP client error has occurred (%s)' % r.status_code )
                sys.exit()
            else:
                print('Connected and authenticated successfully.')
        
        return(r.json())
        
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
    for ntp_server in cluster_in["ntp_servers"]:
        ntp_servers = ntp_servers + ", " + ntp_server
    ntp_servers = ntp_servers.strip(',')

    name_servers = ""
    for name_server in cluster_in["name_servers"]:
        name_servers = name_servers + ", " + name_server
    name_servers = name_servers.strip(',')

    hypervisors = ""
    for hypervisor in cluster_in["hypervisor_types"]:
        if hypervisor == "kKvm":
            hypervisor_name = "AHV"
        elif hypervisor == "kVMware":
            hypervisor_name = "ESXi"
        elif hypervisor == "kHyperv":
            hypervisor_name = "Hyper-V"
        elif hypervisor == "kXen":
            hypervisor_name = "Xen Server"
        hypervisors = hypervisors + ", " + hypervisor_name
    hypervisors = hypervisors.strip(',')

    node_models = ""
    for model in cluster_in["rackable_units"]:
        try:
            node_models = node_models + ", " + model["model_name"] + " [ S/N " + model["serial"] + " ]"
        except TypeError:
            node_models = 'None available'
    node_models = node_models.strip(',')

    containers = ""
    for container in container_in["entities"]:
        containers = containers + "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (container["name"], str(container["replication_factor"]), str(container["compression_enabled"]), str(container["on_disk_dedup"]) )

    # specify the HTML page template
    # at this point we have already verified that template.html exists, at least
    if os.path.isfile( "./templates/nutanix.html" ):
        template_name = "./templates/nutanix.html"
    else:
        template_name = "./templates/template.html"

    # load the HTML content from the template
    with open( template_name, "r") as data_file:
        source_html = Template( data_file.read() )

    # substitute the template variables for actual cluster data
    template = source_html.safe_substitute(
        day=day,
        now=time,
        name=name,
        username=getpass.getuser(),
        cluster_name=str(cluster_in["name"]),
        cluster_ip=str(cluster_in["cluster_external_ipaddress"]) if cluster_in["cluster_external_ipaddress"] else "Not set",
        nodes=str(cluster_in["num_nodes"]),
        nos=str(cluster_in["version"]),
        hypervisors=hypervisors,
        models=str(node_models),
        timezone=str(cluster_in["timezone"]),
        ntp_servers=str(ntp_servers),
        name_servers=str(name_servers),
        desired_rf=cluster_in["cluster_redundancy_state"]["desired_redundancy_factor"],
        actual_rf=cluster_in["cluster_redundancy_state"]["current_redundancy_factor"],
        nos_full=str(cluster_in["full_version"]),
        containers=str(containers),
        container_count=container_in["metadata"]["grand_total_entities"],
        computer_name=socket.gethostname()
    )
    
    # generate the final PDF file
    convert_html_to_pdf(template, pdf_file)

    print("""Finished generating PDF file: %s """ % pdf_file)

# utility function for HTML to PDF conversion
def convert_html_to_pdf(source_html, output_filename):
    # open output file for writing (truncated binary)
    # result_file = open(output_filename, "w+b")
        
    font_config = FontConfiguration()
        
    # HTML(string=source_html).write_pdf(output_filename,stylesheets=[CSS(string='@font-face {font-family: grb;src: url(./resources/Bariol.ttf);}#header_content {left: 50pt; width: 512pt; top: 50pt; height: 40pt;}#footer_content {left: 50pt; width: 512pt; top: 772pt; height: 20pt;}#main_content {left: 50pt; width: 512pt; top: 90pt; height: 632pt;}margin: 2cm;body { font-family: grb; font-size: 120%; }h1 { color: #3f6fb4; }tr.final { border-bottom: 1px solid #eee; padding: 3px 0; }tr.footer { padding: 5px; text-align: center; }div#footer_content { text-align: center; }h1 { font-family: Gentium }', font_config=font_config)])
    
    x=HTML(string=source_html)
    x.write_pdf(output_filename,stylesheets=[CSS(string='''
        @font-face { font-family: bariol; src: url(Bariol.ttf); }
        h1 { color: #3f6fb4; }
        body { font-family: sans-serif; font-size: 80%; }
        #main_content { margin: 0 auto; text-align: left; width: 75%; }
        table{ width: 100%; border-bottom: 1px solid #ddd; padding-bottom: 20px; }
        tr.final { border-bottom: 1px solid #eee; padding: 3px 0; }
        tr.footer { padding: 5px; text-align: center; }
        tr.tr_header { font-weight: bold; }
        div#footer_content { text-align: center; margin-top: 20px; }
    ''',font_config=font_config)])    
    
    sys.exit()
    
    # convert HTML to PDF
    #pisaStatus = pisa.CreatePDF(
    #    source_html,
    #    dest=result_file)

    # close output file
    # result_file.close()

    # return True on success and False on errors
    # return pisaStatus.err

def show_intro():
    print( """
%s:

Connect to a Nutanix cluster, get some detail about the cluster and generate a basic PDF from those details.

Intended to generate a very high-level and *unofficial* as-built document.

This script is GPL and there is *no warranty* provided with this script ... AT ALL.  You can use and modify this script as you wish, but please make sure the changes are appropriate for the intended environment.

Formal documentation should always be generated using best-practice methods that suit your environment.
""" % sys.argv[0])

def main():

    if os.path.isfile("./templates/nutanix.html"):
        show_intro()

        # first we must make sure the cluster JSON file exists in the currect directory
        # if os.path.isfile( 'cluster.json' ) == True:

        # get the cluster connection info
        get_options()

        # disable warnings
        # don't do this in production scripts but will disable annoying warnings here
        # requests.packages.urllib3.disable_warnings()

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
            container_client = ApiClient(cluster_ip, "storage_containers", username, password)
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
        print("\nNo HTML templates were found in the 'templates' directory.  You'll need one of these to continue.\n")

if __name__ == "__main__":
    main()
