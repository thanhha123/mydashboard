# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from horizon import views
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import json
import urllib2


def getToken(url, iduser, passuser, idproject):
    """
    Returns a token to the user given a tenant,
    user name, password, and OpenStack API URL.
    """
    url = url + '/auth/tokens'
    tokenRequest = urllib2.Request(url)
    tokenRequest.add_header("Content-type", "application/json")
    jsonPayload = json.dumps(
        {"auth": {"identity": {"methods": ["password"], "password": {"user": {"id": iduser, "password": passuser}}},"scope": {"project": {"id": idproject}}}})
    request = urllib2.urlopen(tokenRequest, jsonPayload)
    request.close()
    return request.info().getheader('X-Subject-Token')


def getdataJson(url, token):
    url = 'http://172.16.69.46:' + url
    hypervisorInfoRequest = urllib2.Request(url)
    hypervisorInfoRequest.add_header("X-Auth-Token", token)
    request = urllib2.urlopen(hypervisorInfoRequest)
    return json.loads(request.read())




def index(request):
    adminToken = getToken('http://172.16.69.46:35357/v3', 'c66fc07c828b4ecd844555e7181850b9', 'Welcome123',
                          'fcafe2cfaa024693b413bce026aee34b')
    dic_h = {}
    list_h = []
    hype_data = getdataJson('8774/v2/os-hypervisors', adminToken)
    for i in range(0, len(hype_data['hypervisors'])):
         list_h.append(hype_data['hypervisors'][i]['hypervisor_hostname'])
    dic_h = { 'computes': list_h}
    if request.method == 'POST':
        compute = request.POST.get('computes')
        return HttpResponseRedirect(reverse('horizon:mydashboard:mypanel2:listvm',kwargs={'com': compute}))
    else:
        pass

    return render(request, 'mydashboard/mypanel2/index.html', dic_h)



def listvm(request,com):
    adminToken = getToken('http://172.16.69.46:35357/v3', 'c66fc07c828b4ecd844555e7181850b9', 'Welcome123',
                          'fcafe2cfaa024693b413bce026aee34b')
    dic_vm = {}
    list_vm = []
    vm_data = getdataJson('8774/v2/servers/detail?node='+com, adminToken)
    for i in range(0, len(vm_data['servers'])):
         list_vm.append(vm_data['servers'][i]['name']+' ('+vm_data['servers'][i]['id'] + ")")
    list_vm2 = [str(r) for r in list_vm] # bo ki tu u'string'
    dic_vm = {'vms': list_vm2}

    list_h = []
    dic_com_id = {}
    hype_data = getdataJson('8774/v2/os-hypervisors', adminToken)
    for i in range(0, len(hype_data['hypervisors'])):
        list_h.append(hype_data['hypervisors'][i]['hypervisor_hostname'])
        dic_com_id[hype_data['hypervisors'][i]['hypervisor_hostname']] = hype_data['hypervisors'][i]['id']
    list_h.remove(com)
    dic_vm['computes'] = list_h


    if request.method == 'POST':
        compute_des = request.POST.get('computes')
        compute_des_id = dic_com_id[compute_des]
        vm = request.POST.get('vms')

        result = check_migrate(vm.split('(')[1][:-1], compute_des_id)

        return render(request, 'mydashboard/mypanel2/result.html', {'result':result})
    else:
        pass

    return render(request, 'mydashboard/mypanel2/listvm.html', dic_vm)




def check_migrate(vm,compute_des_id):
    adminToken = getToken('http://172.16.69.46:35357/v3', 'c66fc07c828b4ecd844555e7181850b9', 'Welcome123',
                          'fcafe2cfaa024693b413bce026aee34b')
    hype_data = getdataJson('8774/v2/os-hypervisors/' + str(compute_des_id), adminToken)
    flavor_vm_data = getdataJson('8774/v2/servers/' + vm, adminToken)
    flavor_vm_id = flavor_vm_data['server']['flavor']['id']
    info_vm_data = getdataJson("8774/v2/flavors/" + flavor_vm_id, adminToken)

    hyper_ram_used = hype_data['hypervisor']['memory_mb_used']
    hyper_ram_total = hype_data['hypervisor']['memory_mb']
    hyper_vpus_used = hype_data['hypervisor']['vcpus_used']
    hyper_vpus_total = hype_data['hypervisor']['vcpus']
    hyper_ram_limit = hyper_ram_total * 1.5
    hyper_vcpus_limit = hyper_vpus_total * 16

    if (info_vm_data['flavor']['ram'] + hyper_ram_used) < hyper_ram_limit and (
        info_vm_data['flavor']['vcpus'] + hyper_vpus_used) < hyper_vcpus_limit:
        return "OK, du tai nguyen "
    else:
        return "Fail, khong du tai nguyen"


'''

    template_name = 'mydashboard/mypanel2/index.html'

    def get_data(self, request, context, *args, **kwargs):
        # Add data to the context here...
        return context

'''