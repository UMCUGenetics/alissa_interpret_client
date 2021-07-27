# Alissa Interpret Client
Alissa Interpret Public Api Client

## Setup from github
```
python3 -m venv venv
source venv/bin/activate
pip install git+ssh://github.com/UMCUGenetics/alissa_interpret_client.git
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
    baseuri='https://umcutrecht.test.alissa.agilent.com',
    client_id='',
    client_secret='',
    username='',
    password=''
)

# Upload vcf file
client.post_data_file('path/to/file.vcf', type='VCF_FILE'))

# Upload and get patient(s)
client.get_patients(accessionNumber='giab')
client.get_patient(id='27592')
client.post_patient(
    accession_number='sample_id',
    family_identifier='family_id',
    gender='gender',
    folder_name='folder_name',
    comments='comments'
)

# Get analyses
client.get_analyses(reference='A_U175754CFgiab12878_gvcf-test_2')
client.get_analyses(last_updated_by='melferink')
client.get_analysis(46098)

```

## Example CLI
```bash
source venv/bin/activate
alissa_client upload_vcf <baseuri> <client_id> <client_secret> <username> <password> <path/to/file.vcf>
```