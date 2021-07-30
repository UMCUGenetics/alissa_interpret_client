from alissa_interpret_client import utils


def test_snake_to_camel_case():
    assert utils.snake_to_camel_case('last_updated_by') == 'lastUpdatedBy'
    assert utils.snake_to_camel_case('reference') == 'reference'
    assert utils.snake_to_camel_case('accessionNumber') == 'accessionNumber'


def test_kwargs_to_dict():
    assert utils.kwargs_to_dict(accession_number='giab') == {'accessionNumber': 'giab'}
    assert utils.kwargs_to_dict(accession_number='giab', last_updated_by='melferink') == {
        'accessionNumber': 'giab', 'lastUpdatedBy': 'melferink'
    }
    assert utils.kwargs_to_dict(accession_number='giab', last_updated_by='') == {'accessionNumber': 'giab'}
