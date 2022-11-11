from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
import urllib

from . import utils


class AlissaInterpret(object):
    "Alissa Interpret Public Api Client interface"

    def __init__(self, base_uri, client_id, client_secret, username, password):
        """Construct a new Alissa Interpret Public Api Client interface

        :param base_uri: Base uri for the Alissa server
        :param client_id: client id received from Agilent
        :param client_secret: client secret received from Agilent
        :param username: account name of the Alissa user account
        :param password: account password of Alissa the user account
        """
        self.base_uri = base_uri

        # Authenticate with OAuth2 and create a new session
        # ToDo: Add token caching to reuse token between sessions.
        self.session = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))
        self.session.fetch_token(
            token_url=f'{self.base_uri}/auth/oauth/token',
            username=username, password=password,
            client_id=client_id, client_secret=client_secret
        )

    def _get(self, end_point, params=None, **kwargs):
        """
        Get data from the end_point, combining base_uri, api uri and end_point. Return the response as decoded json

        :param end_point: end point to get data from
        :param params: Optional params dict

        """
        uri = f'{self.base_uri}/interpret/api/2/{end_point}'
        response = self.session.get(uri, params=params, **kwargs)
        response.raise_for_status()  # Raise exception on request error
        return response.json()

    def _post(self, end_point, data=None, json=None, **kwargs):
        """
        Post data to the end_point, combining base_uri, api uri and end_point. Return the response as decoded json

        :param end_point: end point to post data to
        :param data: Optional dictionary, list of tuples, bytes, or file-like object
        :param json: Optional json data
        """
        uri = f'{self.base_uri}/interpret/api/2/{end_point}'
        response = self.session.post(uri, data, json, **kwargs)
        response.raise_for_status()  # Raise exception on request error
        return response.json()

    def get_analyses(self, **kwargs):
        """Get all analyses. When kwargs are provided the result is limited to the analyses matching the criteria."""
        params = utils.kwargs_to_dict(**kwargs)
        return self._get('analyses', params)

    def get_analyses_of_patient(self, patient_id):
        """
        Get all analyses of a patient

        :param patient_id: patient id
        """
        return self._get(f'patients/{patient_id}/analyses')

    def get_analysis(self, id):
        """
        Get an analysis via id.

        :param id: analysis id
        """
        return self._get(f'analyses/{id}')

    def get_analysis_sources(self, id):
        """
        Get all sources used in an analysis.

        :param id: analysis id
        """
        return self._get(f'analyses/{id}/sources')

    def get_analysis_report(self, id):
        """
        Get all reports of an analysis.

        :param id: analysis id
        """
        return self._get(f'analyses/{id}/reports')

    def get_data_files(self, **kwargs):
        """Get all data files. When kwargs are provided the result is limited to the data files matching the criteria."""
        params = utils.kwargs_to_dict(**kwargs)
        return self._get('data_files', params)

    def get_data_file(self, id):
        """
        Get an data file via id.

        :param id: data file id
        """
        return self._get(f'data_files/{id}')

    def post_data_file(self, file, type):
        """
        Upload a new file.

        :param file: path to file
        :param type: The type of the data file. This type is used to select the correct file parser.
                     In order to use the default VCF parser the value ‘VCF_FILE’ should be provided.
        """
        files = {'file': open(file, 'r')}
        params = urllib.parse.urlencode({'type': type}, quote_via=urllib.parse.quote)
        return self._post('data_files', files=files, params=params)

    def get_inheritance_analyses(self, analysis_id):
        """
        Get an inheritance analysis via id.

        :param analysis_id: analysis id
        """
        return self._get(f'inheritance_analyses/{analysis_id}')

    def post_inheritance_analyses_variants_export(self, analysis_id, marked_review=False, marked_include_report=False):
        """
        Request an export of all molecular variants from an inheritance analysis via id.

        :param id: analysis id
        :param marked_review: Filter on marked for review
        :param marked_include_report: Filter on marked include in report
        """
        data = {
            'markedForReview': marked_review,
            'markedIncludeInReport': marked_include_report,
        }
        return self._post(f'inheritance_analyses/{analysis_id}/molecular_variants/exports', json=data)

    def get_inheritance_analyses_variants_export(self, analysis_id, export_id):
        """
        Get an requested export of all molecular variants from an inheritance analysis via id.

        :param analysis_id: analysis id
        :param export_id: export id
        """
        return self._get(f'inheritance_analyses/{analysis_id}/molecular_variants/exports/{export_id}')

    def post_inheritance_analyses_cnv_export(self, analysis_id, marked_review=False, marked_include_report=False):
        """
        Request an export of all copy number variants from an inheritance analysis via id.

        :param id: analysis id
        :param marked_review: Filter on marked for review
        :param marked_include_report: Filter on marked include in report
        """
        data = {
            'markedForReview': marked_review,
            'markedIncludeInReport': marked_include_report,
        }
        return self._post(f'inheritance_analyses/{analysis_id}/copy_number_variations/exports', json=data)

    def get_inheritance_analyses_cnv_export(self, analysis_id, export_id):
        """
        Get an requested export of all copy number variants from an inheritance analysis via id.

        :param analysis_id: analysis id
        :param export_id: export id
        """
        return self._get(f'inheritance_analyses/{analysis_id}/copy_number_variations/exports/{export_id}')

    def get_lab_results(self, patient_id):
        """
        Get all lab results of a patient

        :param patient_id: patient id
        """
        return self._get(f'patients/{patient_id}/lab_results')

    def get_lab_result(self, id):
        """
        Get a lab result via its id.

        :param id: lab result id
        """
        return self._get(f'lab_results/{id}')

    def post_lab_result(self, patient_id, data_file_id, sample):
        """
        Create a new lab result.

        :param patient_id: The unique identifier of a patient
        :param data_file_id: The unique identifier of a data file.
        :param sample: Sample name in data file

        """
        data = {
            'dataFileId': data_file_id,
            'sampleIdentifier': sample,
        }
        return self._post(f'patients/{patient_id}/lab_results', json=data)

    def get_patients(self, **kwargs):
        """Get all patients. When kwargs are provided the result is limited to the patients matching the criteria."""
        params = utils.kwargs_to_dict(**kwargs)
        return self._get('patients', params)

    def get_patient(self, id):
        """
        Get an patient via id.

        :param id: patient id
        """
        return self._get(f'patients/{id}')

    def post_patient(self, accession_number, family_identifier, gender, folder_name, comments):
        """
        Create a new patient.

        :param accession_number: The unique identifier of the patient.
        :param family_identifier: The unique identifier of the family.
        :param gender: The gender of the patient.
        :param folder_name: The folder name of the patient.
        :param comments: Comments about the patient.

        """
        data = {
            'accessionNumber': accession_number,
            'comments': comments,
            'familyIdentifier': family_identifier,
            'folderName': folder_name,
            'gender': gender
        }
        return self._post('patients', json=data)

    def get_patient_analyses(self, id):
        """
        Get an patient analysis via id.

        :param id: analysis id
        """
        return self._get(f'patient_analyses/{id}')

    def post_patient_analyses_variants_export(self, analysis_id, marked_review=False, marked_include_report=False):
        """
        Request an export of all molecular variants from an patient analysis via id.

        :param id: analysis id
        :param marked_review: Filter on marked for review
        :param marked_include_report: Filter on marked include in report
        """
        data = {
            'markedForReview': marked_review,
            'markedIncludeInReport': marked_include_report,
        }
        return self._post(f'patient_analyses/{analysis_id}/molecular_variants/exports', json=data)

    def get_patient_analyses_variants_export(self, analysis_id, export_id):
        """
        Get an requested export of all molecular variants from an patient analysis via id.

        :param analysis_id: analysis id
        :param export_id: export id
        """
        return self._get(f'patient_analyses/{analysis_id}/molecular_variants/exports/{export_id}')

    def post_patient_analyses_cnv_export(self, analysis_id, marked_review=False, marked_include_report=False):
        """
        Request an export of all copy number variants from an patient analysis via id.

        :param id: analysis id
        :param marked_review: Filter on marked for review
        :param marked_include_report: Filter on marked include in report
        """
        data = {
            'markedForReview': marked_review,
            'markedIncludeInReport': marked_include_report,
        }
        return self._post(f'patient_analyses/{analysis_id}/copy_number_variations/exports', json=data)

    def get_patient_analyses_cnv_export(self, analysis_id, export_id):
        """
        Get an requested export of all copy number variants from an patient analysis via id.

        :param analysis_id: analysis id
        :param export_id: export id
        """
        return self._get(f'patient_analyses/{analysis_id}/copy_number_variations/exports/{export_id}')
