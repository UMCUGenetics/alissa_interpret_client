# Alissa Interpret Public API Python Client
![python-package](https://github.com/UMCUGenetics/alissa_interpret_client/actions/workflows/python-package.yml/badge.svg)
Python client for the Alissa Interpret Public API v2.

## Setup from github
```
python3 -m venv venv
source venv/bin/activate
pip install git+ssh://git@github.com/UMCUGenetics/alissa_interpret_client.git
```
or
```
pip install git+https://github.com/UMCUGenetics/alissa_interpret_client.git
```

## Setup from github in your requirements.txt
Add this line to your requirements file. Edit "branchname" if needed. Specific version tags and commits can also be used.
```
git+https://github.com/UMCUGenetics/alissa_interpret_client.git@branchname#egg=alissa_interpret_client
```
Install packages and Alissa Interpret Public API Python Client
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


## Setup local
```
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Example Python package
```python
from alissa_interpret_client.alissa_interpret import AlissaInterpret

client = AlissaInterpret(
    base_uri='https://umcutrecht.test.alissa.agilent.com',
    client_id='',
    client_secret='',
    username='',
    password=''
)

# Upload vcf file
data_file = client.post_data_file('path/to/file.vcf', type='VCF_FILE'))

# Upload and get patient(s)
patient = client.post_patient(
    accession_number='sample_id',
    family_identifier='family_id',
    gender='gender',
    folder_name='folder_name',
    comments='comments'
)
client.get_patients(accession_number='giab')
client.get_patient(id='27592')


# Create and get lab result(s)
lab_result = client.post_lab_result(patient['id'], data_file['id'], 'sample_name')
client.get_lab_results(patient['id']))
client.get_lab_result(lab_result['id']))

# Get analyses
client.get_analyses(reference='A_U175754CFgiab12878_gvcf-test_2')
client.get_analyses(last_updated_by='melferink')
client.get_analysis(46098)
```

## Example CLI
```bash
source venv/bin/activate
alissa_client upload_vcf <base_uri> <client_id> <client_secret> <username> <password> <path/to/file.vcf>
```
