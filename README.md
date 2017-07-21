## Testing

- `pip install git+https://github.com/sivel/ansible-testing.git#egg=ansible_testing`
- `ansible-validate-modules lib/ansible/modules/monitoring/pagerduty_user.py`
- `ansible-validate-modules lib/ansible/modules/monitoring/pagerduty_team.py`
- `ansible-validate-modules lib/ansible/modules/monitoring/pagerduty_contact_method.py`
- `ansible-validate-modules lib/ansible/module_utils/pagerduty_common.py`
- `make pep8` )ignore line length


## Roadmap

### v1

- ansible container
- ansible front-end

### v2

- ansible can send email, and slack notifications
- summary of what tasks have produced changes
- break playbook into roles
- proper return values for the playbook
- document ansible/pd naming scheme
- set crud variables correctly
- why multiple passes before stable [BUG]

### v3

- no_log password warning
- python 2/3 compliant
- unit tests for the module
- tests for the playbook
- urllib for the module
- sanity tests in the module

### v4

- ansible pr
