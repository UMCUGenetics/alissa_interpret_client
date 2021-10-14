"""manual_review_analyses.py - counts manual review variants in patient or inheritance (trio) analysis.

ToDo:
    - Discuss with Agilent about directly filtering 'manual review' variants. Exporting all variants takes a lot of time.
    - check large analyses (variant count > 20000)
    - Cleanup code (line length and duplicated code)
"""

from requests.exceptions import HTTPError
import time

from alissa_interpret_client.alissa_interpret import AlissaInterpret

client = AlissaInterpret(
    base_uri='',
    client_id='',
    client_secret='',
    username='',
    password=''
)

print(f"analysis_reference\tanalysis_type\tcreated_on\tlast_updated_on\tmanual_review_count")

for analysis in client.get_analyses(status='IN_PROGRESS', created_after='2021-01-01T00:00:00.000+0000'):
    if not analysis['classificationTreeName']:  # Skip analysis without classification tree
        continue

    if analysis['analysisType'] == 'PATIENT':
        patient_analysis = client.get_patient_analyses(analysis['id'])
        variant_count = sum([lab_result['analysisVariantCount']['molecularVariantCount'] for lab_result in patient_analysis['labResults']])
        if variant_count > 20000:  # skip large analyses
            print(f"{analysis['reference']}\t{analysis['analysisType']}\t{analysis['createdOn'][0:10]}\t{analysis['lastUpdatedOn'][0:10]}\tskipped_large_analysis")
            continue

        export_id = client.post_patient_analyses_variants_export(analysis['id'])['exportId']
        export = None

        while export is None:
            try:
                time.sleep(variant_count/100)  # 5 sec delay to request exported report.
                export = client.get_patient_analyses_variants_export(analysis['id'], export_id)
            except HTTPError:
                pass

        manual_review = ['Y,manual review' in variant['classificationTreeLabelsScore']['labels'] for variant in export]
        manual_review_count = sum(manual_review)

        print(f"{analysis['reference']}\t{analysis['analysisType']}\t{analysis['createdOn'][0:10]}\t{analysis['lastUpdatedOn'][0:10]}\t{manual_review_count}")

    elif analysis['analysisType'] == 'INHERITANCE':
        inheritance_analysis = client.get_inheritance_analyses(analysis['id'])
        variant_count = sum([lab_result['analysisVariantCount']['molecularVariantCount'] for lab_result in inheritance_analysis['labResults']])
        if variant_count > 20000:  # skip large analyses
            print(f"{analysis['reference']}\t{analysis['analysisType']}\t{analysis['createdOn'][0:10]}\t{analysis['lastUpdatedOn'][0:10]}\tskipped_large_analysis")
            continue

        export_id = client.post_inheritance_analyses_variants_export(analysis['id'])['exportId']
        export = None

        while export is None:
            try:
                time.sleep(variant_count/100)  # 5 sec delay to request exported report.
                export = client.get_inheritance_analyses_variants_export(analysis['id'], export_id)
            except HTTPError:
                pass

        manual_review = ['Y,manual review' in variant['classificationTreeLabelsScore']['labels'] for variant in export]
        manual_review_count = sum(manual_review)

        print(f"{analysis['reference']}\t{analysis['analysisType']}\t{analysis['createdOn'][0:10]}\t{analysis['lastUpdatedOn'][0:10]}\t{manual_review_count}")