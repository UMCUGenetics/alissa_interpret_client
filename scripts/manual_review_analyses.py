"""manual_review_analyses.py - counts manual review variants in patient or inheritance (trio) analysis.

ToDo:
    - Discuss with Agilent about directly filtering 'manual review' variants. Exporting all variants takes a lot of time.
"""
import time
from requests.exceptions import HTTPError
from datetime import datetime

from alissa_interpret_client.alissa_interpret import AlissaInterpret

import config


def get_analysis_data(client, type, id):
    if type == 'PATIENT':
        return client.get_patient_analyses(id)
    elif type == 'INHERITANCE':
        return client.get_inheritance_analyses(id)


def post_variants_export(client, type, id):
    if type == 'PATIENT':
        return client.post_patient_analyses_variants_export(id)['exportId']
    elif type == 'INHERITANCE':
        return client.post_inheritance_analyses_variants_export(id)['exportId']


def get_variants_export(client, type, id, export_id):
    if type == 'PATIENT':
        return client.get_patient_analyses_variants_export(id, export_id)
    elif type == 'INHERITANCE':
        return client.get_inheritance_analyses_variants_export(id, export_id)


if __name__ == '__main__':
    # Create Alissa connection
    client = AlissaInterpret(
        base_uri=config.alissa_base_uri, client_id=config.alissa_client_id, client_secret=config.alissa_client_secret,
        username=config.alissa_username, password=config.alissa_password
    )

    # Print header
    print((
        "analysis_reference\tanalysis_type\tcreated_on\tlast_updated_on\t"
        "molecular_variant_count\tcnv_count\tmanual_review_count_Y\tmanual_review_count_Y2\tmanual_review_count_Y3"
    ))

    # Get in progress analyses and < 1 year old.
    filter_date = datetime.now().replace(year=datetime.now().year - 1)
    for analysis in client.get_analyses(status='IN_PROGRESS', created_after=filter_date.strftime('%Y-%m-%dT%H:%M:%S.%f+0000')):
        analysis_id = analysis['id']
        analysis_type = analysis['analysisType']

        # Skip analysis without classification tree or PATIENT/INHERITANCE analysis type
        if not analysis['classificationTreeName'] or analysis_type not in ['PATIENT', 'INHERITANCE']:
            continue

        # Get analysis data and calculate variant counts
        analysis_data = get_analysis_data(client, analysis_type, analysis_id)
        mol_var_count = sum(
            [lab_result['analysisVariantCount']['molecularVariantCount'] for lab_result in analysis_data['labResults']]
        )
        cnv_count = sum(
            [lab_result['analysisVariantCount']['copyNumberVariationCount'] for lab_result in analysis_data['labResults']]
        )

        # skip analysis with cnv results
        if cnv_count >= 1:
            print((
                f"{analysis['reference']}\t{analysis_type}\t{analysis['createdOn'][0:10]}\t"
                f"{analysis['lastUpdatedOn'][0:10]}\t{mol_var_count}\t{cnv_count}\tskipped_analysis_contains_cnv"
            ))
            continue

        # skip analysis with a lot of variants (slow export)
        if mol_var_count > 10000:
            print((
                f"{analysis['reference']}\t{analysis_type}\t{analysis['createdOn'][0:10]}\t"
                f"{analysis['lastUpdatedOn'][0:10]}\t{mol_var_count}\t{cnv_count}\tskipped_large_analysis"
            ))
            continue

        # Export variants and count manual review
        export_id = post_variants_export(client, analysis_type, analysis_id)
        export = None
        while export is None:
            try:
                time.sleep(mol_var_count/100 + 1)  # delay to request exported report, min 1 sec.
                export = get_variants_export(client, analysis_type, analysis_id, export_id)
            except HTTPError:
                pass

        # Count manual review labels
        manual_review_count = [0, 0, 0]  # manual_review labes Y, Y2, Y3 (rare)
        for variant in export:
            variant_labels = variant['classificationTreeLabelsScore']['labels'].lower()

            if 'y,manual review' in variant_labels:
                manual_review_count[0] += 1
            if 'y2,manual review' in variant_labels:
                manual_review_count[1] += 1
            if 'y3 (rare),manual review' in variant_labels:
                manual_review_count[2] += 1

        # Print result
        print((
            f"{analysis['reference']}\t{analysis_type}\t{analysis['createdOn'][0:10]}\t"
            f"{analysis['lastUpdatedOn'][0:10]}\t{mol_var_count}\t{cnv_count}\t"
            f"{manual_review_count[0]}\t{manual_review_count[1]}\t{manual_review_count[2]}"
        ))