import re

from alissa_interpret_client.alissa_interpret import AlissaInterpret

import config


def parse_freemix_file(file_path='/mnt/bgarray/Illumina/Exomes/Contaminatie_scores/results/from_4_percent_contamination_freemix_scores.txt'):
    samples = {}
    gender_options = {'F': 'FEMALE', 'M': 'MALE', 'O': 'UNKOWN'}
    with open(file_path) as freemix_file:
        freemix_file.readline()  # skip header

        for line in freemix_file:
            sample, freemix, run = line.strip().split()

            # Get gender and family
            sample_match = re.search('(U\d+)[CP]([FMO]).+', sample)

            samples[sample] = {
                'run': run,
                'freemix': freemix,
                'family': sample_match.group(1),
                'gender': gender_options[sample_match.group(2)]
            }
    return samples


if __name__ == '__main__':
    client = AlissaInterpret(
        base_uri=config.alissa_base_uri, client_id=config.alissa_client_id, client_secret=config.alissa_client_secret,
        username=config.alissa_username, password=config.alissa_password
    )

    samples = parse_freemix_file()

    for sample, sample_data in samples.items():
        patient = None

        alissa_patients = client.get_patients(family_identifier=sample_data['family'], gender=sample_data['gender'])
        if not alissa_patients:
            print(sample, sample_data['run'], 'WARNING: No patient found in Alissa.', sep='\t')
            continue
        elif len(alissa_patients) == 1:  # Lucky, only one patient with this family / gender combination
            patient = alissa_patients[0]
        else:  # Find correct patient
            for alissa_patient in alissa_patients:
                if sample in alissa_patient['comments']:
                    patient = alissa_patient

        patient_analyses = client.get_analyses_of_patient(patient['id'])
        if not patient_analyses:
            print(sample, sample_data['run'], 'WARNING: No patient analyses found in Alissa.', sep='\t')
        else:
            for patient_analysis in patient_analyses:
                if patient_analysis['analysisType'] == 'PATIENT':
                    analysis_data = client.get_patient_analyses(patient_analysis['id'])
                elif patient_analysis['analysisType'] == 'INHERITANCE':
                    analysis_data = client.get_inheritance_analyses(patient_analysis['id'])

                # Look for gatk (SNP/INDEL = molecularVariant) lab_result
                gatk_lab_result = None
                for lab_result in analysis_data['labResults']:
                    if(
                        lab_result['sampleIdentifier'] == sample
                        and lab_result['labResultVariantPositionCount']['molecularVariantCount'] > 0
                    ):
                        gatk_lab_result = lab_result
                        break
                if not gatk_lab_result:
                    print(sample, sample_data['run'], ','.join(patient_analysis['targetPanelNames']), 'WARNING: No GATK lab result found in Alissa.', sep='\t')
                    continue
                gatk_data_file = client.get_data_file(gatk_lab_result['dataFileId'])

                print(sample, sample_data['run'], ','.join(patient_analysis['targetPanelNames']), gatk_data_file['name'], gatk_lab_result['analysisVariantCount']['molecularVariantCount'], sep='\t')
