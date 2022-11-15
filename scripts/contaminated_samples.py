import re
import os

from alissa_interpret_client.alissa_interpret import AlissaInterpret

import config


def parse_freemix_file(file_path='/mnt/bgarray/Illumina/Exomes/Contaminatie_scores/results/from_1_percent_contamination_freemix_scores.txt'):
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
                    print(sample, sample_data['run'], patient_analysis['targetPanelNames'][0], 'WARNING: No GATK lab result found in Alissa.', sep='\t')
                    continue
                gatk_data_file = client.get_data_file(gatk_lab_result['dataFileId'])

                print(sample, sample_data['run'], patient_analysis['targetPanelNames'][0], gatk_data_file['name'], gatk_lab_result['analysisVariantCount']['molecularVariantCount'], sep='\t')

                # Filter vcf on panel

                # Remove '_' and lower version.
                panel = patient_analysis['targetPanelNames'][0]
                panel = panel.split('_')
                if len(panel) > 1:
                    panel[1] = panel[1].lower()
                panel = ''.join(panel)
                panel = panel.split('/')
                panel = ''.join(panel)

                bed_file = 'bed_files/{panel}.bed'.format(panel=panel)
                command = (
                    '/diaggen/software/tools/bcftools-1.15.1/bcftools view -s {sample} -T {bed_file} {bgarray}/{run}/{vcf} | '
                    'ssh hpct01 cat ">{hpc_location}/{run}_{sample}.{panel}.vcf"'
                ).format(
                    sample=sample,
                    bgarray='/mnt/bgarray/Illumina/Exomes/',
                    run=sample_data['run'],
                    vcf=gatk_data_file['name'],
                    bed_file=bed_file,
                    hpc_location='/hpc/diaggen/projects/contaminated_samples',
                    panel=panel
                )

                if not os.path.isfile(bed_file):
                    print('WARNING: Bed file not found: {bed_file}'.format(bed_file=bed_file))
                elif sample_data['run'] not in gatk_data_file['name']:  # Not realy a warning, sample probably sequenced twice, just skip?
                    print('WARNING: VCF is from other run: {vcf}'.format(vcf=gatk_data_file['name']))
                # else:
                #     os.system(command)
                print(command)
                print()
