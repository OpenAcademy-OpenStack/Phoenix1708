import os
import time
import keystoneclient.v2_0.client as ksclient
import glanceclient.v2.client as glclient
import novaclient.v1_1.client as nvclient
from credentials import get_nova_creds
from credentials import get_keystone_creds

creds = get_keystone_creds()
nova_creds = get_nova_creds()

keystone = ksclient.Client(**creds)
glance_endpoint = keystone.service_catalog.url_for(service_type='image',
                                                   endpoint_type='publicURL')
glance = glclient.Client(glance_endpoint, token=keystone.auth_token)
nova = nvclient.Client(**nova_creds)

images = glance.images.list()

# for each image retrieved check whether the 'name' contains 'ubuntu'
for image in images:
	if 'ubuntu' in image['name']:
		print 'id: ', image['id'], '\n', 'name: ', image['name']
		# find a built in flavor
		flavor = nova.flavors.find(name="m1.small")
		# start a instance with the id of the image as name
		instance = nova.servers.create(name=image['id'], 
						image=image, 
						flavor=flavor)
		# check whether the instance has been successfully started
		status = instance.status
		print "status: %s" %instance.status
		while status == 'BUILD':
    			time.sleep(5)
    			instance = nova.servers.get(instance.id)
			print "status: %s" %instance.status
			if status == 'ERROR' or 'ACTIVE':
				break
