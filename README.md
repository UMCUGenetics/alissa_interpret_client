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
pip install git+ssh://github.com/UMCUGenetics/alissa_interpret_client.git
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

# Get analyses
client.get_analyses(reference='A_U175754CFgiab12878_gvcf-test_2')
client.get_analyses(last_updated_by='melferink')
client.get_analysis(46098)

# Upload vcf file
client.post_data_file('path/to/file.vcf', type='VCF_FILE'))
```

## Example CLI
```bash
source venv/bin/activate
alissa_client upload_vcf <baseuri> <client_id> <client_secret> <username> <password> <path/to/file.vcf>
```