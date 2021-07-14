# Alissa Interpret Client
Alissa Interpret Public Api Client

## Setup from github
```
python3 -m venv venv
source venv/bin/activate
pip install git+ssh://github.com/UMCUGenetics/alissa_interpret_client.git
```

## Example
```python
from alissa_interpret_client.alissa_interpret import AlissaInterpret

client = AlissaInterpret(
    baseuri='https://umcutrecht.test.alissa.agilent.com',
    client_id='',
    client_secret='',
    username='',
    password=''
)

print(client.get_analyses(reference='A_U175754CFgiab12878_gvcf-test_2'))
print(client.get_analyses(last_updated_by='melferink'))
print(client.get_analysis(46098))
```