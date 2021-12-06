#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Red Hat, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: ovirt_datacenter_info
short_description: Retrieve information about one or more oVirt/RHV datacenters
version_added: "1.0.0"
author:
- "Ondra Machacek (@machacekondra)"
- "Martin Necas (@mnecas)"
description:
    - "Retrieve information about one or more oVirt/RHV datacenters."
    - This module was called C(ovirt_datacenter_facts) before Ansible 2.9, returning C(ansible_facts).
      Note that the M(@NAMESPACE@.@NAME@.ovirt_datacenter_info) module no longer returns C(ansible_facts)!
notes:
    - "This module returns a variable C(ovirt_datacenters), which
       contains a list of datacenters. You need to register the result with
       the I(register) keyword to use it."
options:
    pattern:
        description:
            - "Search term which is accepted by oVirt/RHV search backend."
            - "For example to search datacenter I(X) use following pattern: I(name=X)"
        type: str
extends_documentation_fragment: @NAMESPACE@.@NAME@.ovirt_info
'''

EXAMPLES = '''
# Examples don't contain auth parameter for simplicity,
# look at ovirt_auth module to see how to reuse authentication:

# Gather information about all data centers which names start with C(production):
- @NAMESPACE@.@NAME@.ovirt_datacenter_info:
    pattern: name=production*
  register: result
- ansible.builtin.debug:
    msg: "{{ result.ovirt_datacenters }}"
'''

RETURN = '''
ovirt_datacenters:
    description: "List of dictionaries describing the datacenters. Datacenter attributes are mapped to dictionary keys,
                  all datacenters attributes can be found at following url: http://ovirt.github.io/ovirt-engine-api-model/master/#types/data_center."
    returned: On success.
    type: list
'''

import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.@NAMESPACE@.@NAME@.plugins.module_utils.ovirt import (
    check_sdk,
    create_connection,
    get_dict_of_struct,
    ovirt_info_full_argument_spec,
)


def main():
    argument_spec = ovirt_info_full_argument_spec(
        pattern=dict(default='', required=False),
    )
    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
    )

    check_sdk(module)
    if module.params['fetch_nested'] or module.params['nested_attributes']:
        module.deprecate(
            "The 'fetch_nested' and 'nested_attributes' are deprecated please use 'follow' parameter",
            version='3.0.0',
            collection_name='ovirt.ovirt'
        )

    try:
        auth = module.params.pop('auth')
        connection = create_connection(auth)
        datacenters_service = connection.system_service().data_centers_service()
        datacenters = datacenters_service.list(
            search=module.params['pattern'],
            follow=",".join(module.params['follow'])
        )
        result = dict(
            ovirt_datacenters=[
                get_dict_of_struct(
                    struct=d,
                    connection=connection,
                    fetch_nested=module.params.get('fetch_nested'),
                    attributes=module.params.get('nested_attributes'),
                ) for d in datacenters
            ],
        )
        module.exit_json(changed=False, **result)
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())
    finally:
        connection.close(logout=auth.get('token') is None)


if __name__ == '__main__':
    main()
