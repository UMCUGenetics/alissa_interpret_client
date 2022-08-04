"""manual_review_analyses.py - counts manual review variants in patient or inheritance (trio) analysis.
    Script functionality is based on GENOOM072 - NGS Sequentie-analyse m.b.v. Agilent Alissa Interpret.
ToDo:
    - Discuss with Agilent about directly filtering 'manual review' variants. Exporting all variants takes a lot of time.
"""
import argparse
import sys
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


def post_variants_export(client, analysis_type, variant_type, analysis_id):
    if analysis_type == 'PATIENT':
        if variant_type == 'molecular_variant':
            return client.post_patient_analyses_variants_export(analysis_id)['exportId']
        elif variant_type == 'copy_number_variation':
            return client.post_patient_analyses_cnv_export(analysis_id)['exportId']
    elif analysis_type == 'INHERITANCE':
        if variant_type == 'molecular_variant':
            return client.post_inheritance_analyses_variants_export(analysis_id)['exportId']
        elif variant_type == 'copy_number_variation':
            return client.post_inheritance_analyses_cnv_export(analysis_id)['exportId']


def get_variants_export(client, analysis_type, variant_type, analysis_id, export_id):
    if analysis_type == 'PATIENT':
        if variant_type == 'molecular_variant':
            return client.get_patient_analyses_variants_export(analysis_id, export_id)
        elif variant_type == 'copy_number_variation':
            return client.get_patient_analyses_cnv_export(analysis_id, export_id)
    elif analysis_type == 'INHERITANCE':
        if variant_type == 'molecular_variant':
            return client.get_inheritance_analyses_variants_export(analysis_id, export_id)
        elif variant_type == 'copy_number_variation':
            return client.get_inheritance_analyses_cnv_export(analysis_id, export_id)


def get_variants(client, analysis_type, variant_type, analysis_id, variant_count):
    export_id = post_variants_export(client, analysis_type, variant_type, analysis_id)
    export = None
    while export is None:
        try:
            time.sleep(variant_count/100 + 1)  # delay to request exported report, min 1 sec.
            export = get_variants_export(client, analysis_type, variant_type, analysis_id, export_id)
        except HTTPError:
            pass

    return export


def count_manual_review_labels(variants_export):
    manual_review_count = [0, 0, 0]  # manual_review labes Y, Y2, Y3 (rare)
    for variant in variants_export:
        variant_labels = variant['classificationTreeLabelsScore']['labels'].lower()  # Correct upercase labels

        if 'y,manual review' in variant_labels:
            manual_review_count[0] += 1
        if 'y2,manual review' in variant_labels:
            manual_review_count[1] += 1
        if 'y3 (rare),manual review' in variant_labels:
            manual_review_count[2] += 1

    return manual_review_count


if __name__ == '__main__':
    # Command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'database_file',
        help='Path to (new or existing) database file containing data from earlier export, used to skip reoccurring exports.'
    )
    args = parser.parse_args()

    database_columns = [
        "analysis_reference", "analysis_type", "analysis_pipeline", "target_panel", "created_on", "last_updated_on",
        "molecular_variant_count", "cnv_count", "manual_review_count_Y", "manual_review_count_Y2", "manual_review_count_Y3",
        "CNV_manual_review_count_Y", "CNV_manual_review_count_Y2", "CNV_manual_review_count_Y3",
    ]
    database_analyses = {}

    # Import data from database file
    try:
        with open(args.database_file, 'r') as database_file:
            header = database_file.readline().strip().split('\t')
            if header != database_columns:
                sys.exit('Error: Database does not contain expected columns.')

            for line in database_file:
                data = line.strip().split('\t')
                database_analyses[data[header.index('analysis_reference')]] = data
    except FileNotFoundError:
        print("Warning: Database not found, creating new database.")

    # Create Alissa connection
    client = AlissaInterpret(
        base_uri=config.alissa_base_uri, client_id=config.alissa_client_id, client_secret=config.alissa_client_secret,
        username=config.alissa_username, password=config.alissa_password
    )

    # Update database file
    with open(args.database_file, 'w') as database_file:
        # Print header
        print("\t".join(database_columns), file=database_file)

        # Get in progress analyses and < 1 year old.
        filter_date = datetime.now().replace(year=datetime.now().year - 1)
        for analysis in client.get_analyses(
            status='IN_PROGRESS', created_after=filter_date.strftime('%Y-%m-%dT%H:%M:%S.%f+0000')
        ):
            analysis_id = analysis['id']
            analysis_type = analysis['analysisType']
            analysis_reference = analysis['reference']
            analysis_pipeline = analysis['analysisPipelineName']
            analysis_panel = ','.join(analysis['targetPanelNames'])

            # Lookup analysis in database, if in database print previous result and skip.
            if analysis_reference in database_analyses:
                print("\t".join(database_analyses[analysis_reference]), file=database_file)
                continue

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

            # skip analysis with a lot of variants (slow export)
            if mol_var_count > 10000:
                result = 'skipped_large_analysis'

            else:
                molecular_variants = get_variants(client, analysis_type, 'molecular_variant', analysis_id, mol_var_count)
                copy_number_variants = get_variants(client, analysis_type, 'copy_number_variation', analysis_id, cnv_count)
                manual_review_count = count_manual_review_labels(molecular_variants)
                manual_review_count.extend(count_manual_review_labels(copy_number_variants))
                result = '\t'.join([str(count) for count in manual_review_count])

            # Print result
            print((
                f"{analysis_reference}\t{analysis_type}\t{analysis_pipeline}\t{analysis_panel}\t"
                f"{analysis['createdOn'][0:10]}\t{analysis['lastUpdatedOn'][0:10]}\t{mol_var_count}\t{cnv_count}\t"
                f"{result}"
            ), file=database_file)
